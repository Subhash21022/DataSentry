# 📋 DataSentry — SWOC Project Admin Application & Overview

This document contains the complete project proposal, architectural justification, tech stack breakdown, and contributor milestone roadmap tailored for the **Social Winter of Code (SWOC) Project Admin Application**.

---

## 1. Project Details at a Glance

* **Project Name**: DataSentry
* **Tagline**: All-in-One Data Quality, Profiling & ML Anomaly Detection Platform
* **Primary Categories**: Machine Learning / Data Science, Full-Stack Web Development, Developer Tools / CLI
* **License**: MIT (Open Source)
* **Target Audience**: Data Engineers, Data Scientists, Backend Developers, and Open Source Contributors of all experience levels

---

## 2. Project Executive Summary & Pitch

In modern data-driven systems, **"Garbage In, Garbage Out"** remains the #1 failure mode. Broken pipelines, silent data drift, missing values, corrupted formats, and anomalous records routinely break downstream ML models and business intelligence dashboards.

Existing open-source solutions are fragmented:
- Profiling tools (like ydata-profiling) generate static HTML reports without actionable validation or real-time APIs.
- Validation tools (like Great Expectations) have a steep learning curve and lack built-in interactive visual exploration and machine learning outlier detection.
- Monitoring SaaS tools (like Validio, Monte Carlo) are proprietary enterprise closed-source platforms.

**DataSentry** solves this by unifying everything into **one complete open-source platform**:
1. **Unified Python Engine**: Core profiling, deterministic rules, and ML anomaly detection contained in a single reusable engine.
2. **Developer CLI (`datasentry`)**: Instant terminal profiling with rich formatting, quality scores, and CI/CD automated quality gates.
3. **Modern Full-Stack Dashboard (React + FastAPI)**: Drag-and-drop dataset upload, real-time interactive charts, visual rule configuration, and exportable reports.
4. **ML Anomaly Detection**: Unsupervised machine learning models (Isolation Forests, Local Outlier Factor, dynamic distribution metrics) flagging multi-column anomalies that static regex/boundary rules fail to catch.

---

## 3. Tech Stack Matrix (Full-Stack + Machine Learning)

DataSentry bridges **Full-Stack Development** and **Machine Learning / Data Science**, making it an ideal open-source repository for contributors from different backgrounds:

### A. Machine Learning & Data Science Track
| Component | Technology | Role & Purpose |
| :--- | :--- | :--- |
| **Data Processing Engine** | `Pandas`, `Polars`, `NumPy` | Fast in-memory tabular manipulation, statistical computations, and chunking |
| **Unsupervised Anomaly Detection** | `Scikit-learn` (`IsolationForest`), `PyOD` | Multi-dimensional outlier detection and density-based anomaly scoring |
| **Statistical Inference & Drift** | `SciPy` | Skewness, Kurtosis, Z-Score, IQR Dynamic Boundaries, KS-distribution tests |
| **Semantic Type Heuristics** | Regex + Token NLP | Automated detection of semantic data types (Emails, IPs, Dates, UUIDs, Geolocation) |
| **Smart Imputation & Cleaning** | `Scikit-learn` (`IterativeImputer`, `KNNImputer`) | Intelligent recommendations for cleaning missing values |

### B. Full-Stack Backend Track
| Component | Technology | Role & Purpose |
| :--- | :--- | :--- |
| **Web Framework** | `FastAPI` (Python 3.10+) | High-performance asynchronous REST API with automatic OpenAPI Swagger docs |
| **Data Contracts & Validation** | `Pydantic v2` | Strict schema serialization and request payload validation |
| **Background Processing** | `FastAPI BackgroundTasks` | Asynchronous file parsing and non-blocking dataset profiling |
| **Database & Persistence** | `SQLAlchemy` + `SQLite` / `PostgreSQL` | Storage for saved datasets, rule suites, and historical quality scores |
| **Report Generation** | `Jinja2` | Dynamic compilation of standalone interactive HTML reports |

### C. Full-Stack Frontend Track
| Component | Technology | Role & Purpose |
| :--- | :--- | :--- |
| **UI Framework** | `React 18` + `TypeScript` + `Vite` | Type-safe, component-driven reactive user interface |
| **Styling & Design System** | `Tailwind CSS` + `Lucide Icons` | Modern, clean UI inspired by platforms like Validio and Linear |
| **Data Visualizations** | `Recharts` | Column distribution histograms, box plots, and quality gauges |
| **Tabular Data Grid** | `@tanstack/react-table` | High-performance interactive dataset viewer with anomaly highlighting |
| **API Client** | `Axios` / `TanStack Query` | Robust asynchronous data fetching and upload progress handling |

### D. CLI & DevOps Track
| Component | Technology | Role & Purpose |
| :--- | :--- | :--- |
| **Terminal CLI** | `Typer` + `Rich` | Intuitive terminal tool with colored tables, spinners, and exit codes |
| **Testing** | `Pytest` + `Jest` / `Vitest` | Comprehensive unit and integration test coverage |
| **Automation & CI** | `GitHub Actions` | Automated linting, test suites, and Docker image builds |

---

## 4. Why DataSentry is Perfect for SWOC (Social Winter of Code)

1. **Clear Modular Boundaries**:
   Because the core engine is decoupled from the web UI and CLI, contributors won't step on each other's toes. One contributor can work on an ML anomaly algorithm while another builds a React chart component.
2. **Inclusive Learning Curve**:
   - **Beginners**: Can contribute regex validators, sample datasets, docs, simple UI components, and test cases.
   - **Intermediate**: Can integrate new chart types (heatmaps), add CLI flags, create FastAPI endpoints, or implement statistical profilers.
   - **Advanced**: Can build data drift detectors, PyOD algorithms, rule auto-generation heuristics, and Dockerized deployments.
3. **Real-World Relevance**:
   Data Quality and Data Observability are among the most sought-after domains in modern tech and data engineering.

---

## 5. SWOC Roadmap & Phased Contribution Timeline

### 🗓️ Phase 1: Core Foundation & Onboarding (Weeks 1 - 2)
* Release initial functional repository with base profiling engine, CLI, and basic FastAPI backend.
* Onboard SWOC participants via Discord/Slack and maintain clear `good first issue` tickets.
* Goals:
  - Add missing file format support (Parquet, TSV, JSON Lines).
  - Add standard column validators (Phone numbers, Postal codes, URLs, Custom regex).
  - Setup React Vite skeleton and base layout with Tailwind CSS.

### 🗓️ Phase 2: Feature Expansion & Visual Dashboard (Weeks 3 - 4)
* Expand the React dashboard and integrate interactive charts.
* Goals:
  - Implement interactive histograms, quantile cards, and correlation matrices.
  - Implement rule builder UI in React allowing users to define constraints interactively.
  - Integrate Scikit-Learn `IsolationForest` and statistical Z-Score thresholding into the CLI & UI.
  - HTML & JSON export functionality.

### 🗓️ Phase 3: Advanced ML & Persistence (Weeks 5 - 6)
* Enhance ML capabilities and pipeline automation.
* Goals:
  - Implement PyOD Local Outlier Factor (LOF) and KNN anomaly detectors.
  - Add automated cleaning suggestions (imputation strategies, deduplication).
  - Add SQLite database persistence to track quality degradation over time.
  - Add CI/CD GitHub Action template for automated pull request data validation.

---

## 6. Pre-Curated Issue List for Contributors

Here are ready-to-publish GitHub issues for the program:

### 🟢 Beginner / Good First Issue (Level 1)
1. **[Docs]**: Create comprehensive API documentation and Swagger tutorial (`documentation`, `good-first-issue`)
2. **[Core]**: Add Parquet and JSON-lines file reader support to the ingestion engine (`backend`, `python`, `easy`)
3. **[Validator]**: Add built-in validators for IP address, UUID, and international phone formats (`python`, `validator`, `easy`)
4. **[Frontend]**: Add dark/light mode toggle with Tailwind theme persistence (`frontend`, `react`, `good-first-issue`)
5. **[CLI]**: Add `--quiet` and `--json-only` output flags to the `datasentry profile` command (`cli`, `python`, `easy`)

### 🔵 Intermediate (Level 2)
6. **[Frontend]**: Build correlation heatmap matrix using Recharts / SVG (`frontend`, `react`, `dataviz`)
7. **[ML Engine]**: Implement Z-score and modified IQR dynamic boundary outlier detection (`machine-learning`, `statistics`)
8. **[Backend]**: Implement SQLite persistence for storing run histories and quality metrics (`backend`, `fastapi`, `database`)
9. **[Reporting]**: Build responsive standalone HTML report template with Jinja2 (`reporting`, `fullstack`)
10. **[Validator]**: Implement conditional/cross-column validation rules (e.g., `if column A == X then column B cannot be null`) (`python`, `validator`)

### 🟣 Advanced (Level 3)
11. **[ML Engine]**: Integrate PyOD Local Outlier Factor (LOF) with auto-hyperparameter tuning (`machine-learning`, `pyod`)
12. **[Core]**: Implement Data Drift detection comparing a baseline dataset against a new batch via KS-tests (`machine-learning`, `data-drift`)
13. **[Frontend]**: Build dynamic No-Code Rule Builder with live validation preview (`frontend`, `react`, `typescript`)
14. **[DevOps]**: Create DataSentry GitHub Action to fail PRs if data quality score drops below threshold (`devops`, `ci-cd`)

---

## 7. Mentorship & Project Admin Commitment

* **Active Review SLA**: Pull requests reviewed within 24–48 hours with constructive code review and guidance.
* **Contributor Recognition**: Contributors will be featured in the project `README.md` and credited in release notes.
* **Weekly Sync / Office Hours**: Discord/Slack support for helping contributors troubleshoot git or environment setup issues.
