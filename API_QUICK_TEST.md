# ExoHunt API - Quick Test Commands 🚀

## Prerequisites
Make sure Django server is running:
```bash
cd exodetect
python manage.py runserver
```

## Quick Tests with curl

### 1. Check Dashboard Stats
```bash
curl http://localhost:8000/api/dashboard/stats/ | jq
```

### 2. Make a Prediction
```bash
# Replace with actual FITS file path
curl -X POST http://localhost:8000/api/predict/single/ \
  -F "fits_file=@../lightcurves/10666592.fits" \
  -F "kepid=10666592" \
  -F "koi_period=3.52" \
  -F "koi_depth=145.3" \
  | jq
```

### 3. Visualize Light Curve
```bash
# Replace PREDICTION_ID with actual UUID from step 2
curl "http://localhost:8000/api/lightcurve/visualize/?prediction_id=PREDICTION_ID" | jq
```

### 4. Phase-Fold Light Curve
```bash
curl -X POST http://localhost:8000/api/lightcurve/phase-fold/ \
  -H "Content-Type: application/json" \
  -d '{
    "prediction_id": "PREDICTION_ID",
    "period": 3.52
  }' | jq
```

### 5. Detect Transits
```bash
curl -X POST http://localhost:8000/api/lightcurve/analyze/ \
  -H "Content-Type: application/json" \
  -d '{
    "prediction_id": "PREDICTION_ID",
    "period_min": 0.5,
    "period_max": 50.0,
    "snr_threshold": 7.0
  }' | jq
```

### 6. Submit Feedback
```bash
curl -X POST http://localhost:8000/api/feedback/submit/ \
  -H "Content-Type: application/json" \
  -d '{
    "prediction": "PREDICTION_ID",
    "verdict": "agree",
    "notes": "Looks like a real transit!",
    "confidence_in_correction": 5
  }' | jq
```

### 7. Create Analysis Session
```bash
curl -X POST http://localhost:8000/api/sessions/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Hot Jupiter Survey",
    "notes": "Analyzing short-period candidates"
  }' | jq
```

### 8. List Sessions
```bash
curl http://localhost:8000/api/sessions/ | jq
```

### 9. Get Recent Predictions
```bash
curl "http://localhost:8000/api/dashboard/recent-predictions/?limit=10" | jq
```

### 10. Get Predictions in Session
```bash
# Replace SESSION_ID with actual UUID
curl http://localhost:8000/api/sessions/SESSION_ID/predictions/ | jq
```

---

## Using Python `requests`

```python
import requests

# Dashboard
response = requests.get('http://localhost:8000/api/dashboard/stats/')
print(response.json())

# Predict
files = {'fits_file': open('../lightcurves/10666592.fits', 'rb')}
data = {'kepid': 10666592, 'koi_period': 3.52}
response = requests.post('http://localhost:8000/api/predict/single/', files=files, data=data)
result = response.json()
print(f"Prediction: {result['prediction']['class']}")

# Visualize
prediction_id = result['prediction_id']
response = requests.get(
    'http://localhost:8000/api/lightcurve/visualize/',
    params={'prediction_id': prediction_id}
)
viz_data = response.json()
```

---

## Using JavaScript `fetch`

```javascript
// Dashboard
const response = await fetch('http://localhost:8000/api/dashboard/stats/');
const stats = await response.json();
console.log(stats);

// Predict
const formData = new FormData();
formData.append('fits_file', fileInput.files[0]);
formData.append('kepid', '10666592');

const response = await fetch('http://localhost:8000/api/predict/single/', {
  method: 'POST',
  body: formData
});

const result = await response.json();
console.log('Prediction:', result.prediction.class);

// Visualize
const vizResponse = await fetch(
  `http://localhost:8000/api/lightcurve/visualize/?prediction_id=${result.prediction_id}`
);
const vizData = await vizResponse.json();
```

---

## Expected Response Examples

### Dashboard Stats
```json
{
  "total_predictions": 0,
  "recent_predictions_7d": 0,
  "average_confidence": 0,
  "class_distribution": {},
  "model_performance": null
}
```

### Prediction
```json
{
  "prediction_id": "123e4567-e89b-12d3-a456-426614174000",
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
  "features_used": {
    "koi_period": 3.52,
    "koi_depth": 145.3
  },
  "links": {
    "visualize": "/api/lightcurve/visualize/?prediction_id=...",
    "explain": "/api/explain/feature-importance/?prediction_id=...",
    "feedback": "/api/feedback/submit/?prediction_id=..."
  }
}
```

---

## Common Issues

**404 Not Found**
- Make sure you're using `/api/` prefix
- Check URL spelling

**500 Internal Server Error**
- Model files not found (check paths in views.py)
- FITS file corrupt
- Check Django console for traceback

**CORS Error (from browser)**
- Add your frontend URL to CORS_ALLOWED_ORIGINS in settings.py

**File Upload Error**
- Check MEDIA_ROOT is configured
- Ensure directory has write permissions

---

## Quick Debug

```bash
# Check if server is running
curl http://localhost:8000/api/dashboard/stats/

# If 404, check Django URLs:
cd exodetect
python manage.py show_urls  # If django-extensions installed

# Check logs
# Django prints all errors in the terminal where runserver is running
```

---

**Ready to integrate with frontend! 🎨**
