# DataSense AI – Autonomous Data Analysis Agent

An enterprise-grade, full-stack AI platform that ingests CSV and Excel datasets, performs automated data cleaning and exploratory data analysis (EDA), generates publication-grade visualizations, and provides natural-language answers to analytical queries using an autonomous agent orchestrated with **LangGraph**.

---

## 1. Project Overview & Architectural Vision

DataSense AI transforms raw tabular datasets into actionable analytical narratives:
- **Intelligent Data Ingestion:** Fast, schema-aware loading of `.csv`, `.xlsx`, and `.xls` files with automatic encoding fallbacks (`utf-8`, `utf-8-sig`, `latin1`).
- **Automated Data Engine:** Missing value detection, duplicate pruning, whitespace normalization, type inference, and automated statistical profiling.
- **Autonomous Agent (LangGraph):** 4-stage cyclic state machine for multi-step reasoning (`plan_analysis` $\rightarrow$ `generate_code` $\rightarrow$ `execute_code` $\rightarrow$ `synthesize_response`).
- **Sandboxed Code Execution:** Secure in-process execution namespace evaluating generated Pandas and Matplotlib code against the active dataset.
- **Dynamic Visualizations:** Automated distribution histograms with mean/median reference lines, annotated correlation heatmaps, scatter plots with regression trendlines, and categorical bar charts rendered via headless Matplotlib.
- **Resilient Relational Persistence:** SQLAlchemy ORM models with seamless SQLite/PostgreSQL auto-fallback, tracking dataset metadata, schemas, and conversational query histories.
- **Modern Full-Stack Experience:** Asynchronous FastAPI backend paired with a high-performance React 18 + Vite Studio interface.

---

## 2. Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | React 18, Vite, Lucide-React | Interactive Studio UI, data preview table, charts gallery, agent chat |
| **Backend** | Python 3.10+, FastAPI, Uvicorn | Async REST API, CORS middleware, file streaming, lifespan handlers |
| **Agent Orchestration** | LangGraph, LangChain Core | Cyclic graph workflows, stateful multi-step reasoning, plan synthesis |
| **Data Processing** | Pandas, NumPy, OpenPyXL | Matrix ops, data cleaning, type inference, Excel/CSV ingestion |
| **Visualization** | Matplotlib (Agg backend) | Headless generation of charts, histograms, heatmaps, and scatter plots |
| **Database** | PostgreSQL, SQLite, SQLAlchemy | Relational persistence of datasets, schemas, and query sessions |
| **Testing** | Pytest, HTTPX, FastAPI TestClient | End-to-end unit and integration test coverage across all subsystems |

---

## 3. Project Directory Structure

```text
DataSense/
├── backend/
│   ├── app/
│   │   ├── __init__.py               # Package initializer
│   │   ├── main.py                   # FastAPI app entrypoint, CORS, lifespan & health check
│   │   ├── config.py                 # Environment configuration & safe directory management
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes.py             # REST API routers (upload, charts, agent query, sessions)
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── graph.py              # LangGraph StateGraph constructor & compilation
│   │   │   ├── state.py              # AgentState TypedDict schema definition
│   │   │   └── nodes.py              # Workflow nodes (planning, code gen, execute, synthesize)
│   │   ├── data_engine/
│   │   │   ├── __init__.py
│   │   │   ├── loader.py             # CSV and Excel dataset loader with encoding fallbacks
│   │   │   ├── cleaner.py            # Deduplication, whitespace normalization & column cleaning
│   │   │   └── profiler.py           # Automated EDA metrics, column summaries & JSON samples
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── analysis_tools.py     # Descriptive statistics & correlation matrices
│   │   │   └── visualization_tools.py# Matplotlib histogram, heatmap, scatter & bar generators
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── analysis_service.py   # Business logic orchestrator between engine & agent
│   │   └── database/
│   │       ├── __init__.py
│   │       ├── connection.py         # SQLAlchemy engine with SQLite/PostgreSQL fallback
│   │       └── models.py             # ORM models (DatasetRecord, AnalysisSession)
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_health.py            # Health and root endpoint verification
│   │   ├── test_data_pipeline.py     # Ingestion, cleaning & profiling tests
│   │   ├── test_visualizations.py    # Matplotlib chart generation & image serving tests
│   │   ├── test_agent.py             # LangGraph agent planning, execution & query tests
│   │   └── test_database.py          # Database connection & persistence tests
│   ├── uploads/                      # Ingested datasets directory
│   ├── generated_charts/             # Headless Matplotlib chart cache
│   ├── requirements.txt              # Backend Python dependencies
│   ├── .env.example                  # Environment variable template
│   └── .env                          # Local environment configuration
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx            # App header with live backend status & navigation
│   │   │   └── HealthStatus.jsx      # Backend connectivity widget
│   │   ├── pages/
│   │   │   └── Dashboard.jsx         # Full Studio interface: Ingestion, Table, Charts & Chat
│   │   ├── services/
│   │   │   └── api.js                # Frontend API client for all backend endpoints
│   │   ├── hooks/
│   │   │   └── useHealthCheck.js     # React hook polling backend health status
│   │   ├── App.jsx                   # Main layout switching Studio and Architecture views
│   │   ├── App.css                   # Custom modern dark-mode stylesheet & design system
│   │   └── main.jsx                  # React application entrypoint
│   ├── index.html                    # HTML document shell with Inter font
│   ├── package.json                  # Frontend dependencies and Vite scripts
│   └── vite.config.js                # Vite build & local dev proxy configuration
├── .gitignore                        # Global repository gitignore
└── README.md                         # Complete project documentation & guide
```

---

## 4. REST API Reference

The FastAPI backend exposes interactive Swagger documentation at **`http://localhost:8000/docs`**.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Root welcome endpoint and API metadata |
| `GET` | `/health` | Live health probe reporting database and LLM status |
| `GET` | `/api/v1/status` | Operational feature matrix and system version |
| `POST` | `/api/v1/datasets/upload` | Multipart file upload (`.csv`, `.xlsx`, `.xls`) with automated cleaning & profiling |
| `GET` | `/api/v1/datasets/demo` | Generates or loads pre-configured 100-row sales demonstration dataset |
| `GET` | `/api/v1/datasets` | Lists all registered datasets from database persistence |
| `GET` | `/api/v1/datasets/preview` | Retrieves profiling summary and sample rows for a dataset ID |
| `GET` | `/api/v1/charts/{filename}` | Serves generated Matplotlib PNG images with path traversal protection |
| `POST` | `/api/v1/charts/generate` | On-demand custom chart generator (`histogram`, `heatmap`, `scatter`, `bar`) |
| `POST` | `/api/v1/agent/query` | Conversational LangGraph agent query endpoint |
| `GET` | `/api/v1/sessions` | Lists past conversational analysis sessions and chart outputs from database |

---

## 5. Getting Started & Setup Guide

### 5.1 Prerequisites
- **Python**: 3.10 or higher
- **Node.js**: v18.0.0 or higher (v20+ recommended)
- **npm**: 9.0.0 or higher

---

### 5.2 Backend Setup

#### Step 1: Create a Python Virtual Environment
```bash
# Windows (PowerShell)
python -m venv backend/.venv

# Linux / macOS
python3 -m venv backend/.venv
```

#### Step 2: Activate the Virtual Environment
- **Windows (PowerShell):**
  ```powershell
  backend\.venv\Scripts\Activate.ps1
  ```
- **Linux / macOS:**
  ```bash
  source backend/.venv/bin/activate
  ```

#### Step 3: Install Dependencies
```bash
pip install -r backend/requirements.txt
```

#### Step 4: Configure Environment Variables
```bash
# From project root:
cp backend/.env.example backend/.env
```
*(By default, the application runs out-of-the-box using local SQLite fallback for database persistence. To connect live PostgreSQL or an external LLM API key, edit `backend/.env`)*.

#### Step 5: Start the FastAPI Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- **API Server:** [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

### 5.3 Frontend Setup

Open a **separate terminal window**:

```bash
cd frontend
npm install
npm run dev
```
- **Studio Interface:** [http://localhost:5173](http://localhost:5173)

---

## 6. Running the Test Suite

The backend includes comprehensive unit and integration tests covering health checks, data pipelines, visualizations, database persistence, and LangGraph agent execution:

```bash
# Activate virtual environment
backend\.venv\Scripts\Activate.ps1

# Run all pytest suites
pytest backend/tests
```

**Test Coverage Summary:**
- `backend/tests/test_health.py`: Root and `/health` availability.
- `backend/tests/test_data_pipeline.py`: Upload streaming, cleaning, deduplication, profiling, and demo dataset generation.
- `backend/tests/test_visualizations.py`: Histograms, correlation heatmaps, scatter plots, bar charts, and image retrieval.
- `backend/tests/test_agent.py`: LangGraph planning, code generation, sandboxed execution, and synthesis.
- `backend/tests/test_database.py`: SQLAlchemy database models and session persistence.

---

## 7. Interactive Studio Dashboard Features

1. **Dataset Ingestion Zone:**
   - Drag-and-drop or file selector supporting `.csv`, `.xlsx`, and `.xls`.
   - **"Load Demo Sales Data"** button for immediate testing.
   - **"Auto-Clean" toggle** for automated whitespace stripping and deduplication.
2. **Metadata Banner:**
   - Displays total rows, columns, cells, missing values count, and duplicates removed.
3. **Data Preview & Schema:**
   - Formatted data preview table with numeric rounding and `null` badges.
   - Column summary cards with min/mean/max stats and one-click chart shortcuts.
4. **Visualizations Gallery:**
   - Grid of auto-generated starter charts.
   - Custom chart generator form to plot histograms, heatmaps, scatter plots, and bar charts on demand.
   - Click-to-Zoom fullscreen modal and high-res PNG download buttons.
5. **LangGraph Agent Assistant:**
   - Conversational chat powered by the autonomous agent workflow.
   - Collapsible **Autonomous Plan** drawer showing agent reasoning steps.
   - Collapsible **Python Code** drawer showing generated Pandas/Matplotlib scripts.
   - Inline generated visual charts embedded directly in conversation responses.
   - Clickable suggested prompt pills.
6. **Query Sessions History:**
   - Persistent log of previous analysis sessions stored in relational database.
