import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import ConnectorStatus from './components/ConnectorStatus';
import CatalogBrowser from './components/CatalogBrowser';
import NegotiationFlow from './components/NegotiationFlow';
import TransferMonitor from './components/TransferMonitor';
import DataViewer from './components/DataViewer';
import ArchitectureDiagram from './components/ArchitectureDiagram';

// API configuration
const API_CONFIG = {
  provider: window.location.hostname === 'localhost'
    ? 'http://localhost:8080'
    : (import.meta.env.VITE_PROVIDER_URL || ''),
  consumer: window.location.hostname === 'localhost'
    ? 'http://localhost:8081'
    : (import.meta.env.VITE_CONSUMER_URL || '')
};

function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [providerStatus, setProviderStatus] = useState(null);
  const [consumerStatus, setConsumerStatus] = useState(null);
  const [catalog, setCatalog] = useState(null);
  const [selectedDataset, setSelectedDataset] = useState(null);
  const [negotiation, setNegotiation] = useState(null);
  const [transfer, setTransfer] = useState(null);
  const [receivedData, setReceivedData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  // Fetch connector statuses on mount
  useEffect(() => {
    fetchStatuses();
    const interval = setInterval(fetchStatuses, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchStatuses = async () => {
    try {
      const [provRes, consRes] = await Promise.all([
        fetch(`${API_CONFIG.provider}/api/status`).catch(() => null),
        fetch(`${API_CONFIG.consumer}/api/status`).catch(() => null)
      ]);

      if (provRes?.ok) setProviderStatus(await provRes.json());
      if (consRes?.ok) setConsumerStatus(await consRes.json());
    } catch (e) {
      console.error('Error fetching statuses:', e);
    }
  };

  const fetchCatalog = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_CONFIG.consumer}/api/catalog/fetch`);
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail?.message || 'Failed to fetch catalog');
      setCatalog(data.catalog);
      setActiveTab('catalog');
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const startNegotiation = async (datasetId) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_CONFIG.consumer}/api/negotiations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ asset_id: datasetId })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail?.message || 'Failed to start negotiation');
      setNegotiation(data);
      setActiveTab('negotiation');
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const advanceNegotiation = async (action) => {
    if (!negotiation) return;
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(
        `${API_CONFIG.consumer}/api/negotiations/${negotiation.local_negotiation_id}/${action}`,
        { method: 'POST', headers: { 'Content-Type': 'application/json' } }
      );
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail?.message || `Failed to ${action}`);

      setNegotiation(prev => ({
        ...prev,
        ...data,
        local_negotiation_id: prev.local_negotiation_id
      }));

      if (data.agreement_id) {
        setActiveTab('transfer');
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const startTransfer = async () => {
    if (!negotiation?.agreement_id) return;
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_CONFIG.consumer}/api/transfers`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ agreement_id: negotiation.agreement_id })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail?.message || 'Failed to start transfer');
      setTransfer(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const advanceTransfer = async (action) => {
    if (!transfer) return;
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(
        `${API_CONFIG.consumer}/api/transfers/${transfer.local_transfer_id}/${action}`,
        { method: 'POST' }
      );
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail?.message || `Failed to ${action}`);

      setTransfer(prev => ({ ...prev, ...data }));

      if (data.status === 'COMPLETED') {
        // Fetch the received data
        const dataResponse = await fetch(
          `${API_CONFIG.consumer}/api/transfers/${transfer.local_transfer_id}/data`
        );
        if (dataResponse.ok) {
          const receivedData = await dataResponse.json();
          setReceivedData(receivedData);
          setActiveTab('data');
        }
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const resetDemo = async () => {
    setLoading(true);
    try {
      await Promise.all([
        fetch(`${API_CONFIG.provider}/api/reset`, { method: 'POST' }),
        fetch(`${API_CONFIG.consumer}/api/reset`, { method: 'POST' })
      ]);
      setCatalog(null);
      setSelectedDataset(null);
      setNegotiation(null);
      setTransfer(null);
      setReceivedData(null);
      setError(null);
      setActiveTab('overview');
      await fetchStatuses();
    } catch (e) {
      setError('Failed to reset demo');
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: '🏠' },
    { id: 'catalog', label: 'Catalog', icon: '📚' },
    { id: 'negotiation', label: 'Negotiation', icon: '🤝' },
    { id: 'transfer', label: 'Transfer', icon: '📦' },
    { id: 'data', label: 'Data', icon: '📊' },
  ];

  return (
    <div className="min-h-screen bg-gray-100">
      <Header onReset={resetDemo} loading={loading} />

      {/* Tab Navigation */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4">
          <nav className="flex space-x-4" aria-label="Tabs">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 mx-4 mt-4">
          <div className="flex">
            <div className="flex-shrink-0">⚠️</div>
            <div className="ml-3">
              <p className="text-sm text-red-700">{error}</p>
            </div>
            <button onClick={() => setError(null)} className="ml-auto text-red-500">×</button>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Connector Status Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <ConnectorStatus
                type="provider"
                name="AutoMotors OEM"
                status={providerStatus}
                endpoint={API_CONFIG.provider}
              />
              <ConnectorStatus
                type="consumer"
                name="TierOne Electronics GmbH"
                status={consumerStatus}
                endpoint={API_CONFIG.consumer}
              />
            </div>

            {/* Architecture Diagram */}
            <ArchitectureDiagram />

            {/* Quick Start */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold mb-4">Quick Start Demo</h2>
              <p className="text-gray-600 mb-4">
                Follow these steps to experience sovereign data exchange between an OEM and Tier-1 Supplier:
              </p>
              <div className="space-y-3">
                <div className="flex items-center">
                  <span className="step-indicator completed">1</span>
                  <span className="ml-3">Both connectors are running</span>
                </div>
                <div className="flex items-center">
                  <span className={`step-indicator ${catalog ? 'completed' : 'pending'}`}>2</span>
                  <span className="ml-3">Fetch and browse the provider's catalog</span>
                  {!catalog && (
                    <button onClick={fetchCatalog} disabled={loading} className="btn-primary ml-auto">
                      {loading ? 'Loading...' : 'Fetch Catalog'}
                    </button>
                  )}
                </div>
                <div className="flex items-center">
                  <span className={`step-indicator ${negotiation?.agreement_id ? 'completed' : negotiation ? 'active' : 'pending'}`}>3</span>
                  <span className="ml-3">Negotiate a contract for data access</span>
                </div>
                <div className="flex items-center">
                  <span className={`step-indicator ${receivedData ? 'completed' : transfer ? 'active' : 'pending'}`}>4</span>
                  <span className="ml-3">Transfer and receive the data</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'catalog' && (
          <CatalogBrowser
            catalog={catalog}
            onFetch={fetchCatalog}
            onSelect={setSelectedDataset}
            onNegotiate={startNegotiation}
            loading={loading}
            selectedDataset={selectedDataset}
          />
        )}

        {activeTab === 'negotiation' && (
          <NegotiationFlow
            negotiation={negotiation}
            selectedDataset={selectedDataset}
            onStart={() => selectedDataset && startNegotiation(selectedDataset.id)}
            onAdvance={advanceNegotiation}
            loading={loading}
          />
        )}

        {activeTab === 'transfer' && (
          <TransferMonitor
            transfer={transfer}
            negotiation={negotiation}
            onStart={startTransfer}
            onAdvance={advanceTransfer}
            loading={loading}
          />
        )}

        {activeTab === 'data' && (
          <DataViewer data={receivedData} transfer={transfer} />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-6 mt-12">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <p className="text-sm">
            EDC Demo - Demonstrating Eclipse Dataspace Connector Principles
          </p>
          <p className="text-xs text-gray-400 mt-2">
            Based on Tractus-X/Catena-X approach for automotive data sovereignty
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
