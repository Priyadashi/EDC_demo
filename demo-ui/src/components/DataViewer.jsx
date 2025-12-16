import React, { useState } from 'react';

function DataViewer({ data, transfer }) {
  const [viewMode, setViewMode] = useState('formatted');
  const [expandedSections, setExpandedSections] = useState({});

  if (!data) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <div className="text-6xl mb-4">📊</div>
        <h2 className="text-xl font-semibold mb-2">No Data Received</h2>
        <p className="text-gray-600">
          Complete a data transfer to view the received data here
        </p>
      </div>
    );
  }

  const toggleSection = (key) => {
    setExpandedSections(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const renderValue = (value, depth = 0) => {
    if (value === null || value === undefined) {
      return <span className="text-gray-400">null</span>;
    }

    if (typeof value === 'boolean') {
      return <span className={value ? 'text-green-600' : 'text-red-600'}>{String(value)}</span>;
    }

    if (typeof value === 'number') {
      return <span className="text-blue-600">{value}</span>;
    }

    if (typeof value === 'string') {
      return <span className="text-green-700">"{value}"</span>;
    }

    if (Array.isArray(value)) {
      if (value.length === 0) return <span className="text-gray-400">[]</span>;
      return (
        <div className="ml-4">
          {value.map((item, index) => (
            <div key={index} className="border-l-2 border-gray-200 pl-3 my-1">
              {renderValue(item, depth + 1)}
            </div>
          ))}
        </div>
      );
    }

    if (typeof value === 'object') {
      const keys = Object.keys(value);
      if (keys.length === 0) return <span className="text-gray-400">{'{}'}</span>;

      return (
        <div className="ml-4">
          {keys.map(key => (
            <div key={key} className="my-1">
              <span className="text-purple-600 font-medium">{key}</span>
              <span className="text-gray-400">: </span>
              {renderValue(value[key], depth + 1)}
            </div>
          ))}
        </div>
      );
    }

    return String(value);
  };

  const renderFormattedData = (dataObj) => {
    if (!dataObj?.data) return null;

    const actualData = dataObj.data;

    return (
      <div className="space-y-4">
        {/* Metadata */}
        {actualData.metadata && (
          <div className="border rounded-lg overflow-hidden">
            <button
              onClick={() => toggleSection('metadata')}
              className="w-full px-4 py-3 bg-gray-50 flex items-center justify-between hover:bg-gray-100"
            >
              <span className="font-medium">📋 Metadata</span>
              <span>{expandedSections['metadata'] ? '▼' : '▶'}</span>
            </button>
            {expandedSections['metadata'] && (
              <div className="p-4 bg-white">
                <div className="grid grid-cols-2 gap-3 text-sm">
                  {Object.entries(actualData.metadata).map(([key, value]) => (
                    <div key={key}>
                      <span className="text-gray-500">{key}:</span>{' '}
                      <span className="font-medium">{String(value)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Main Data Sections */}
        {Object.entries(actualData)
          .filter(([key]) => key !== 'metadata')
          .map(([key, value]) => (
            <div key={key} className="border rounded-lg overflow-hidden">
              <button
                onClick={() => toggleSection(key)}
                className="w-full px-4 py-3 bg-gray-50 flex items-center justify-between hover:bg-gray-100"
              >
                <span className="font-medium">
                  {key === 'catalog' ? '📦 Catalog' :
                   key === 'qualityMetrics' ? '📈 Quality Metrics' :
                   key === 'traceabilityData' ? '🔗 Traceability' :
                   `📄 ${key}`}
                </span>
                <span className="text-sm text-gray-500">
                  {Array.isArray(value) ? `${value.length} items` :
                   typeof value === 'object' ? `${Object.keys(value).length} fields` : ''}
                </span>
              </button>
              {expandedSections[key] && (
                <div className="p-4 bg-white overflow-auto max-h-96">
                  {renderValue(value)}
                </div>
              )}
            </div>
          ))}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-semibold">Received Data</h2>
            <p className="text-gray-600 text-sm">
              Asset: {data.asset_id} • Received: {data.received_at || 'Just now'}
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setViewMode('formatted')}
              className={`px-3 py-1 rounded text-sm ${
                viewMode === 'formatted' ? 'bg-blue-600 text-white' : 'bg-gray-200'
              }`}
            >
              Formatted
            </button>
            <button
              onClick={() => setViewMode('raw')}
              className={`px-3 py-1 rounded text-sm ${
                viewMode === 'raw' ? 'bg-blue-600 text-white' : 'bg-gray-200'
              }`}
            >
              Raw JSON
            </button>
          </div>
        </div>

        {/* Success Banner */}
        <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center text-green-800">
            <span className="text-2xl mr-3">✅</span>
            <div>
              <div className="font-semibold">Data Successfully Transferred!</div>
              <div className="text-sm text-green-600">
                This data was transferred through a sovereign data exchange,
                governed by the contract agreement you negotiated.
              </div>
            </div>
          </div>
        </div>

        {/* Data Display */}
        {viewMode === 'formatted' ? (
          renderFormattedData(data)
        ) : (
          <div className="json-viewer">
            <pre>{JSON.stringify(data, null, 2)}</pre>
          </div>
        )}
      </div>

      {/* Data Governance Info */}
      <div className="bg-blue-50 rounded-lg p-6">
        <h3 className="font-semibold text-blue-900 mb-3">🔒 Data Governance</h3>
        <div className="text-sm text-blue-800 space-y-2">
          <p>
            <strong>This data transfer was governed by:</strong>
          </p>
          <ul className="list-disc list-inside space-y-1 ml-2">
            <li>Contract negotiation between provider and consumer</li>
            <li>Policy-based access control (only authorized partners)</li>
            <li>Complete audit trail of all operations</li>
            <li>Data sovereignty principles from Catena-X/Tractus-X</li>
          </ul>
          <p className="mt-3 text-blue-600">
            In a production environment, usage policies would continue to govern
            how this data can be used, shared, and retained.
          </p>
        </div>
      </div>
    </div>
  );
}

export default DataViewer;
