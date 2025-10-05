import { useEffect, useState } from 'react';
import Plot from 'react-plotly.js';
import { visualizeLightCurve } from '../utils/api';
import { FiLoader } from 'react-icons/fi';

function LightCurveViewer({ lightCurveId }) {
  const [plotData, setPlotData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPlotData = async () => {
      try {
        setLoading(true);
        const data = await visualizeLightCurve(lightCurveId);
        setPlotData(data);
      } catch (err) {
        setError('Failed to load light curve visualization');
        console.error('Visualization error:', err);
      } finally {
        setLoading(false);
      }
    };

    if (lightCurveId) {
      fetchPlotData();
    }
  }, [lightCurveId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <FiLoader className="animate-spin text-4xl text-blue-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
        {error}
      </div>
    );
  }

  if (!plotData) {
    return null;
  }

  return (
    <div className="card">
      <h3 className="text-xl font-bold mb-4 text-gray-800">Light Curve Visualization</h3>
      <Plot
        data={plotData.data}
        layout={{
          ...plotData.layout,
          autosize: true,
          responsive: true,
        }}
        config={{
          responsive: true,
          displayModeBar: true,
          displaylogo: false,
        }}
        style={{ width: '100%', height: '500px' }}
      />
    </div>
  );
}

export default LightCurveViewer;
