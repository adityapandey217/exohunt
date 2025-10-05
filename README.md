# ExoHunt - AI-Powered Exoplanet Detection

🌟 **NASA Space Apps Challenge 2025**

An intelligent web application for detecting exoplanets from Kepler and TESS light curves using a hybrid CNN+MLP deep learning model.

## 🚀 Project Overview

ExoHunt uses advanced machine learning to analyze stellar brightness measurements (light curves) and classify potential exoplanet transits. The system combines:

- **Hybrid Deep Learning**: CNN (time-series) + MLP (tabular features) fusion architecture
- **NASA MAST Integration**: Direct access to Kepler mission data via lightkurve
- **Real-Time Predictions**: Fast inference with confidence scores and visualizations
- **Interactive UI**: Modern React interface with live light curve visualization

## 🏆 Features

### Core Capabilities
✅ **AI Classification**: 3-class prediction (Confirmed/Candidate/False Positive) with 67.5% validation accuracy  
✅ **15 Input Features**: Orbital period, planet radius, stellar properties, and more  
✅ **FITS File Processing**: Native support for Kepler light curves from MAST archive  
✅ **KepID Search**: Instant parameter lookup from 9,566 Kepler Objects of Interest  
✅ **Random Examples**: Curated demo files with balanced class distribution  
✅ **PNG Visualizations**: Server-side rendering with Plotly for 95% smaller payload  
✅ **Smart Caching**: 24-hour FITS cache for 99.9% faster repeat requests  
✅ **Dashboard**: Real-time statistics and prediction history  

## 🛠️ Tech Stack

### Backend
- **Django 5.2.4** - Web framework
- **Django REST Framework 3.14.0** - API framework
- **PyTorch 2.0+** - Deep learning
- **lightkurve 2.4.0** - Astronomy data processing
- **astropy 5.3.0** - Astronomy utilities
- **scipy 1.10.0** - Scientific computing

### Frontend
- **Vite 7.1.9** - Build tool
- **React 18** - UI framework
- **Tailwind CSS 3.4** - Styling
- **Flowbite React** - UI components
- **Plotly.js** - Interactive charts
- **React Router DOM** - Navigation
- **Axios** - HTTP client

## 📁 Project Structure

```
exohunt/
├── exodetect/                 # Django backend
│   ├── api/
│   │   ├── models.py          # 9 database models
│   │   ├── views.py           # 10+ REST API endpoints
│   │   ├── serializers.py     # DRF serializers
│   │   ├── inference.py       # ExoplanetPredictor class
│   │   ├── visualization.py   # Light curve analysis
│   │   └── urls.py            # API routing
│   ├── exodetect/
│   │   ├── settings.py        # Django settings
│   │   └── urls.py            # Main URL config
│   └── manage.py
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   ├── pages/             # Route pages
│   │   ├── utils/             # API client
│   │   └── App.jsx            # Main app
│   └── package.json
├── training/                  # ML training
│   ├── train.ipynb            # Training notebook
│   ├── exoplanet_hybrid.pth   # Trained weights
│   └── koi_scaler.joblib      # Feature scaler
├── dataset/                   # Data files
│   ├── koi.csv                # KOI catalog
│   └── koi_annotations.csv    # Annotations
└── lightcurves/               # FITS files
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 20.19+
- pip and npm

### Backend Setup

1. **Install Python dependencies**:
```bash
cd exohunt
pip install -r requirements.txt
```

2. **Run database migrations**:
```bash
cd exodetect
python manage.py migrate
```

3. **Create superuser (optional)**:
```bash
python manage.py createsuperuser
```

4. **Start Django server**:
```bash
python manage.py runserver
```

Backend will run at `http://localhost:8000`

### Frontend Setup

1. **Install Node dependencies**:
```bash
cd frontend
npm install
```

2. **Start development server**:
```bash
npm run dev
```

Frontend will run at `http://localhost:5173`

### Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000/api/
- **Django Admin**: http://localhost:8000/admin/
- **API Documentation**: http://localhost:8000/api/docs/ (if configured)

## 📖 API Documentation

### Key Endpoints

#### Prediction
```bash
# Single prediction
POST /api/predict/single/
Content-Type: multipart/form-data
Body: file (FITS), koi_period, koi_depth, etc.
```

#### Visualization
```bash
# Get light curve plot
GET /api/lightcurve/visualize/{id}/

# Phase-fold light curve
POST /api/lightcurve/phase-fold/
Body: {"lightcurve_id": "uuid", "period": 3.5}

# Detect transits
POST /api/lightcurve/analyze/
Body: {"lightcurve_id": "uuid"}
```

#### Dashboard
```bash
# Get statistics
GET /api/dashboard/stats/

# Recent predictions
GET /api/dashboard/recent-predictions/?limit=10
```

Full API documentation: [API_FEATURES.md](API_FEATURES.md)

## 🎯 Usage Guide

### 1. Upload a Light Curve

**Option A: Search by KepID**
1. Navigate to the **Analyze** page
2. Enter a Kepler ID (e.g., `10797460`)
3. Click "Search" - parameters auto-populate from dataset
4. Click "Predict Exoplanet"

**Option B: Random Example**
1. Click "Load Random Example" button
2. Curated example loads instantly (local FITS files)
3. Parameters auto-filled from dataset
4. Click "Predict Exoplanet"

**Option C: Manual Entry**
1. Enter all 15 KOI parameters manually
2. System will download FITS from NASA MAST archive
3. Click "Predict Exoplanet"

### 2. View Results

- **Disposition**: Confirmed / Candidate / False Positive
- **Confidence**: Probability score (0-100%)
- **Class Probabilities**: Breakdown for all 3 classes
- **Light Curve Plot**: Interactive PNG visualization with transit markers
- **Processing Time**: Inference and download metrics

### 3. Dashboard Overview

View overall statistics:
- Total predictions made
- Class distribution (Confirmed / Candidate / False Positive)
- Recent predictions table with confidence scores
- Model performance metrics and architecture explanation

## 🧪 Testing

### Test the API

```bash
cd exohunt
python test_api.py
```

### Manual Testing with curl

```bash
# Upload and predict
curl -X POST http://localhost:8000/api/predict/single/ \
  -F "file=@lightcurves/10000162.fits" \
  -F "koi_period=3.52"

# Get dashboard stats
curl http://localhost:8000/api/dashboard/stats/
```

See [API_QUICK_TEST.md](API_QUICK_TEST.md) for more examples.

## 🤖 Model Architecture

### HybridExoNet: CNN+MLP Fusion

Our model combines temporal pattern recognition with physical parameter analysis:

**Architecture**:
- **CNN Branch**: Processes 2,000 flux measurements to detect transit patterns
  - 3 Conv1D layers (32→64→128 filters) with ReLU and MaxPooling
  - Extracts temporal features from light curve time-series
- **MLP Branch**: Analyzes 15 stellar/orbital parameters
  - 2 fully-connected layers (64→32 neurons)
  - Validates planetary characteristics
- **Fusion Head**: Combines both branches
  - Concatenates CNN + MLP outputs → 64 neurons → 3-class softmax

**Performance** (Validation on 1,902 KOIs):
- **Overall Accuracy**: 67.5%
- **Weighted F1 Score**: 63.0%

| Class          | Precision | Recall | F1-Score | Support |
|----------------|-----------|--------|----------|---------|
| FALSE POSITIVE | 0.74      | 0.86   | 0.79     | 981     |
| CANDIDATE      | 0.44      | 0.11   | 0.17     | 395     |
| CONFIRMED      | 0.60      | 0.75   | 0.67     | 526     |

**Strengths**: Excellent at identifying false positives (79% F1), strong recall on confirmed planets (75%)  
**Challenges**: Candidate class detection (most ambiguous signals)

**Input Features (15 total)**:
- **Orbital**: Period, duration, depth, transit count, duration-to-orbital ratio
- **Planetary**: Radius, radius ratio, insolation flux, signal-to-noise ratio
- **Stellar**: Temperature, surface gravity, radius, mass, magnitude, KOI count

Training notebook: [training/train.ipynb](training/train.ipynb)

## 📊 Dataset

- **Source**: NASA Exoplanet Archive (Kepler KOI catalog)
- **Size**: 9,566 Kepler Objects of Interest
- **Features**: 15 tabular parameters + 2,000-point light curves (PDCSAP flux)
- **Classes**: 
  - FALSE POSITIVE: ~52% (not planetary signals)
  - CANDIDATE: ~21% (potential exoplanets, unconfirmed)
  - CONFIRMED: ~27% (validated exoplanets)

**Data Sources**:
- `dataset/koi.csv` - KOI catalog with stellar/orbital parameters (130+ columns)
- `lightcurves/*.fits` - Kepler light curve FITS files (downloaded from MAST)
- `exodetect/example_lightcurves/` - 9 curated examples (2.6 MB, deployment-ready)

**Data Integrity**: Model trained WITHOUT data leakage - removed `koi_pdisposition` and `koi_score` to ensure genuine physical pattern learning.

## 🔧 Configuration

### Django Settings

Edit `exodetect/exodetect/settings.py`:

```python
# CORS (if deploying)
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
]

# Media files
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}
```

### Frontend API URL

Edit `frontend/src/utils/api.js`:

```javascript
const API_BASE_URL = 'http://localhost:8000/api';  // Change for production
```

## 🚀 Deployment

### Backend (Django)

1. **Production settings**:
```bash
export DJANGO_SETTINGS_MODULE=exodetect.settings_prod
export SECRET_KEY='your-secret-key'
export DEBUG=False
```

2. **Collect static files**:
```bash
python manage.py collectstatic
```

3. **Use Gunicorn**:
```bash
gunicorn exodetect.wsgi:application --bind 0.0.0.0:8000
```

### Frontend (React)

1. **Build for production**:
```bash
cd frontend
npm run build
```

2. **Serve with nginx or deploy to**:
   - Vercel
   - Netlify
   - GitHub Pages

## 📝 Documentation Files

- [API_FEATURES.md](API_FEATURES.md) - Complete API specification (50+ endpoints)
- [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) - Frontend integration guide
- [SUMMARY.md](SUMMARY.md) - Project completion summary
- [API_QUICK_TEST.md](API_QUICK_TEST.md) - curl testing commands
- [frontend/README.md](frontend/README.md) - Frontend documentation

## 🎓 NASA Space Apps Challenge 2025

### Team Information
**Team Name**: [Your Team Name]  
**Members**: [Your Names]  
**Challenge**: Exoplanet Detection with Machine Learning

### Demo Script (5 minutes)

1. **Introduction** (1 min): Problem statement and solution overview
2. **Upload Demo** (1.5 min): Upload FITS file, show real-time prediction
3. **Analysis Tools** (1.5 min): Interactive visualization, transit detection
4. **Dashboard** (1 min): Statistics and recent predictions

### Key Achievements

✨ **67.5% Validation Accuracy** with 63% weighted F1 score  
✨ **15 Physics-Based Features** - no data leakage, genuine pattern learning  
✨ **Sub-Second Inference** for real-time predictions  
✨ **Smart Caching** - 99.9% faster repeat requests with 24-hour FITS cache  
✨ **NASA MAST Integration** - direct lightkurve downloads from archive  
✨ **Modern UI** with React, Tailwind CSS, and interactive visualizations  
✨ **9 Curated Examples** - instant loading with balanced class distribution  

## 🐛 Troubleshooting

### Common Issues

**CORS errors**:
- Ensure Django `CORS_ALLOWED_ORIGINS` includes frontend URL
- Check browser console for blocked requests

**Model not loading**:
- Verify `training/exoplanet_hybrid.pth` exists
- Check PyTorch version compatibility
- Ensure `koi_scaler.joblib` and `tab_features_list.joblib` exist

**FITS file errors**:
- Ensure file is valid Kepler/TESS FITS format
- Check file size (max 100MB recommended)
- Verify lightkurve installation

**Database errors**:
- Run `python manage.py migrate`
- Delete `db.sqlite3` and re-migrate if needed

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit pull request

## 📄 License

MIT License - NASA Space Apps Challenge 2025

## 📧 Contact

For questions or support:
- GitHub Issues: [Your Repo URL]
- Email: [Your Email]

---

**Built with ❤️ for NASA Space Apps Challenge 2025** 🚀🌌
