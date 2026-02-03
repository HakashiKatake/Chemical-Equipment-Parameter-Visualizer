import React, { useState } from 'react';
import { datasetAPI } from '../api';

function UploadCSV({ onSuccess }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      if (!selectedFile.name.endsWith('.csv')) {
        setError('Please select a CSV file');
        setFile(null);
        return;
      }
      setFile(selectedFile);
      setError(null);
      setSuccess(false);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    setUploading(true);
    setError(null);

    try {
      await datasetAPI.upload(file);
      setSuccess(true);
      setFile(null);
      
      // Reset file input
      document.getElementById('csv-file-input').value = '';
      
      setTimeout(() => {
        setSuccess(false);
        onSuccess();
      }, 1000);
    } catch (err) {
      if (err.response?.data?.errors) {
        const errors = err.response.data.errors;
        setError(
          <div>
            <strong>Validation errors:</strong>
            <ul className="error-list">
              {errors.map((e, i) => (
                <li key={i}>
                  {e.row && `Row ${e.row}, `}
                  {e.column && `Column "${e.column}": `}
                  {e.error}
                </li>
              ))}
            </ul>
          </div>
        );
      } else {
        setError(err.response?.data?.error || 'Upload failed. Please try again.');
      }
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      {error && <div className="error">{error}</div>}
      {success && <div className="success">File uploaded successfully!</div>}

      <div className="file-upload" onClick={() => document.getElementById('csv-file-input').click()}>
        <input
          id="csv-file-input"
          type="file"
          accept=".csv"
          onChange={handleFileChange}
        />
        <div>
          <svg
            width="48"
            height="48"
            viewBox="0 0 24 24"
            fill="none"
            stroke="#3498db"
            strokeWidth="2"
            style={{ margin: '0 auto 1rem' }}
          >
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="17 8 12 3 7 8" />
            <line x1="12" y1="3" x2="12" y2="15" />
          </svg>
          <p>
            {file ? (
              <strong>{file.name}</strong>
            ) : (
              <>
                <strong>Click to select CSV file</strong>
                <br />
                <small style={{ color: '#7f8c8d' }}>
                  Must contain: Equipment Name, Type, Flowrate, Pressure, Temperature
                </small>
              </>
            )}
          </p>
        </div>
      </div>

      {file && (
        <button
          className="btn btn-success"
          onClick={handleUpload}
          disabled={uploading}
          style={{ width: '100%', marginTop: '1rem' }}
        >
          {uploading ? 'Uploading...' : 'Upload and Process'}
        </button>
      )}
    </div>
  );
}

export default UploadCSV;
