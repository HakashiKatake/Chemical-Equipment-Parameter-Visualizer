import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar, Pie, Scatter } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

function Charts({ histogram, typeDistribution, scatter, units }) {
  // Histogram data
  const histogramData = {
    labels: histogram.bin_labels,
    datasets: [
      {
        label: 'Equipment Count',
        data: histogram.counts,
        backgroundColor: '#3498db',
        borderColor: '#2c3e50',
        borderWidth: 1,
      },
    ],
  };

  const histogramOptions = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: true,
        text: `Flowrate Distribution (${histogram.unit})`,
        font: {
          size: 16,
          weight: 'bold',
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          precision: 0,
        },
        title: {
          display: true,
          text: 'Count',
        },
      },
      x: {
        title: {
          display: true,
          text: `Flowrate (${histogram.unit})`,
        },
      },
    },
  };

  // Type distribution pie chart
  const pieData = {
    labels: Object.keys(typeDistribution),
    datasets: [
      {
        data: Object.values(typeDistribution),
        backgroundColor: [
          '#3498db',
          '#e74c3c',
          '#27ae60',
          '#f39c12',
          '#9b59b6',
          '#1abc9c',
          '#34495e',
          '#e67e22',
        ],
        borderColor: '#fff',
        borderWidth: 2,
      },
    ],
  };

  const pieOptions = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        position: 'right',
      },
      title: {
        display: true,
        text: 'Equipment Type Distribution',
        font: {
          size: 16,
          weight: 'bold',
        },
      },
    },
  };

  // Scatter plot data
  const scatterData = {
    datasets: [
      {
        label: 'Equipment',
        data: scatter.map(point => ({
          x: point.x,
          y: point.y,
          equipment: point.label,
          type: point.type,
        })),
        backgroundColor: '#e74c3c',
        borderColor: '#2c3e50',
        borderWidth: 1,
        pointRadius: 6,
        pointHoverRadius: 8,
      },
    ],
  };

  const scatterOptions = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: true,
        text: 'Pressure vs Temperature',
        font: {
          size: 16,
          weight: 'bold',
        },
      },
      tooltip: {
        callbacks: {
          label: function (context) {
            const point = context.raw;
            return [
              `Equipment: ${point.equipment}`,
              `Type: ${point.type}`,
              `Pressure: ${point.x} ${units.pressure}`,
              `Temperature: ${point.y} ${units.temperature}`,
            ];
          },
        },
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: `Pressure (${units.pressure})`,
        },
      },
      y: {
        title: {
          display: true,
          text: `Temperature (${units.temperature})`,
        },
      },
    },
  };

  return (
    <div className="card">
      <h2>Visualizations</h2>
      <div className="charts-grid">
        <div className="chart-container">
          <Bar data={histogramData} options={histogramOptions} />
        </div>

        <div className="chart-container">
          <Pie data={pieData} options={pieOptions} />
        </div>

        <div className="chart-container" style={{ gridColumn: 'span 2' }}>
          <Scatter data={scatterData} options={scatterOptions} />
        </div>
      </div>
    </div>
  );
}

export default Charts;
