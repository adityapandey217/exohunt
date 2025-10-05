# ExoHunt - AI-Powered Exoplanet Detection

🌟 **NASA Space Apps Challenge 2025**

An intelligent web application for detecting exoplanets from Kepler and TESS light curves using a hybrid CNN+MLP deep learning model.

## 🚀 Project Overview

ExoHunt uses advanced machine learning to analyze stellar brightness measurements (light curves) and classify potential exoplanet transits. The system combines:

- **Deep Learning**: Hybrid CNN+MLP architecture trained on thousands of Kepler light curves
- **Transit Analysis**: BLS period search, phase-folding, and periodogram analysis
- **Interactive Visualization**: Real-time light curve exploration with Plotly
- **Research Tools**: Active learning, batch processing, and explainability features

## 🏆 Features

### Core Capabilities
✅ **AI Classification**: 3-class prediction (Confirmed/Candidate/False Positive) with 95%+ accuracy  
✅ **FITS File Processing**: Native support for Kepler and TESS data formats  
✅ **Transit Detection**: Automated BLS algorithm with SNR thresholding  
✅ **Phase-Folding**: Orbital period analysis and visualization  
✅ **Interactive Plots**: Zoom, pan, and explore light curves  
✅ **Dashboard**: Real-time statistics and prediction history  

### Advanced Features
🔬 **Periodogram Analysis**: Lomb-Scargle frequency detection  
🔍 **Anomaly Detection**: Sigma-clipping outlier identification  
📊 **Batch Processing**: Async processing for multiple light curves  
🎓 **Active Learning**: Expert feedback integration for model improvement  
💡 **Explainability**: Grad-CAM and SHAP value visualization  

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

1. Navigate to the **Analyze** page
2. Click "Upload" or drag-and-drop a FITS file
3. (Optional) Enter KOI parameters for improved accuracy:
   - Period (days)
   - Depth (ppm)
   - Duration (hours)
   - Planet radius (Earth radii)
4. Click "Predict Exoplanet"

### 2. View Results

- **Disposition**: Confirmed / Candidate / False Positive
- **Confidence**: Probability score (0-100%)
- **Class Probabilities**: Breakdown for all 3 classes
- **Metadata**: KIC ID, duration, data points, quality score

### 3. Advanced Analysis

Click "Advanced Analysis & Visualization" to access:
- Interactive light curve plot
- Transit detection results
- Phase-folded light curve
- Periodogram analysis

### 4. Dashboard Overview

View overall statistics:
- Total predictions
- Confirmed exoplanets count
- Candidate count
- False positive count
- Recent predictions table

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

### Hybrid CNN+MLP (HybridExoNet)

**Input**:
- Light curve: 2000 flux measurements (1D CNN)
- Tabular features: 16 KOI parameters (MLP)

**CNN Branch**:
```
Conv1D(64) → ReLU → MaxPool
Conv1D(128) → ReLU → MaxPool
Conv1D(256) → ReLU → Flatten
```

**MLP Branch**:
```
Linear(128) → ReLU → Dropout(0.3)
Linear(64) → ReLU
```

**Fusion**:
```
Concat(CNN + MLP) → Linear(128) → ReLU → Dropout(0.5)
Linear(3) → Softmax
```

**Output**: 3-class probabilities (FALSE POSITIVE, CANDIDATE, CONFIRMED)

Training details: [training/train.ipynb](training/train.ipynb)

## 📊 Dataset

- **Source**: NASA Exoplanet Archive (Kepler KOI catalog)
- **Size**: ~9,000 KOIs
- **Features**: 16 tabular parameters + 2000-point light curves
- **Classes**: 
  - FALSE POSITIVE: 6,000+
  - CANDIDATE: 2,000+
  - CONFIRMED: 1,000+

Files:
- `dataset/koi.csv` - KOI catalog with parameters
- `dataset/koi_annotations.csv` - Ground truth labels
- `lightcurves/*.fits` - FITS light curve files

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

✨ **95%+ Accuracy** on test set  
✨ **Sub-second Inference** for real-time predictions  
✨ **Interactive Visualization** with Plotly  
✨ **Production-Ready** API with comprehensive documentation  
✨ **Modern UI** with React, Tailwind CSS, and Flowbite  

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
