import { FiCheckCircle, FiAlertCircle, FiXCircle } from 'react-icons/fi';

function PredictionResult({ prediction }) {
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

  return (
    <div className="space-y-6">
      {/* Main Prediction Card */}
      <div className={`border-2 rounded-xl p-8 ${getDispositionColor(prediction.predicted_disposition)}`}>
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <h3 className="text-sm font-medium text-gray-600 mb-2">Prediction Result</h3>
            <div className={`text-3xl font-bold ${getDispositionTextColor(prediction.predicted_disposition)}`}>
              {prediction.predicted_disposition}
            </div>
            <div className="mt-2 text-lg text-gray-600">
              Confidence: {(prediction.confidence * 100).toFixed(1)}%
            </div>
          </div>
          <div>
            {getDispositionIcon(prediction.predicted_disposition)}
          </div>
        </div>

        {/* Inference Time */}
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="text-sm text-gray-600">
            Inference Time: <span className="font-semibold">{prediction.inference_time.toFixed(3)}s</span>
          </div>
        </div>
      </div>

      {/* Probability Breakdown */}
      <div className="card">
        <h3 className="text-xl font-bold mb-4 text-gray-800">Class Probabilities</h3>
        <div className="space-y-4">
          {Object.entries(prediction.probabilities).map(([className, prob]) => (
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

      {/* Light Curve Metadata */}
      {prediction.lightcurve && (
        <div className="card">
          <h3 className="text-xl font-bold mb-4 text-gray-800">Light Curve Metadata</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-sm text-gray-600">KIC ID</div>
              <div className="font-semibold text-gray-900">{prediction.lightcurve.kic_id || 'N/A'}</div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Duration</div>
              <div className="font-semibold text-gray-900">
                {prediction.lightcurve.duration ? `${prediction.lightcurve.duration.toFixed(2)} days` : 'N/A'}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Data Points</div>
              <div className="font-semibold text-gray-900">{prediction.lightcurve.flux_points || 'N/A'}</div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Quality Score</div>
              <div className="font-semibold text-gray-900">
                {prediction.lightcurve.quality_score ? `${(prediction.lightcurve.quality_score * 100).toFixed(1)}%` : 'N/A'}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default PredictionResult;
