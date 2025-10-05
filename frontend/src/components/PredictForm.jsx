import { useState } from 'react';
import { predictSingle } from '../utils/api';
import { FiUpload, FiLoader } from 'react-icons/fi';
import { Alert } from 'flowbite-react';

function PredictForm({ onPredictionComplete }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [koiParams, setKoiParams] = useState({
    koi_period: '',
    koi_depth: '',
    koi_duration: '',
    koi_prad: '',
    koi_teq: '',
    koi_srad: '',
    koi_steff: '',
  });

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError(null);
    }
  };

  const handleParamChange = (e) => {
    setKoiParams({
      ...koiParams,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a FITS file');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('fits_file', file);
      
      // Add KOI parameters if provided
      Object.keys(koiParams).forEach(key => {
        if (koiParams[key]) {
          formData.append(key, koiParams[key]);
        }
      });

      const result = await predictSingle(formData);
      onPredictionComplete(result);
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred during prediction');
      console.error('Prediction error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Upload Light Curve</h2>
      
      {error && (
        <Alert color="failure" className="mb-4">
          {error}
        </Alert>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* File Upload */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            FITS File *
          </label>
          <div className="flex items-center justify-center w-full">
            <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100 transition-colors duration-200">
              <div className="flex flex-col items-center justify-center pt-5 pb-6">
                <FiUpload className="w-10 h-10 mb-3 text-gray-400" />
                <p className="mb-2 text-sm text-gray-500">
                  <span className="font-semibold">Click to upload</span> or drag and drop
                </p>
                <p className="text-xs text-gray-500">
                  {file ? file.name : 'FITS file from Kepler/TESS'}
                </p>
              </div>
              <input
                type="file"
                className="hidden"
                accept=".fits"
                onChange={handleFileChange}
              />
            </label>
          </div>
        </div>

        {/* Optional KOI Parameters */}
        <div className="border-t pt-4">
          <h3 className="text-lg font-semibold mb-4 text-gray-700">
            Optional Parameters (improves accuracy)
          </h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Period (days)
              </label>
              <input
                type="number"
                step="any"
                name="koi_period"
                value={koiParams.koi_period}
                onChange={handleParamChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="e.g., 3.52"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Depth (ppm)
              </label>
              <input
                type="number"
                step="any"
                name="koi_depth"
                value={koiParams.koi_depth}
                onChange={handleParamChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="e.g., 1234.5"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Duration (hours)
              </label>
              <input
                type="number"
                step="any"
                name="koi_duration"
                value={koiParams.koi_duration}
                onChange={handleParamChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="e.g., 2.5"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Planet Radius (Earth radii)
              </label>
              <input
                type="number"
                step="any"
                name="koi_prad"
                value={koiParams.koi_prad}
                onChange={handleParamChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="e.g., 1.2"
              />
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          className="w-full btn-primary flex items-center justify-center space-x-2"
        >
          {loading ? (
            <>
              <FiLoader className="animate-spin text-xl" />
              <span>Analyzing...</span>
            </>
          ) : (
            <span>Predict Exoplanet</span>
          )}
        </button>
      </form>
    </div>
  );
}

export default PredictForm;
