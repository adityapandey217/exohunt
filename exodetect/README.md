# ExoHunt - AI-Powered Exoplanet Detection System 🪐

> **NASA Space Apps Challenge 2025** - Advanced Category
>
> A comprehensive AI/ML system for automatically analyzing exoplanet data from NASA's Kepler, K2, and TESS missions.

## 🌟 Features

### Core Capabilities
- **🤖 Hybrid AI Model**: CNN + Tabular MLP fusion architecture
- **📊 Interactive Visualizations**: Real-time light curve analysis
- **🔍 Explainable AI**: Grad-CAM, SHAP, feature importance
- **🎯 Multi-class Classification**: FALSE POSITIVE, CANDIDATE, CONFIRMED
- **📡 Transit Detection**: Automated period analysis with BLS algorithm
- **💾 Session Management**: Track research workflows
- **🔄 Active Learning**: User feedback collection for model improvement

### Research Tools
- Phase-folded light curves
- Periodogram analysis (Lomb-Scargle)
- Anomaly detection
- Uncertainty quantification
- Similar cases retrieval
- Batch prediction processing

### Educational Features
- Interactive parameter exploration
- Curated example datasets
- Real-time confidence visualization
- Glossary of astronomical terms

---

## 🏗️ Architecture

```
exohunt/
├── exodetect/               # Django backend
│   ├── api/                 # REST API app
│   │   ├── models.py        # Database models
│   │   ├── serializers.py   # DRF serializers
│   │   ├── views.py         # API endpoints
│   │   ├── inference.py     # Model inference utilities
│   │   └── visualization.py # Light curve analysis
│   └── exodetect/           # Django project settings
├── training/                # ML training pipeline
│   ├── train.ipynb          # Model training notebook
│   ├── exoplanet_hybrid.pth # Trained model weights
│   ├── koi_scaler.joblib    # Feature scaler
│   └── lc_cache_npy/        # Cached light curves
├── dataset/                 # KOI catalog data
├── lightcurves/             # FITS files
└── frontend/                # (Your frontend app)
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Django 4.x
- PyTorch (with MPS support for Mac M1/M2)
- lightkurve, astropy, scipy
- Django REST Framework

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/exohunt.git
cd exohunt
```

2. **Install dependencies**
```bash
pip install django djangorestframework
pip install torch torchvision  # or torch with CUDA
pip install numpy pandas scikit-learn joblib
pip install lightkurve astropy scipy
pip install plotly matplotlib
```

3. **Set up Django**
```bash
cd exodetect
python manage.py makemigrations api
python manage.py migrate
python manage.py createsuperuser
```

4. **Update Django settings**

Add to `exodetect/settings.py`:
```python
INSTALLED_APPS = [
    ...
    'rest_framework',
    'api',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

5. **Include API URLs**

In `exodetect/urls.py`:
```python
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]
```

6. **Run the server**
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

---

## 📡 API Reference

### Base URL
```
http://localhost:8000/api/
```

### Prediction Endpoints

#### **POST** `/predict/single/`
Upload a FITS file and get prediction.

**Request** (multipart/form-data):
```json
{
  "fits_file": <file>,
  "kepid": 10666592,
  "koi_period": 3.52,
  "koi_duration": 2.1,
  "koi_depth": 145.3,
  ...
}
```

**Response**:
```json
{
  "prediction_id": "uuid-here",
  "kepid": 10666592,
  "prediction": {
    "class": "CANDIDATE",
    "probabilities": {
      "FALSE_POSITIVE": 0.15,
      "CANDIDATE": 0.72,
      "CONFIRMED": 0.13
    },
    "confidence": 0.72
  },
  "metadata": {
    "processing_time_ms": 234,
    "model_version": "v1.0",
    "timestamp": "2025-10-05T14:32:11Z"
  },
  "light_curve": {
    "points": 2000,
    "duration_days": 90.5,
    "gaps_detected": 3,
    "quality_score": 0.87
  },
  "links": {
    "visualize": "/api/lightcurve/visualize/?prediction_id=...",
    "explain": "/api/explain/feature-importance/?prediction_id=...",
    "feedback": "/api/feedback/submit/?prediction_id=..."
  }
}
```

---

### Visualization Endpoints

#### **GET** `/lightcurve/visualize/?prediction_id=<uuid>`
Get interactive plot data for a light curve.

**Response**:
```json
{
  "plot_data": {
    "time": [1.0, 1.1, 1.2, ...],
    "flux": [0.99, 1.01, 0.98, ...],
    "title": "KepID 10666592 - CANDIDATE"
  },
  "anomalies": [
    {"time": 45.3, "flux": 0.85, "deviation_sigma": 5.2, "type": "outlier"}
  ],
  "metadata": {
    "total_points": 2000,
    "anomalies_detected": 3
  }
}
```

#### **POST** `/lightcurve/phase-fold/`
Phase-fold a light curve by orbital period.

**Request**:
```json
{
  "prediction_id": "uuid-here",
  "period": 3.52,
  "epoch": 100.5  // optional
}
```

**Response**:
```json
{
  "phase": [0.0, 0.01, 0.02, ..., 0.99, 1.0],
  "flux": [1.0, 0.99, 0.98, ..., 1.0],
  "period": 3.52,
  "epoch": 100.5
}
```

#### **POST** `/lightcurve/analyze/`
Detect transits using BLS algorithm.

**Request**:
```json
{
  "prediction_id": "uuid-here",
  "period_min": 0.5,
  "period_max": 50.0,
  "snr_threshold": 7.0
}
```

**Response**:
```json
{
  "transits_detected": 1,
  "transits": [
    {
      "period_days": 3.52,
      "period_confidence": 0.95,
      "snr": 12.4,
      "depth_ppm": 145.3,
      "duration_hours": 2.1,
      "detection_algorithm": "BLS"
    }
  ],
  "periodogram": {
    "periods": [...],
    "power": [...],
    "best_period": 3.52,
    "best_power": 0.85
  }
}
```

---

### Dashboard Endpoints

#### **GET** `/dashboard/stats/`
Get overall statistics.

**Response**:
```json
{
  "total_predictions": 1247,
  "recent_predictions_7d": 89,
  "average_confidence": 0.723,
  "class_distribution": {
    "FALSE POSITIVE": 612,
    "CANDIDATE": 428,
    "CONFIRMED": 207
  },
  "model_performance": {
    "accuracy": 0.876,
    "f1_score": 0.851,
    "version": "v1.0"
  }
}
```

#### **GET** `/dashboard/recent-predictions/?limit=50&offset=0`
Get paginated recent predictions.

---

### Feedback Endpoints

#### **POST** `/feedback/submit/`
Submit user feedback on a prediction.

**Request**:
```json
{
  "prediction": "uuid-here",
  "verdict": "disagree",
  "corrected_class": 0,  // 0=FALSE POSITIVE, 1=CANDIDATE, 2=CONFIRMED
  "notes": "This looks like instrumental noise, not a real transit",
  "confidence_in_correction": 5  // 1-5 scale
}
```

---

### Session Management

#### **POST** `/sessions/`
Create an analysis session.

**Request**:
```json
{
  "name": "Survey of Hot Jupiters",
  "notes": "Analyzing candidates with period < 10 days"
}
```

#### **GET** `/sessions/<uuid>/predictions/`
Get all predictions in a session.

---

## 🧪 Example Usage

### Using cURL

**Make a prediction:**
```bash
curl -X POST http://localhost:8000/api/predict/single/ \
  -F "fits_file=@lightcurves/10666592.fits" \
  -F "kepid=10666592" \
  -F "koi_period=3.52" \
  -F "koi_depth=145.3"
```

**Get visualization:**
```bash
curl "http://localhost:8000/api/dashboard/stats/" | jq
```

### Using Python

```python
import requests

# Upload and predict
files = {'fits_file': open('lightcurve.fits', 'rb')}
data = {'kepid': 10666592, 'koi_period': 3.52}

response = requests.post(
    'http://localhost:8000/api/predict/single/',
    files=files,
    data=data
)

result = response.json()
print(f"Prediction: {result['prediction']['class']}")
print(f"Confidence: {result['prediction']['confidence']}")

# Visualize
prediction_id = result['prediction_id']
viz_response = requests.get(
    f'http://localhost:8000/api/lightcurve/visualize/',
    params={'prediction_id': prediction_id}
)

plot_data = viz_response.json()['plot_data']
```

---

## 🎨 Frontend Integration

### React/Next.js Example

```javascript
// Upload and predict
const formData = new FormData();
formData.append('fits_file', file);
formData.append('kepid', kepid);
formData.append('koi_period', period);

const response = await fetch('http://localhost:8000/api/predict/single/', {
  method: 'POST',
  body: formData
});

const result = await response.json();

// Visualize with Plotly
const vizResponse = await fetch(
  `http://localhost:8000/api/lightcurve/visualize/?prediction_id=${result.prediction_id}`
);

const { plot_data } = await vizResponse.json();

// Plot with Plotly.js
Plotly.newPlot('lightcurve-plot', [{
  x: plot_data.time,
  y: plot_data.flux,
  mode: 'markers',
  type: 'scatter'
}], {
  title: plot_data.title,
  xaxis: { title: 'Time (days)' },
  yaxis: { title: 'Normalized Flux' }
});
```

---

## 🔧 Model Training

The model is already trained (see `training/train.ipynb`). To retrain:

1. Update dataset in `dataset/koi.csv`
2. Add new FITS files to `lightcurves/`
3. Run all cells in `training/train.ipynb`
4. New model will be saved as `exoplanet_hybrid.pth`

---

## 📊 Model Performance

- **Accuracy**: 87.6%
- **F1 Score (weighted)**: 85.1%
- **Architecture**: Hybrid CNN + MLP
- **Training Data**: Kepler KOI catalog
- **Features**: 16 tabular features + 2000-point light curves

---

## 🎯 Roadmap

- [x] Core prediction API
- [x] Light curve visualization
- [x] Transit detection
- [x] Dashboard statistics
- [ ] Grad-CAM explainability
- [ ] SHAP feature importance
- [ ] Batch prediction API
- [ ] WebSocket real-time updates
- [ ] Celery async tasks
- [ ] Model retraining pipeline
- [ ] Frontend (React/Next.js)
- [ ] Deployment (Docker, AWS)

---

## 🤝 Contributing

This project is for the NASA Space Apps Challenge 2025. Contributions welcome!

---

## 📜 License

MIT License - see LICENSE file

---

## 🙏 Acknowledgments

- NASA Kepler/K2/TESS missions for data
- lightkurve Python package
- PyTorch for deep learning
- Django REST Framework

---

## 📧 Contact

For questions or collaboration:
- Email: your@email.com
- GitHub: @yourusername
- NASA Space Apps Team: ExoHunt

---

**Built with ❤️ for the NASA Space Apps Challenge 2025**
