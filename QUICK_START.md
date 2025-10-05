# 🚀 ExoHunt Quick Start Guide

Get ExoHunt running in 5 minutes!

## Prerequisites Check

```bash
# Check Python version (need 3.8+)
python --version

# Check Node.js version (need 20.19+)
node --version

# Check pip
pip --version

# Check npm
npm --version
```

## Step 1: Backend Setup (2 minutes)

```bash
# Navigate to project root
cd /Users/bimalsilwal/programming/exohunt

# Install Python dependencies
pip install -r requirements.txt

# Navigate to Django project
cd exodetect

# Run migrations
python manage.py migrate

# Start Django server (keep this terminal open)
python manage.py runserver
```

✅ **Backend running at**: http://localhost:8000  
✅ **API endpoint**: http://localhost:8000/api/

## Step 2: Frontend Setup (2 minutes)

Open a **NEW terminal window**:

```bash
# Navigate to frontend folder
cd /Users/bimalsilwal/programming/exohunt/frontend

# Install dependencies (if not already done)
npm install

# Start development server (keep this terminal open)
npm run dev
```

✅ **Frontend running at**: http://localhost:5173

## Step 3: Test the Application (1 minute)

1. **Open browser**: http://localhost:5173
2. **Navigate to "Analyze" page**
3. **Upload a test FITS file** from `lightcurves/` folder:
   ```
   /Users/bimalsilwal/programming/exohunt/lightcurves/10000162.fits
   ```
4. **Click "Predict Exoplanet"**
5. **View results** with confidence scores and visualizations

## Quick Test with curl

```bash
# Test API health
curl http://localhost:8000/api/dashboard/stats/

# Upload and predict (from project root)
curl -X POST http://localhost:8000/api/predict/single/ \
  -F "file=@lightcurves/10000162.fits" \
  -F "koi_period=3.52" \
  -F "koi_depth=1234.5"
```

## Troubleshooting

### Backend Issues

**Port 8000 already in use**:
```bash
# Kill existing process
lsof -ti:8000 | xargs kill -9

# Or use different port
python manage.py runserver 8001
# Update frontend/src/utils/api.js to use port 8001
```

**Migration errors**:
```bash
# Delete database and re-migrate
rm db.sqlite3
python manage.py migrate
```

**Missing dependencies**:
```bash
pip install django djangorestframework django-cors-headers \
            torch lightkurve astropy scipy pillow joblib
```

### Frontend Issues

**Port 5173 already in use**:
```bash
# Kill existing process
lsof -ti:5173 | xargs kill -9

# Or edit vite.config.js to use different port
```

**npm install fails**:
```bash
# Clear cache and retry
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

**CORS errors in browser**:
- Check Django CORS settings in `exodetect/exodetect/settings.py`
- Ensure `CORS_ALLOWED_ORIGINS` includes `http://localhost:5173`

## File Structure Overview

```
exohunt/
├── exodetect/              # Django backend
│   ├── manage.py           # Django management
│   ├── db.sqlite3          # Database (auto-created)
│   └── api/                # API app
├── frontend/               # React frontend
│   ├── src/                # Source code
│   └── package.json        # Dependencies
├── training/               # ML model
│   ├── exoplanet_hybrid.pth    # Model weights
│   ├── koi_scaler.joblib       # Feature scaler
│   └── tab_features_list.joblib # Feature list
└── lightcurves/            # Test FITS files
```

## Next Steps

1. **Explore the Dashboard**: http://localhost:5173/dashboard
2. **Try different light curves** from `lightcurves/` folder
3. **Add KOI parameters** for improved predictions
4. **Check advanced visualizations** (phase-folding, transit detection)
5. **View API documentation**: [API_FEATURES.md](API_FEATURES.md)

## Development Workflow

### Terminal 1 - Backend
```bash
cd exodetect
python manage.py runserver
# Keep running...
```

### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
# Keep running...
```

### Terminal 3 - Testing/Commands
```bash
# Run Python scripts
python test_api.py

# Django shell
cd exodetect
python manage.py shell

# Database migrations
python manage.py makemigrations
python manage.py migrate
```

## Production Build

### Backend
```bash
cd exodetect
python manage.py collectstatic
gunicorn exodetect.wsgi:application
```

### Frontend
```bash
cd frontend
npm run build
# Output in dist/ folder
npm run preview  # Test production build
```

## API Testing Examples

```bash
# Get dashboard stats
curl http://localhost:8000/api/dashboard/stats/

# Get recent predictions
curl http://localhost:8000/api/dashboard/recent-predictions/?limit=5

# Visualize light curve (replace UUID)
curl http://localhost:8000/api/lightcurve/visualize/YOUR-UUID-HERE/

# Phase-fold (replace UUID)
curl -X POST http://localhost:8000/api/lightcurve/phase-fold/ \
  -H "Content-Type: application/json" \
  -d '{"lightcurve_id": "YOUR-UUID-HERE", "period": 3.5}'
```

## Sample FITS Files

Located in `lightcurves/` folder:
- `10000162.fits` - Good candidate
- `10000490.fits` - False positive
- `10001368.fits` - Confirmed planet
- ... (100+ more files)

## Key URLs

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:5173 | React app |
| Backend API | http://localhost:8000/api/ | REST API |
| Django Admin | http://localhost:8000/admin/ | Admin panel |
| API Stats | http://localhost:8000/api/dashboard/stats/ | JSON stats |

## Success Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] Can access frontend in browser
- [ ] Can upload FITS file
- [ ] Can see prediction results
- [ ] Interactive charts working
- [ ] Dashboard showing statistics

## Need Help?

1. **Check terminal output** for error messages
2. **Check browser console** (F12) for frontend errors
3. **Review documentation**: 
   - [API_FEATURES.md](API_FEATURES.md) - API reference
   - [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) - Frontend guide
   - [frontend/README.md](frontend/README.md) - Frontend docs

## Demo for NASA Space Apps Challenge

**5-Minute Demo Flow**:

1. **Introduction** (30 sec)
   - "ExoHunt uses deep learning to detect exoplanets from light curves"
   
2. **Upload Demo** (90 sec)
   - Navigate to Analyze page
   - Upload FITS file
   - Show real-time prediction
   
3. **Results** (90 sec)
   - Explain disposition (Confirmed/Candidate/False Positive)
   - Show confidence scores
   - Highlight class probabilities
   
4. **Visualization** (60 sec)
   - Open advanced analysis
   - Show interactive light curve
   - Zoom/pan demonstration
   
5. **Dashboard** (60 sec)
   - Show statistics
   - Recent predictions table
   - Highlight accuracy metrics

Good luck! 🚀🌌
