import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API endpoints
export const predictSingle = async (formData) => {
  const response = await api.post('/predict/single/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const visualizeLightCurve = async (lightCurveId) => {
  const response = await api.get(`/lightcurve/visualize/${lightCurveId}/`);
  return response.data;
};

export const phaseFold = async (lightCurveId, period) => {
  const response = await api.post('/lightcurve/phase-fold/', {
    lightcurve_id: lightCurveId,
    period: period,
  });
  return response.data;
};

export const analyzeTransits = async (lightCurveId) => {
  const response = await api.post('/lightcurve/analyze/', {
    lightcurve_id: lightCurveId,
  });
  return response.data;
};

export const getDashboardStats = async () => {
  const response = await api.get('/dashboard/stats/');
  return response.data;
};

export const getRecentPredictions = async (limit = 10) => {
  const response = await api.get('/dashboard/recent-predictions/', {
    params: { limit },
  });
  return response.data;
};

export const submitFeedback = async (predictionId, correctedDisposition, confidence, comments) => {
  const response = await api.post('/feedback/submit/', {
    prediction_id: predictionId,
    corrected_disposition: correctedDisposition,
    confidence: confidence,
    comments: comments,
  });
  return response.data;
};

export const searchByKepID = async (kepid) => {
  const response = await api.get('/search-kepid/', {
    params: { kepid },
  });
  return response.data;
};

export const getExampleData = async () => {
  const response = await api.get('/get-example/');
  return response.data;
};

export default api;
