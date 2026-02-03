import React, { useState, useMemo } from 'react';

function DataTable({ data, units }) {
  const [sortField, setSortField] = useState('equipment_name');
  const [sortDirection, setSortDirection] = useState('asc');
  const [filterText, setFilterText] = useState('');
  const [filterType, setFilterType] = useState('all');

  // Get unique types for filter
  const types = useMemo(() => {
    const uniqueTypes = [...new Set(data.map(item => item.type))];
    return uniqueTypes.sort();
  }, [data]);

  // Filter and sort data
  const filteredData = useMemo(() => {
    let filtered = data;

    // Apply text filter
    if (filterText) {
      const search = filterText.toLowerCase();
      filtered = filtered.filter(
        item =>
          item.equipment_name.toLowerCase().includes(search) ||
          item.type.toLowerCase().includes(search)
      );
    }

    // Apply type filter
    if (filterType !== 'all') {
      filtered = filtered.filter(item => item.type === filterType);
    }

    // Sort
    filtered = [...filtered].sort((a, b) => {
      const aVal = a[sortField];
      const bVal = b[sortField];

      if (typeof aVal === 'string') {
        return sortDirection === 'asc'
          ? aVal.localeCompare(bVal)
          : bVal.localeCompare(aVal);
      } else {
        return sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
      }
    });

    return filtered;
  }, [data, filterText, filterType, sortField, sortDirection]);

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const getSortIndicator = (field) => {
    if (sortField !== field) return ' ↕';
    return sortDirection === 'asc' ? ' ↑' : ' ↓';
  };

  return (
    <div className="card">
      <h2>Equipment Data</h2>

      {/* Filters */}
      <div className="filter-controls">
        <input
          type="text"
          placeholder="Search by name or type..."
          value={filterText}
          onChange={(e) => setFilterText(e.target.value)}
        />
        <select value={filterType} onChange={(e) => setFilterType(e.target.value)}>
          <option value="all">All Types</option>
          {types.map(type => (
            <option key={type} value={type}>
              {type}
            </option>
          ))}
        </select>
      </div>

      <p style={{ color: '#7f8c8d', marginBottom: '1rem' }}>
        Showing {filteredData.length} of {data.length} equipment
      </p>

      {/* Table */}
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th onClick={() => handleSort('equipment_name')}>
                Equipment Name{getSortIndicator('equipment_name')}
              </th>
              <th onClick={() => handleSort('type')}>
                Type{getSortIndicator('type')}
              </th>
              <th onClick={() => handleSort('flowrate')}>
                Flowrate ({units.flowrate}){getSortIndicator('flowrate')}
              </th>
              <th onClick={() => handleSort('pressure')}>
                Pressure ({units.pressure}){getSortIndicator('pressure')}
              </th>
              <th onClick={() => handleSort('temperature')}>
                Temperature ({units.temperature}){getSortIndicator('temperature')}
              </th>
            </tr>
          </thead>
          <tbody>
            {filteredData.map((item, index) => (
              <tr key={index}>
                <td>{item.equipment_name}</td>
                <td>{item.type}</td>
                <td>{item.flowrate.toFixed(2)}</td>
                <td>{item.pressure.toFixed(2)}</td>
                <td>{item.temperature.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {filteredData.length === 0 && (
        <p style={{ textAlign: 'center', color: '#7f8c8d', padding: '2rem' }}>
          No equipment found matching the filters
        </p>
      )}
    </div>
  );
}

export default DataTable;
