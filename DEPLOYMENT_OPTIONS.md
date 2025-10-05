# ⚠️ Heroku Deployment Challenge: Slug Size Limit

## Problem

The deployment failed because the compiled slug size is **3.1GB**, which exceeds Heroku's **500MB limit**.

```
remote:  !     Compiled slug size: 3.1G is too large (max is 500M).
remote:  !     See: http://devcenter.heroku.com/articles/slug-size
```

## Root Cause

PyTorch with CUDA support includes massive NVIDIA libraries:
- `torch-2.7.1` with CUDA: ~821 MB
- NVIDIA CUDA libraries: ~2.3 GB total
  - nvidia-cublas-cu12: 393 MB
  - nvidia-cudnn-cu12: 571 MB
  - nvidia-cusparse-cu12: 216 MB  
  - nvidia-cusolver-cu12: 158 MB
  - nvidia-cufft-cu12: 200 MB
  - nvidia-nccl-cu12: 201 MB
  - triton: 155 MB
- lightkurve + astropy dependencies: ~300 MB

**Total: ~3.5 GB** (way over 500 MB limit!)

## Solutions

### Option 1: CPU-Only PyTorch (Recommended for Heroku) ✅

Use `requirements-heroku.txt` with CPU-only PyTorch:

```bash
# Copy CPU-only requirements
cp requirements-heroku.txt requirements.txt

# Redeploy
git add requirements.txt
git commit -m "Use CPU-only PyTorch for Heroku"
git push heroku main
```

**Pros:**
- Fits within Heroku's 500MB limit (~800MB total)
- Still functional for predictions
- Free/cheap hosting

**Cons:**
- Slower inference (~2-5x slower than GPU)
- Still might be close to the limit

**Estimated slug size:** ~600-800 MB (should fit!)

### Option 2: Remove Lightkurve (Minimal Dependencies) ✅✅

Since you have `example_lightcurves/` with curated FITS files:

```python
# requirements-minimal.txt
Django==5.2.4
djangorestframework==3.16.0
django-cors-headers==4.7.0
gunicorn==23.0.0
whitenoise==6.8.2

--extra-index-url https://download.pytorch.org/whl/cpu
torch==2.7.1+cpu
joblib==1.4.2

# Minimal data processing
numpy==2.1.3
pandas==2.2.3
scipy==1.15.3

# Visualization
plotly==5.24.1
kaleido==0.2.1

Pillow>=10.0.0
psycopg2-binary==2.9.10
dj-database-url==2.3.0
python-decouple==3.8
```

Then update views.py to NOT use lightkurve downloads - only local FITS.

**Estimated slug size:** ~500-600 MB

### Option 3: Deploy to Railway.app (Better for ML) 🚂

Railway has NO slug size limit and better ML support:

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize
railway init

# Deploy
railway up
```

**Pros:**
- No size limits
- Better performance for ML
- Similar pricing to Heroku
- Supports Docker

**Free tier:** $5/month credit

### Option 4: Deploy to Render.com 🎨

Render is Heroku-alternative with better limits:

```bash
# Create render.yaml
services:
  - type: web
    name: exohunt-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn --chdir exodetect exodetect.wsgi
```

**Pros:**
- 1GB slug limit (2x Heroku)
- Free tier available
- Auto-deploy from GitHub

### Option 5: Use Docker + Any Platform 🐳

Create lightweight Docker image:

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Copy requirements
COPY requirements-heroku.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY exodetect /app/exodetect
COPY dataset /app/dataset
COPY training /app/training

# Run
CMD gunicorn --chdir exodetect exodetect.wsgi:application --bind 0.0.0.0:$PORT
```

Deploy to:
- **Fly.io** (recommended - free tier)
- **Google Cloud Run**
- **AWS App Runner**
- **DigitalOcean App Platform**

## Recommended Approach for NASA Space Apps

### Quick Fix (For Demo): Use Heroku with CPU PyTorch

```bash
cd /Users/bimalsilwal/programming/exohunt

# Use minimal requirements
cat > requirements.txt << 'EOF'
Django==5.2.4
djangorestframework==3.16.0
django-cors-headers==4.7.0
gunicorn==23.0.0
whitenoise==6.8.2

--extra-index-url https://download.pytorch.org/whl/cpu
torch==2.7.1+cpu
joblib==1.4.2

numpy==2.1.3
pandas==2.2.3
scipy==1.15.3
plotly==5.24.1
kaleido==0.2.1
Pillow>=10.0.0

psycopg2-binary==2.9.10
dj-database-url==2.3.0
python-decouple==3.8
EOF

# Commit and deploy
git add requirements.txt
git commit -m "Switch to CPU-only PyTorch for Heroku compatibility"
git push heroku main
```

### Better Solution: Use Railway or Render

For hackathon/production, use Railway (easier) or Render:

**Railway Quick Start:**
```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

## File Storage Warning ⚠️

Remember: Heroku has **ephemeral filesystem**!

Your model files in `training/` will persist (they're in git), but:
- Uploaded FITS files get deleted on dyno restart
- Downloaded light curves don't persist
- Need AWS S3 or similar for user uploads

For the hackathon demo:
✅ Use `example_lightcurves/` (committed to git)
✅ KepID search with lightkurve download (works but doesn't cache)
❌ User FITS uploads (need S3)

## Next Steps

1. **Choose a platform:**
   - Heroku (CPU-only): For simplicity
   - Railway: For better performance  
   - Render: Middle ground

2. **Deploy with CPU PyTorch**
3. **Test predictions**
4. **Update frontend CORS URL**
5. **Demo ready!** 🎉

##Would you like me to help you deploy to Railway or continue with Heroku CPU-only?
