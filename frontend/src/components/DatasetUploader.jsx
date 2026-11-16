import React, { useState, useRef } from 'react';
import {
  UploadCloud,
  FileSpreadsheet,
  CheckCircle,
  AlertCircle,
  BarChart2,
  Table,
  Sparkles,
  Send,
  RefreshCw,
  Sliders,
  Maximize2
} from 'lucide-react';
import { uploadDataset, cleanDataset, queryAgent } from '../services/api';

export default function DatasetUploader({ dataset: propDataset, onDatasetChange, onLoadSample }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [cleaning, setCleaning] = useState(false);
  const [error, setError] = useState(null);
  const [internalDataset, setInternalDataset] = useState(null);
  const dataset = propDataset !== undefined ? propDataset : internalDataset;

  const setDataset = (valOrFn) => {
    if (typeof valOrFn === 'function') {
      const updated = valOrFn(dataset);
      setInternalDataset(updated);
      if (onDatasetChange) onDatasetChange(updated);
    } else {
      setInternalDataset(valOrFn);
      if (onDatasetChange) onDatasetChange(valOrFn);
    }
  };

  const [activeTab, setActiveTab] = useState('preview'); // 'preview', 'profile', 'charts', 'agent'

  // Agent Chat State
  const [chatMessages, setChatMessages] = useState([
    {
      sender: 'agent',
      text: 'Hello! Upload a dataset, and I will analyze its features, compute statistics, or answer complex analytical queries.',
    },
  ]);
  const [queryInput, setQueryInput] = useState('');
  const [queryLoading, setQueryLoading] = useState(false);

  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleProcessFile(e.target.files[0]);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleProcessFile(e.dataTransfer.files[0]);
    }
  };

  const handleProcessFile = async (selectedFile) => {
    setError(null);
    setFile(selectedFile);
    setLoading(true);

    try {
      const data = await uploadDataset(selectedFile);
      setDataset(data);
      setActiveTab('preview');
      setChatMessages((prev) => [
        ...prev,
        {
          sender: 'agent',
          text: `🎉 Ingested **${selectedFile.name}** (${data.shape[0]} rows, ${data.shape[1]} columns). You can explore the data preview, statistical profile, generated charts, or ask me questions about this dataset below!`,
        },
      ]);
    } catch (err) {
      setError(err.message || 'Error uploading dataset.');
    } finally {
      setLoading(false);
    }
  };

  const handleClean = async () => {
    if (!dataset?.dataset_id) return;
    setCleaning(true);
    try {
      const result = await cleanDataset(dataset.dataset_id);
      setDataset((prev) => ({
        ...prev,
        shape: result.new_shape,
        preview: result.preview,
        profile: result.profile,
      }));
      setChatMessages((prev) => [
        ...prev,
        {
          sender: 'agent',
          text: `🧹 **Automated Cleaning Completed:** Removed ${result.cleaning_report.duplicates_removed} duplicate rows and standardized all column headers. Dataset is now ${result.new_shape[0]} rows × ${result.new_shape[1]} columns.`,
        },
      ]);
    } catch (err) {
      setError(err.message || 'Cleaning failed.');
    } finally {
      setCleaning(false);
    }
  };

  const handleSendQuery = async (e) => {
    e?.preventDefault();
    const query = queryInput.trim();
    if (!query || queryLoading) return;
    handleSendQueryWithText(query);
    setQueryInput('');
  };

  const handleSendQueryWithText = async (text) => {
    if (!text || queryLoading) return;

    setChatMessages((prev) => [...prev, { sender: 'user', text }]);
    setQueryLoading(true);

    try {
      const res = await queryAgent(text, dataset?.dataset_id);
      setChatMessages((prev) => [
        ...prev,
        { sender: 'agent', text: res.response || 'No response returned from agent.' },
      ]);
    } catch (err) {
      setChatMessages((prev) => [
        ...prev,
        { sender: 'agent', text: `❌ Error: ${err.message}` },
      ]);
    } finally {
      setQueryLoading(false);
    }
  };

  return (
    <section className="dataset-section" id="dataset-workspace">
      <div className="section-header">
        <h2 className="section-title">
          Interactive <span className="title-gradient">Data Engine & Agent</span>
        </h2>
        <p className="section-subtitle">
          Upload any CSV or Excel file to trigger automated schema validation, missing value profiling, chart generation, and agent intelligence.
        </p>
      </div>

      {/* Upload Box / Dropzone */}
      <div
        className={`upload-dropzone ${loading ? 'uploading' : ''}`}
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          type="file"
          ref={fileInputRef}
          style={{ display: 'none' }}
          accept=".csv,.xlsx,.xls"
          onChange={handleFileChange}
        />
        <div className="dropzone-content">
          <div className="dropzone-icon-bubble">
            <UploadCloud className="w-8 h-8 text-primary" />
          </div>
          <h4>
            {loading ? 'Processing & Profiling Dataset...' : 'Click to Upload or Drag & Drop'}
          </h4>
          <p className="dropzone-help">Supports CSV, XLSX, and XLS tabular files</p>
          <div className="dropzone-actions" onClick={(e) => e.stopPropagation()}>
            <button
              type="button"
              className="btn btn-secondary btn-sm sample-load-btn"
              onClick={async (e) => {
                e.stopPropagation();
                if (onLoadSample) {
                  onLoadSample();
                } else {
                  try {
                    setLoading(true);
                    const res = await fetch('/sample_sales_dataset.csv');
                    const blob = await res.blob();
                    const sampleFile = new File([blob], 'sample_sales_dataset.csv', { type: 'text/csv' });
                    await handleProcessFile(sampleFile);
                  } catch (err) {
                    setError('Failed to load sample dataset: ' + err.message);
                    setLoading(false);
                  }
                }
              }}
            >
              <Sparkles className="w-3.5 h-3.5 text-primary" />
              Try Sample Sales Dataset
            </button>
          </div>
          {file && (
            <div className="file-badge">
              <FileSpreadsheet className="w-4 h-4 text-emerald-400" />
              <span>{file.name}</span>
            </div>
          )}
        </div>
      </div>

      {error && (
        <div className="error-banner">
          <AlertCircle className="w-5 h-5" />
          <span>{error}</span>
        </div>
      )}

      {/* Dataset Loaded View */}
      {dataset && (
        <div className="dataset-container glass-card">
          {/* Header & Stats Bar */}
          <div className="dataset-header-bar">
            <div>
              <h3 className="dataset-title">
                <FileSpreadsheet className="w-5 h-5 text-indigo-400 inline mr-2" />
                {dataset.filename}
              </h3>
              <div className="dataset-meta-chips">
                <span className="meta-chip">
                  <strong>{dataset.shape[0]}</strong> Rows
                </span>
                <span className="meta-chip">
                  <strong>{dataset.shape[1]}</strong> Columns
                </span>
                <span className="meta-chip">
                  <strong>{dataset.profile?.total_nulls ?? 0}</strong> Missing Values
                </span>
              </div>
            </div>

            <div className="dataset-actions">
              <button
                className="btn btn-secondary btn-sm"
                onClick={handleClean}
                disabled={cleaning}
              >
                <RefreshCw className={`w-4 h-4 ${cleaning ? 'spin' : ''}`} />
                {cleaning ? 'Cleaning...' : 'Auto-Clean Data'}
              </button>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="workspace-tabs">
            <button
              className={`tab-btn ${activeTab === 'preview' ? 'active' : ''}`}
              onClick={() => setActiveTab('preview')}
            >
              <Table className="w-4 h-4" />
              Data Preview
            </button>
            <button
              className={`tab-btn ${activeTab === 'profile' ? 'active' : ''}`}
              onClick={() => setActiveTab('profile')}
            >
              <Sliders className="w-4 h-4" />
              Column Profiler
            </button>
            <button
              className={`tab-btn ${activeTab === 'charts' ? 'active' : ''}`}
              onClick={() => setActiveTab('charts')}
            >
              <BarChart2 className="w-4 h-4" />
              Charts ({dataset.charts?.length || 0})
            </button>
            <button
              className={`tab-btn ${activeTab === 'agent' ? 'active' : ''}`}
              onClick={() => setActiveTab('agent')}
            >
              <Sparkles className="w-4 h-4" />
              AI Agent Chat
            </button>
          </div>

          {/* TAB 1: DATA PREVIEW */}
          {activeTab === 'preview' && (
            <div className="tab-pane">
              <div className="table-responsive">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>#</th>
                      {dataset.columns?.map((col) => (
                        <th key={col}>{col}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {dataset.preview?.map((row, idx) => (
                      <tr key={idx}>
                        <td className="row-num">{idx + 1}</td>
                        {dataset.columns?.map((col) => (
                          <td key={col}>{row[col] !== null ? String(row[col]) : <span className="null-val">null</span>}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 2: COLUMN PROFILER */}
          {activeTab === 'profile' && (
            <div className="tab-pane">
              <div className="table-responsive">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Column</th>
                      <th>Data Type</th>
                      <th>Missing %</th>
                      <th>Unique</th>
                      <th>Min</th>
                      <th>Mean</th>
                      <th>Max</th>
                    </tr>
                  </thead>
                  <tbody>
                    {dataset.profile?.columns_info?.map((col) => (
                      <tr key={col.name}>
                        <td className="font-semibold text-indigo-300">{col.name}</td>
                        <td><code>{col.dtype}</code></td>
                        <td>
                          <span className={col.null_count > 0 ? 'text-amber-400' : 'text-emerald-400'}>
                            {col.null_percentage}% ({col.null_count})
                          </span>
                        </td>
                        <td>{col.unique_count}</td>
                        <td>{col.stats?.min !== undefined ? col.stats.min : '-'}</td>
                        <td>{col.stats?.mean !== undefined ? col.stats.mean : '-'}</td>
                        <td>{col.stats?.max !== undefined ? col.stats.max : '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 3: VISUALIZATIONS */}
          {activeTab === 'charts' && (
            <div className="tab-pane">
              {dataset.charts && dataset.charts.length > 0 ? (
                <div className="charts-gallery">
                  {dataset.charts.map((chart, idx) => (
                    <div key={idx} className="chart-card">
                      <div className="chart-header">
                        <h4>{chart.title}</h4>
                      </div>
                      <div className="chart-image-wrap">
                        <img src={chart.url} alt={chart.title} loading="lazy" />
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="empty-state">
                  <BarChart2 className="w-12 h-12 text-muted" />
                  <p>No numeric columns detected to generate automated plots.</p>
                </div>
              )}
            </div>
          )}

          {/* TAB 4: AGENT CHAT */}
          {activeTab === 'agent' && (
            <div className="tab-pane tab-chat-pane">
              <div className="tab-chat-header">
                <div className="tab-chat-info">
                  <span className="chat-bot-icon">🤖</span>
                  <div>
                    <h4 className="tab-chat-title">DataSense AI Analyst</h4>
                    <p className="tab-chat-subtitle">
                      Analyzing <strong>{dataset.filename}</strong> &bull; {dataset.shape[0]} rows &bull; {dataset.shape[1]} columns
                    </p>
                  </div>
                </div>
              </div>

              {/* Suggestions */}
              <div className="tab-chat-suggestions">
                <span className="suggestions-label">Suggestions:</span>
                <div className="suggestions-scroll">
                  <button
                    type="button"
                    className="tab-prompt-chip"
                    onClick={() => handleSendQueryWithText('What is the summary of this dataset?')}
                  >
                    Dataset Summary
                  </button>
                  <button
                    type="button"
                    className="tab-prompt-chip"
                    onClick={() => handleSendQueryWithText('Are there any missing or null values?')}
                  >
                    Check Missing Values
                  </button>
                  <button
                    type="button"
                    className="tab-prompt-chip"
                    onClick={() => handleSendQueryWithText('What are the highest and lowest values?')}
                  >
                    Min / Max Stats
                  </button>
                  <button
                    type="button"
                    className="tab-prompt-chip"
                    onClick={() => handleSendQueryWithText('Which features have strong correlation?')}
                  >
                    Correlations
                  </button>
                </div>
              </div>

              <div className="tab-chat-messages">
                {chatMessages.map((msg, idx) => (
                  <div key={idx} className={`tab-msg-row ${msg.sender}`}>
                    <div className="tab-msg-bubble">
                      <div className="tab-msg-sender">
                        {msg.sender === 'agent' ? '🤖 DataSense Agent' : '👤 You'}
                      </div>
                      <div className="tab-msg-text">{msg.text}</div>
                    </div>
                  </div>
                ))}
                {queryLoading && (
                  <div className="tab-msg-row agent">
                    <div className="tab-msg-bubble thinking">
                      <div className="chat-typing-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              <form onSubmit={handleSendQuery} className="tab-chat-input-bar">
                <input
                  type="text"
                  className="tab-chat-input"
                  placeholder={`Ask a question about ${dataset.filename} (e.g. 'What is the average of each column?')...`}
                  value={queryInput}
                  onChange={(e) => setQueryInput(e.target.value)}
                  disabled={queryLoading}
                />
                <button type="submit" className="btn btn-primary tab-chat-btn" disabled={!queryInput.trim() || queryLoading}>
                  <Send className="w-4 h-4" />
                  <span>Send</span>
                </button>
              </form>
            </div>
          )}
        </div>
      )}
    </section>
  );
}
