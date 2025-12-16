import React from 'react';

function ConnectorStatus({ type, name, status, endpoint }) {
  const isProvider = type === 'provider';
  const isOnline = status?.status === 'operational';

  return (
    <div className={`connector-card ${type}`}>
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-2xl">{isProvider ? '🏭' : '🔧'}</span>
            <div>
              <h3 className="font-semibold text-lg">{name}</h3>
              <p className="text-sm text-gray-500">
                {isProvider ? 'OEM Data Provider' : 'Tier-1 Supplier Consumer'}
              </p>
            </div>
          </div>
        </div>

        <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-sm ${
          isOnline ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        }`}>
          <span className={`w-2 h-2 rounded-full ${isOnline ? 'bg-green-500' : 'bg-red-500'}`}></span>
          <span>{isOnline ? 'Online' : 'Offline'}</span>
        </div>
      </div>

      {status && (
        <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
          {isProvider ? (
            <>
              <div className="bg-gray-50 p-3 rounded">
                <div className="text-gray-500">Assets</div>
                <div className="text-xl font-semibold">{status.statistics?.assets || 0}</div>
              </div>
              <div className="bg-gray-50 p-3 rounded">
                <div className="text-gray-500">Active Negotiations</div>
                <div className="text-xl font-semibold">{status.statistics?.active_negotiations || 0}</div>
              </div>
              <div className="bg-gray-50 p-3 rounded">
                <div className="text-gray-500">Agreements</div>
                <div className="text-xl font-semibold">{status.statistics?.completed_agreements || 0}</div>
              </div>
              <div className="bg-gray-50 p-3 rounded">
                <div className="text-gray-500">Transfers</div>
                <div className="text-xl font-semibold">{status.statistics?.completed_transfers || 0}</div>
              </div>
            </>
          ) : (
            <>
              <div className="bg-gray-50 p-3 rounded">
                <div className="text-gray-500">Cached Catalogs</div>
                <div className="text-xl font-semibold">{status.statistics?.cached_catalogs || 0}</div>
              </div>
              <div className="bg-gray-50 p-3 rounded">
                <div className="text-gray-500">Negotiations</div>
                <div className="text-xl font-semibold">{status.statistics?.active_negotiations || 0}</div>
              </div>
              <div className="bg-gray-50 p-3 rounded">
                <div className="text-gray-500">Agreements</div>
                <div className="text-xl font-semibold">{status.statistics?.agreements || 0}</div>
              </div>
              <div className="bg-gray-50 p-3 rounded">
                <div className="text-gray-500">Received Data</div>
                <div className="text-xl font-semibold">{status.statistics?.received_data || 0}</div>
              </div>
            </>
          )}
        </div>
      )}

      {status?.identity && (
        <div className="mt-4 p-3 bg-blue-50 rounded text-sm">
          <div className="font-medium text-blue-800 mb-2">Identity Attributes</div>
          <div className="grid grid-cols-2 gap-2 text-blue-700">
            <div>Partner Type: <span className="font-medium">{status.identity.partner_type}</span></div>
            <div>Region: <span className="font-medium">{status.identity.region}</span></div>
            <div className="col-span-2">
              Certifications: <span className="font-medium">{status.identity.certifications?.join(', ')}</span>
            </div>
          </div>
        </div>
      )}

      <div className="mt-3 text-xs text-gray-400">
        Endpoint: {endpoint}
      </div>
    </div>
  );
}

export default ConnectorStatus;
