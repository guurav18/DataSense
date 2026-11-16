import React from 'react';
import { LayoutDashboard, Layers, Sparkles } from 'lucide-react';

export default function Navbar({ health, currentTab, onSelectTab }) {
  const isHealthy = health?.status === 'healthy';

  return (
    <header className="navbar" id="app-navbar">
      <div className="navbar-container">
        <div className="navbar-brand" onClick={() => onSelectTab && onSelectTab('dashboard')} style={{ cursor: 'pointer' }}>
          <div className="brand-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M3 3v18h18" />
              <path d="m19 9-5 5-4-4-3 3" />
            </svg>
          </div>
          <div className="brand-text">
            <span className="brand-title">DataSense AI</span>
            <span className="brand-tag">Autonomous Agent</span>
          </div>
        </div>

        {onSelectTab && (
          <nav className="navbar-nav">
            <button
              className={`nav-tab-btn ${currentTab === 'dashboard' ? 'active' : ''}`}
              onClick={() => onSelectTab('dashboard')}
            >
              <LayoutDashboard size={16} />
              <span>Studio Dashboard</span>
            </button>
            <button
              className={`nav-tab-btn ${currentTab === 'overview' ? 'active' : ''}`}
              onClick={() => onSelectTab('overview')}
            >
              <Layers size={16} />
              <span>Architecture & Roadmap</span>
            </button>
          </nav>
        )}

        <div className="navbar-actions">
          <div
            id="backend-status-pill"
            className={`status-pill ${isHealthy ? 'status-online' : 'status-pending'}`}
            title={isHealthy ? 'FastAPI Backend Connected' : 'Checking Backend Connectivity'}
          >
            <span className="status-dot"></span>
            <span className="status-label">
              {isHealthy ? 'Backend Active' : health?.status === 'offline' ? 'Backend Offline' : 'Connecting...'}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
