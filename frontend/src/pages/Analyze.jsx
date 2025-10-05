import { useState } from 'react';
import PredictForm from '../components/PredictForm';
import PredictionResult from '../components/PredictionResult';
import LightCurveViewer from '../components/LightCurveViewer';
import { FiChevronDown, FiChevronUp } from 'react-icons/fi';

function Analyze() {
  const [prediction, setPrediction] = useState(null);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handlePredictionComplete = (result) => {
    setPrediction(result);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">Analyze Light Curve</h1>
          <p className="text-gray-600">
            Upload a FITS file to detect exoplanet transits using our AI model
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Left Column - Upload Form */}
          <div>
            <PredictForm onPredictionComplete={handlePredictionComplete} />
          </div>

          {/* Right Column - Prediction Results */}
          <div>
            {prediction ? (
              <PredictionResult prediction={prediction} />
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
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-gray-600 mb-2">
                  No Prediction Yet
                </h3>
                <p className="text-gray-500">
                  Upload a light curve file to see the results
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Advanced Analysis Section */}
        {prediction && prediction.lightcurve && (
          <div className="mt-8">
            <button
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="w-full bg-white rounded-lg shadow-md p-4 flex items-center justify-between hover:shadow-lg transition-shadow duration-200"
            >
              <span className="text-xl font-bold text-gray-800">
                Advanced Analysis & Visualization
              </span>
              {showAdvanced ? (
                <FiChevronUp className="text-2xl text-gray-600" />
              ) : (
                <FiChevronDown className="text-2xl text-gray-600" />
              )}
            </button>

            {showAdvanced && (
              <div className="mt-6 space-y-6 animate-fade-in">
                <LightCurveViewer lightCurveId={prediction.lightcurve.id} />
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default Analyze;
