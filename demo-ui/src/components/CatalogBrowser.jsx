import React from 'react';

function CatalogBrowser({ catalog, onFetch, onSelect, onNegotiate, loading, selectedDataset }) {
  if (!catalog) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <div className="text-6xl mb-4">📚</div>
        <h2 className="text-xl font-semibold mb-2">No Catalog Loaded</h2>
        <p className="text-gray-600 mb-6">
          Fetch the provider's catalog to see available datasets
        </p>
        <button onClick={onFetch} disabled={loading} className="btn-primary">
          {loading ? 'Fetching...' : 'Fetch Provider Catalog'}
        </button>
      </div>
    );
  }

  const datasets = catalog['dspace:dataset'] || [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">Provider Catalog</h2>
          <p className="text-gray-600">
            From: {catalog['dspace:participantId']} • {datasets.length} datasets available
          </p>
        </div>
        <button onClick={onFetch} disabled={loading} className="btn-secondary">
          {loading ? 'Refreshing...' : 'Refresh Catalog'}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Dataset List */}
        <div className="space-y-4">
          <h3 className="font-medium text-gray-700">Available Datasets</h3>
          {datasets.map((dataset) => {
            const isSelected = selectedDataset?.id === dataset['@id'];
            const policy = dataset['odrl:hasPolicy']?.[0]?.policy;

            return (
              <div
                key={dataset['@id']}
                onClick={() => onSelect({
                  id: dataset['@id'],
                  title: dataset['dct:title'],
                  description: dataset['dct:description'],
                  format: dataset['dct:format'],
                  properties: dataset.properties,
                  policy
                })}
                className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                  isSelected
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300 bg-white'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-900">{dataset['dct:title']}</h4>
                    <p className="text-sm text-gray-600 mt-1">{dataset['dct:description']}</p>
                  </div>
                  <span className="text-xs bg-gray-100 px-2 py-1 rounded">
                    {dataset['dct:format']}
                  </span>
                </div>

                {/* Properties */}
                {dataset.properties && (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {Object.entries(dataset.properties).slice(0, 3).map(([key, value]) => (
                      <span key={key} className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                        {key.replace('automotive:', '')}: {String(value).substring(0, 20)}
                      </span>
                    ))}
                  </div>
                )}

                {/* Policy Summary */}
                {policy && (
                  <div className="mt-3 p-2 bg-yellow-50 rounded text-sm">
                    <span className="text-yellow-800">📋 Policy: </span>
                    <span className="text-yellow-700">{policy.description}</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Dataset Details */}
        <div className="bg-white rounded-lg shadow-md p-6">
          {selectedDataset ? (
            <>
              <h3 className="font-semibold text-lg mb-4">{selectedDataset.title}</h3>
              <div className="space-y-4">
                <div>
                  <div className="text-sm text-gray-500">Description</div>
                  <div className="text-gray-800">{selectedDataset.description}</div>
                </div>

                <div>
                  <div className="text-sm text-gray-500">Format</div>
                  <div className="text-gray-800">{selectedDataset.format}</div>
                </div>

                {selectedDataset.properties && (
                  <div>
                    <div className="text-sm text-gray-500 mb-2">Properties</div>
                    <div className="bg-gray-50 rounded p-3 space-y-1">
                      {Object.entries(selectedDataset.properties).map(([key, value]) => (
                        <div key={key} className="flex justify-between text-sm">
                          <span className="text-gray-600">{key.replace('automotive:', '')}</span>
                          <span className="text-gray-800 font-medium">
                            {Array.isArray(value) ? value.join(', ') : String(value)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {selectedDataset.policy && (
                  <div>
                    <div className="text-sm text-gray-500 mb-2">Access Policy</div>
                    <div className="bg-yellow-50 border border-yellow-200 rounded p-3">
                      <div className="text-yellow-800 font-medium mb-2">
                        {selectedDataset.policy.id}
                      </div>
                      <div className="text-sm text-yellow-700">
                        {selectedDataset.policy.description}
                      </div>

                      {selectedDataset.policy.permissions?.map((perm, idx) => (
                        <div key={idx} className="mt-2 text-sm">
                          <span className="text-green-700">✓ {perm.action}</span>
                          {perm.constraints?.length > 0 && (
                            <ul className="ml-4 text-gray-600">
                              {perm.constraints.map((c, i) => (
                                <li key={i}>
                                  {c.leftOperand} {c.operator} {JSON.stringify(c.rightOperand)}
                                </li>
                              ))}
                            </ul>
                          )}
                        </div>
                      ))}

                      {selectedDataset.policy.prohibitions?.map((prohib, idx) => (
                        <div key={idx} className="mt-2 text-sm text-red-700">
                          ✗ {prohib.action} prohibited
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <button
                  onClick={() => onNegotiate(selectedDataset.id)}
                  disabled={loading}
                  className="btn-primary w-full mt-4"
                >
                  {loading ? 'Starting...' : 'Request Access (Start Negotiation)'}
                </button>
              </div>
            </>
          ) : (
            <div className="text-center text-gray-500 py-12">
              <div className="text-4xl mb-4">👆</div>
              <p>Select a dataset to view details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default CatalogBrowser;
