import { useState } from 'react';
import { predictSingle, searchByKepID, getExampleData } from '../utils/api';
import { FiUpload, FiLoader, FiSearch, FiZap } from 'react-icons/fi';
import { Alert } from 'flowbite-react';

function PredictForm({ onPredictionComplete }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [kepidSearch, setKepidSearch] = useState('');
  const [searchingKepid, setSearchingKepid] = useState(false);
  const [koiParams, setKoiParams] = useState({
    koi_period: '',
    koi_duration: '',
    koi_depth: '',
    koi_prad: '',
    koi_ror: '',
    koi_model_snr: '',
    koi_num_transits: '',
    koi_steff: '',
    koi_slogg: '',
    koi_srad: '',
    koi_smass: '',
    koi_kepmag: '',
    koi_insol: '',
    koi_dor: '',
    koi_count: '',
    // koi_score: REMOVED - severe data leakage (0.89 correlation with label)
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

  const handleKepidSearch = async () => {
    if (!kepidSearch) {
      setError('Please enter a KepID');
      return;
    }

    setSearchingKepid(true);
    setError(null);
    setSuccess(null);

    try {
      const result = await searchByKepID(kepidSearch);
      
      if (result.success) {
        // Fill in parameters
        const params = result.parameters;
        setKoiParams({
          koi_period: params.koi_period || '',
          koi_duration: params.koi_duration || '',
          koi_depth: params.koi_depth || '',
          koi_prad: params.koi_prad || '',
          koi_ror: params.koi_ror || '',
          koi_model_snr: params.koi_model_snr || '',
          koi_num_transits: params.koi_num_transits || '',
          koi_steff: params.koi_steff || '',
          koi_slogg: params.koi_slogg || '',
          koi_srad: params.koi_srad || '',
          koi_smass: params.koi_smass || '',
          koi_kepmag: params.koi_kepmag || '',
          koi_insol: params.koi_insol || '',
          koi_dor: params.koi_dor || '',
          koi_count: params.koi_count || '',
          // koi_score removed - data leakage
        });

        // FITS file will be downloaded via lightkurve
        setSuccess(`✅ ${result.message} Parameters loaded!`);
        setFile({ name: `KepID ${result.kepid} (via MAST)`, fromServer: true, kepid: result.kepid });
      }
    } catch (err) {
      setError(err.response?.data?.error || `Failed to find data for KepID ${kepidSearch}`);
    } finally {
      setSearchingKepid(false);
    }
  };

  const handleLoadExample = async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const result = await getExampleData();
      
      if (result.success) {
        // Fill in parameters
        const params = result.parameters;
        setKoiParams({
          koi_period: params.koi_period || '',
          koi_duration: params.koi_duration || '',
          koi_depth: params.koi_depth || '',
          koi_prad: params.koi_prad || '',
          koi_ror: params.koi_ror || '',
          koi_model_snr: params.koi_model_snr || '',
          koi_num_transits: params.koi_num_transits || '',
          koi_steff: params.koi_steff || '',
          koi_slogg: params.koi_slogg || '',
          koi_srad: params.koi_srad || '',
          koi_smass: params.koi_smass || '',
          koi_kepmag: params.koi_kepmag || '',
          koi_insol: params.koi_insol || '',
          koi_dor: params.koi_dor || '',
          koi_count: params.koi_count || '',
          // koi_score removed - data leakage
        });

        setKepidSearch(result.kepid);
        setFile({ name: `KepID ${result.kepid} (via MAST)`, fromServer: true, kepid: result.kepid });
        setSuccess(`🎯 ${result.message} Ready to predict!`);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load example data');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a FITS file');
      return;
    }

    // Validate required KOI parameters
    const requiredParams = [
      'koi_period', 'koi_duration', 'koi_depth', 'koi_prad', 'koi_ror',
      'koi_model_snr', 'koi_num_transits', 'koi_steff', 'koi_slogg',
      'koi_srad', 'koi_smass', 'koi_kepmag', 'koi_insol', 'koi_dor',
      'koi_count'
      // koi_score removed - data leakage (0.89 correlation with label)
    ];
    
    const missingParams = requiredParams.filter(param => !koiParams[param] || koiParams[param] === '');
    if (missingParams.length > 0) {
      setError(`Please fill in all required parameters. Missing: ${missingParams.join(', ')}`);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      
      // If file is from server (via KepID search), send kepid instead
      if (file.fromServer) {
        formData.append('kepid', file.kepid);
      } else {
        formData.append('fits_file', file);
      }
      
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
      
      {/* Quick Actions */}
      <div className="mb-6 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
        <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
          <FiZap className="mr-2 text-blue-600" />
          Quick Start for NASA Space Apps Hackathon
        </h3>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={handleLoadExample}
            disabled={loading || searchingKepid}
            className="flex-1 bg-gradient-to-r from-purple-600 to-indigo-600 text-white px-4 py-2 rounded-lg hover:from-purple-700 hover:to-indigo-700 transition-all duration-200 font-semibold shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            {loading ? (
              <>
                <FiLoader className="animate-spin mr-2" />
                Loading...
              </>
            ) : (
              <>
                <FiZap className="mr-2" />
                Load Random Example
              </>
            )}
          </button>
        </div>
        <p className="text-xs text-gray-600 mt-2">
          ⚡ Instantly load a real confirmed exoplanet with all data filled in!
        </p>
      </div>

      {error && (
        <Alert color="failure" className="mb-4">
          {error}
        </Alert>
      )}

      {success && (
        <Alert color="success" className="mb-4">
          {success}
        </Alert>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* KepID Search */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Search by KepID (Optional)
          </label>
          <div className="flex gap-2">
            <input
              type="text"
              value={kepidSearch}
              onChange={(e) => setKepidSearch(e.target.value)}
              placeholder="e.g., 10797460"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleKepidSearch())}
            />
            <button
              type="button"
              onClick={handleKepidSearch}
              disabled={searchingKepid || !kepidSearch}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
            >
              {searchingKepid ? (
                <FiLoader className="animate-spin" />
              ) : (
                <>
                  <FiSearch className="mr-2" />
                  Search
                </>
              )}
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Enter a Kepler ID to auto-load parameters and FITS file from our dataset
          </p>
        </div>

        {/* File Upload */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            FITS File {!file?.fromServer && '*'}
          </label>
          <div className="flex items-center justify-center w-full">
            <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100 transition-colors duration-200">
              <div className="flex flex-col items-center justify-center pt-5 pb-6">
                <FiUpload className="w-10 h-10 mb-3 text-gray-400" />
                <p className="mb-2 text-sm text-gray-500">
                  <span className="font-semibold">Click to upload</span> or drag and drop
                </p>
                <p className="text-xs text-gray-500">
                  {file ? (
                    <span className="font-semibold text-green-600">
                      {file.fromServer ? `✅ Using ${file.name} from server` : file.name}
                    </span>
                  ) : (
                    'FITS file from Kepler/TESS'
                  )}
                </p>
              </div>
              <input
                type="file"
                className="hidden"
                accept=".fits"
                onChange={handleFileChange}
                disabled={file?.fromServer}
              />
            </label>
          </div>
          {file?.fromServer && (
            <p className="text-xs text-blue-600 mt-1">
              💡 FITS file will be downloaded from MAST archive via lightkurve. Upload your own file to override.
            </p>
          )}
        </div>

        {/* Required KOI Parameters */}
        <div className="border-t pt-4">
          <h3 className="text-lg font-semibold mb-4 text-gray-700">
            Required Parameters *
          </h3>
          
          {/* Orbital Parameters */}
          <div className="mb-4">
            <h4 className="text-sm font-semibold text-gray-600 mb-2">Orbital Parameters</h4>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Period (days) *
                </label>
                <input
                  type="number"
                  step="any"
                  name="koi_period"
                  value={koiParams.koi_period}
                  onChange={handleParamChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., 3.52"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Duration (hours) *
                </label>
                <input
                  type="number"
                  step="any"
                  name="koi_duration"
                  value={koiParams.koi_duration}
                  onChange={handleParamChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., 2.5"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Depth (ppm) *
                </label>
                <input
                  type="number"
                  step="any"
                  name="koi_depth"
                  value={koiParams.koi_depth}
                  onChange={handleParamChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., 1234.5"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Planet Radius (Earth radii) *
                </label>
                <input
                  type="number"
                  step="any"
                  name="koi_prad"
                  value={koiParams.koi_prad}
                  onChange={handleParamChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., 1.2"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Planet/Star Radius Ratio *
                </label>
                <input
                  type="number"
                  step="any"
                  name="koi_ror"
                  value={koiParams.koi_ror}
                  onChange={handleParamChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., 0.015"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Signal-to-Noise Ratio *
                </label>
                <input
                  type="number"
                  step="any"
                  name="koi_model_snr"
                  value={koiParams.koi_model_snr}
                  onChange={handleParamChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., 15.2"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Number of Transits *
                </label>
                <input
                  type="number"
                  name="koi_num_transits"
                  value={koiParams.koi_num_transits}
                  onChange={handleParamChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., 12"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Insolation Flux (Earth flux) *
                </label>
                <input
                  type="number"
                  step="any"
                  name="koi_insol"
                  value={koiParams.koi_insol}
                  onChange={handleParamChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., 5.8"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Planet-Star Distance / Star Radius *
                </label>
                <input
                  type="number"
                  step="any"
                  name="koi_dor"
                  value={koiParams.koi_dor}
                  onChange={handleParamChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., 18.5"
                  required
                />
              </div>
            </div>
          </div>

          {/* Stellar Parameters */}
          <div className="mb-4">
            <h4 className="text-sm font-semibold text-gray-600 mb-2">Stellar Parameters</h4>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Stellar Temperature (K) *
                </label>
                <input
                  type="number"
                  step="any"
                  name="koi_steff"
                  value={koiParams.koi_steff}
                  onChange={handleParamChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., 5778"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Stellar Surface Gravity *
                </label>
                <input
                  type="number"
                  step="any"
                  name="koi_slogg"
                  value={koiParams.koi_slogg}
                  onChange={handleParamChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., 4.5"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Stellar Radius (solar radii) *
                </label>
                <input
                  type="number"
                  step="any"
                  name="koi_srad"
                  value={koiParams.koi_srad}
                  onChange={handleParamChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., 1.0"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Stellar Mass (solar masses) *
                </label>
                <input
                  type="number"
                  step="any"
                  name="koi_smass"
                  value={koiParams.koi_smass}
                  onChange={handleParamChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., 1.0"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Kepler Magnitude *
                </label>
                <input
                  type="number"
                  step="any"
                  name="koi_kepmag"
                  value={koiParams.koi_kepmag}
                  onChange={handleParamChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., 12.5"
                  required
                />
              </div>
            </div>
          </div>

          {/* Metadata */}
          <div>
            <h4 className="text-sm font-semibold text-gray-600 mb-2">Metadata</h4>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Number of KOIs for this Star *
                </label>
                <input
                  type="number"
                  name="koi_count"
                  value={koiParams.koi_count}
                  onChange={handleParamChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., 3"
                  required
                />
              </div>
              {/* koi_score field REMOVED - data leakage (0.89 correlation with label) */}
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
