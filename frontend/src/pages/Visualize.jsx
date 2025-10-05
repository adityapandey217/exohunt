import { useState } from 'react';
import { FiUpload, FiLoader, FiSearch, FiZap } from 'react-icons/fi';
import { searchByKepID, getExampleData } from '../utils/api';
import { Alert } from 'flowbite-react';
import axios from 'axios';

function Visualize() {
  const [file, setFile] = useState(null);
  const [kepidSearch, setKepidSearch] = useState('');
  const [searchingKepid, setSearchingKepid] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [plotData, setPlotData] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError(null);
      setPlotData(null);
    }
  };

  const handleKepidSearch = async () => {
    if (!kepidSearch) {
      setError('Please enter a KepID');
      return;
    }

    setSearchingKepid(true);
    setError(null);
    setSuccess(null);
    setPlotData(null);

    try {
      // Verify KepID exists in dataset
      const result = await searchByKepID(kepidSearch);
      
      // Now visualize directly using lightkurve via GET
      const response = await axios.get('http://localhost:8000/api/lightcurve/visualize/', {
        params: { kepid: kepidSearch }
      });
      
      if (response.data) {
        setPlotData(response.data);
        setSuccess(`✅ Light curve for KepID ${kepidSearch} loaded from MAST archive!`);
        setFile({ name: `KepID ${kepidSearch}`, fromServer: true, kepid: kepidSearch });
      }
    } catch (err) {
      setError(err.response?.data?.error || `Failed to find/visualize KepID ${kepidSearch}`);
    } finally {
      setSearchingKepid(false);
    }
  };

  const handleLoadExample = async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);
    setPlotData(null);

    try {
      const result = await getExampleData();
      
      if (result.kepid) {
        setKepidSearch(result.kepid.toString());
        
        // Visualize directly using lightkurve
        const response = await axios.get('http://localhost:8000/api/lightcurve/visualize/', {
          params: { kepid: result.kepid }
        });
        
        if (response.data) {
          setPlotData(response.data);
          setSuccess(`🎯 Loaded confirmed exoplanet KepID ${result.kepid} from MAST archive!`);
          setFile({ name: `KepID ${result.kepid}`, fromServer: true, kepid: result.kepid });
        }
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load example data');
    } finally {
      setLoading(false);
    }
  };

  const handleVisualize = async () => {
    if (!file) {
      setError('Please upload a FITS file or search by KepID');
      return;
    }

    setLoading(true);
    setError(null);
    setPlotData(null);

    try {
      if (file.fromServer) {
        // Use GET with kepid parameter
        const response = await axios.get('http://localhost:8000/api/lightcurve/visualize/', {
          params: { kepid: file.kepid }
        });
        
        if (response.data) {
          setPlotData(response.data);
          setSuccess('✅ Light curve loaded successfully from MAST archive!');
        }
      } else {
        // Upload FITS file
        const formData = new FormData();
        formData.append('fits_file', file);

        const response = await axios.post('http://localhost:8000/api/lightcurve/visualize/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        if (response.data) {
          setPlotData(response.data);
          setSuccess('✅ Light curve loaded successfully from uploaded file!');
        }
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to visualize light curve');
      console.error('Visualization error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">Light Curve Visualization</h1>
          <p className="text-gray-600">
            Visualize and analyze Kepler/TESS light curves
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left Column - Upload/Search */}
          <div className="lg:col-span-1">
            <div className="card sticky top-8">
              <h2 className="text-2xl font-bold mb-6 text-gray-800">Load Light Curve</h2>
              
              {/* Quick Actions */}
              <div className="mb-6 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
                <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
                  <FiZap className="mr-2 text-blue-600" />
                  Quick Start
                </h3>
                <button
                  type="button"
                  onClick={handleLoadExample}
                  disabled={loading || searchingKepid}
                  className="w-full bg-gradient-to-r from-purple-600 to-indigo-600 text-white px-4 py-2 rounded-lg hover:from-purple-700 hover:to-indigo-700 transition-all duration-200 font-semibold shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
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

              <div className="space-y-6">
                {/* KepID Search */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Search by KepID
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
                </div>

                {/* File Upload */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Or Upload FITS File
                  </label>
                  <div className="flex items-center justify-center w-full">
                    <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100 transition-colors duration-200">
                      <div className="flex flex-col items-center justify-center pt-5 pb-6">
                        <FiUpload className="w-10 h-10 mb-3 text-gray-400" />
                        <p className="mb-2 text-sm text-gray-500">
                          <span className="font-semibold">Click to upload</span>
                        </p>
                        <p className="text-xs text-gray-500">
                          {file ? (
                            <span className="font-semibold text-green-600">
                              {file.fromServer ? `✅ ${file.name}` : file.name}
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
                      />
                    </label>
                  </div>
                </div>

                {/* Visualize Button */}
                <button
                  onClick={handleVisualize}
                  disabled={loading || !file}
                  className="w-full btn-primary flex items-center justify-center space-x-2"
                >
                  {loading ? (
                    <>
                      <FiLoader className="animate-spin text-xl" />
                      <span>Loading...</span>
                    </>
                  ) : (
                    <span>Visualize Light Curve</span>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Right Column - Visualization */}
          <div className="lg:col-span-2">
            {plotData ? (
              <div className="card">
                <h3 className="text-xl font-bold mb-4 text-gray-800">
                  Light Curve Visualization
                </h3>
                
                {/* PNG Image Plot */}
                {plotData.plot_image && (
                  <img 
                    src={plotData.plot_image} 
                    alt="Light Curve" 
                    className="w-full mb-6 rounded-lg shadow-md"
                  />
                )}

                {/* Metadata */}
                {plotData.metadata && (
                  <div className="pt-6 border-t border-gray-200">
                    <h4 className="text-lg font-semibold mb-4 text-gray-800">Light Curve Statistics</h4>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="bg-blue-50 rounded-lg p-3">
                        <div className="text-xs text-blue-600 font-semibold mb-1">Data Points</div>
                        <div className="text-lg font-bold text-blue-900">
                          {plotData.metadata.flux_points?.toLocaleString() || 'N/A'}
                        </div>
                      </div>
                      <div className="bg-purple-50 rounded-lg p-3">
                        <div className="text-xs text-purple-600 font-semibold mb-1">Duration</div>
                        <div className="text-lg font-bold text-purple-900">
                          {plotData.metadata.duration_days?.toFixed(1) || 'N/A'} days
                        </div>
                      </div>
                      <div className="bg-green-50 rounded-lg p-3">
                        <div className="text-xs text-green-600 font-semibold mb-1">Quality Score</div>
                        <div className="text-lg font-bold text-green-900">
                          {plotData.metadata.data_quality_score ? (plotData.metadata.data_quality_score * 100).toFixed(1) + '%' : 'N/A'}
                        </div>
                      </div>
                      <div className="bg-yellow-50 rounded-lg p-3">
                        <div className="text-xs text-yellow-600 font-semibold mb-1">Gaps Detected</div>
                        <div className="text-lg font-bold text-yellow-900">
                          {plotData.metadata.gaps_detected ?? 'N/A'}
                        </div>
                      </div>
                      <div className="bg-indigo-50 rounded-lg p-3">
                        <div className="text-xs text-indigo-600 font-semibold mb-1">Mean Flux</div>
                        <div className="text-lg font-bold text-indigo-900">
                          {plotData.metadata.flux_mean?.toExponential(3) || 'N/A'}
                        </div>
                      </div>
                      <div className="bg-pink-50 rounded-lg p-3">
                        <div className="text-xs text-pink-600 font-semibold mb-1">Std Dev</div>
                        <div className="text-lg font-bold text-pink-900">
                          {plotData.metadata.flux_std?.toExponential(3) || 'N/A'}
                        </div>
                      </div>
                      <div className="bg-red-50 rounded-lg p-3">
                        <div className="text-xs text-red-600 font-semibold mb-1">Median Flux</div>
                        <div className="text-lg font-bold text-red-900">
                          {plotData.metadata.flux_median?.toExponential(3) || 'N/A'}
                        </div>
                      </div>
                      <div className="bg-teal-50 rounded-lg p-3">
                        <div className="text-xs text-teal-600 font-semibold mb-1">Flux Type</div>
                        <div className="text-lg font-bold text-teal-900">
                          {plotData.metadata.flux_type || 'N/A'}
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="card text-center py-20">
                <div className="text-gray-400 mb-4">
                  <svg
                    className="w-20 h-20 mx-auto"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"
                    />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-gray-600 mb-2">
                  No Visualization Yet
                </h3>
                <p className="text-gray-500">
                  Upload or search for a light curve to visualize
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Visualize;
