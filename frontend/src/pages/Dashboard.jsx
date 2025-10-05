import { useEffect, useState } from 'react';
import { getDashboardStats, getRecentPredictions } from '../utils/api';
import { FiTrendingUp, FiCheckCircle, FiAlertCircle, FiXCircle, FiLoader } from 'react-icons/fi';

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [recentPredictions, setRecentPredictions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsData, predictionsData] = await Promise.all([
          getDashboardStats(),
          getRecentPredictions(10),
        ]);
        setStats(statsData);
        setRecentPredictions(predictionsData);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <FiLoader className="animate-spin text-6xl text-blue-600" />
      </div>
    );
  }

  const getDispositionIcon = (disposition) => {
    switch (disposition) {
      case 'CONFIRMED':
        return <FiCheckCircle className="text-2xl text-green-500" />;
      case 'CANDIDATE':
        return <FiAlertCircle className="text-2xl text-yellow-500" />;
      case 'FALSE POSITIVE':
        return <FiXCircle className="text-2xl text-red-500" />;
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">Dashboard</h1>
          <p className="text-gray-600">Overview of exoplanet detection statistics</p>
        </div>

        {/* Stats Grid */}
        {stats && (
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="stat-card">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm opacity-90">Total Predictions</span>
                <FiTrendingUp className="text-2xl" />
              </div>
              <div className="text-3xl font-bold">{stats.total_predictions}</div>
            </div>

            <div className="bg-gradient-to-br from-green-500 to-green-600 text-white rounded-xl p-6 shadow-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm opacity-90">Confirmed</span>
                <FiCheckCircle className="text-2xl" />
              </div>
              <div className="text-3xl font-bold">{stats.confirmed_count}</div>
              <div className="text-sm opacity-90 mt-1">
                {stats.total_predictions > 0
                  ? ((stats.confirmed_count / stats.total_predictions) * 100).toFixed(1)
                  : 0}
                %
              </div>
            </div>

            <div className="bg-gradient-to-br from-yellow-500 to-yellow-600 text-white rounded-xl p-6 shadow-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm opacity-90">Candidates</span>
                <FiAlertCircle className="text-2xl" />
              </div>
              <div className="text-3xl font-bold">{stats.candidate_count}</div>
              <div className="text-sm opacity-90 mt-1">
                {stats.total_predictions > 0
                  ? ((stats.candidate_count / stats.total_predictions) * 100).toFixed(1)
                  : 0}
                %
              </div>
            </div>

            <div className="bg-gradient-to-br from-red-500 to-red-600 text-white rounded-xl p-6 shadow-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm opacity-90">False Positives</span>
                <FiXCircle className="text-2xl" />
              </div>
              <div className="text-3xl font-bold">{stats.false_positive_count}</div>
              <div className="text-sm opacity-90 mt-1">
                {stats.total_predictions > 0
                  ? ((stats.false_positive_count / stats.total_predictions) * 100).toFixed(1)
                  : 0}
                %
              </div>
            </div>
          </div>
        )}

        {/* Recent Predictions Table */}
        <div className="card">
          <h2 className="text-2xl font-bold mb-6 text-gray-800">Recent Predictions</h2>
          {recentPredictions.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">KIC ID</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Disposition</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Confidence</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Time</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Date</th>
                  </tr>
                </thead>
                <tbody>
                  {recentPredictions.map((pred) => (
                    <tr key={pred.id} className="border-b border-gray-100 hover:bg-gray-50 transition-colors duration-150">
                      <td className="py-3 px-4 font-mono text-sm">
                        {pred.lightcurve?.kic_id || 'N/A'}
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center space-x-2">
                          {getDispositionIcon(pred.predicted_disposition)}
                          <span className="font-medium">{pred.predicted_disposition}</span>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center space-x-2">
                          <div className="flex-1 bg-gray-200 rounded-full h-2 max-w-[100px]">
                            <div
                              className="bg-blue-600 h-2 rounded-full"
                              style={{ width: `${pred.confidence * 100}%` }}
                            />
                          </div>
                          <span className="text-sm font-semibold">
                            {(pred.confidence * 100).toFixed(1)}%
                          </span>
                        </div>
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-600">
                        {pred.inference_time.toFixed(3)}s
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-600">
                        {new Date(pred.timestamp).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">
              <p>No predictions yet. Upload a light curve to get started!</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
