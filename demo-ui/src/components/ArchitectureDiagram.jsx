import React from 'react';

function ArchitectureDiagram() {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold mb-4">Architecture Overview</h2>
      <p className="text-gray-600 mb-6">
        This demo simulates the Eclipse Dataspace Connector (EDC) architecture
        for sovereign data exchange in the automotive industry.
      </p>

      {/* Visual Diagram */}
      <div className="relative p-4 bg-gray-50 rounded-lg">
        <div className="flex items-center justify-between">
          {/* Provider Side */}
          <div className="flex-1 max-w-xs">
            <div className="bg-blue-100 border-2 border-blue-500 rounded-lg p-4">
              <div className="text-center">
                <div className="text-3xl mb-2">🏭</div>
                <div className="font-semibold text-blue-800">Provider Connector</div>
                <div className="text-sm text-blue-600">AutoMotors OEM</div>
              </div>
              <div className="mt-4 space-y-2 text-xs">
                <div className="bg-white rounded p-2">📚 Catalog API</div>
                <div className="bg-white rounded p-2">📝 Contract API</div>
                <div className="bg-white rounded p-2">📦 Transfer API</div>
                <div className="bg-white rounded p-2">💾 Data Plane</div>
              </div>
            </div>
            <div className="mt-3 bg-blue-50 rounded p-3 text-center">
              <div className="text-sm font-medium text-blue-800">Assets</div>
              <div className="text-xs text-blue-600">Parts, Quality, Traceability</div>
            </div>
          </div>

          {/* Protocol Flow */}
          <div className="flex-1 max-w-md px-4">
            <div className="space-y-3">
              <div className="flex items-center">
                <div className="flex-1 text-right text-xs text-gray-600">1. Catalog Request</div>
                <div className="w-24 border-t-2 border-dashed border-gray-400 mx-2"></div>
                <div className="flex-1 text-xs text-gray-400">Response</div>
              </div>
              <div className="flex items-center">
                <div className="flex-1 text-right text-xs text-gray-600">2. Contract Negotiation</div>
                <div className="w-24 flex items-center justify-center">
                  <span className="text-lg">⟷</span>
                </div>
                <div className="flex-1 text-xs text-gray-400">Offer/Agree</div>
              </div>
              <div className="flex items-center">
                <div className="flex-1 text-right text-xs text-gray-600">3. Data Transfer</div>
                <div className="w-24 border-t-2 border-dashed border-green-500 mx-2"></div>
                <div className="flex-1 text-xs text-green-600">Data →</div>
              </div>
            </div>
            <div className="mt-4 text-center">
              <div className="inline-block bg-yellow-100 border border-yellow-300 rounded-full px-4 py-1 text-xs text-yellow-800">
                Dataspace Protocol (DSP)
              </div>
            </div>
          </div>

          {/* Consumer Side */}
          <div className="flex-1 max-w-xs">
            <div className="bg-green-100 border-2 border-green-500 rounded-lg p-4">
              <div className="text-center">
                <div className="text-3xl mb-2">🔧</div>
                <div className="font-semibold text-green-800">Consumer Connector</div>
                <div className="text-sm text-green-600">TierOne Electronics</div>
              </div>
              <div className="mt-4 space-y-2 text-xs">
                <div className="bg-white rounded p-2">🔍 Catalog Browser</div>
                <div className="bg-white rounded p-2">🤝 Negotiation Client</div>
                <div className="bg-white rounded p-2">📥 Transfer Receiver</div>
                <div className="bg-white rounded p-2">💾 Data Store</div>
              </div>
            </div>
            <div className="mt-3 bg-green-50 rounded p-3 text-center">
              <div className="text-sm font-medium text-green-800">Identity</div>
              <div className="text-xs text-green-600">Tier-1 Supplier, EU, TISAX</div>
            </div>
          </div>
        </div>
      </div>

      {/* Key Concepts */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-4 bg-purple-50 rounded-lg">
          <div className="text-2xl mb-2">🔐</div>
          <div className="font-semibold text-purple-800">Data Sovereignty</div>
          <div className="text-sm text-purple-600">
            Data providers maintain control over their data through policies and contracts.
          </div>
        </div>
        <div className="p-4 bg-orange-50 rounded-lg">
          <div className="text-2xl mb-2">📜</div>
          <div className="font-semibold text-orange-800">Contract-Based Exchange</div>
          <div className="text-sm text-orange-600">
            Every data transfer requires a negotiated contract that defines usage rights.
          </div>
        </div>
        <div className="p-4 bg-cyan-50 rounded-lg">
          <div className="text-2xl mb-2">🔗</div>
          <div className="font-semibold text-cyan-800">Interoperability</div>
          <div className="text-sm text-cyan-600">
            Standardized protocols enable data exchange across organizational boundaries.
          </div>
        </div>
      </div>

      {/* Links */}
      <div className="mt-6 p-4 bg-gray-100 rounded-lg">
        <div className="text-sm text-gray-600">
          <strong>Learn More:</strong>
          <span className="ml-4">
            <a href="https://github.com/eclipse-tractusx/tractusx-edc" target="_blank" rel="noopener noreferrer"
               className="text-blue-600 hover:underline">Tractus-X EDC</a>
            {' • '}
            <a href="https://eclipse-edc.github.io/docs/" target="_blank" rel="noopener noreferrer"
               className="text-blue-600 hover:underline">Eclipse EDC Docs</a>
            {' • '}
            <a href="https://catena-x.net" target="_blank" rel="noopener noreferrer"
               className="text-blue-600 hover:underline">Catena-X</a>
          </span>
        </div>
      </div>
    </div>
  );
}

export default ArchitectureDiagram;
