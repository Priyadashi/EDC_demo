import React from 'react';

const TRANSFER_STEPS = [
  { id: 'REQUESTED', label: 'Requested', description: 'Transfer initiated' },
  { id: 'STARTED', label: 'In Progress', description: 'Data transfer active' },
  { id: 'COMPLETED', label: 'Completed', description: 'Data received' },
];

function TransferMonitor({ transfer, negotiation, onStart, onAdvance, loading }) {
  const currentState = transfer?.status || null;

  const getStepStatus = (stepId) => {
    if (!currentState) return 'pending';

    const currentIndex = TRANSFER_STEPS.findIndex(s => s.id === currentState);
    const stepIndex = TRANSFER_STEPS.findIndex(s => s.id === stepId);

    if (stepIndex < currentIndex) return 'completed';
    if (stepIndex === currentIndex) return 'active';
    return 'pending';
  };

  const getNextAction = () => {
    switch (currentState) {
      case 'REQUESTED':
        return { action: 'start', label: 'Start Transfer' };
      case 'STARTED':
        return { action: 'complete', label: 'Complete & Receive Data' };
      default:
        return null;
    }
  };

  if (!negotiation?.agreement_id) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <div className="text-6xl mb-4">📦</div>
        <h2 className="text-xl font-semibold mb-2">No Active Agreement</h2>
        <p className="text-gray-600">
          Complete a contract negotiation first to initiate a data transfer
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-2">Data Transfer</h2>
        <p className="text-gray-600">
          Transfer data using agreement: <code className="bg-gray-100 px-2 py-1 rounded">{negotiation.agreement_id}</code>
        </p>

        {/* Step Indicator */}
        <div className="mt-8">
          <div className="flex items-center justify-between max-w-2xl mx-auto">
            {TRANSFER_STEPS.map((step, index) => {
              const status = getStepStatus(step.id);
              return (
                <React.Fragment key={step.id}>
                  <div className="flex flex-col items-center">
                    <div className={`step-indicator ${status}`}>
                      {status === 'completed' ? '✓' : status === 'active' ? '⟳' : index + 1}
                    </div>
                    <div className={`mt-2 text-sm font-medium ${
                      status === 'active' ? 'text-blue-600' :
                      status === 'completed' ? 'text-green-600' : 'text-gray-400'
                    }`}>
                      {step.label}
                    </div>
                    <div className="text-xs text-gray-500 text-center">
                      {step.description}
                    </div>
                  </div>
                  {index < TRANSFER_STEPS.length - 1 && (
                    <div className="flex-1 mx-4">
                      <div className={`h-1 rounded ${
                        getStepStatus(TRANSFER_STEPS[index + 1].id) === 'pending'
                          ? 'bg-gray-200' : 'bg-green-500'
                      }`} />
                      {status === 'active' && (
                        <div className="text-center text-2xl data-flow-arrow mt-2">➡️</div>
                      )}
                    </div>
                  )}
                </React.Fragment>
              );
            })}
          </div>
        </div>

        {/* Transfer Animation */}
        {currentState === 'STARTED' && (
          <div className="mt-8 p-6 bg-blue-50 rounded-lg">
            <div className="flex items-center justify-center space-x-8">
              <div className="text-center">
                <div className="text-4xl mb-2">🏭</div>
                <div className="text-sm font-medium">Provider</div>
              </div>
              <div className="flex-1 max-w-xs">
                <div className="flex items-center justify-center space-x-2">
                  <div className="data-flow-arrow text-2xl">📦</div>
                  <div className="data-flow-arrow text-2xl" style={{ animationDelay: '0.3s' }}>📦</div>
                  <div className="data-flow-arrow text-2xl" style={{ animationDelay: '0.6s' }}>📦</div>
                </div>
                <div className="h-2 bg-blue-200 rounded mt-2 overflow-hidden">
                  <div className="h-full bg-blue-500 rounded animate-pulse" style={{ width: '60%' }} />
                </div>
              </div>
              <div className="text-center">
                <div className="text-4xl mb-2">🔧</div>
                <div className="text-sm font-medium">Consumer</div>
              </div>
            </div>
          </div>
        )}

        {/* Completed State */}
        {currentState === 'COMPLETED' && (
          <div className="mt-8 p-6 bg-green-50 rounded-lg text-center">
            <div className="text-5xl mb-4">✅</div>
            <div className="text-xl font-semibold text-green-800">Transfer Complete!</div>
            <p className="text-green-600 mt-2">
              Data has been successfully transferred and is now available.
            </p>
            <p className="text-sm text-gray-600 mt-4">
              Go to the Data tab to view the received data.
            </p>
          </div>
        )}

        {/* Action Buttons */}
        <div className="mt-6 flex justify-center gap-4">
          {!transfer && negotiation?.agreement_id && (
            <button onClick={onStart} disabled={loading} className="btn-primary">
              {loading ? 'Initiating...' : 'Initiate Data Transfer'}
            </button>
          )}

          {transfer && currentState !== 'COMPLETED' && getNextAction() && (
            <button
              onClick={() => onAdvance(getNextAction().action)}
              disabled={loading}
              className="btn-primary"
            >
              {loading ? 'Processing...' : getNextAction().label}
            </button>
          )}
        </div>
      </div>

      {/* Transfer Details */}
      {transfer && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="font-semibold mb-4">Transfer Details</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <div className="text-gray-500">Local Transfer ID</div>
              <div className="font-mono">{transfer.local_transfer_id}</div>
            </div>
            <div>
              <div className="text-gray-500">Provider Transfer ID</div>
              <div className="font-mono">{transfer.provider_transfer_id}</div>
            </div>
            <div>
              <div className="text-gray-500">Asset ID</div>
              <div className="font-mono">{transfer.asset_id}</div>
            </div>
            <div>
              <div className="text-gray-500">Current State</div>
              <div className="font-semibold">{currentState}</div>
            </div>
          </div>

          {transfer.data_summary && (
            <div className="mt-4 p-3 bg-gray-50 rounded">
              <div className="text-sm text-gray-500 mb-1">Data Summary</div>
              <div className="text-sm">
                <span className="font-medium">Received:</span> {transfer.data_summary.received_at}
              </div>
              <div className="text-sm">
                <span className="font-medium">Data Keys:</span>{' '}
                {Array.isArray(transfer.data_summary.data_keys)
                  ? transfer.data_summary.data_keys.join(', ')
                  : transfer.data_summary.data_keys}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default TransferMonitor;
