"""
Core utilities for loading the trained model and making predictions
"""
import os
import time
import numpy as np
import torch
import torch.nn as nn
import joblib
import lightkurve as lk
from pathlib import Path
from typing import Dict, Tuple, Optional, List
import re


# Model architecture (same as training notebook)
class HybridExoNet(nn.Module):
    def __init__(self, seq_len, tab_dim, num_classes=3):
        super().__init__()
        # Light curve CNN encoder
        self.cnn = nn.Sequential(
            nn.Conv1d(1, 32, kernel_size=11, padding=5),
            nn.ReLU(),
            nn.MaxPool1d(4),
            nn.Conv1d(32, 64, kernel_size=9, padding=4),
            nn.ReLU(),
            nn.MaxPool1d(4),
            nn.Conv1d(64, 128, kernel_size=7, padding=3),
            nn.ReLU(),
            nn.AdaptiveAvgPool1d(1),
            nn.Flatten()
        )

        # Fully connected (light curve)
        self.lc_fc = nn.Sequential(
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Dropout(0.3)
        )

        # Tabular MLP
        self.tab_fc = nn.Sequential(
            nn.Linear(tab_dim, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU()
        )

        # Fusion Head
        self.head = nn.Sequential(
            nn.Linear(128 + 32, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, num_classes)
        )

    def forward(self, x_lc, x_tab):
        a = self.cnn(x_lc)
        a = self.lc_fc(a)
        b = self.tab_fc(x_tab)
        c = torch.cat([a, b], dim=1)
        out = self.head(c)
        return out


class ExoplanetPredictor:
    """Main predictor class for inference"""
    
    CLASS_NAMES = {
        0: 'FALSE POSITIVE',
        1: 'CANDIDATE',
        2: 'CONFIRMED'
    }
    
    def __init__(
        self,
        model_path: str,
        scaler_path: str,
        features_path: str,
        seq_len: int = 2000,
        device: Optional[str] = None
    ):
        """
        Initialize the predictor
        
        Args:
            model_path: Path to trained .pth model
            scaler_path: Path to StandardScaler joblib file
            features_path: Path to feature list joblib file
            seq_len: Sequence length for light curves
            device: 'cuda', 'mps', 'cpu', or None (auto-detect)
        """
        self.seq_len = seq_len
        self.model_version = "v1.0"
        
        # Device selection
        if device is None:
            if torch.backends.mps.is_available():
                self.device = torch.device("mps")
            elif torch.cuda.is_available():
                self.device = torch.device("cuda")
            else:
                self.device = torch.device("cpu")
        else:
            self.device = torch.device(device)
        
        print(f"Using device: {self.device}")
        
        # Load scaler and features
        self.scaler = joblib.load(scaler_path)
        self.feature_cols = joblib.load(features_path)
        self.tab_dim = len(self.feature_cols)
        
        # Load model
        self.model = HybridExoNet(seq_len, self.tab_dim, num_classes=3)
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()
        
        print(f"Model loaded: {len(self.feature_cols)} features, seq_len={seq_len}")
    
    def process_light_curve(
        self,
        fits_path: str,
        cache_dir: Optional[str] = None
    ) -> np.ndarray:
        """
        Process FITS file into normalized flux array
        
        Args:
            fits_path: Path to FITS file
            cache_dir: Optional cache directory for .npy files
            
        Returns:
            Normalized flux array of length seq_len
        """
        # Check cache first
        if cache_dir:
            base_match = re.search(r'(\d{6,9})', os.path.basename(fits_path))
            if base_match:
                cache_path = os.path.join(cache_dir, f"{base_match.group(1)}.npy")
                if os.path.exists(cache_path):
                    return np.load(cache_path)
        
        # Read FITS file
        try:
            lc = lk.read(fits_path)
        except Exception as e:
            print(f"Error reading {fits_path}: {e}")
            return np.ones(self.seq_len, dtype=np.float32)
        
        # Extract flux (prefer PDCSAP_FLUX)
        arr = None
        try:
            if hasattr(lc, "PDCSAP_FLUX") and lc.PDCSAP_FLUX is not None:
                arr = lc.PDCSAP_FLUX.value
            elif hasattr(lc, "SAP_FLUX") and lc.SAP_FLUX is not None:
                arr = lc.SAP_FLUX.value
            else:
                arr = getattr(lc, "flux", None)
                if arr is None:
                    arr = np.zeros(self.seq_len)
        except Exception:
            arr = np.zeros(self.seq_len)
        
        arr = np.asarray(arr, dtype=np.float32)
        
        # Normalize
        if np.all(np.isnan(arr)) or np.nanmax(np.abs(arr)) == 0:
            arr = np.ones(self.seq_len, dtype=np.float32)
        else:
            med = np.nanmedian(arr)
            if not np.isfinite(med) or med == 0:
                med = 1.0
            arr = np.nan_to_num(arr / med, nan=0.0, posinf=0.0, neginf=0.0)
        
        # Pad/truncate
        if len(arr) < self.seq_len:
            padded = np.ones(self.seq_len, dtype=np.float32)
            padded[:len(arr)] = arr
            arr = padded
        else:
            arr = arr[:self.seq_len]
        
        # Cache if requested
        if cache_dir and base_match:
            os.makedirs(cache_dir, exist_ok=True)
            np.save(cache_path, arr)
        
        return arr
    
    def prepare_tabular_features(self, koi_params: Dict[str, float]) -> np.ndarray:
        """
        Prepare and scale tabular features
        
        Args:
            koi_params: Dictionary of KOI parameter names to values
            
        Returns:
            Scaled feature array
        """
        # Build feature vector in correct order
        features = []
        for col in self.feature_cols:
            val = koi_params.get(col, np.nan)
            if val is None or (isinstance(val, float) and np.isnan(val)):
                # Use median from training data (which is 0 after scaling)
                val = 0.0
            features.append(float(val))
        
        features = np.array(features, dtype=np.float32).reshape(1, -1)
        
        # Scale
        features_scaled = self.scaler.transform(features)
        return features_scaled[0]
    
    def predict(
        self,
        fits_path: str,
        koi_params: Optional[Dict[str, float]] = None,
        cache_dir: Optional[str] = None
    ) -> Dict:
        """
        Make a prediction on a single FITS file
        
        Args:
            fits_path: Path to FITS file
            koi_params: Optional dictionary of KOI parameters
            cache_dir: Optional cache directory
            
        Returns:
            Dictionary with prediction results
        """
        start_time = time.time()
        
        # Process light curve
        flux = self.process_light_curve(fits_path, cache_dir)
        
        # Prepare tabular features (use zeros if not provided)
        if koi_params is None:
            koi_params = {}
        tab_features = self.prepare_tabular_features(koi_params)
        
        # Convert to tensors
        lc_tensor = torch.from_numpy(flux).float().unsqueeze(0).unsqueeze(0)  # (1, 1, seq_len)
        tab_tensor = torch.from_numpy(tab_features).float().unsqueeze(0)  # (1, tab_dim)
        
        # Move to device
        lc_tensor = lc_tensor.to(self.device)
        tab_tensor = tab_tensor.to(self.device)
        
        # Inference
        with torch.no_grad():
            logits = self.model(lc_tensor, tab_tensor)
            probs = torch.softmax(logits, dim=1).cpu().numpy()[0]
        
        # Get predicted class
        predicted_class = int(np.argmax(probs))
        confidence = float(probs[predicted_class])
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        return {
            'predicted_class': predicted_class,
            'predicted_class_name': self.CLASS_NAMES[predicted_class],
            'probabilities': {
                'FALSE_POSITIVE': float(probs[0]),
                'CANDIDATE': float(probs[1]),
                'CONFIRMED': float(probs[2]),
            },
            'confidence': confidence,
            'processing_time_ms': processing_time_ms,
            'model_version': self.model_version,
            'features_used': koi_params,
        }
    
    def predict_batch(
        self,
        fits_paths: List[str],
        koi_params_list: Optional[List[Dict[str, float]]] = None,
        cache_dir: Optional[str] = None,
        batch_size: int = 16
    ) -> List[Dict]:
        """
        Make predictions on multiple FITS files
        
        Args:
            fits_paths: List of paths to FITS files
            koi_params_list: Optional list of KOI parameter dicts (same length as fits_paths)
            cache_dir: Optional cache directory
            batch_size: Batch size for inference
            
        Returns:
            List of prediction dictionaries
        """
        if koi_params_list is None:
            koi_params_list = [{}] * len(fits_paths)
        
        results = []
        
        for i in range(0, len(fits_paths), batch_size):
            batch_fits = fits_paths[i:i+batch_size]
            batch_params = koi_params_list[i:i+batch_size]
            
            for fits_path, koi_params in zip(batch_fits, batch_params):
                try:
                    result = self.predict(fits_path, koi_params, cache_dir)
                    result['fits_path'] = fits_path
                    result['success'] = True
                except Exception as e:
                    result = {
                        'fits_path': fits_path,
                        'success': False,
                        'error': str(e)
                    }
                results.append(result)
        
        return results


def extract_light_curve_metadata(fits_path: str) -> Dict:
    """
    Extract metadata from FITS file
    
    Returns:
        Dictionary with metadata (duration, points, gaps, etc.)
    """
    try:
        lc = lk.read(fits_path)
        
        # Get flux
        if hasattr(lc, "PDCSAP_FLUX") and lc.PDCSAP_FLUX is not None:
            flux = lc.PDCSAP_FLUX.value
            flux_type = 'PDCSAP_FLUX'
        elif hasattr(lc, "SAP_FLUX") and lc.SAP_FLUX is not None:
            flux = lc.SAP_FLUX.value
            flux_type = 'SAP_FLUX'
        else:
            flux = None
            flux_type = 'unknown'
        
        if flux is not None:
            flux_points = len(flux)
            valid_points = np.sum(~np.isnan(flux))
            gaps_detected = flux_points - valid_points
            
            # Get time range
            if hasattr(lc, 'time'):
                time_array = lc.time.value
                duration_days = float(np.nanmax(time_array) - np.nanmin(time_array))
            else:
                duration_days = None
            
            # Data quality score (fraction of valid points)
            data_quality_score = valid_points / flux_points if flux_points > 0 else 0.0
        else:
            flux_points = None
            duration_days = None
            gaps_detected = None
            data_quality_score = 0.0
        
        # Try to extract KepID
        kepid = None
        if hasattr(lc, 'meta') and 'KEPLERID' in lc.meta:
            kepid = int(lc.meta['KEPLERID'])
        
        return {
            'kepid': kepid,
            'flux_points': flux_points,
            'duration_days': duration_days,
            'gaps_detected': gaps_detected,
            'data_quality_score': data_quality_score,
            'flux_type': flux_type,
        }
    
    except Exception as e:
        return {
            'error': str(e),
            'kepid': None,
            'flux_points': None,
            'duration_days': None,
            'gaps_detected': None,
            'data_quality_score': 0.0,
            'flux_type': 'error',
        }
