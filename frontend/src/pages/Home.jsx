import { Link } from 'react-router-dom';
import { FiArrowRight, FiStar, FiTrendingUp, FiDatabase, FiInfo, FiLayers, FiCpu, FiTarget, FiCheckCircle, FiAlertCircle, FiXCircle } from 'react-icons/fi';

function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20">
        <div className="text-center max-w-4xl mx-auto animate-fade-in">
          <h1 className="text-6xl font-bold mb-6 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
            Discover Exoplanets with AI
          </h1>
          <p className="text-xl text-gray-600 mb-8 leading-relaxed">
            Harness the power of deep learning to detect exoplanets from Kepler and TESS light curves.
            Our hybrid CNN+MLP model analyzes stellar brightness variations to identify planetary transits.
          </p>
          <div className="flex justify-center space-x-4">
            <Link to="/analyze" className="btn-primary flex items-center space-x-2">
              <span>Start Analysis</span>
              <FiArrowRight />
            </Link>
            <Link to="/dashboard" className="btn-secondary">
              View Dashboard
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-16">
        <div className="grid md:grid-cols-3 gap-8">
          <div className="card text-center">
            <div className="flex justify-center mb-4">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
                <FiStar className="text-3xl text-blue-600" />
              </div>
            </div>
            <h3 className="text-xl font-bold mb-3 text-gray-800">Deep Learning Detection</h3>
            <p className="text-gray-600">
              Hybrid CNN+MLP architecture trained on thousands of Kepler light curves with 67.5% validation accuracy.
            </p>
          </div>

          <div className="card text-center">
            <div className="flex justify-center mb-4">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center">
                <FiTrendingUp className="text-3xl text-purple-600" />
              </div>
            </div>
            <h3 className="text-xl font-bold mb-3 text-gray-800">Real-Time Analysis</h3>
            <p className="text-gray-600">
              Processes 2,000 flux measurements and 15 stellar parameters to detect exoplanet transit signatures.
            </p>
          </div>

          <div className="card text-center">
            <div className="flex justify-center mb-4">
              <div className="w-16 h-16 bg-pink-100 rounded-full flex items-center justify-center">
                <FiDatabase className="text-3xl text-pink-600" />
              </div>
            </div>
            <h3 className="text-xl font-bold mb-3 text-gray-800">NASA MAST Integration</h3>
            <p className="text-gray-600">
              Direct access to Kepler mission data with interactive visualizations and comprehensive analysis tools.
            </p>
          </div>
        </div>
      </section>

      {/* About Our Model Section */}
      <section className="container mx-auto px-4 py-16 bg-white">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center justify-center mb-8">
            <FiInfo className="text-4xl text-blue-600 mr-3" />
            <h2 className="text-4xl font-bold text-gray-800">Our AI Model</h2>
          </div>

          {/* Overview */}
          <div className="mb-12 p-8 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border-2 border-blue-200">
            <h3 className="text-2xl font-semibold text-gray-800 mb-4 flex items-center">
              <FiCpu className="mr-3 text-blue-600 text-3xl" />
              Hybrid Deep Learning Architecture
            </h3>
            <p className="text-gray-700 leading-relaxed mb-6 text-lg">
              Our exoplanet detection system uses a <strong>hybrid neural network</strong> that combines the power of 
              Convolutional Neural Networks (CNN) and Multi-Layer Perceptrons (MLP) to analyze both time-series light curve 
              data and stellar parameters simultaneously. This dual-stream approach captures both temporal patterns and 
              physical characteristics to make accurate predictions.
            </p>
            <div className="grid md:grid-cols-2 gap-6 mt-6">
              <div className="bg-white p-6 rounded-xl shadow-md border border-blue-100">
                <h4 className="font-bold text-gray-800 mb-3 text-lg flex items-center">
                  🌟 Light Curve Analysis (CNN)
                </h4>
                <p className="text-gray-600">
                  Processes <strong>2,000 time-series data points</strong> from Kepler space telescope observations to detect 
                  periodic dimming patterns characteristic of planetary transits. The CNN automatically learns to identify 
                  the distinctive U-shaped dips in stellar brightness.
                </p>
              </div>
              <div className="bg-white p-6 rounded-xl shadow-md border border-purple-100">
                <h4 className="font-bold text-gray-800 mb-3 text-lg flex items-center">
                  📊 Stellar Parameters (MLP)
                </h4>
                <p className="text-gray-600">
                  Analyzes <strong>15 critical features</strong> including orbital period, planet radius, stellar temperature, 
                  and transit depth to validate planetary characteristics. The MLP provides context about the host star 
                  and orbital dynamics.
                </p>
              </div>
            </div>
          </div>

          {/* Model Architecture Workflow */}
          <div className="mb-12">
            <h3 className="text-2xl font-semibold text-gray-800 mb-6 flex items-center">
              <FiLayers className="mr-3 text-indigo-600 text-3xl" />
              How Our Model Works
            </h3>
            <div className="grid md:grid-cols-3 gap-8">
              {/* Step 1 */}
              <div className="bg-gradient-to-br from-purple-100 to-purple-50 p-8 rounded-xl border-2 border-purple-300 shadow-lg transform hover:scale-105 transition-transform duration-200">
                <div className="text-5xl font-bold text-purple-600 mb-3">1</div>
                <h4 className="font-bold text-gray-800 mb-3 text-xl">Data Input</h4>
                <p className="text-gray-700">
                  Light curve from NASA MAST archive (FITS file) containing flux measurements + 15 KOI stellar/orbital parameters
                </p>
              </div>

              {/* Step 2 */}
              <div className="bg-gradient-to-br from-blue-100 to-blue-50 p-8 rounded-xl border-2 border-blue-300 shadow-lg transform hover:scale-105 transition-transform duration-200">
                <div className="text-5xl font-bold text-blue-600 mb-3">2</div>
                <h4 className="font-bold text-gray-800 mb-3 text-xl">Dual Processing</h4>
                <p className="text-gray-700">
                  CNN extracts temporal patterns from light curve • MLP processes tabular features • Both neural pathways run in parallel
                </p>
              </div>

              {/* Step 3 */}
              <div className="bg-gradient-to-br from-green-100 to-green-50 p-8 rounded-xl border-2 border-green-300 shadow-lg transform hover:scale-105 transition-transform duration-200">
                <div className="text-5xl font-bold text-green-600 mb-3">3</div>
                <h4 className="font-bold text-gray-800 mb-3 text-xl">Fusion & Prediction</h4>
                <p className="text-gray-700">
                  Combined features fed to final classifier → 3-class prediction (Confirmed/Candidate/False Positive) with confidence scores
                </p>
              </div>
            </div>
          </div>

          {/* Model Performance */}
          <div className="mb-12">
            <h3 className="text-2xl font-semibold text-gray-800 mb-6 flex items-center">
              <FiTarget className="mr-3 text-green-600 text-3xl" />
              Model Performance Metrics
            </h3>
            
            {/* Overall Accuracy */}
            <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-8 rounded-xl border-2 border-green-200 mb-8 shadow-md">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xl font-semibold text-gray-800">Overall Validation Accuracy</span>
                <span className="text-5xl font-bold text-green-600">67.5%</span>
              </div>
              <div className="w-full bg-gray-300 rounded-full h-6 mb-3">
                <div className="bg-gradient-to-r from-green-500 to-green-600 h-6 rounded-full flex items-center justify-end pr-3" style={{ width: '67.5%' }}>
                  <span className="text-white text-sm font-bold">67.5%</span>
                </div>
              </div>
              <p className="text-gray-700 text-lg">
                Weighted F1 Score: <strong>63.0%</strong> • Validated on <strong>1,902 Kepler Objects of Interest</strong>
              </p>
            </div>

            {/* Per-Class Performance */}
            <div className="grid md:grid-cols-3 gap-8">
              {/* FALSE POSITIVE */}
              <div className="bg-white p-8 rounded-xl shadow-lg border-l-4 border-red-500">
                <div className="flex items-center justify-between mb-5">
                  <h4 className="font-bold text-gray-800 text-lg flex items-center">
                    <FiXCircle className="mr-2 text-red-500 text-2xl" />
                    False Positive
                  </h4>
                  <span className="text-sm text-gray-500 font-semibold">981 samples</span>
                </div>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-gray-600 font-medium">Precision</span>
                      <span className="font-bold text-gray-800 text-lg">74%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div className="bg-red-500 h-3 rounded-full" style={{ width: '74%' }}></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-gray-600 font-medium">Recall</span>
                      <span className="font-bold text-gray-800 text-lg">86%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div className="bg-red-500 h-3 rounded-full" style={{ width: '86%' }}></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-gray-600 font-medium">F1-Score</span>
                      <span className="font-bold text-gray-800 text-lg">79%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div className="bg-red-500 h-3 rounded-full" style={{ width: '79%' }}></div>
                    </div>
                  </div>
                </div>
                <div className="mt-4 p-3 bg-red-50 rounded-lg border border-red-200">
                  <p className="text-sm text-gray-700">
                    ✅ <strong>Best performing class</strong> - Model excels at identifying non-planetary signals
                  </p>
                </div>
              </div>

              {/* CANDIDATE */}
              <div className="bg-white p-8 rounded-xl shadow-lg border-l-4 border-yellow-500">
                <div className="flex items-center justify-between mb-5">
                  <h4 className="font-bold text-gray-800 text-lg flex items-center">
                    <FiAlertCircle className="mr-2 text-yellow-500 text-2xl" />
                    Candidate
                  </h4>
                  <span className="text-sm text-gray-500 font-semibold">395 samples</span>
                </div>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-gray-600 font-medium">Precision</span>
                      <span className="font-bold text-gray-800 text-lg">44%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div className="bg-yellow-500 h-3 rounded-full" style={{ width: '44%' }}></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-gray-600 font-medium">Recall</span>
                      <span className="font-bold text-gray-800 text-lg">11%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div className="bg-yellow-500 h-3 rounded-full" style={{ width: '11%' }}></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-gray-600 font-medium">F1-Score</span>
                      <span className="font-bold text-gray-800 text-lg">17%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div className="bg-yellow-500 h-3 rounded-full" style={{ width: '17%' }}></div>
                    </div>
                  </div>
                </div>
                <div className="mt-4 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                  <p className="text-sm text-gray-700">
                    ⚠️ <strong>Most challenging class</strong> - Ambiguous signals often misclassified
                  </p>
                </div>
              </div>

              {/* CONFIRMED */}
              <div className="bg-white p-8 rounded-xl shadow-lg border-l-4 border-green-500">
                <div className="flex items-center justify-between mb-5">
                  <h4 className="font-bold text-gray-800 text-lg flex items-center">
                    <FiCheckCircle className="mr-2 text-green-500 text-2xl" />
                    Confirmed
                  </h4>
                  <span className="text-sm text-gray-500 font-semibold">526 samples</span>
                </div>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-gray-600 font-medium">Precision</span>
                      <span className="font-bold text-gray-800 text-lg">60%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div className="bg-green-500 h-3 rounded-full" style={{ width: '60%' }}></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-gray-600 font-medium">Recall</span>
                      <span className="font-bold text-gray-800 text-lg">75%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div className="bg-green-500 h-3 rounded-full" style={{ width: '75%' }}></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-gray-600 font-medium">F1-Score</span>
                      <span className="font-bold text-gray-800 text-lg">67%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div className="bg-green-500 h-3 rounded-full" style={{ width: '67%' }}></div>
                    </div>
                  </div>
                </div>
                <div className="mt-4 p-3 bg-green-50 rounded-lg border border-green-200">
                  <p className="text-sm text-gray-700">
                    ✨ <strong>Strong performance</strong> - Good balance of precision and recall
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Key Features */}
          <div className="bg-gradient-to-r from-indigo-50 to-purple-50 p-8 rounded-xl border-2 border-indigo-200 shadow-md mb-8">
            <h3 className="text-2xl font-bold text-gray-800 mb-6">🔑 15 Input Features Used by Our Model</h3>
            <div className="grid md:grid-cols-3 gap-6">
              <div className="bg-white p-6 rounded-lg shadow-sm">
                <h4 className="font-bold text-gray-800 mb-3 text-lg border-b-2 border-blue-300 pb-2">Orbital Properties</h4>
                <ul className="text-sm text-gray-700 space-y-2">
                  <li>• <strong>Orbital Period</strong></li>
                  <li>• <strong>Transit Duration</strong></li>
                  <li>• <strong>Transit Depth</strong></li>
                  <li>• <strong>Number of Transits</strong></li>
                  <li>• <strong>Duration-to-Orbital Ratio</strong></li>
                </ul>
              </div>
              <div className="bg-white p-6 rounded-lg shadow-sm">
                <h4 className="font-bold text-gray-800 mb-3 text-lg border-b-2 border-purple-300 pb-2">Planetary Characteristics</h4>
                <ul className="text-sm text-gray-700 space-y-2">
                  <li>• <strong>Planet Radius</strong></li>
                  <li>• <strong>Planet-to-Star Radius Ratio</strong></li>
                  <li>• <strong>Insolation Flux</strong></li>
                  <li>• <strong>Model Signal-to-Noise Ratio</strong></li>
                </ul>
              </div>
              <div className="bg-white p-6 rounded-lg shadow-sm">
                <h4 className="font-bold text-gray-800 mb-3 text-lg border-b-2 border-pink-300 pb-2">Stellar Properties</h4>
                <ul className="text-sm text-gray-700 space-y-2">
                  <li>• <strong>Effective Temperature</strong></li>
                  <li>• <strong>Surface Gravity</strong></li>
                  <li>• <strong>Stellar Radius</strong></li>
                  <li>• <strong>Stellar Mass</strong></li>
                  <li>• <strong>Kepler Magnitude</strong></li>
                  <li>• <strong>KOI Count</strong> (multiple planets)</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Data Integrity Note */}
          <div className="p-6 bg-blue-50 border-l-4 border-blue-600 rounded-lg shadow-sm">
            <p className="text-gray-700 leading-relaxed">
              <strong className="text-blue-800 text-lg">🛡️ Data Integrity & Ethical AI:</strong> Our model has been carefully designed 
              to prevent data leakage. We removed preliminary disposition labels (koi_pdisposition) and internal scoring metrics (koi_score) 
              from training to ensure the model learns genuine physical patterns from light curves and stellar properties rather than 
              memorizing pre-existing classifications. This approach ensures our AI makes predictions based on real science.
            </p>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-4xl font-bold text-center mb-12 text-gray-800">How It Works</h2>
          <div className="space-y-8">
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0 w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-xl">
                1
              </div>
              <div>
                <h3 className="text-xl font-bold mb-2 text-gray-800">Upload Light Curve</h3>
                <p className="text-gray-600">
                  Upload a FITS file from Kepler or TESS missions containing stellar brightness measurements over time.
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0 w-12 h-12 bg-purple-600 text-white rounded-full flex items-center justify-center font-bold text-xl">
                2
              </div>
              <div>
                <h3 className="text-xl font-bold mb-2 text-gray-800">AI Analysis</h3>
                <p className="text-gray-600">
                  Our hybrid model processes 2000 flux measurements and stellar parameters to detect transit patterns.
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0 w-12 h-12 bg-pink-600 text-white rounded-full flex items-center justify-center font-bold text-xl">
                3
              </div>
              <div>
                <h3 className="text-xl font-bold mb-2 text-gray-800">Get Results</h3>
                <p className="text-gray-600">
                  Receive classification (Confirmed/Candidate/False Positive) with confidence scores and interactive visualizations.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-4 py-20">
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-12 text-center text-white">
          <h2 className="text-4xl font-bold mb-4">Ready to Hunt for Exoplanets?</h2>
          <p className="text-xl mb-8 opacity-90">
            Join the search for worlds beyond our solar system
          </p>
          <Link to="/analyze" className="bg-white text-blue-600 px-8 py-3 rounded-lg font-bold hover:bg-gray-100 transition-colors duration-200 inline-block">
            Start Your Analysis
          </Link>
        </div>
      </section>
    </div>
  );
}

export default Home;
