import React from 'react';

function Header({ onReset, loading }) {
  return (
    <header className="bg-gradient-to-r from-blue-900 to-blue-700 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center">
              <svg viewBox="0 0 100 100" className="w-8 h-8">
                <circle cx="50" cy="50" r="45" fill="#1a365d" />
                <path d="M30 50 L50 30 L70 50 L50 70 Z" fill="#22543d" />
                <circle cx="50" cy="50" r="10" fill="white" />
              </svg>
            </div>
            <div>
              <h1 className="text-2xl font-bold">Automotive EDC Demo</h1>
              <p className="text-blue-200 text-sm">
                Sovereign Data Exchange with Eclipse Dataspace Connector
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <div className="text-right text-sm">
              <div className="text-blue-200">Based on</div>
              <div className="font-semibold">Tractus-X / Catena-X</div>
            </div>
            <button
              onClick={onReset}
              disabled={loading}
              className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded text-sm font-medium transition-colors disabled:opacity-50"
            >
              {loading ? 'Resetting...' : 'Reset Demo'}
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Header;
