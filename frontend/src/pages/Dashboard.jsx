import React, { useState, useRef, useEffect } from 'react';
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
  Code2,
  ChevronDown,
  ChevronUp,
  Database,
  History,
} from 'lucide-react';
import {
  uploadDataset,
  fetchDemoDataset,
  generateCustomChart,
  getChartUrl,
  dispatchAgentQuery,
  fetchDatasets,
  fetchDatasetPreview,
  fetchSessions,
} from '../services/api';

export default function Dashboard() {
  const [dataset, setDataset] = useState(null);
  const [savedDatasets, setSavedDatasets] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [autoClean, setAutoClean] = useState(true);
  const [activeTab, setActiveTab] = useState('preview'); // 'preview' | 'charts' | 'chat' | 'history'
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
      content: 'Hello! I am DataSense AI, your autonomous data analysis agent. Ask me questions, request statistical summaries, or ask for charts.',
      time: 'Just now',
    },
  ]);
  const [queryInput, setQueryInput] = useState('');
  const [queryLoading, setQueryLoading] = useState(false);
  const [pastSessions, setPastSessions] = useState([]);

  // Toggles for code/plan visibility per message
  const [expandedCode, setExpandedCode] = useState({});
  const [expandedPlan, setExpandedPlan] = useState({});

  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);

  // Auto-scroll chat to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages, queryLoading]);

  // Load registered datasets list on mount
  useEffect(() => {
    loadSavedDatasets();
  }, []);

  const loadSavedDatasets = async () => {
    try {
      const res = await fetchDatasets();
      if (res?.datasets) {
        setSavedDatasets(res.datasets);
      }
    } catch {
      // Ignored if initial load
    }
  };

  // Load preconfigured demo dataset
  const handleLoadDemo = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetchDemoDataset();
      applyDataset(response);
      loadSavedDatasets();
      setChatMessages((prev) => [
        ...prev,
        {
          role: 'agent',
          content: `Loaded demo dataset "${response.original_name}" with ${response.data?.profile?.rows} records and ${response.data?.profile?.columns} features. Ready for exploration!`,
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
      applyDataset(response);
      loadSavedDatasets();
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

  const applyDataset = (res) => {
    setDataset(res);
    setCharts(res.data?.charts || []);
    const cols = res.data?.profile?.column_names || [];
    if (cols.length > 0) {
      setChartCol(cols[0]);
      setChartXCol(cols[0]);
      setChartYCol(cols[1] || cols[0]);
    }
    loadDatasetSessions(res.dataset_id);
  };

  const loadDatasetSessions = async (datasetId) => {
    try {
      const res = await fetchSessions(datasetId);
      if (res?.sessions) {
        setPastSessions(res.sessions);
      }
    } catch {
      // Ignored
    }
  };

  // Switch to previously saved dataset
  const handleSelectSavedDataset = async (datasetUid) => {
    if (!datasetUid) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetchDatasetPreview(datasetUid);
      setDataset({
        dataset_id: res.dataset_id,
        filename: res.filename,
        original_name: res.filename,
        file_size_bytes: 0,
        data: res.data,
      });
      setCharts([]);
      const cols = res.data?.profile?.column_names || [];
      if (cols.length > 0) {
        setChartCol(cols[0]);
        setChartXCol(cols[0]);
        setChartYCol(cols[1] || cols[0]);
      }
      loadDatasetSessions(datasetUid);
    } catch (err) {
      setError(err.message || 'Failed to load selected dataset');
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

  // Dispatch conversational query to backend LangGraph agent
  const executeQuery = async (queryText) => {
    if (!queryText.trim() || queryLoading) return;

    const userText = queryText.trim();
    setQueryInput('');
    const nowTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    setChatMessages((prev) => [
      ...prev,
      { role: 'user', content: userText, time: nowTime },
    ]);
    setQueryLoading(true);

    try {
      const data = await dispatchAgentQuery(userText, dataset?.dataset_id);

      // If new charts were produced by the agent query, register them in gallery as well
      if (data.chart_urls?.length > 0) {
        const newCharts = data.chart_urls.map((url, i) => ({
          chart_id: `agent_${Date.now()}_${i}`,
          chart_type: 'agent_plot',
          title: `Plot: ${userText}`,
          filename: url.split('/').pop(),
          url,
        }));
        setCharts((prev) => [...newCharts, ...prev]);
      }

      setChatMessages((prev) => [
        ...prev,
        {
          role: 'agent',
          content: data.final_response || 'Analysis complete.',
          plan: data.plan,
          code: data.generated_code,
          chart_urls: data.chart_urls || [],
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);

      loadDatasetSessions(dataset?.dataset_id);
    } catch (err) {
      setChatMessages((prev) => [
        ...prev,
        {
          role: 'agent',
          content: `Error executing query: ${err.message}`,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } finally {
      setQueryLoading(false);
    }
  };

  const handleSendQuery = (e) => {
    e.preventDefault();
    executeQuery(queryInput);
  };

  const profile = dataset?.data?.profile;
  const cleaningReport = dataset?.data?.cleaning_report;
  const columnNames = profile?.column_names || [];
  const numericColumns = profile?.columns_info?.filter((c) => c.stats) || [];

  const suggestedPrompts = [
    'What is the total revenue by product?',
    'Show distribution of units sold',
    'Correlation between numerical variables',
    'Summarize key statistics and overview',
  ];

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
              Autonomous tabular data analysis &bull; LangGraph Agent &bull; Dynamic Matplotlib Visualizations
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

            {savedDatasets.length > 0 && (
              <div className="saved-datasets-dropdown">
                <select
                  onChange={(e) => handleSelectSavedDataset(e.target.value)}
                  value={dataset?.dataset_id || ''}
                  className="dataset-select"
                >
                  <option value="" disabled>Saved Datasets ({savedDatasets.length})</option>
                  {savedDatasets.map((d) => (
                    <option key={d.dataset_uid || d.id} value={d.dataset_uid}>
                      {d.original_name} ({d.row_count} rows)
                    </option>
                  ))}
                </select>
              </div>
            )}

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
                    {dataset.file_size_bytes ? `${(dataset.file_size_bytes / 1024).toFixed(1)} KB • ` : ''}
                    Database Persistent &bull; Active in Memory
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
              <span>LangGraph Agent Assistant</span>
            </button>
            <button
              className={`studio-tab-btn ${activeTab === 'history' ? 'active' : ''}`}
              onClick={() => setActiveTab('history')}
            >
              <History size={18} />
              <span>Query Sessions History ({pastSessions.length})</span>
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

          {/* TAB 3: LANGGRAPH AGENT CHAT ASSISTANT */}
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
                        <div className="message-header-row">
                          <span className="message-sender">
                            {msg.role === 'user' ? 'You' : 'DataSense Agent (LangGraph)'}
                          </span>
                          <span className="message-time">{msg.time}</span>
                        </div>

                        {/* Plan Accordion */}
                        {msg.plan && msg.plan.length > 0 && (
                          <div className="chat-plan-box">
                            <button
                              type="button"
                              className="chat-toggle-btn"
                              onClick={() =>
                                setExpandedPlan((prev) => ({
                                  ...prev,
                                  [index]: !prev[index],
                                }))
                              }
                            >
                              <span>Autonomous Plan ({msg.plan.length} steps)</span>
                              {expandedPlan[index] ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                            </button>
                            {expandedPlan[index] && (
                              <ul className="plan-steps-list">
                                {msg.plan.map((step, sIdx) => (
                                  <li key={sIdx}>{step}</li>
                                ))}
                              </ul>
                            )}
                          </div>
                        )}

                        {/* Main Response Narrative */}
                        <div className="message-body-text">
                          {msg.content.split('\n').map((line, lIdx) => (
                            <p key={lIdx}>{line}</p>
                          ))}
                        </div>

                        {/* Generated Code Toggle */}
                        {msg.code && (
                          <div className="chat-code-box">
                            <button
                              type="button"
                              className="chat-toggle-btn"
                              onClick={() =>
                                setExpandedCode((prev) => ({
                                  ...prev,
                                  [index]: !prev[index],
                                }))
                              }
                            >
                              <Code2 size={14} />
                              <span>{expandedCode[index] ? 'Hide Python Code' : 'View Generated Pandas Code'}</span>
                            </button>
                            {expandedCode[index] && (
                              <pre className="code-preview-block">
                                <code>{msg.code}</code>
                              </pre>
                            )}
                          </div>
                        )}

                        {/* Inline Generated Charts */}
                        {msg.chart_urls && msg.chart_urls.length > 0 && (
                          <div className="chat-charts-row">
                            {msg.chart_urls.map((cUrl, cIdx) => (
                              <div
                                key={cIdx}
                                className="chat-chart-thumb"
                                onClick={() => setSelectedImage(getChartUrl(cUrl))}
                                title="Click to enlarge"
                              >
                                <img src={getChartUrl(cUrl)} alt="Agent Visual Output" />
                                <span className="zoom-hint">Click to enlarge</span>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}

                  {queryLoading && (
                    <div className="chat-message message-agent">
                      <div className="message-content">
                        <span className="message-sender">DataSense Agent (Reasoning &amp; Executing Code)</span>
                        <div className="loading-dots">
                          <span>.</span><span>.</span><span>.</span>
                        </div>
                      </div>
                    </div>
                  )}

                  <div ref={messagesEndRef} />
                </div>

                {/* Suggested Prompts Pills */}
                <div className="suggested-prompts-row">
                  <span className="prompts-label">Suggestions:</span>
                  {suggestedPrompts.map((p, idx) => (
                    <button
                      key={idx}
                      type="button"
                      className="prompt-pill"
                      onClick={() => executeQuery(p)}
                      disabled={queryLoading}
                    >
                      {p}
                    </button>
                  ))}
                </div>

                <form className="chat-input-bar" onSubmit={handleSendQuery}>
                  <input
                    type="text"
                    placeholder="Ask a question about your dataset (e.g., 'What is the total revenue by product?')"
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

          {/* TAB 4: PERSISTENT SESSION HISTORY */}
          {activeTab === 'history' && (
            <div className="tab-pane-history">
              <div className="glass-card history-card">
                <div className="pane-header">
                  <h3 className="pane-title">Past Analysis Sessions (Database Persisted)</h3>
                  <p className="text-muted text-xs">
                    Persistent query history stored via SQLAlchemy database connection
                  </p>
                </div>

                {pastSessions.length === 0 ? (
                  <p className="text-dim text-sm" style={{ padding: '1rem 0' }}>
                    No previous queries logged for this dataset yet. Ask questions in the Agent Assistant tab!
                  </p>
                ) : (
                  <div className="sessions-list">
                    {pastSessions.map((s) => (
                      <div key={s.id} className="session-item glass-card">
                        <div className="session-top">
                          <strong className="session-query">"{s.user_query}"</strong>
                          <span className={`pill ${s.status === 'completed' ? 'pill-success' : 'pill-warning'} text-xs`}>
                            {s.status}
                          </span>
                        </div>
                        <div className="session-body">
                          <p className="session-summary">{s.response_summary?.slice(0, 200)}...</p>
                        </div>
                        {s.chart_paths?.length > 0 && (
                          <div className="session-charts-row">
                            {s.chart_paths.map((p, i) => (
                              <button
                                key={i}
                                className="btn-link"
                                onClick={() => setSelectedImage(getChartUrl(p))}
                              >
                                View Chart {i + 1} &rarr;
                              </button>
                            ))}
                          </div>
                        )}
                        <span className="session-date text-xs text-dim">
                          {s.created_at ? new Date(s.created_at).toLocaleString() : ''}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
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
