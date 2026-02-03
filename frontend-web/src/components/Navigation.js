import React from 'react';

function Navigation({ username, onLogout }) {
  return (
    <nav className="nav">
      <h1>Chemical Equipment Visualizer</h1>
      <div className="nav-buttons">
        <span style={{ marginRight: '1rem' }}>Welcome, {username}</span>
        <button className="btn btn-secondary" onClick={onLogout}>
          Logout
        </button>
      </div>
    </nav>
  );
}

export default Navigation;
