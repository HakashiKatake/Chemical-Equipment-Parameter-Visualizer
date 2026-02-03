import React from 'react';

function DatasetList({ datasets, selectedDataset, onSelect }) {
  if (datasets.length === 0) {
    return (
      <div className="card">
        <h2>Dataset History</h2>
        <p style={{ color: '#7f8c8d', textAlign: 'center', padding: '2rem' }}>
          No datasets uploaded yet. Upload a CSV file to get started.
        </p>
      </div>
    );
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  return (
    <div className="card">
      <h2>Dataset History (Last {datasets.length})</h2>
      <div className="dataset-list">
        {datasets.map((dataset) => (
          <div
            key={dataset.id}
            className={`dataset-item ${selectedDataset === dataset.id ? 'active' : ''}`}
            onClick={() => onSelect(dataset.id)}
          >
            <div>
              <strong>{dataset.filename}</strong>
              <br />
              <small style={{ opacity: 0.8 }}>
                {formatDate(dataset.uploaded_at)} • {dataset.equipment_count} equipment
              </small>
            </div>
            <div>
              {selectedDataset === dataset.id && (
                <span style={{ fontWeight: 'bold' }}>Selected</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default DatasetList;
