"""
Caching utilities for FITS files to avoid repeated downloads
"""
import os
import time
from pathlib import Path
from typing import Optional
import hashlib

# Cache directory for downloaded FITS files
CACHE_DIR = Path(__file__).parent.parent.parent / 'lightcurves_cache'
CACHE_DIR.mkdir(exist_ok=True)

# Cache metadata: kepid -> (filepath, timestamp)
_cache = {}
CACHE_EXPIRY = 3600 * 24  # 24 hours


def get_cached_fits(kepid: int) -> Optional[str]:
    """
    Get cached FITS file path if it exists and is not expired.
    
    Args:
        kepid: Kepler ID
        
    Returns:
        Path to cached FITS file or None if not in cache
    """
    cache_path = CACHE_DIR / f"{kepid}.fits"
    
    # Check if file exists and is recent
    if cache_path.exists():
        age = time.time() - cache_path.stat().st_mtime
        if age < CACHE_EXPIRY:
            return str(cache_path)
    
    return None


def save_to_cache(kepid: int, fits_path: str) -> str:
    """
    Save FITS file to cache.
    
    Args:
        kepid: Kepler ID
        fits_path: Path to source FITS file
        
    Returns:
        Path to cached file
    """
    import shutil
    
    cache_path = CACHE_DIR / f"{kepid}.fits"
    
    # Copy file to cache
    shutil.copy2(fits_path, cache_path)
    
    return str(cache_path)


def clear_cache(max_age_hours: Optional[int] = None):
    """
    Clear old cached files.
    
    Args:
        max_age_hours: Remove files older than this (hours). None = remove all
    """
    if max_age_hours is None:
        # Remove all
        import shutil
        shutil.rmtree(CACHE_DIR, ignore_errors=True)
        CACHE_DIR.mkdir(exist_ok=True)
        return
    
    # Remove old files
    cutoff_time = time.time() - (max_age_hours * 3600)
    for fits_file in CACHE_DIR.glob('*.fits'):
        if fits_file.stat().st_mtime < cutoff_time:
            fits_file.unlink(missing_ok=True)


def get_cache_stats():
    """Get cache statistics"""
    files = list(CACHE_DIR.glob('*.fits'))
    total_size = sum(f.stat().st_size for f in files)
    
    return {
        'files': len(files),
        'size_mb': total_size / (1024 * 1024),
        'cache_dir': str(CACHE_DIR)
    }
