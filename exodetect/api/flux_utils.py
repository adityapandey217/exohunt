"""
Utility functions for extracting flux from lightkurve objects
"""
import numpy as np


def get_flux_from_lc(lc):
    """
    Robustly extract flux from a lightkurve object.
    Handles both uppercase and lowercase column names.
    
    Args:
        lc: Lightkurve light curve object
        
    Returns:
        numpy array of flux values
    """
    flux = None
    
    # Try different column names (case-insensitive, prioritize PDCSAP)
    preferred_order = ['pdcsap_flux', 'sap_flux', 'flux']
    
    for col_name in preferred_order:
        try:
            if col_name.lower() in [c.lower() for c in lc.colnames]:
                # Find the actual column name (preserving case)
                actual_col = [c for c in lc.colnames if c.lower() == col_name.lower()][0]
                flux = lc[actual_col].value
                return flux
        except (KeyError, AttributeError):
            continue
    
    # Fallback: try flux attribute
    if flux is None:
        try:
            flux = lc.flux.value
            return flux
        except AttributeError:
            pass
    
    # Last resort: use first numeric column
    if flux is None:
        for col in lc.colnames:
            try:
                data = lc[col].value
                if np.issubdtype(data.dtype, np.number) and len(data) > 100:
                    flux = data
                    return flux
            except:
                continue
    
    if flux is None:
        raise ValueError("Could not extract flux data from light curve")
    
    return flux


def get_time_from_lc(lc):
    """
    Robustly extract time from a lightkurve object.
    
    Args:
        lc: Lightkurve light curve object
        
    Returns:
        numpy array of time values
    """
    try:
        if hasattr(lc, 'time') and lc.time is not None:
            return lc.time.value
    except:
        pass
    
    # Fallback: create index
    try:
        flux = get_flux_from_lc(lc)
        return np.arange(len(flux))
    except:
        return np.arange(len(lc))
