import React from 'react';

const NEGOTIATION_STEPS = [
  { id: 'REQUESTED', label: 'Requested', description: 'Consumer requests access to dataset' },
  { id: 'OFFERED', label: 'Offered', description: 'Provider evaluates and makes offer' },
  { id: 'AGREED', label: 'Agreed', description: 'Consumer agrees to terms' },
  { id: 'VERIFIED', label: 'Verified', description: 'Both parties verify agreement' },
  { id: 'FINALIZED', label: 'Finalized', description: 'Contract is active' },
];

function NegotiationFlow({ negotiation, selectedDataset, onStart, onAdvance, loading }) {
  const currentState = negotiation?.status || negotiation?.provider_response?.['dspace:state'] || null;
  const isTerminated = currentState === 'TERMINATED';

  const getStepStatus = (stepId) => {
    if (!currentState) return 'pending';
    if (isTerminated) return 'terminated';

    const currentIndex = NEGOTIATION_STEPS.findIndex(s => s.id === currentState);
    const stepIndex = NEGOTIATION_STEPS.findIndex(s => s.id === stepId);

    if (stepIndex < currentIndex) return 'completed';
    if (stepIndex === currentIndex) return 'active';
    return 'pending';
  };

  const getNextAction = () => {
    switch (currentState) {
      case 'REQUESTED':
        return { action: 'request-offer', label: 'Request Provider Offer' };
      case 'OFFERED':
        return { action: 'agree', label: 'Agree to Offer' };
      case 'AGREED':
        return { action: 'verify', label: 'Verify Agreement' };
      case 'VERIFIED':
        return { action: 'finalize', label: 'Finalize Contract' };
      default:
        return null;
    }
  };

  if (!negotiation && !selectedDataset) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <div className="text-6xl mb-4">🤝</div>
        <h2 className="text-xl font-semibold mb-2">No Active Negotiation</h2>
        <p className="text-gray-600">
          Select a dataset from the catalog to start a contract negotiation
        </p>
      </div>
    );
  }

  const policyEval = negotiation?.policy_evaluation || negotiation?.provider_response?.policy_evaluation;

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-2">Contract Negotiation</h2>
        <p className="text-gray-600">
          {negotiation
            ? `Negotiating access to: ${negotiation.asset_id}`
            : `Ready to negotiate for: ${selectedDataset?.title}`
          }
        </p>

        {/* Step Indicator */}
        <div className="mt-8">
          <div className="flex items-center justify-between">
            {NEGOTIATION_STEPS.map((step, index) => {
              const status = getStepStatus(step.id);
              return (
                <React.Fragment key={step.id}>
                  <div className="flex flex-col items-center">
                    <div className={`step-indicator ${status}`}>
                      {status === 'completed' ? '✓' : index + 1}
                    </div>
                    <div className={`mt-2 text-sm font-medium ${
                      status === 'active' ? 'text-blue-600' :
                      status === 'completed' ? 'text-green-600' : 'text-gray-400'
                    }`}>
                      {step.label}
                    </div>
                    <div className="text-xs text-gray-500 text-center max-w-24">
                      {step.description}
                    </div>
                  </div>
                  {index < NEGOTIATION_STEPS.length - 1 && (
                    <div className={`flex-1 h-1 mx-2 rounded ${
                      getStepStatus(NEGOTIATION_STEPS[index + 1].id) === 'pending'
                        ? 'bg-gray-200' : 'bg-green-500'
                    }`} />
                  )}
                </React.Fragment>
              );
            })}
          </div>
        </div>

        {/* Terminated State */}
        {isTerminated && (
          <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center text-red-800">
              <span className="text-2xl mr-3">❌</span>
              <div>
                <div className="font-semibold">Negotiation Terminated</div>
                <div className="text-sm">
                  {policyEval?.reason || 'Policy requirements not met'}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Policy Evaluation Result */}
        {policyEval && !isTerminated && (
          <div className={`mt-6 p-4 rounded-lg border ${
            policyEval.result === 'ALLOWED' || policyEval.allowed
              ? 'bg-green-50 border-green-200'
              : 'bg-red-50 border-red-200'
          }`}>
            <div className="font-semibold mb-2">
              Policy Evaluation: {policyEval.result || (policyEval.allowed ? 'ALLOWED' : 'DENIED')}
            </div>
            <div className="text-sm mb-2">{policyEval.reason}</div>

            {policyEval.constraints_checked?.length > 0 && (
              <div className="mt-3">
                <div className="text-sm font-medium mb-1">Constraints Checked:</div>
                <div className="space-y-1">
                  {policyEval.constraints_checked.map((c, i) => (
                    <div key={i} className="text-sm flex items-center">
                      <span className={c.satisfied ? 'text-green-600' : 'text-red-600'}>
                        {c.satisfied ? '✓' : '✗'}
                      </span>
                      <span className="ml-2">{c.constraint}</span>
                      <span className="ml-2 text-gray-500">
                        (your value: {JSON.stringify(c.context_value)})
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Action Buttons */}
        <div className="mt-6 flex justify-center gap-4">
          {!negotiation && selectedDataset && (
            <button onClick={onStart} disabled={loading} className="btn-primary">
              {loading ? 'Starting...' : 'Start Negotiation'}
            </button>
          )}

          {negotiation && !isTerminated && currentState !== 'FINALIZED' && getNextAction() && (
            <button
              onClick={() => onAdvance(getNextAction().action)}
              disabled={loading}
              className="btn-primary"
            >
              {loading ? 'Processing...' : getNextAction().label}
            </button>
          )}

          {currentState === 'FINALIZED' && (
            <div className="text-center">
              <div className="text-green-600 font-semibold text-lg mb-2">
                ✓ Contract Finalized!
              </div>
              <div className="text-gray-600">
                Agreement ID: <code className="bg-gray-100 px-2 py-1 rounded">{negotiation.agreement_id}</code>
              </div>
              <p className="text-sm text-gray-500 mt-2">
                You can now proceed to the Transfer tab to receive the data.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Negotiation Details */}
      {negotiation && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="font-semibold mb-4">Negotiation Details</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <div className="text-gray-500">Local ID</div>
              <div className="font-mono">{negotiation.local_negotiation_id}</div>
            </div>
            <div>
              <div className="text-gray-500">Provider ID</div>
              <div className="font-mono">{negotiation.provider_negotiation_id}</div>
            </div>
            <div>
              <div className="text-gray-500">Asset ID</div>
              <div className="font-mono">{negotiation.asset_id}</div>
            </div>
            <div>
              <div className="text-gray-500">Current State</div>
              <div className="font-semibold">{currentState}</div>
            </div>
          </div>

          {negotiation.consumer_attributes && (
            <div className="mt-4">
              <div className="text-gray-500 text-sm mb-2">Your Attributes (sent to provider)</div>
              <div className="bg-gray-50 p-3 rounded text-sm font-mono">
                {JSON.stringify(negotiation.consumer_attributes, null, 2)}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default NegotiationFlow;
