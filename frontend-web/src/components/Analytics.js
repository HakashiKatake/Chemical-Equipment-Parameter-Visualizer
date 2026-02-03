import React, { useState, useEffect, useCallback } from 'react';
import { datasetAPI } from '../api';
import DataTable from './DataTable';
import Charts from './Charts';

function Analytics({ datasetId }) {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [downloading, setDownloading] = useState(false);

  const fetchAnalytics = useCallback(async () => {
    try {
      setLoading(true);
      setError('');
      const response = await datasetAPI.getAnalytics(datasetId);
      setAnalytics(response.data);
    } catch (err) {
      setError('Failed to load analytics');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [datasetId]);

  useEffect(() => {
    fetchAnalytics();
  }, [fetchAnalytics]);

  const handleDownloadReport = async () => {
    try {
      setDownloading(true);
      const response = await datasetAPI.downloadReport(datasetId);
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `equipment_report_${datasetId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert('Failed to download report');
      console.error(err);
    } finally {
      setDownloading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading analytics...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  if (!analytics) {
    return null;
  }

  const { summary, type_distribution, histogram, scatter, table } = analytics;

  return (
    <div>
      {/* Summary Statistics */}
      <div className="card">
        <h2>Summary Statistics</h2>
        <div className="stats-grid">
          <div className="stat-card">
            <h4>Total Equipment</h4>
            <p>{summary.total_count}</p>
          </div>
          
          <div className="stat-card" style={{ borderTopColor: '#3498db' }}>
            <h4>Avg Flowrate</h4>
            <p>
              {summary.avg_flowrate.toFixed(2)}
              <span> {summary.units.flowrate}</span>
            </p>
            <small style={{ display: 'block', marginTop: '0.5rem' }}>
              Range: {summary.min_flowrate.toFixed(2)} - {summary.max_flowrate.toFixed(2)}
            </small>
          </div>
          
          <div className="stat-card" style={{ borderTopColor: '#27ae60' }}>
            <h4>Avg Pressure</h4>
            <p>
              {summary.avg_pressure.toFixed(2)}
              <span> {summary.units.pressure}</span>
            </p>
            <small style={{ display: 'block', marginTop: '0.5rem' }}>
              Range: {summary.min_pressure.toFixed(2)} - {summary.max_pressure.toFixed(2)}
            </small>
          </div>
          
          <div className="stat-card" style={{ borderTopColor: '#e74c3c' }}>
            <h4>Avg Temperature</h4>
            <p>
              {summary.avg_temperature.toFixed(2)}
              <span> {summary.units.temperature}</span>
            </p>
            <small style={{ display: 'block', marginTop: '0.5rem' }}>
              Range: {summary.min_temperature.toFixed(2)} - {summary.max_temperature.toFixed(2)}
            </small>
          </div>
        </div>

        <button
          className="btn btn-primary"
          onClick={handleDownloadReport}
          disabled={downloading}
          style={{ marginTop: '1.5rem' }}
        >
          {downloading ? 'Generating PDF...' : 'Download PDF Report'}
        </button>
      </div>

      {/* Charts */}
      <Charts
        histogram={histogram}
        typeDistribution={type_distribution}
        scatter={scatter}
        units={summary.units}
      />

      {/* Data Table */}
      <DataTable data={table} units={summary.units} />
    </div>
  );
}

export default Analytics;
