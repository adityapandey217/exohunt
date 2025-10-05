import { useState, useEffect } from 'react';
import { FiCheckCircle, FiAlertCircle, FiXCircle, FiLoader } from 'react-icons/fi';
import axios from 'axios';

function PredictionResult({ prediction }) {
  const [visualizationData, setVisualizationData] = useState(null);
  const [loadingViz, setLoadingViz] = useState(false);
  
  if (!prediction) return null;

  const getDispositionIcon = (disposition) => {
    switch (disposition) {
      case 'CONFIRMED':
        return <FiCheckCircle className="text-5xl text-green-500" />;
      case 'CANDIDATE':
        return <FiAlertCircle className="text-5xl text-yellow-500" />;
      case 'FALSE POSITIVE':
        return <FiXCircle className="text-5xl text-red-500" />;
      default:
        return null;
    }
  };

  const getDispositionColor = (disposition) => {
    switch (disposition) {
      case 'CONFIRMED':
        return 'bg-green-50 border-green-200';
      case 'CANDIDATE':
        return 'bg-yellow-50 border-yellow-200';
      case 'FALSE POSITIVE':
        return 'bg-red-50 border-red-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  const getDispositionTextColor = (disposition) => {
    switch (disposition) {
      case 'CONFIRMED':
        return 'text-green-800';
      case 'CANDIDATE':
        return 'text-yellow-800';
      case 'FALSE POSITIVE':
        return 'text-red-800';
      default:
        return 'text-gray-800';
    }
  };

  // Extract the actual prediction data structure from API response
  const predictionData = prediction.prediction || prediction;
  const disposition = predictionData.class || predictionData.predicted_class_name || predictionData.predicted_disposition || 'UNKNOWN';
  const confidence = predictionData.confidence || 0;
  const probabilities = predictionData.probabilities || {};
  const metadata = prediction.metadata || {};
  const lightCurve = prediction.light_curve || prediction.lightcurve || {};
  const kepid = prediction.kepid || lightCurve.kepid || predictionData.kepid;
  
  // Load visualization asynchronously after prediction
  useEffect(() => {
    const loadVisualization = async () => {
      if (!kepid) return;
      
      // Small delay to let prediction display first
      await new Promise(resolve => setTimeout(resolve, 100));
      
      setLoadingViz(true);
      try {
        const response = await axios.get('http://localhost:8000/api/lightcurve/visualize/', {
          params: { kepid }
        });
        setVisualizationData(response.data);
      } catch (err) {
        console.error('Failed to load visualization:', err);
      } finally {
        setLoadingViz(false);
      }
    };
    
    loadVisualization();
  }, [kepid]);

  return (
    <div className="space-y-6">
      {/* Main Prediction Card */}
      <div className={`border-2 rounded-xl p-8 ${getDispositionColor(disposition)}`}>
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <h3 className="text-sm font-medium text-gray-600 mb-2">Prediction Result</h3>
            <div className={`text-3xl font-bold ${getDispositionTextColor(disposition)}`}>
              {disposition}
            </div>
            <div className="mt-2 text-lg text-gray-600">
              Confidence: {(confidence * 100).toFixed(1)}%
            </div>
          </div>
          <div>
            {getDispositionIcon(disposition)}
          </div>
        </div>

        {/* Inference Time */}
        {metadata.processing_time_ms && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="text-sm text-gray-600">
              Processing Time: <span className="font-semibold">{metadata.processing_time_ms}ms</span>
            </div>
          </div>
        )}
      </div>

      {/* Probability Breakdown */}
      <div className="card">
        <h3 className="text-xl font-bold mb-4 text-gray-800">Class Probabilities</h3>
        <div className="space-y-4">
          {Object.entries(probabilities).map(([className, prob]) => (
            <div key={className}>
              <div className="flex justify-between mb-2">
                <span className="font-medium text-gray-700">{className}</span>
                <span className="font-semibold text-gray-900">{(prob * 100).toFixed(2)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className={`h-3 rounded-full transition-all duration-500 ${
                    className === 'CONFIRMED' ? 'bg-green-500' :
                    className === 'CANDIDATE' ? 'bg-yellow-500' :
                    'bg-red-500'
                  }`}
                  style={{ width: `${prob * 100}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Light Curve Visualization */}
      {loadingViz && (
        <div className="card text-center py-8">
          <FiLoader className="animate-spin text-4xl text-indigo-600 mx-auto mb-2" />
          <p className="text-gray-600">Loading light curve visualization...</p>
        </div>
      )}
      
      {visualizationData && !loadingViz && (
        <div className="card">
          <h3 className="text-xl font-bold mb-4 text-gray-800">Light Curve</h3>
          {visualizationData.plot_image && (
            <img 
              src={visualizationData.plot_image} 
              alt="Light Curve" 
              className="w-full mb-4 rounded-lg shadow-md"
            />
          )}
          
          {/* Key Features from KOI Parameters */}
          {prediction.koi_parameters && (
            <div className="mt-6 pt-6 border-t border-gray-200">
              <h4 className="text-lg font-semibold mb-4 text-gray-800">Important Features</h4>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {prediction.koi_parameters.koi_period && (
                  <div className="bg-blue-50 rounded-lg p-3">
                    <div className="text-xs text-blue-600 font-semibold mb-1">Orbital Period</div>
                    <div className="text-lg font-bold text-blue-900">
                      {prediction.koi_parameters.koi_period.toFixed(2)} days
                    </div>
                  </div>
                )}
                {prediction.koi_parameters.koi_prad && (
                  <div className="bg-purple-50 rounded-lg p-3">
                    <div className="text-xs text-purple-600 font-semibold mb-1">Planet Radius</div>
                    <div className="text-lg font-bold text-purple-900">
                      {prediction.koi_parameters.koi_prad.toFixed(2)} R⊕
                    </div>
                  </div>
                )}
                {prediction.koi_parameters.koi_depth && (
                  <div className="bg-green-50 rounded-lg p-3">
                    <div className="text-xs text-green-600 font-semibold mb-1">Transit Depth</div>
                    <div className="text-lg font-bold text-green-900">
                      {prediction.koi_parameters.koi_depth.toFixed(0)} ppm
                    </div>
                  </div>
                )}
                {prediction.koi_parameters.koi_steff && (
                  <div className="bg-yellow-50 rounded-lg p-3">
                    <div className="text-xs text-yellow-600 font-semibold mb-1">Stellar Temp</div>
                    <div className="text-lg font-bold text-yellow-900">
                      {prediction.koi_parameters.koi_steff.toFixed(0)} K
                    </div>
                  </div>
                )}
                {prediction.koi_parameters.koi_insol && (
                  <div className="bg-red-50 rounded-lg p-3">
                    <div className="text-xs text-red-600 font-semibold mb-1">Insolation</div>
                    <div className="text-lg font-bold text-red-900">
                      {prediction.koi_parameters.koi_insol.toFixed(2)} S⊕
                    </div>
                  </div>
                )}
                {prediction.koi_parameters.koi_model_snr && (
                  <div className="bg-indigo-50 rounded-lg p-3">
                    <div className="text-xs text-indigo-600 font-semibold mb-1">Signal-to-Noise</div>
                    <div className="text-lg font-bold text-indigo-900">
                      {prediction.koi_parameters.koi_model_snr.toFixed(1)}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
          
          {/* Light Curve Statistics */}
          {visualizationData.metadata && (
            <div className="mt-6 pt-6 border-t border-gray-200">
              <h4 className="text-lg font-semibold mb-4 text-gray-800">Light Curve Statistics</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="text-xs text-gray-600 font-semibold mb-1">Data Points</div>
                  <div className="text-base font-bold text-gray-900">
                    {visualizationData.metadata.flux_points?.toLocaleString()}
                  </div>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="text-xs text-gray-600 font-semibold mb-1">Duration</div>
                  <div className="text-base font-bold text-gray-900">
                    {visualizationData.metadata.duration_days?.toFixed(1)} d
                  </div>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="text-xs text-gray-600 font-semibold mb-1">Quality</div>
                  <div className="text-base font-bold text-gray-900">
                    {(visualizationData.metadata.data_quality_score * 100).toFixed(1)}%
                  </div>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="text-xs text-gray-600 font-semibold mb-1">Flux Type</div>
                  <div className="text-base font-bold text-gray-900">
                    {visualizationData.metadata.flux_type}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Light Curve Metadata */}
      {!visualizationData && !loadingViz && (kepid || lightCurve.points || lightCurve.duration_days || lightCurve.quality_score) && (
        <div className="card">
          <h3 className="text-xl font-bold mb-4 text-gray-800">Light Curve Metadata</h3>
          <div className="grid grid-cols-2 gap-4">
            {kepid && (
              <div>
                <div className="text-sm text-gray-600">KepID</div>
                <div className="font-semibold text-gray-900">{kepid}</div>
              </div>
            )}
            <div>
              <div className="text-sm text-gray-600">Duration</div>
              <div className="font-semibold text-gray-900">
                {lightCurve.duration_days ? `${lightCurve.duration_days.toFixed(2)} days` : 'N/A'}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Data Points</div>
              <div className="font-semibold text-gray-900">{lightCurve.points || lightCurve.flux_points || 'N/A'}</div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Quality Score</div>
              <div className="font-semibold text-gray-900">
                {lightCurve.quality_score ? `${(lightCurve.quality_score * 100).toFixed(1)}%` : 'N/A'}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default PredictionResult;
