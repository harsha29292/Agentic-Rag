# Agentic RAG – Patent Innovation Predictor

An agentic Retrieval-Augmented Generation (RAG) system that collects patent data, indexes it in OpenSearch with vector embeddings, and uses a multi-agent CrewAI pipeline (powered by a local Ollama LLM) to analyze trends and forecast future innovations.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [1. Collect Patent Data](#1-collect-patent-data)
  - [2. Index Patents into OpenSearch](#2-index-patents-into-opensearch)
  - [3. Run the Interactive CLI](#3-run-the-interactive-cli)
- [Project Structure](#project-structure)
- [Search Modes](#search-modes)
- [Multi-Agent Pipeline](#multi-agent-pipeline)

---

## Overview

This project combines several components to deliver end-to-end patent intelligence:

- **Data collection** – Fetches patent data from [Google Patents via SerpApi](https://serpapi.com/google-patents-api) and stores raw results as JSON files.
- **Indexing** – Generates semantic embeddings with [Ollama](https://ollama.com/) and stores both text and vector data in [OpenSearch](https://opensearch.org/).
- **Multi-agent analysis** – Runs a four-agent CrewAI crew that sequentially: defines a research plan, retrieves the most relevant patents, analyzes trends and patterns, and forecasts future innovations.

---

## Architecture

```
SerpApi (Google Patents)
        │
        ▼
information_collector.py  ──► results/ (JSON files)
        │
        ▼
ingestion.py              ──► OpenSearch index "patents"
        │                        ├── text fields (title, abstract, …)
        │                        └── knn_vector field (embedding)
        │
        ▼
patent_search_tools.py    ──► keyword / semantic / hybrid / iterative search
        │
        ▼
patent_crew.py            ──► CrewAI agents (Ollama LLM)
        │                        ├── Research Director
        │                        ├── Patent Retriever
        │                        ├── Patent Data Analyst
        │                        └── Innovation Forecaster
        │
        ▼
agentic_rag.py            ──► Interactive CLI
```

---

## Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | ≥ 3.10 | |
| Docker & Docker Compose | any recent | Runs OpenSearch + Dashboards |
| [Ollama](https://ollama.com/) | latest | Must be running locally on port 11434 |
| SerpApi account | — | For patent data collection |

Pull the required Ollama models:

```bash
ollama pull deepseek-r1:1.5b   # default LLM used by the agents
ollama pull nomic-embed-text   # embedding model
```

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/harsha29292/Agentic-Rag.git
cd Agentic-Rag

# 2. Create and activate a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Start OpenSearch and OpenSearch Dashboards
docker compose up -d
```

OpenSearch will be available at `http://localhost:9200` and the Dashboards UI at `http://localhost:5601`.

---

## Configuration

Create a `.env` file in the project root:

```env
SERP_API_KEY=your_serpapi_key_here
```

> **Note:** `SERP_API_KEY` is only required for **Step 1 (Collect Patent Data)**. If you already have patent JSON files in `results/`, you can skip that step and proceed directly to indexing.

---

## Usage

### 1. Collect Patent Data

Fetch patents from Google Patents and save them as JSON files to the `results/` directory:

```bash
python information_collector.py
# Prompts: search query (e.g. "lithium battery") and output directory (e.g. results)
```

### 2. Index Patents into OpenSearch

Load the collected JSON files, generate embeddings, and index everything into OpenSearch:

```bash
python ingestion.py
```

This script will:
- **⚠️ Delete and recreate** the `patents` index (any previously indexed data will be lost)
- Generate a 768-dimensional embedding for each patent abstract
- Index all valid patents

### 3. Run the Interactive CLI

```bash
python agentic_rag.py
```

The menu provides five options:

```
============================================================
  PATENT INNOVATION PREDICTOR - LITHIUM BATTERY TECHNOLOGY
============================================================
1. Run complete patent trend analysis and forecasting
2. Search for specific patents
3. Iterative patent exploration
4. View system status
5. Exit
```

---

## Project Structure

```
Agentic-Rag/
├── agentic_rag.py           # Main interactive CLI
├── patent_crew.py           # CrewAI agents and tasks
├── patent_search_tools.py   # Keyword, semantic, hybrid & iterative search
├── ingestion.py             # Data loading and OpenSearch indexing
├── information_collector.py # SerpApi patent data collector
├── embedding.py             # Ollama embedding helper
├── opensearch_client.py     # OpenSearch client and index management
├── helper.py                # SerpApi URL helpers
├── docker-compose.yml       # OpenSearch + Dashboards services
├── requirements.txt         # Python dependencies
├── results/                 # Downloaded patent JSON files (git-ignored)
├── files/                   # Additional data files
└── tests/                   # Unit tests
```

---

## Search Modes

| Mode | Description |
|---|---|
| **Keyword** | Full-text BM25 match on the `abstract` field |
| **Semantic** | KNN vector search using `nomic-embed-text` embeddings |
| **Hybrid** | Combines keyword and semantic search with a boolean `should` query |
| **Iterative** | Repeats keyword search, refining the query with the top result's title each iteration |

---

## Multi-Agent Pipeline

The CrewAI pipeline runs four sequential agents, each building on the previous one's output:

| Agent | Role |
|---|---|
| **Research Director** | Defines the research plan: key technology areas and time periods |
| **Patent Retriever** | Fetches relevant patents using `search_patents` and `search_patents_by_date_range` tools |
| **Patent Data Analyst** | Identifies trends, patterns, and emerging sub-technologies |
| **Innovation Forecaster** | Predicts breakthrough technologies and recommends R&D investment areas |

Results are saved to a timestamped text file (`patent_analysis_YYYYMMDD_HHMMSS.txt`).
