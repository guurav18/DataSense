import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import { useHealthCheck } from './hooks/useHealthCheck';

export default function App() {
  const { health, loading, refetch } = useHealthCheck(15000);
  const [selectedTab, setSelectedTab] = useState('dashboard'); // 'dashboard' | 'overview'

  const capabilities = [
    {
      title: 'CSV & Excel Ingestion',
      category: 'Data Engine',
      description: 'Streamlined upload and validation of tabular datasets using Pandas and OpenPyXL.',
      badge: 'Active & Verified',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
          <polyline points="14 2 14 8 20 8" />
          <line x1="16" y1="13" x2="8" y2="13" />
          <line x1="16" y1="17" x2="8" y2="17" />
          <polyline points="10 9 9 9 8 9" />
        </svg>
      ),
    },
    {
      title: 'Automated Cleaning & Profiling',
      category: 'Data Engine',
      description: 'Instant missing-value detection, column type normalization, duplicate removal, and summary stats.',
      badge: 'Active & Verified',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
        </svg>
      ),
    },
    {
      title: 'Dynamic Visualizations',
      category: 'Visualization',
      description: 'Automated generation of distribution histograms, correlation heatmaps, scatter, and bar plots.',
      badge: 'Active & Verified',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <line x1="18" y1="20" x2="18" y2="10" />
          <line x1="12" y1="20" x2="12" y2="4" />
          <line x1="6" y1="20" x2="6" y2="14" />
        </svg>
      ),
    },
    {
      title: 'LangGraph Autonomous Agent',
      category: 'AI Orchestration',
      description: 'Stateful agent workflow: planning, code generation, sandboxed execution, and synthesis.',
      badge: 'Scaffolded',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="3" />
          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
        </svg>
      ),
    },
    {
      title: 'PostgreSQL & SQLAlchemy',
      category: 'Persistence',
      description: 'Reliable storage for dataset schemas, analysis logs, generated charts, and query histories.',
      badge: 'Models Defined',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <ellipse cx="12" cy="5" rx="9" ry="3" />
          <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" />
          <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
        </svg>
      ),
    },
    {
      title: 'FastAPI Backend Core',
      category: 'API Engine',
      description: 'High-performance asynchronous REST endpoints with automated docs and CORS protection.',
      badge: 'Active & Verified',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
        </svg>
      ),
    },
  ];

  return (
    <div className="app-layout" id="datasense-app">
      <Navbar
        health={health}
        currentTab={selectedTab}
        onSelectTab={setSelectedTab}
      />

      <main className="main-content">
        {selectedTab === 'dashboard' ? (
          <Dashboard />
        ) : (
          <>
            {/* Hero Section */}
            <section className="hero-section" id="hero">
              <div className="hero-badge">
                <span className="badge-pulse"></span>
                <span>Data Ingestion &bull; Automated Profiling &bull; Visualizations Live</span>
              </div>

              <h1 className="hero-title">
                DataSense <span className="title-gradient">AI</span>
              </h1>

              <p className="hero-subtitle">
                Autonomous Data Analysis Agent Architecture
              </p>

              <p className="hero-description">
                An advanced AI-powered system that accepts CSV and Excel datasets, performs automated data cleaning
                and exploratory data analysis (EDA), generates visualizations, and answers complex analytical queries
                in natural language through an autonomous LangGraph agent.
              </p>

              <div className="hero-cta-group">
                <button
                  onClick={() => setSelectedTab('dashboard')}
                  className="btn btn-primary"
                >
                  Open Studio Dashboard &rarr;
                </button>

                <a
                  href="http://localhost:8000/docs"
                  target="_blank"
                  rel="noreferrer"
                  className="btn btn-secondary"
                  id="btn-api-docs"
                >
                  Explore FastAPI Swagger Docs
                </a>

                <button
                  onClick={refetch}
                  className="btn btn-secondary"
                  id="btn-check-backend"
                >
                  Verify Backend Health
                </button>
              </div>
            </section>

            {/* Live Backend Status Card */}
            <section className="status-section" id="status-card-section">
              <div className="glass-card status-card">
                <div className="status-card-header">
                  <div className="status-card-title-group">
                    <h3>Backend Connectivity &amp; Environment Status</h3>
                    <span className="text-muted">Direct verification from FastAPI /health endpoint</span>
                  </div>
                  <span className={`pill ${health?.status === 'healthy' ? 'pill-success' : 'pill-warning'}`}>
                    {loading ? 'Checking...' : health?.status?.toUpperCase()}
                  </span>
                </div>

                <div className="status-grid">
                  <div className="status-item">
                    <span className="status-item-label">API Service</span>
                    <span className="status-item-value">{health?.service || 'DataSense AI'}</span>
                  </div>
                  <div className="status-item">
                    <span className="status-item-label">Environment</span>
                    <span className="status-item-value capitalize">{health?.environment || 'development'}</span>
                  </div>
                  <div className="status-item">
                    <span className="status-item-label">Ingestion Engine</span>
                    <span className="status-item-value text-success">Active (.csv, .xlsx, .xls)</span>
                  </div>
                  <div className="status-item">
                    <span className="status-item-label">Visualization Engine</span>
                    <span className="status-item-value text-success">Active (Headless Matplotlib)</span>
                  </div>
                </div>
              </div>
            </section>

            {/* Architecture Grid */}
            <section className="capabilities-section" id="capabilities">
              <div className="section-header">
                <h2 className="section-title">Architectural Foundation</h2>
                <p className="section-subtitle">
                  Modular components scaffolded for scalable development and step-by-step feature implementation.
                </p>
              </div>

              <div className="cards-grid">
                {capabilities.map((cap, idx) => (
                  <div key={idx} className="glass-card capability-card">
                    <div className="card-top">
                      <div className="card-icon">{cap.icon}</div>
                      <span className="card-badge">{cap.badge}</span>
                    </div>
                    <h4 className="card-title">{cap.title}</h4>
                    <p className="card-desc">{cap.description}</p>
                    <div className="card-footer">
                      <span className="card-category">{cap.category}</span>
                      <span className="card-ready-status">{cap.badge}</span>
                    </div>
                  </div>
                ))}
              </div>
            </section>

            {/* Next Implementation Steps */}
            <section className="steps-section" id="next-steps">
              <div className="glass-card roadmap-card">
                <h3 className="roadmap-title">Implementation Milestones</h3>
                <div className="roadmap-list">
                  <div className="roadmap-item">
                    <span className="step-number" style={{ background: '#10b981' }}>✓</span>
                    <div>
                      <strong>Dataset Ingestion &amp; Validation</strong>
                      <p>CSV &amp; Excel streaming, encoding fallback, and upload storage.</p>
                    </div>
                  </div>

                  <div className="roadmap-item">
                    <span className="step-number" style={{ background: '#10b981' }}>✓</span>
                    <div>
                      <strong>Automated Cleaning &amp; EDA Profiler</strong>
                      <p>Deduplication, whitespace trimming, summary stats &amp; column profiles.</p>
                    </div>
                  </div>

                  <div className="roadmap-item">
                    <span className="step-number" style={{ background: '#10b981' }}>✓</span>
                    <div>
                      <strong>Dynamic Visualizations</strong>
                      <p>Histograms, correlation heatmaps, scatter plots &amp; bar charts.</p>
                    </div>
                  </div>

                  <div className="roadmap-item">
                    <span className="step-number">4</span>
                    <div>
                      <strong>LangGraph Autonomous Agent Workflow</strong>
                      <p>Configure plan-and-solve execution loop with LLM code synthesis.</p>
                    </div>
                  </div>
                </div>
              </div>
            </section>
          </>
        )}
      </main>

      <footer className="footer">
        <p>DataSense AI &bull; Autonomous Data Analysis Agent &bull; Modern Interactive Studio</p>
      </footer>
    </div>
  );
}
