# Example Light Curves

This directory contains curated FITS files used for the "Random Example" feature in the ExoHunt application.

## Files Included

| KepID    | Disposition     | Period (days) | File Size | Description |
|----------|----------------|---------------|-----------|-------------|
| 10797460 | CONFIRMED      | ~9.48         | 0.07 MB   | Kepler-444 system |
| 10854555 | CONFIRMED      | ~2.52         | 0.18 MB   | Confirmed exoplanet |
| 10872983 | CONFIRMED      | ~11.09        | 0.18 MB   | Confirmed exoplanet |
| 10811496 | CANDIDATE      | ~19.89        | 0.07 MB   | Exoplanet candidate |
| 11818800 | CANDIDATE      | ~40.41        | 0.07 MB   | Exoplanet candidate |
| 11918099 | CANDIDATE      | ~7.24         | 0.07 MB   | Exoplanet candidate |
| 10848459 | FALSE POSITIVE | ~1.73         | 0.07 MB   | Not a planet |
| 6721123  | FALSE POSITIVE | ~7.36         | 1.82 MB   | Not a planet |
| 10419211 | FALSE POSITIVE | ~11.52        | 0.07 MB   | Not a planet |

## Purpose

These files provide:
- **Instant loading** for demo/testing purposes
- **Balanced examples** across all three classification categories
- **Pre-validated data** to ensure reliable model predictions
- **Local availability** to avoid MAST download delays during demos

## Usage

The backend API automatically checks this directory first when serving random examples. If a file exists here, it loads instantly. Otherwise, it falls back to downloading from NASA MAST archive using lightkurve.

## Total Size

Approximately **2.6 MB** for all 9 FITS files.

## Data Source

All FITS files are from the Kepler mission, downloaded from NASA MAST archive (Mikulski Archive for Space Telescopes).
