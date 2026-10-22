# DataSense AI – Autonomous Data Analysis Agent

An advanced, AI-powered web platform that ingests CSV and Excel datasets, performs automated data cleaning and exploratory data analysis (EDA), generates publication-grade visualizations, and provides natural-language answers to complex analytical questions using an autonomous agent orchestrated with **LangGraph**.

---

## 1. Project Overview & Architectural Vision

DataSense AI transforms raw tabular datasets into actionable analytical narratives:
- **Intelligent Data Ingestion:** Fast, schema-aware loading of `.csv`, `.xlsx`, and `.xls` files.
- **Automated Data Engine:** Missing value detection, duplicate pruning, whitespace normalization, type inference, and automated statistical profiling.
- **Autonomous Agent (LangGraph):** Multi-step planning, automated code synthesis (Pandas/Matplotlib), sandboxed execution, and natural-language synthesis.
- **Dynamic Visualizations:** Automated distribution histograms, correlation heatmaps, and customizable charts rendered via headless Matplotlib.
- **Enterprise Persistence:** PostgreSQL and SQLAlchemy for storing dataset metadata, data audit logs, analysis sessions, and chart outputs.
- **Modern Full-Stack Experience:** Asynchronous FastAPI backend paired with a high-performance React + Vite user interface.

---

## 2. Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | React 18, Vite | Component architecture, responsive UI, hot reload |
| **Backend** | Python 3.10+, FastAPI, Uvicorn | Async REST API, route handlers, CORS middleware |
| **Agent Orchestration** | LangGraph, LangChain Core | Cyclic graph workflows, stateful multi-step reasoning |
| **Data Processing** | Pandas, NumPy, OpenPyXL | High-speed data manipulation, matrix ops, spreadsheet I/O |
| **Visualization** | Matplotlib (Agg backend) | Headless generation of charts and correlation heatmaps |
| **Database** | PostgreSQL, SQLAlchemy, Psycopg 3 | Relational persistence of sessions, schemas, and audits |
| **Configuration** | python-dotenv | Environment-variable management |
| **Version Control** | Git | Source code and revision tracking |

---

## 3. Project Directory Structure

```text
DataSense-AI/
├── backend/
│   ├── app/
│   │   ├── __init__.py               # Backend package initializer
│   │   ├── main.py                   # FastAPI app entrypoint, CORS, root & /health endpoints
│   │   ├── config.py                 # Environment-based configuration & safe defaults
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes.py             # REST API routers (dataset upload, agent queries)
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── graph.py              # LangGraph StateGraph constructor & compilation
│   │   │   ├── state.py              # AgentState TypedDict schema definition
│   │   │   └── nodes.py              # Workflow nodes (planning, code gen, execute, synthesize)
│   │   ├── data_engine/
│   │   │   ├── __init__.py
│   │   │   ├── loader.py             # CSV and Excel dataset loader
│   │   │   ├── cleaner.py            # Deduplication, whitespace normalization & null handling
│   │   │   └── profiler.py           # Automated EDA metrics, shapes & column summaries
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── analysis_tools.py     # Descriptive statistics & correlation matrices
│   │   │   └── visualization_tools.py# Matplotlib histogram & correlation heatmap generators
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── analysis_service.py   # Business logic orchestrator between engine & agent
│   │   └── database/
│   │       ├── __init__.py
│   │       ├── connection.py         # SQLAlchemy engine, session maker & health probe
│   │       └── models.py             # ORM models (DatasetRecord, AnalysisSession)
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_health.py            # Starter test cases for root and health checks
│   ├── requirements.txt              # Backend Python dependencies
│   ├── .env.example                  # Environment variable template with placeholders
│   └── .gitignore                    # Backend gitignore rules
├── frontend/
│   ├── src/
│   │   ├── components/               # Reusable UI components (Navbar, HealthStatus, etc.)
│   │   ├── pages/                    # Views and dashboard layouts
│   │   ├── services/                 # API client wrapper functions (fetch/axios)
│   │   ├── hooks/                    # Custom React hooks (useHealthCheck)
│   │   ├── assets/                   # Static imagery and branding assets
│   │   ├── App.jsx                   # Main welcome page titled DataSense AI
│   │   ├── App.css                   # Custom modern dark-mode stylesheet
│   │   └── main.jsx                  # React application entrypoint
│   ├── public/                       # Static public assets (favicon, SVG)
│   ├── index.html                    # HTML document shell with Inter font
│   ├── package.json                  # Frontend dependencies and Vite scripts
│   ├── vite.config.js                # Vite build & local dev proxy configuration
│   └── .gitignore                    # Frontend gitignore rules
├── .gitignore                        # Global repository gitignore
└── README.md                         # Complete project documentation & guide
```

---

## 4. Getting Started & Setup Guide

### 4.1 Prerequisites
- **Python**: 3.10 or higher
- **Node.js**: v18.0.0 or higher (v20+ recommended)
- **npm**: 9.0.0 or higher

---

### 4.2 Backend Setup

#### Step 1: Create a Python Virtual Environment
Open PowerShell or your command terminal in the project directory:

```bash
# Windows (PowerShell)
python -m venv .venv

# Linux / macOS
python3 -m venv .venv
```

#### Step 2: Activate the Virtual Environment

- **Windows (PowerShell):**
  ```powershell
  .venv\Scripts\Activate.ps1
  ```
  *(If PowerShell execution policies block script execution, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

- **Windows (Command Prompt):**
  ```cmd
  .venv\Scripts\activate.bat
  ```

- **Linux / macOS:**
  ```bash
  source .venv/bin/activate
  ```

#### Step 3: Install Backend Dependencies

```bash
cd backend
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 4: Configure Environment Variables

```bash
# Inside the backend/ directory:
cp .env.example .env
```
*(Open `.env` to customize settings when you are ready to connect a live PostgreSQL database or LLM API key. **Neither is required for initial health check or root endpoints**).*

#### Step 5: Start the FastAPI Server

```bash
# From the backend/ folder:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Verify your backend is running:
- **Root endpoint:** [http://localhost:8000/](http://localhost:8000/)
- **Health check:** [http://localhost:8000/health](http://localhost:8000/health)
- **Interactive Swagger API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

### 4.3 Frontend Setup

Open a **separate terminal window** for the frontend:

#### Step 1: Navigate to the Frontend Directory

```bash
cd frontend
```

#### Step 2: Install Node Dependencies

```bash
npm install
```

#### Step 3: Start the Vite Development Server

```bash
npm run dev
```

The frontend will start at:
- **Local URL:** [http://localhost:5173/](http://localhost:5173/)

The welcome page displays a live connection status widget that communicates with the FastAPI `/health` endpoint via the configured Vite proxy.

---

## 5. Development Roadmap & Next Steps

1. **Dataset Ingestion Pipeline:** Expand `loader.py` with multi-sheet Excel parsing, file validation, and upload stream endpoints in `routes.py`.
2. **Automated Cleaning & EDA Profiling:** Enhance `cleaner.py` and `profiler.py` with outlier detection, automated imputation strategies, and skewness calculations.
3. **LangGraph Agent Workflow:** Connect stateful LLM node graph with tool calling (`analysis_tools.py`, `visualization_tools.py`) and safety validation.
4. **Interactive Dashboard:** Build interactive chat interface, dataset preview table, and dynamic chart gallery in React.
5. **PostgreSQL Persistence:** Run database migrations with Alembic and store persistent analysis histories.
