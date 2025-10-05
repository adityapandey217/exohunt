#!/usr/bin/env python3
"""
Simple test script for exoplanet prediction using local FITS files and KOI data.

Usage:
    python test_prediction.py 10797460
    python test_prediction.py 10854555 10872983 11918099
"""

import sys
import os
import time
from pathlib import Path
import pandas as pd

# Add Django project to path
sys.path.insert(0, str(Path(__file__).parent / 'exodetect'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exodetect.settings')
import django
django.setup()

from api.inference import ExoplanetPredictor
import lightkurve as lk


def load_koi_parameters(kepid: int) -> dict:
    """Load KOI parameters from dataset CSV."""
    koi_csv = Path(__file__).parent / 'dataset' / 'koi.csv'
    
    if not koi_csv.exists():
        raise FileNotFoundError(f"KOI dataset not found at {koi_csv}")
    
    df = pd.read_csv(koi_csv)
    koi_data = df[df['kepid'] == kepid]
    
    if koi_data.empty:
        raise ValueError(f"No KOI data found for KepID {kepid}")
    
    row = koi_data.iloc[0]
    
    # Helper to safely convert values
    def safe_float(value):
        return float(value) if pd.notna(value) else None
    
    def safe_int(value):
        return int(value) if pd.notna(value) else None
    
    def safe_str(value):
        return str(value) if pd.notna(value) and value != '' else None
    
    params = {
        'koi_period': safe_float(row.get('koi_period')),
        'koi_duration': safe_float(row.get('koi_duration')),
        'koi_depth': safe_float(row.get('koi_depth')),
        'koi_prad': safe_float(row.get('koi_prad')),
        'koi_ror': safe_float(row.get('koi_ror')),
        'koi_model_snr': safe_float(row.get('koi_model_snr')),
        'koi_num_transits': safe_int(row.get('koi_num_transits')),
        'koi_steff': safe_float(row.get('koi_steff')),
        'koi_slogg': safe_float(row.get('koi_slogg')),
        'koi_srad': safe_float(row.get('koi_srad')),
        'koi_smass': safe_float(row.get('koi_smass')),
        'koi_kepmag': safe_float(row.get('koi_kepmag')),
        'koi_insol': safe_float(row.get('koi_insol')),
        'koi_dor': safe_float(row.get('koi_dor')),
        'koi_count': safe_int(row.get('koi_count')),
        # 'koi_score': REMOVED - data leakage (0.89 correlation with disposition)
    }
    
    # Additional info for display
    params['_disposition'] = safe_str(row.get('koi_disposition'))
    params['_kepler_name'] = safe_str(row.get('kepler_name'))
    
    return params


def load_fits_file(kepid: int) -> str:
    """Find and return path to local FITS file."""
    # Check multiple possible locations
    possible_paths = [
        Path(__file__).parent / 'lightcurves' / f'{kepid}.fits',
        Path(__file__).parent / 'lightcurves_cache' / f'{kepid}.fits',
    ]
    
    for fits_path in possible_paths:
        if fits_path.exists():
            return str(fits_path)
    
    raise FileNotFoundError(
        f"FITS file for KepID {kepid} not found in:\n" +
        "\n".join(f"  - {p}" for p in possible_paths)
    )


def predict_exoplanet(kepid: int, verbose: bool = True):
    """
    Make prediction for a given KepID using local files.
    
    Args:
        kepid: Kepler ID to predict
        verbose: Print detailed output
    
    Returns:
        Dictionary with prediction results
    """
    if verbose:
        print(f"\n{'='*70}")
        print(f"🔭 Predicting for KepID: {kepid}")
        print(f"{'='*70}")
    
    # Load KOI parameters
    if verbose:
        print("\n1️⃣  Loading KOI parameters from dataset...")
    
    try:
        params = load_koi_parameters(kepid)
        actual_disposition = params.pop('_disposition', None)
        kepler_name = params.pop('_kepler_name', None)
        
        if verbose:
            print(f"   ✅ Parameters loaded")
            print(f"   📊 Actual Classification: {actual_disposition}")
            if kepler_name:
                print(f"   🪐 Kepler Name: {kepler_name}")
    except Exception as e:
        print(f"   ❌ Error loading parameters: {e}")
        return None
    
    # Load FITS file
    if verbose:
        print("\n2️⃣  Loading light curve from local FITS file...")
    
    try:
        fits_path = load_fits_file(kepid)
        if verbose:
            print(f"   ✅ Found: {fits_path}")
        
        # Load with lightkurve
        lc = lk.read(fits_path)
        if verbose:
            print(f"   📈 Light curve loaded: {len(lc)} data points")
    except Exception as e:
        print(f"   ❌ Error loading FITS: {e}")
        return None
    
    # Make prediction
    if verbose:
        print("\n3️⃣  Running model prediction...")
    
    try:
        start_time = time.time()
        
        # Initialize predictor with model paths
        base_dir = Path(__file__).parent
        model_path = base_dir / 'training' / 'exoplanet_hybrid.pth'
        scaler_path = base_dir / 'training' / 'koi_scaler.joblib'
        features_path = base_dir / 'training' / 'tab_features_list.joblib'
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found at {model_path}")
        
        predictor = ExoplanetPredictor(
            model_path=str(model_path),
            scaler_path=str(scaler_path),
            features_path=str(features_path),
            seq_len=2000
        )
        
        # Make prediction using FITS file path
        result = predictor.predict(
            fits_path=fits_path,
            koi_params=params
        )
        
        elapsed = time.time() - start_time
        
        if verbose:
            print(f"   ✅ Prediction completed in {elapsed:.2f}s")
        
        # Display results
        predicted_class = result['predicted_class_name']
        confidence = result['confidence']
        probabilities = result['probabilities']
        
        if verbose:
            print(f"\n{'='*70}")
            print(f"📊 RESULTS")
            print(f"{'='*70}")
            print(f"Predicted Class:  {predicted_class}")
            print(f"Confidence:       {confidence*100:.2f}%")
            print(f"\nClass Probabilities:")
            for cls, prob in probabilities.items():
                bar_length = int(prob * 40)
                bar = '█' * bar_length + '░' * (40 - bar_length)
                print(f"  {cls:15} {bar} {prob*100:.2f}%")
            
            # Compare with actual
            if actual_disposition:
                match = '✅ CORRECT' if predicted_class == actual_disposition else '❌ INCORRECT'
                print(f"\nActual:           {actual_disposition}")
                print(f"Match:            {match}")
            
            print(f"{'='*70}\n")
        
        return {
            'kepid': kepid,
            'predicted_class': predicted_class,
            'confidence': confidence,
            'probabilities': probabilities,
            'actual_disposition': actual_disposition,
            'kepler_name': kepler_name,
            'processing_time': elapsed,
            'correct': predicted_class == actual_disposition if actual_disposition else None
        }
        
    except Exception as e:
        print(f"   ❌ Error during prediction: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python test_prediction.py <kepid1> [kepid2] [kepid3] ...")
        print("\nExample:")
        print("  python test_prediction.py 10797460")
        print("  python test_prediction.py 10854555 10872983 11918099")
        print("\nCurated examples available:")
        print("  CONFIRMED:      10797460, 10854555, 10872983")
        print("  CANDIDATE:      10811496, 11818800, 11918099")
        print("  FALSE POSITIVE: 10848459, 6721123, 10419211")
        sys.exit(1)
    
    kepids = []
    for arg in sys.argv[1:]:
        try:
            kepids.append(int(arg))
        except ValueError:
            print(f"Error: '{arg}' is not a valid integer KepID")
            sys.exit(1)
    
    # Run predictions
    results = []
    for kepid in kepids:
        result = predict_exoplanet(kepid, verbose=True)
        if result:
            results.append(result)
    
    # Summary if multiple predictions
    if len(results) > 1:
        print(f"\n{'='*70}")
        print(f"📈 SUMMARY ({len(results)} predictions)")
        print(f"{'='*70}")
        
        correct = sum(1 for r in results if r.get('correct') is True)
        incorrect = sum(1 for r in results if r.get('correct') is False)
        unknown = sum(1 for r in results if r.get('correct') is None)
        
        print(f"\nAccuracy: {correct}/{correct+incorrect} correct ({correct/(correct+incorrect)*100:.1f}%)" if (correct+incorrect) > 0 else "")
        print(f"\nDetailed Results:")
        for r in results:
            status = '✅' if r.get('correct') else ('❌' if r.get('correct') is False else '❓')
            print(f"  {status} KepID {r['kepid']:8} - Predicted: {r['predicted_class']:15} "
                  f"(Confidence: {r['confidence']*100:5.1f}%) - Actual: {r.get('actual_disposition', 'N/A')}")
        
        avg_time = sum(r['processing_time'] for r in results) / len(results)
        print(f"\nAverage processing time: {avg_time:.2f}s")
        print(f"{'='*70}\n")


if __name__ == '__main__':
    main()
