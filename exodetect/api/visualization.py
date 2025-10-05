"""
Light curve visualization and analysis utilities
"""
import numpy as np
import lightkurve as lk
from typing import Dict, List, Tuple, Optional
from scipy import signal
from scipy.stats import median_abs_deviation
import plotly.graph_objects as go
from .flux_utils import get_flux_from_lc, get_time_from_lc


def create_interactive_plot(
    fits_path: str,
    flux_array: Optional[np.ndarray] = None,
    highlighted_regions: Optional[List[Tuple[float, float]]] = None,
    title: Optional[str] = None
) -> str:
    """
    Create interactive Plotly visualization as HTML string for a light curve
    
    Args:
        fits_path: Path to FITS file
        flux_array: Optional preprocessed flux array
        highlighted_regions: List of (start, end) time ranges to highlight
        title: Optional plot title
        
    Returns:
        HTML string with embedded Plotly plot
    """
    # Load light curve
    lc = lk.read(fits_path)
    
    # Get time and flux using helper functions
    time = get_time_from_lc(lc)
    
    if flux_array is not None:
        flux = flux_array
    else:
        flux = get_flux_from_lc(lc)
    
    # Remove NaNs for plotting
    valid_mask = ~np.isnan(flux)
    time = time[valid_mask]
    flux = flux[valid_mask]
    
    # Convert to native endianness for Plotly/kaleido compatibility
    time = np.asarray(time, dtype=np.float64)
    flux = np.asarray(flux, dtype=np.float64)
    
    # Create Plotly figure
    fig = go.Figure()
    
    # Add main light curve trace
    fig.add_trace(go.Scattergl(
        x=time,
        y=flux,
        mode='markers',
        marker=dict(
            size=2,
            color='rgba(59, 130, 246, 0.6)',
            line=dict(width=0)
        ),
        name='Flux',
        hovertemplate='Time: %{x:.2f}<br>Flux: %{y:.6f}<extra></extra>'
    ))
    
    # Add highlighted regions if provided
    if highlighted_regions:
        for i, (start, end) in enumerate(highlighted_regions):
            fig.add_vrect(
                x0=start, x1=end,
                fillcolor="red", opacity=0.2,
                layer="below", line_width=0,
                annotation_text=f"Transit {i+1}",
                annotation_position="top left"
            )
    
    # Update layout
    fig.update_layout(
        title=dict(
            text=title or 'Light Curve',
            font=dict(size=20, color='#1f2937')
        ),
        xaxis=dict(
            title='Time (BKJD - days)',
            gridcolor='#e5e7eb',
            showgrid=True,
            zeroline=False
        ),
        yaxis=dict(
            title='Normalized Flux',
            gridcolor='#e5e7eb',
            showgrid=True,
            zeroline=False
        ),
        plot_bgcolor='#f9fafb',
        paper_bgcolor='#ffffff',
        hovermode='closest',
        showlegend=False,
        height=500,
        width=1200,
        margin=dict(l=60, r=30, t=60, b=60)
    )
    
    # Return as PNG image bytes
    img_bytes = fig.to_image(format='png', width=1200, height=500, scale=2)
    return img_bytes


def detect_transits(
    fits_path: str,
    period_min: float = 0.5,
    period_max: float = 50.0,
    snr_threshold: float = 7.0
) -> List[Dict]:
    """
    Detect transit events in a light curve using BLS (Box Least Squares)
    
    Args:
        fits_path: Path to FITS file
        period_min: Minimum period to search (days)
        period_max: Maximum period to search (days)
        snr_threshold: Minimum SNR for detection
        
    Returns:
        List of detected transit dictionaries
    """
    try:
        lc = lk.read(fits_path)
        
        # Flatten light curve to remove stellar variability
        lc_flat = lc.flatten(window_length=401)
        
        # Run BLS periodogram
        from astropy.timeseries import BoxLeastSquares
        
        time = get_time_from_lc(lc_flat)
        flux = get_flux_from_lc(lc_flat)
        
        # Remove NaNs
        valid = ~np.isnan(flux)
        time = time[valid]
        flux = flux[valid]
        
        # BLS
        model = BoxLeastSquares(time, flux)
        periods = np.linspace(period_min, period_max, 10000)
        
        results = model.power(periods, 0.1)  # 0.1 = duration in fraction of period
        
        # Find peak
        best_period = results.period[np.argmax(results.power)]
        best_power = np.max(results.power)
        
        # Calculate SNR (power relative to noise)
        noise_level = np.median(results.power)
        snr = (best_power - noise_level) / median_abs_deviation(results.power)
        
        transits = []
        
        if snr > snr_threshold:
            # Find transit times
            stats = model.compute_stats(best_period, 0.1, results.transit_time[np.argmax(results.power)])
            
            transit = {
                'period_days': float(best_period),
                'period_confidence': float(snr / snr_threshold),  # normalized SNR
                'snr': float(snr),
                'depth_ppm': float(stats['depth'] * 1e6) if 'depth' in stats else None,
                'duration_hours': float(stats['duration'] * 24) if 'duration' in stats else None,
                'detection_algorithm': 'BLS',
                'is_anomaly': False,
            }
            transits.append(transit)
        
        return transits
    
    except Exception as e:
        print(f"Transit detection error: {e}")
        return []


def phase_fold_light_curve(
    fits_path: str,
    period: float,
    epoch: Optional[float] = None
) -> Dict:
    """
    Phase-fold a light curve by a given period
    
    Args:
        fits_path: Path to FITS file
        period: Orbital period in days
        epoch: Reference time (default: first time point)
        
    Returns:
        Dictionary with phase and flux arrays
    """
    lc = lk.read(fits_path)
    
    time = get_time_from_lc(lc)
    flux = get_flux_from_lc(lc)
    
    # Remove NaNs
    valid = ~np.isnan(flux)
    time = time[valid]
    flux = flux[valid]
    
    if epoch is None:
        epoch = time[0]
    
    # Calculate phase (0 to 1)
    phase = ((time - epoch) % period) / period
    
    # Sort by phase
    sort_idx = np.argsort(phase)
    phase = phase[sort_idx]
    flux = flux[sort_idx]
    
    return {
        'phase': phase.tolist(),
        'flux': flux.tolist(),
        'period': period,
        'epoch': epoch,
    }


def calculate_periodogram(fits_path: str) -> Dict:
    """
    Calculate Lomb-Scargle periodogram for period analysis
    
    Args:
        fits_path: Path to FITS file
        
    Returns:
        Dictionary with periods and power
    """
    lc = lk.read(fits_path)
    
    time = get_time_from_lc(lc)
    flux = get_flux_from_lc(lc)
    
    # Remove NaNs and normalize
    valid = ~np.isnan(flux)
    time = time[valid]
    flux = flux[valid]
    flux = (flux - np.mean(flux)) / np.std(flux)
    
    # Lomb-Scargle
    from scipy.signal import lombscargle
    
    # Frequency range (1/50 days to 1/0.5 days)
    freqs = np.linspace(1/50, 1/0.5, 10000)
    power = lombscargle(time, flux, freqs * 2 * np.pi)
    
    # Convert to periods
    periods = 1 / freqs
    
    # Find peaks
    peak_idx = np.argmax(power)
    best_period = periods[peak_idx]
    best_power = power[peak_idx]
    
    return {
        'periods': periods.tolist(),
        'power': power.tolist(),
        'best_period': float(best_period),
        'best_power': float(best_power),
    }


def detect_anomalies(
    fits_path: str,
    sigma_threshold: float = 5.0
) -> List[Dict]:
    """
    Detect outliers/anomalies in light curve
    
    Args:
        fits_path: Path to FITS file
        sigma_threshold: Number of sigma for outlier detection
        
    Returns:
        List of anomaly dictionaries
    """
    lc = lk.read(fits_path)
    
    time = get_time_from_lc(lc)
    flux = get_flux_from_lc(lc)
    
    # Remove NaNs
    valid = ~np.isnan(flux)
    time = time[valid]
    flux = flux[valid]
    
    # Median filtering to remove slow trends
    flux_smooth = signal.medfilt(flux, kernel_size=51)
    residuals = flux - flux_smooth
    
    # Sigma clipping
    mad = median_abs_deviation(residuals, nan_policy='omit')
    sigma = 1.4826 * mad  # Convert MAD to standard deviation
    
    anomaly_mask = np.abs(residuals) > sigma_threshold * sigma
    anomaly_indices = np.where(anomaly_mask)[0]
    
    anomalies = []
    for idx in anomaly_indices:
        anomalies.append({
            'time': float(time[idx]),
            'flux': float(flux[idx]),
            'deviation_sigma': float(np.abs(residuals[idx]) / sigma),
            'type': 'outlier',
        })
    
    return anomalies


def compare_light_curves(fits_paths: List[str], labels: Optional[List[str]] = None) -> Dict:
    """
    Prepare data for comparing multiple light curves side-by-side
    
    Args:
        fits_paths: List of paths to FITS files
        labels: Optional labels for each curve
        
    Returns:
        Dictionary with data for all curves
    """
    if labels is None:
        labels = [f"Curve {i+1}" for i in range(len(fits_paths))]
    
    curves_data = []
    
    for fits_path, label in zip(fits_paths, labels):
        try:
            lc = lk.read(fits_path)
            time = get_time_from_lc(lc)
            flux = get_flux_from_lc(lc)
            
            # Remove NaNs
            valid = ~np.isnan(flux)
            time = time[valid]
            flux = flux[valid]
            
            # Normalize
            flux = flux / np.median(flux)
            
            curves_data.append({
                'label': label,
                'time': time.tolist(),
                'flux': flux.tolist(),
                'points': len(time),
            })
        except Exception as e:
            curves_data.append({
                'label': label,
                'error': str(e),
            })
    
    return {'curves': curves_data}
