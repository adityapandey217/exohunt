#!/usr/bin/env python3
"""
Optimized parallel downloader for Kepler light curves.
Uses concurrent downloads, caching, and progress tracking for maximum performance.
"""

import lightkurve as lk
import pandas as pd
import argparse
import os
import warnings
import gc
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import time
import logging

# Global lock for FITS file operations
_fits_lock = threading.Lock()

# Suppress astropy/lightkurve warnings for cleaner output
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', module='astropy')
warnings.filterwarnings('ignore', module='lightkurve')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('download_log.txt'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def download_lc(kic, output_dir, skip_existing=True):
    """
    Download a single light curve with robust error handling.
    Thread-safe with global lock for FITS operations.
    
    Args:
        kic: Kepler Input Catalog ID
        output_dir: Directory to save FITS files
        skip_existing: Skip if file already exists
    
    Returns:
        Tuple of (kic, success, error_message)
    """
    import shutil
    
    output_path = Path(output_dir) / f"{kic}.fits"
    
    # Skip if already downloaded
    if skip_existing and output_path.exists():
        return (kic, 'skipped', None)
    
    def clear_kic_cache(kic_id):
        """Clear all cache entries for a specific KIC"""
        cache_dir = Path.home() / '.lightkurve' / 'cache'
        if cache_dir.exists():
            for item in cache_dir.glob(f'**/kplr{kic_id:09d}*'):
                try:
                    if item.is_dir():
                        shutil.rmtree(item, ignore_errors=True)
                    elif item.is_file():
                        item.unlink(missing_ok=True)
                except:
                    pass
    
    # Attempt download with retry logic
    max_attempts = 2
    for attempt in range(max_attempts):
        try:
            # Clear cache before retry attempt
            if attempt > 0:
                clear_kic_cache(kic)
            
            # Search for light curve
            search_result = lk.search_lightcurve(f"KIC {kic}", mission='Kepler')
            
            if len(search_result) == 0:
                return (kic, 'failed', 'No light curve found')
            
            # Download the light curve
            lc = search_result[0].download()
            
            # Thread-safe FITS file write operation
            with _fits_lock:
                temp_path = str(output_path) + '.tmp'
                lc.to_fits(temp_path, overwrite=True)
                
                # Explicitly close any file handles
                del lc
                gc.collect()
                
                # Rename temp file to final name (atomic operation)
                shutil.move(temp_path, str(output_path))
            
            return (kic, 'success', None)
            
        except Exception as e:
            error_str = str(e).lower()
            
            # Check if this is a retryable error (cache corruption or I/O issues)
            is_retryable = any(keyword in error_str for keyword in [
                'corrupt', 'interrupted', 'i/o operation', 'closed file'
            ])
            
            # If retryable and we have attempts left, try again
            if is_retryable and attempt < max_attempts - 1:
                continue
            
            # Clean up temp file if it exists
            temp_path = str(output_path) + '.tmp'
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
            
            # Return failure
            return (kic, 'failed', str(e))


def download_batch(kepids, output_dir='lightcurves', max_workers=10, skip_existing=True):
    """
    Download light curves in parallel with progress tracking.
    Uses ProcessPoolExecutor for better isolation and thread-safety.
    
    Args:
        kepids: List of Kepler IDs to download
        output_dir: Directory to save files
        max_workers: Number of parallel download processes
        skip_existing: Skip already downloaded files
    
    Returns:
        Dictionary with download statistics
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    stats = {'success': 0, 'failed': 0, 'skipped': 0, 'errors': []}
    
    logger.info(f"Starting download of {len(kepids)} light curves using {max_workers} workers")
    
    # Use ThreadPoolExecutor with thread-safe FITS operations
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all download tasks
        future_to_kic = {
            executor.submit(download_lc, kic, output_dir, skip_existing): kic 
            for kic in kepids
        }
        
        # Process results with progress bar
        with tqdm(total=len(kepids), desc="Downloading", unit="files") as pbar:
            for future in as_completed(future_to_kic):
                kic, status, error = future.result()
                
                if status == 'success':
                    stats['success'] += 1
                elif status == 'skipped':
                    stats['skipped'] += 1
                else:  # failed
                    stats['failed'] += 1
                    stats['errors'].append((kic, error))
                    logger.warning(f"Failed KIC {kic}: {error}")
                
                pbar.update(1)
                pbar.set_postfix({
                    'OK': stats['success'],
                    'Skip': stats['skipped'],
                    'Fail': stats['failed']
                })
    
    return stats


def main():
    parser = argparse.ArgumentParser(
        description='Download Kepler light curves in parallel',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--input', '-i',
        default='dataset/koi.csv',
        help='Path to CSV file with kepid column'
    )
    parser.add_argument(
        '--output', '-o',
        default='lightcurves',
        help='Output directory for FITS files'
    )
    parser.add_argument(
        '--workers', '-w',
        type=int,
        default=10,
        help='Number of parallel download workers (4-20 recommended)'
    )
    parser.add_argument(
        '--limit', '-l',
        type=int,
        default=None,
        help='Limit number of downloads (for testing)'
    )
    parser.add_argument(
        '--no-skip',
        action='store_true',
        help='Re-download existing files'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be downloaded without downloading'
    )
    
    args = parser.parse_args()
    
    # Load KepIDs from CSV
    logger.info(f"Loading KepIDs from {args.input}")
    df = pd.read_csv(args.input)
    kepids = df['kepid'].unique().tolist()
    
    # Apply limit if specified
    if args.limit:
        kepids = kepids[:args.limit]
        logger.info(f"Limited to first {args.limit} KepIDs")
    
    logger.info(f"Found {len(kepids)} unique KepIDs to process")
    
    # Dry run mode
    if args.dry_run:
        logger.info("DRY RUN MODE - No files will be downloaded")
        logger.info(f"Would download to: {args.output}")
        logger.info(f"Workers: {args.workers}")
        logger.info(f"Total KepIDs: {len(kepids)}")
        return
    
    # Run the download
    start_time = time.time()
    stats = download_batch(
        kepids,
        output_dir=args.output,
        max_workers=args.workers,
        skip_existing=not args.no_skip
    )
    elapsed = time.time() - start_time
    
    # Print summary
    logger.info("\n" + "="*60)
    logger.info("DOWNLOAD SUMMARY")
    logger.info("="*60)
    logger.info(f"Total processed:  {len(kepids)}")
    logger.info(f"Successfully downloaded: {stats['success']}")
    logger.info(f"Skipped (existing):      {stats['skipped']}")
    logger.info(f"Failed:                  {stats['failed']}")
    logger.info(f"Time elapsed:            {elapsed:.2f} seconds")
    logger.info(f"Average rate:            {len(kepids)/elapsed:.2f} files/sec")
    logger.info("="*60)
    
    # Save error log if any failures
    if stats['errors']:
        error_file = 'download_errors.txt'
        with open(error_file, 'w') as f:
            for kic, error in stats['errors']:
                f.write(f"KIC {kic}: {error}\n")
        logger.info(f"Error details saved to {error_file}")


if __name__ == "__main__":
    main()
