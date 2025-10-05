import React, { useMemo } from 'react';
import Plot from 'react-plotly.js';

/**
 * PlotlyChart component for rendering Plotly visualizations from JSON
 * @param {Object} props
 * @param {string} props.plotJson - Plotly figure JSON string from backend
 */
function PlotlyChart({ plotJson }) {
  // Parse the JSON string into a plotly figure object
  const plotData = useMemo(() => {
    try {
      if (!plotJson) return null;
      
      // Parse the JSON string
      const fig = typeof plotJson === 'string' ? JSON.parse(plotJson) : plotJson;
      
      return {
        data: fig.data || [],
        layout: {
          ...fig.layout,
          // Ensure responsive layout
          autosize: true,
          // Keep the original height but make it responsive
          height: fig.layout?.height || 500,
        },
        config: {
          responsive: true,
          displayModeBar: true,
          displaylogo: false,
          modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
          toImageButtonOptions: {
            format: 'png',
            filename: 'light_curve',
            height: 1000,
            width: 2400,
            scale: 2
          }
        }
      };
    } catch (error) {
      console.error('Error parsing plotly JSON:', error);
      return null;
    }
  }, [plotJson]);

  if (!plotData) {
    return (
      <div className="w-full h-64 flex items-center justify-center bg-gray-100 rounded-lg">
        <p className="text-gray-500">Unable to load visualization</p>
      </div>
    );
  }

  return (
    <div className="w-full rounded-lg shadow-md overflow-hidden bg-white">
      <Plot
        data={plotData.data}
        layout={plotData.layout}
        config={plotData.config}
        useResizeHandler={true}
        style={{ width: '100%', height: '100%' }}
        className="plotly-chart"
      />
    </div>
  );
}

export default PlotlyChart;
