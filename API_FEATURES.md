# ExoHunt API - Comprehensive Feature List

## 🎯 Core Features for NASA Space Apps Challenge

### 1. **Prediction & Classification Endpoints**

#### `/api/predict/single/`
- **Method**: POST
- **Input**: Upload FITS file + optional tabular features (KOI parameters)
- **Output**: 
  - Prediction class (FALSE POSITIVE, CANDIDATE, CONFIRMED)
  - Confidence scores for each class
  - Prediction ID for tracking
  - Processing time
- **Use Case**: Quick classification of individual exoplanet candidates

#### `/api/predict/batch/`
- **Method**: POST
- **Input**: Multiple FITS files (up to 50) + CSV with tabular data
- **Output**: 
  - Batch prediction results
  - Download link for results CSV
  - Summary statistics
  - Job ID for async processing
- **Use Case**: Researchers analyzing multiple candidates at once

#### `/api/predict/from-kepid/`
- **Method**: POST
- **Input**: KepID(s)
- **Output**: Fetch data from NASA archives, run prediction
- **Use Case**: Analyze specific Kepler targets by ID

---

### 2. **Light Curve Visualization & Analysis**

#### `/api/lightcurve/visualize/`
- **Method**: POST
- **Input**: FITS file or prediction ID
- **Output**: 
  - Interactive plotly.js JSON for frontend
  - Raw flux data points
  - Time series metadata
  - Detected transits highlighted
- **Features**:
  - Zoom to specific time ranges
  - Toggle between PDCSAP_FLUX and SAP_FLUX
  - Highlight anomalies/outliers
  - Show model attention regions

#### `/api/lightcurve/analyze/`
- **Method**: POST
- **Input**: FITS file
- **Output**:
  - Transit detection results
  - Period analysis (Lomb-Scargle periodogram)
  - Signal-to-noise ratio
  - Transit depth, duration estimates
  - Data quality metrics (gaps, outliers)
- **Use Case**: Deep dive into light curve characteristics

#### `/api/lightcurve/compare/`
- **Method**: POST
- **Input**: 2-4 FITS files or prediction IDs
- **Output**: Side-by-side comparison visualization
- **Use Case**: Compare similar candidates or confirmed vs false positives

#### `/api/lightcurve/phase-fold/`
- **Method**: POST
- **Input**: FITS file + orbital period
- **Output**: Phase-folded light curve plot data
- **Use Case**: Visualize periodic transits clearly

---

### 3. **Model Explainability (XAI)**

#### `/api/explain/gradcam/`
- **Method**: POST
- **Input**: Prediction ID
- **Output**: 
  - Grad-CAM heatmap overlay on light curve
  - Shows which time regions influenced prediction
- **Use Case**: Understand what the CNN "sees" in the light curve

#### `/api/explain/feature-importance/`
- **Method**: POST
- **Input**: Prediction ID
- **Output**:
  - SHAP values for tabular features
  - Bar chart data of feature contributions
  - Feature importance rankings
- **Use Case**: See which KOI parameters drove the decision

#### `/api/explain/attention-weights/`
- **Method**: POST
- **Input**: Prediction ID
- **Output**: Attention scores across time series
- **Use Case**: Advanced interpretability for research

#### `/api/explain/similar-cases/`
- **Method**: GET
- **Input**: Prediction ID
- **Output**: 5 most similar examples from training data with outcomes
- **Use Case**: "Show me similar cases" - builds researcher trust

---

### 4. **Interactive Dashboard Data**

#### `/api/dashboard/stats/`
- **Method**: GET
- **Output**:
  - Total predictions made
  - Accuracy on validation set
  - Class distribution (pie chart data)
  - Predictions over time (line chart)
  - Most active users/sessions

#### `/api/dashboard/model-performance/`
- **Method**: GET
- **Output**:
  - ROC curves (multi-class)
  - Precision-Recall curves
  - Confusion matrix
  - Per-class metrics (precision, recall, F1)
  - Calibration plots

#### `/api/dashboard/confidence-distribution/`
- **Method**: GET
- **Output**: Histogram of prediction confidences
- **Use Case**: Monitor model uncertainty

#### `/api/dashboard/recent-predictions/`
- **Method**: GET
- **Output**: Last 50 predictions with thumbnails, confidence, class

---

### 5. **Research Tools**

#### `/api/research/uncertainty-analysis/`
- **Method**: POST
- **Input**: Prediction ID
- **Output**:
  - Monte Carlo dropout uncertainty estimates
  - Prediction intervals
  - Epistemic vs aleatoric uncertainty
- **Use Case**: Identify candidates needing human review

#### `/api/research/ensemble-predict/`
- **Method**: POST
- **Input**: FITS file
- **Output**: Predictions from multiple model checkpoints with variance
- **Use Case**: More robust predictions for critical decisions

#### `/api/research/counterfactual/`
- **Method**: POST
- **Input**: Prediction ID + feature to modify
- **Output**: "What if X feature was different?" analysis
- **Use Case**: Understand decision boundaries

#### `/api/research/export-annotations/`
- **Method**: POST
- **Input**: List of prediction IDs + user corrections
- **Output**: Export corrected labels for model retraining
- **Use Case**: Continuous learning from expert feedback

---

### 6. **User Interaction & Feedback**

#### `/api/feedback/submit/`
- **Method**: POST
- **Input**: Prediction ID + user verdict (agree/disagree) + notes
- **Output**: Feedback stored
- **Use Case**: Collect expert corrections for active learning

#### `/api/feedback/statistics/`
- **Method**: GET
- **Output**: Agreement rates, disagreement patterns
- **Use Case**: Model improvement insights

#### `/api/sessions/create/`
- **Method**: POST
- **Output**: Session ID for tracking analysis workflows
- **Use Case**: Save research sessions

#### `/api/sessions/{id}/history/`
- **Method**: GET
- **Output**: All predictions in this session
- **Use Case**: Resume research workflows

---

### 7. **Data Management**

#### `/api/upload/fits/`
- **Method**: POST
- **Input**: FITS file
- **Output**: File ID, metadata extracted
- **Use Case**: Upload new light curves

#### `/api/upload/batch-csv/`
- **Method**: POST
- **Input**: CSV with KOI parameters
- **Output**: Validated data, ready for batch prediction

#### `/api/datasets/list/`
- **Method**: GET
- **Output**: Available datasets (Kepler, K2, TESS)
- **Use Case**: Browse catalog

#### `/api/datasets/download-sample/`
- **Method**: GET
- **Input**: Dataset name, sample size
- **Output**: ZIP with sample FITS + CSV
- **Use Case**: Help users test the system

---

### 8. **Educational Features**

#### `/api/tutorial/example-candidates/`
- **Method**: GET
- **Output**: Curated examples of clear FALSE POSITIVES, CANDIDATES, CONFIRMED
- **Use Case**: Educational demos

#### `/api/tutorial/interactive-demo/`
- **Method**: POST
- **Input**: Synthetic parameters
- **Output**: Synthetic light curve + prediction
- **Use Case**: "Build your own exoplanet" interactive tool

#### `/api/glossary/terms/`
- **Method**: GET
- **Output**: Definitions of KOI parameters, astronomy terms
- **Use Case**: Help novice users

---

### 9. **Advanced Analytics**

#### `/api/analytics/transit-search/`
- **Method**: POST
- **Input**: FITS file, search parameters
- **Output**: All detected transit-like events with characteristics
- **Use Case**: Multi-planet system detection

#### `/api/analytics/stellar-classification/`
- **Method**: POST
- **Input**: Stellar parameters from KOI
- **Output**: Star type, habitability zone, planet size estimates
- **Use Case**: Contextual information

#### `/api/analytics/contamination-check/`
- **Method**: POST
- **Input**: KepID
- **Output**: Nearby stars, potential contamination sources
- **Use Case**: Validate true planet vs false positive

---

### 10. **Model Management**

#### `/api/model/info/`
- **Method**: GET
- **Output**: Model architecture, training date, metrics, version

#### `/api/model/hyperparameters/`
- **Method**: GET/POST (admin only)
- **Output**: View/update hyperparameters for retraining

#### `/api/model/retrain-trigger/`
- **Method**: POST (admin only)
- **Input**: New labeled data
- **Output**: Trigger async retraining job

---

## 🎨 Frontend Visualization Features

### Light Curve Viewer
- **Zoomable time series** with Plotly.js
- **Toggle transit markers**
- **Fold by period** button
- **Export to PNG/SVG**
- **Anomaly highlighting**

### Prediction Dashboard
- **Real-time confidence gauge**
- **Similar cases carousel**
- **Feature importance waterfall chart**
- **Grad-CAM overlay animation**

### Comparison Tool
- **Multi-panel light curve grid**
- **Synchronized zoom/pan**
- **Parameter comparison table**

### Batch Analysis Interface
- **Upload CSV + FITS files**
- **Progress bar for batch jobs**
- **Downloadable results table**
- **Filter/sort by confidence**

### Educational Mode
- **Slider to modify KOI parameters**
- **Live prediction updates**
- **"What makes a planet?" guide**
- **Quiz mode with validation**

---

## 🔧 Technical Implementation Notes

### Real-time Features
- Use **WebSockets** for long-running batch predictions
- **Celery** for async tasks (batch processing, retraining)
- **Redis** for caching light curve data

### Performance
- Cache preprocessed light curves (your `.npy` files)
- Use **pagination** for list endpoints
- **Lazy loading** for visualizations
- **CDN** for static plots

### Security
- Rate limiting on prediction endpoints
- File size limits (FITS < 50MB)
- Virus scanning on uploads
- API key authentication for batch API

### Scalability
- Model served via **TorchServe** or similar
- Load balancing for multiple workers
- Database indexing on prediction timestamps, user IDs

---

## 📊 Example API Response

```json
// POST /api/predict/single/
{
  "prediction_id": "pred_abc123",
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
    "model_version": "v1.0.2",
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
    "koi_duration": 2.1,
    "koi_depth": 145.3,
    "koi_prad": 1.2,
    "koi_model_snr": 12.4
  },
  "links": {
    "visualize": "/api/lightcurve/visualize/pred_abc123/",
    "explain": "/api/explain/gradcam/pred_abc123/",
    "similar": "/api/explain/similar-cases/pred_abc123/"
  }
}
```

---

## 🚀 Priority Implementation Order

1. **Core Prediction API** (single + batch)
2. **Light curve visualization** (interactive plots)
3. **Dashboard stats** (show model performance)
4. **Explainability** (Grad-CAM, feature importance)
5. **User feedback system** (collect corrections)
6. **Educational features** (tutorials, examples)
7. **Advanced analytics** (transit search, multi-planet)
8. **Continuous learning** (retraining pipeline)

This will make your project stand out with both **research-grade tools** and **accessible education features**! 🌟
