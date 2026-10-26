import React, { useState, useRef } from 'react';
import {
  UploadCloud,
  FileSpreadsheet,
  BarChart2,
  Table,
  MessageSquare,
  Sparkles,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  Eye,
  Info,
  Layers,
  ArrowRight,
  TrendingUp,
  X,
  Send,
} from 'lucide-react';
import {
  uploadDataset,
  fetchDemoDataset,
  generateCustomChart,
  getChartUrl,
} from '../services/api';

export default function Dashboard() {
  const [dataset, setDataset] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [autoClean, setAutoClean] = useState(true);
  const [activeTab, setActiveTab] = useState('preview'); // 'preview' | 'charts' | 'chat'
  const [charts, setCharts] = useState([]);
  const [selectedImage, setSelectedImage] = useState(null);

  // Custom Chart Generator Form State
  const [chartType, setChartType] = useState('histogram');
  const [chartCol, setChartCol] = useState('');
  const [chartXCol, setChartXCol] = useState('');
  const [chartYCol, setChartYCol] = useState('');
  const [chartBins, setChartBins] = useState(20);
  const [chartLoading, setChartLoading] = useState(false);

  // Agent Chat State
  const [chatMessages, setChatMessages] = useState([
    {
      role: 'agent',
      content: 'Hello! Upload a dataset or load the demo dataset to ask questions and explore insights.',
      time: 'Just now',
    },
  ]);
  const [queryInput, setQueryInput] = useState('');
  const [queryLoading, setQueryLoading] = useState(false);

  const fileInputRef = useRef(null);

  // Load preconfigured demo dataset
  const handleLoadDemo = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetchDemoDataset();
      setDataset(response);
      setCharts(response.data?.charts || []);
      // Pre-select first column for chart generator
      const cols = response.data?.profile?.column_names || [];
      if (cols.length > 0) {
        setChartCol(cols[0]);
        setChartXCol(cols[0]);
        setChartYCol(cols[1] || cols[0]);
      }
      setChatMessages((prev) => [
        ...prev,
        {
          role: 'agent',
          content: `Loaded demo dataset "${response.original_name}" with ${response.data?.profile?.rows} rows and ${response.data?.profile?.columns} columns. Initial visualizations are ready!`,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } catch (err) {
      setError(err.message || 'Failed to load demo dataset');
    } finally {
      setLoading(false);
    }
  };

  // Handle file drop & selection
  const handleFileChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    await processFile(file);
  };

  const processFile = async (file) => {
    setLoading(true);
    setError(null);
    try {
      const response = await uploadDataset(file, autoClean, true);
      setDataset(response);
      setCharts(response.data?.charts || []);

      const cols = response.data?.profile?.column_names || [];
      if (cols.length > 0) {
        setChartCol(cols[0]);
        setChartXCol(cols[0]);
        setChartYCol(cols[1] || cols[0]);
      }

      setChatMessages((prev) => [
        ...prev,
        {
          role: 'agent',
          content: `Successfully ingested and cleaned "${response.original_name}". Rows: ${response.data?.profile?.rows}, Columns: ${response.data?.profile?.columns}.`,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } catch (err) {
      setError(err.message || 'Failed to upload and process file');
    } finally {
      setLoading(false);
    }
  };

  // Generate on-demand custom chart
  const handleCreateCustomChart = async (e) => {
    e.preventDefault();
    if (!dataset?.dataset_id) return;

    setChartLoading(true);
    setError(null);

    const params = {};
    if (chartType === 'histogram' || chartType === 'bar') {
      params.column = chartCol;
      if (chartType === 'histogram') params.bins = chartBins;
    } else if (chartType === 'scatter') {
      params.x_column = chartXCol;
      params.y_column = chartYCol;
      params.add_trendline = true;
    }

    try {
      const res = await generateCustomChart(dataset.dataset_id, chartType, params);
      if (res?.chart) {
        setCharts((prev) => [res.chart, ...prev]);
        setActiveTab('charts');
      }
    } catch (err) {
      setError(err.message || 'Failed to generate custom chart');
    } finally {
      setChartLoading(false);
    }
  };

  // Dispatch conversational query to backend agent
  const handleSendQuery = async (e) => {
    e.preventDefault();
    if (!queryInput.trim() || queryLoading) return;

    const userText = queryInput.trim();
    setQueryInput('');
    const nowTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    setChatMessages((prev) => [...prev, { role: 'user', content: userText, time: nowTime }]);
    setQueryLoading(true);

    try {
      const res = await fetch('/api/v1/agent/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: userText,
          dataset_id: dataset?.dataset_id,
        }),
      });
      const data = await res.json();
      setChatMessages((prev) => [
        ...prev,
        {
          role: 'agent',
          content: data.message || `Query received. Analysis graph acknowledged: "${userText}".`,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } catch (err) {
      setChatMessages((prev) => [
        ...prev,
        {
          role: 'agent',
          content: `Error dispatching query: ${err.message}`,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } finally {
      setQueryLoading(false);
    }
  };

  const profile = dataset?.data?.profile;
  const cleaningReport = dataset?.data?.cleaning_report;
  const columnNames = profile?.column_names || [];
  const numericColumns = profile?.columns_info?.filter((c) => c.stats) || [];

  return (
    <div className="dashboard-page" id="analysis-dashboard">
      {/* Top Banner / Ingestion Controls */}
      <section className="dashboard-header-card glass-card">
        <div className="dashboard-header-content">
          <div>
            <h2 className="dashboard-title">
              DataSense <span className="title-gradient">Studio</span>
            </h2>
            <p className="text-muted">
              Upload your dataset or load a sample to inspect distributions, run automated profiling, and generate charts.
            </p>
          </div>

          <div className="ingestion-actions">
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept=".csv,.xlsx,.xls"
              style={{ display: 'none' }}
            />
            <button
              className="btn btn-primary"
              onClick={() => fileInputRef.current?.click()}
              disabled={loading}
            >
              <UploadCloud size={18} />
              <span>{loading ? 'Processing...' : 'Upload CSV / Excel'}</span>
            </button>

            <button
              className="btn btn-secondary"
              onClick={handleLoadDemo}
              disabled={loading}
            >
              <Sparkles size={18} />
              <span>Load Demo Sales Data</span>
            </button>

            <label className="toggle-label" title="Standardize columns, strip whitespace, remove duplicates">
              <input
                type="checkbox"
                checked={autoClean}
                onChange={(e) => setAutoClean(e.target.checked)}
              />
              <span>Auto-Clean</span>
            </label>
          </div>
        </div>

        {error && (
          <div className="alert alert-error">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}
      </section>

      {/* Dataset Overview Bar (If dataset loaded) */}
      {dataset && (
        <section className="dataset-meta-section">
          <div className="meta-card glass-card">
            <div className="meta-card-header">
              <div className="meta-title-group">
                <FileSpreadsheet className="text-primary" size={24} />
                <div>
                  <h4 className="meta-filename">{dataset.original_name}</h4>
                  <span className="text-muted text-xs">
                    {(dataset.file_size_bytes / 1024).toFixed(1)} KB &bull; Ingested &amp; Profiled
                  </span>
                </div>
              </div>

              {cleaningReport && (
                <div className="clean-badge">
                  <CheckCircle2 size={16} />
                  <span>
                    Auto-Cleaned ({cleaningReport.duplicates_removed} duplicates removed)
                  </span>
                </div>
              )}
            </div>

            <div className="stats-row">
              <div className="stat-box">
                <span className="stat-label">Total Rows</span>
                <span className="stat-val">{profile?.rows?.toLocaleString()}</span>
              </div>
              <div className="stat-box">
                <span className="stat-label">Columns</span>
                <span className="stat-val">{profile?.columns}</span>
              </div>
              <div className="stat-box">
                <span className="stat-label">Total Cells</span>
                <span className="stat-val">{profile?.total_cells?.toLocaleString()}</span>
              </div>
              <div className="stat-box">
                <span className="stat-label">Missing Values</span>
                <span className={`stat-val ${profile?.total_nulls > 0 ? 'text-warning' : 'text-success'}`}>
                  {profile?.total_nulls}
                </span>
              </div>
              <div className="stat-box">
                <span className="stat-label">Visualizations</span>
                <span className="stat-val">{charts.length}</span>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Main Studio Workspace Tabs */}
      {dataset ? (
        <div className="studio-tabs-container">
          <div className="studio-tabs-bar">
            <button
              className={`studio-tab-btn ${activeTab === 'preview' ? 'active' : ''}`}
              onClick={() => setActiveTab('preview')}
            >
              <Table size={18} />
              <span>Data Preview &amp; Schema ({profile?.columns} cols)</span>
            </button>
            <button
              className={`studio-tab-btn ${activeTab === 'charts' ? 'active' : ''}`}
              onClick={() => setActiveTab('charts')}
            >
              <BarChart2 size={18} />
              <span>Visualizations Gallery ({charts.length})</span>
            </button>
            <button
              className={`studio-tab-btn ${activeTab === 'chat' ? 'active' : ''}`}
              onClick={() => setActiveTab('chat')}
            >
              <MessageSquare size={18} />
              <span>Agent Assistant</span>
            </button>
          </div>

          {/* TAB 1: DATA PREVIEW & COLUMN PROFILES */}
          {activeTab === 'preview' && (
            <div className="tab-pane-preview">
              {/* Preview Table */}
              <div className="glass-card preview-card">
                <div className="pane-header">
                  <div>
                    <h3 className="pane-title">Sample Data Preview</h3>
                    <p className="text-muted text-xs">First {profile?.sample_rows?.length} records of the dataset</p>
                  </div>
                </div>

                <div className="table-responsive">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>#</th>
                        {columnNames.map((col) => (
                          <th key={col}>{col}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {profile?.sample_rows?.map((row, idx) => (
                        <tr key={idx}>
                          <td className="row-index">{idx + 1}</td>
                          {columnNames.map((col) => (
                            <td key={col}>
                              {row[col] === null || row[col] === undefined ? (
                                <span className="null-tag">null</span>
                              ) : typeof row[col] === 'number' ? (
                                Number.isInteger(row[col]) ? row[col] : row[col].toFixed(2)
                              ) : (
                                String(row[col])
                              )}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Column Schema & Statistics Cards */}
              <div className="glass-card columns-card">
                <h3 className="pane-title">Column Profiles &amp; Summary Statistics</h3>
                <div className="columns-grid">
                  {profile?.columns_info?.map((col) => (
                    <div key={col.name} className="column-metric-card">
                      <div className="col-top">
                        <strong className="col-name">{col.name}</strong>
                        <span className="col-dtype">{col.dtype}</span>
                      </div>

                      <div className="col-meta-row">
                        <span>Unique: {col.unique_count}</span>
                        <span>Nulls: {col.null_count} ({col.null_percentage}%)</span>
                      </div>

                      {col.stats ? (
                        <div className="col-stats-row">
                          <span>Min: {col.stats.min}</span>
                          <span>Mean: {col.stats.mean}</span>
                          <span>Max: {col.stats.max}</span>
                        </div>
                      ) : (
                        <span className="text-dim text-xs">Categorical / Text Feature</span>
                      )}

                      <div className="col-action-row">
                        {col.stats ? (
                          <button
                            className="btn-link"
                            onClick={() => {
                              setChartType('histogram');
                              setChartCol(col.name);
                              setActiveTab('charts');
                            }}
                          >
                            Plot Histogram &rarr;
                          </button>
                        ) : (
                          <button
                            className="btn-link"
                            onClick={() => {
                              setChartType('bar');
                              setChartCol(col.name);
                              setActiveTab('charts');
                            }}
                          >
                            Plot Bar Chart &rarr;
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: VISUALIZATIONS GALLERY & GENERATOR */}
          {activeTab === 'charts' && (
            <div className="tab-pane-charts">
              {/* Custom Chart Generator Form */}
              <div className="glass-card chart-generator-card">
                <h3 className="pane-title">Generate Custom Visualization</h3>
                <form className="generator-form" onSubmit={handleCreateCustomChart}>
                  <div className="form-group">
                    <label>Chart Type</label>
                    <select
                      value={chartType}
                      onChange={(e) => setChartType(e.target.value)}
                    >
                      <option value="histogram">Distribution Histogram</option>
                      <option value="heatmap">Correlation Matrix Heatmap</option>
                      <option value="scatter">Scatter Plot (X vs Y)</option>
                      <option value="bar">Categorical Bar Chart</option>
                    </select>
                  </div>

                  {(chartType === 'histogram' || chartType === 'bar') && (
                    <div className="form-group">
                      <label>Target Column</label>
                      <select
                        value={chartCol}
                        onChange={(e) => setChartCol(e.target.value)}
                      >
                        {columnNames.map((c) => (
                          <option key={c} value={c}>{c}</option>
                        ))}
                      </select>
                    </div>
                  )}

                  {chartType === 'histogram' && (
                    <div className="form-group">
                      <label>Bins: {chartBins}</label>
                      <input
                        type="range"
                        min="5"
                        max="50"
                        value={chartBins}
                        onChange={(e) => setChartBins(parseInt(e.target.value))}
                      />
                    </div>
                  )}

                  {chartType === 'scatter' && (
                    <>
                      <div className="form-group">
                        <label>X-Axis (Numerical)</label>
                        <select
                          value={chartXCol}
                          onChange={(e) => setChartXCol(e.target.value)}
                        >
                          {numericColumns.map((c) => (
                            <option key={c.name} value={c.name}>{c.name}</option>
                          ))}
                        </select>
                      </div>

                      <div className="form-group">
                        <label>Y-Axis (Numerical)</label>
                        <select
                          value={chartYCol}
                          onChange={(e) => setChartYCol(e.target.value)}
                        >
                          {numericColumns.map((c) => (
                            <option key={c.name} value={c.name}>{c.name}</option>
                          ))}
                        </select>
                      </div>
                    </>
                  )}

                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={chartLoading}
                    style={{ alignSelf: 'flex-end' }}
                  >
                    <TrendingUp size={16} />
                    <span>{chartLoading ? 'Rendering...' : 'Render Chart'}</span>
                  </button>
                </form>
              </div>

              {/* Charts Grid */}
              <div className="charts-gallery-grid">
                {charts.length === 0 ? (
                  <div className="glass-card empty-charts">
                    <BarChart2 size={40} className="text-muted" />
                    <p>No charts generated yet. Use the form above to render plots.</p>
                  </div>
                ) : (
                  charts.map((chart, idx) => (
                    <div key={chart.chart_id || idx} className="glass-card chart-card">
                      <div className="chart-card-top">
                        <h4 className="chart-title">{chart.title}</h4>
                        <span className="pill pill-primary text-xs capitalize">{chart.chart_type}</span>
                      </div>

                      <div
                        className="chart-img-container"
                        onClick={() => setSelectedImage(getChartUrl(chart.url))}
                      >
                        <img
                          src={getChartUrl(chart.url)}
                          alt={chart.title}
                          loading="lazy"
                          className="chart-img"
                        />
                        <div className="chart-img-overlay">
                          <Eye size={20} />
                          <span>Click to Zoom</span>
                        </div>
                      </div>

                      <div className="chart-card-footer">
                        <a
                          href={getChartUrl(chart.url)}
                          download={chart.filename}
                          target="_blank"
                          rel="noreferrer"
                          className="btn-download"
                        >
                          Download High-Res PNG
                        </a>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {/* TAB 3: AGENT CHAT ASSISTANT */}
          {activeTab === 'chat' && (
            <div className="tab-pane-chat">
              <div className="glass-card chat-card">
                <div className="chat-messages-container">
                  {chatMessages.map((msg, index) => (
                    <div
                      key={index}
                      className={`chat-message ${msg.role === 'user' ? 'message-user' : 'message-agent'}`}
                    >
                      <div className="message-content">
                        <span className="message-sender">
                          {msg.role === 'user' ? 'You' : 'DataSense Agent'}
                        </span>
                        <p>{msg.content}</p>
                        <span className="message-time">{msg.time}</span>
                      </div>
                    </div>
                  ))}
                  {queryLoading && (
                    <div className="chat-message message-agent">
                      <div className="message-content">
                        <span className="message-sender">DataSense Agent</span>
                        <div className="loading-dots">
                          <span>.</span><span>.</span><span>.</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                <form className="chat-input-bar" onSubmit={handleSendQuery}>
                  <input
                    type="text"
                    placeholder="Ask a question about your dataset (e.g., 'What is the correlation between revenue and units sold?')"
                    value={queryInput}
                    onChange={(e) => setQueryInput(e.target.value)}
                    disabled={queryLoading}
                  />
                  <button type="submit" className="btn btn-primary" disabled={queryLoading || !queryInput.trim()}>
                    <Send size={16} />
                  </button>
                </form>
              </div>
            </div>
          )}
        </div>
      ) : (
        /* Empty State Placeholder */
        <section className="empty-state-section glass-card">
          <UploadCloud size={56} className="empty-icon text-primary" />
          <h3 className="empty-title">Ready for Your Tabular Data</h3>
          <p className="empty-desc text-muted">
            Drag and drop your CSV or Excel file here, or click below to explore our sample sales dataset.
          </p>
          <div className="empty-actions">
            <button
              className="btn btn-primary btn-lg"
              onClick={() => fileInputRef.current?.click()}
              disabled={loading}
            >
              <UploadCloud size={20} />
              <span>Choose File (.csv, .xlsx)</span>
            </button>
            <button
              className="btn btn-secondary btn-lg"
              onClick={handleLoadDemo}
              disabled={loading}
            >
              <Sparkles size={20} />
              <span>Explore Demo Sales Data</span>
            </button>
          </div>
        </section>
      )}

      {/* Fullscreen Image Zoom Modal */}
      {selectedImage && (
        <div className="chart-modal-backdrop" onClick={() => setSelectedImage(null)}>
          <div className="chart-modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close-btn" onClick={() => setSelectedImage(null)}>
              <X size={24} />
            </button>
            <img src={selectedImage} alt="Enlarged Chart" className="modal-img" />
          </div>
        </div>
      )}
    </div>
  );
}
