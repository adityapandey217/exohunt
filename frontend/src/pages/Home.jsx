import { Link } from 'react-router-dom';
import { FiArrowRight, FiStar, FiTrendingUp, FiDatabase } from 'react-icons/fi';

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
              Hybrid CNN+MLP architecture trained on thousands of Kepler light curves with 95%+ accuracy.
            </p>
          </div>

          <div className="card text-center">
            <div className="flex justify-center mb-4">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center">
                <FiTrendingUp className="text-3xl text-purple-600" />
              </div>
            </div>
            <h3 className="text-xl font-bold mb-3 text-gray-800">Transit Analysis</h3>
            <p className="text-gray-600">
              BLS period search, phase-folding, and periodogram analysis to characterize detected transits.
            </p>
          </div>

          <div className="card text-center">
            <div className="flex justify-center mb-4">
              <div className="w-16 h-16 bg-pink-100 rounded-full flex items-center justify-center">
                <FiDatabase className="text-3xl text-pink-600" />
              </div>
            </div>
            <h3 className="text-xl font-bold mb-3 text-gray-800">Interactive Visualization</h3>
            <p className="text-gray-600">
              Explore light curves with interactive Plotly charts, zoom, pan, and inspect individual data points.
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
