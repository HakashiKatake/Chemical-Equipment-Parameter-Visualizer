import React, { useState, useEffect, useCallback } from 'react';
import { datasetAPI } from '../api';
import DatasetList from './DatasetList';
import UploadCSV from './UploadCSV';
import Analytics from './Analytics';

function Dashboard() {
  const [datasets, setDatasets] = useState([]);
  const [selectedDataset, setSelectedDataset] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchDatasets = useCallback(async () => {
    try {
      setLoading(true);
      const response = await datasetAPI.list();
      // Handle paginated response from DRF
      const data = response.data.results || response.data;
      setDatasets(data);
      
      // Auto-select first dataset if available
      if (data.length > 0 && !selectedDataset) {
        setSelectedDataset(data[0].id);
      }
    } catch (err) {
      setError('Failed to load datasets');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [selectedDataset]);

  useEffect(() => {
    fetchDatasets();
  }, [fetchDatasets]);

  const handleUploadSuccess = () => {
    fetchDatasets();
  };

  return (
    <div className="container">
      <div className="card">
        <h2>Upload New Dataset</h2>
        <UploadCSV onSuccess={handleUploadSuccess} />
      </div>

      {error && <div className="error">{error}</div>}

      {loading ? (
        <div className="loading">Loading datasets...</div>
      ) : (
        <>
          <DatasetList
            datasets={datasets}
            selectedDataset={selectedDataset}
            onSelect={setSelectedDataset}
          />

          {selectedDataset && (
            <Analytics datasetId={selectedDataset} />
          )}
        </>
      )}
    </div>
  );
}

export default Dashboard;
