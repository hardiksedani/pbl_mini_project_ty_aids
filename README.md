# Predicting the Impact of El Niño on Agricultural GDP using Panel Data Machine Learning

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![License: Academic](https://img.shields.io/badge/License-Academic%20PBL-orange.svg)]()

### Project-Based Learning (PBL) Capstone Project
- **Institution**: K. J. Somaiya Institute of Technology
- **Department**: Department of Artificial Intelligence and Data Science
- **Objective**: Develop an empirical, multi-model panel data machine learning system to estimate and simulate the macroeconomic impact of El Niño-Southern Oscillation (ENSO) climate shocks on Indian state-wise Agricultural Gross State Value Added (GSVA).

---

## 1. Academic Abstract & Economic Target

### Economic Target Definition
The dependent variable in this study is officially defined as:
> **Agricultural Gross State Value Added (GSVA) at Constant Prices (Base Year: 2011–12), measured in ₹ Crore.**

*Methodological Note on GVA vs GDP:*
In accordance with standard national accounting standards (System of National Accounts - SNA 2008) utilized by the Central Statistics Office (CSO) and Reserve Bank of India (RBI):
$$\text{Gross Domestic Product (GDP)} = \text{Gross Value Added (GVA at Basic Prices)} + \text{Product Taxes} - \text{Product Subsidies}$$
Because state-wise agricultural sectoral accounts are compiled at factor cost / basic prices, the precise target is **Agricultural GSVA**. In literature and non-technical discourse, this is conventionally termed *Agricultural GDP*. Our platform explicitly maintains this economic distinction for viva and presentation rigor.

---

## 2. Multi-Model Research Philosophy

Rather than presuming a single machine learning model (such as Random Forest) is superior a priori, this platform implements a rigorous **Five-Model Benchmark**:

| Model | Category | Academic Role |
| :--- | :--- | :--- |
| **Linear Regression (OLS)** | Econometric Baseline | Tests linear climate-elasticity hypothesis; benchmark for non-linear gains |
| **Random Forest Regressor** | Bagging Ensemble | Mitigates variance; models non-linear interactions across panel dimensions |
| **Gradient Boosting Regressor** | Sequential Boosting | Optimizes residual errors sequentially across climate anomaly thresholds |
| **XGBoost Regressor** | Regularized Boosting | Employs $L_1$/$L_2$ leaf regularization and second-order Taylor gradients |
| **Extra Trees Regressor** | Extremely Randomized Trees | Extreme randomization of cut points; robust against panel collinearity |

### Out-of-Sample Chronological Validation
To prevent temporal data leakage endemic to panel data, we enforce a strict **time-aware chronological split**:
- **In-Sample Training Period**: 2009–2019 (11 years)
- **Held-out Out-of-Sample Test Period**: 2020–2023 (4 years)

Selection Rule: The platform dynamically designates the **Best Model** based on the lowest **Root Mean Squared Error (RMSE)** and **Mean Absolute Error (MAE)** on the held-out test partition.

---

## 3. Real-World Data Provenance & Engineered Features

The dataset comprises a 15-year balanced panel (2009–2023) across 10 representative agricultural states of India (Maharashtra, Punjab, Uttar Pradesh, Madhya Pradesh, Rajasthan, Gujarat, Andhra Pradesh, Karnataka, Haryana, and West Bengal).

| Dimension | Source Provider | Measurement & Units | Coverage |
| :--- | :--- | :--- | :--- |
| **Oceanic Niño Index (ONI)** | NOAA Climate Prediction Center (CPC) | 3-month running mean ERSST.v5 SST anomalies in Niño 3.4 (°C) | Monthly, 2009–2023 |
| **Monsoon Precipitation** | Open-Meteo ERA5 Reanalysis Archive | Total annual & monsoon precipitation (mm) | Daily aggregated, 2009–2023 |
| **2-Meter Temperature** | Open-Meteo ERA5 Reanalysis Archive | Mean daily 2-meter air temperature (°C) | Daily aggregated, 2009–2023 |
| **Agricultural GSVA** | RBI Handbook of Statistics / MoSPI | Sectoral Agriculture & Allied GSVA at Constant 2011-12 Prices (₹ Cr) | Annual, 2009–2023 |

### Engineered Panel Features
- **Rainfall Anomaly ($A_{\text{rain}}$)**: $R_{i,t} - \bar{R}_i$ (deviation from state 15-year historical mean).
- **Temperature Anomaly ($A_{\text{temp}}$)**: $T_{i,t} - \bar{T}_i$ (thermal stress index).
- **Lagged ENSO Effects**: $ONI_{t-1}$ to capture delayed kharif-to-rabi macroeconomic propagation.

---

## 4. Platform Capabilities & Architecture

```
┌─────────────────────────────────────────────────────────────┐
│               Next.js 14 App Router (React)                 │
│  - Scenario Lab (/scenario)     - AI Search Assistant (/search) │
│  - Multi-Model Bench (/models)  - Methodology & Viva (/methodology)│
│  - State Profiles (/states/[s]) - Data & Export (/data)     │
└──────────────────────────────┬──────────────────────────────┘
                               │ JSON REST API
┌──────────────────────────────▼──────────────────────────────┐
│                    FastAPI Python Backend                   │
│  - Multi-Model Training & Evaluation (scikit-learn, XGBoost)│
│  - Scenario Simulation Engine (deviation, ensemble, attribution)│
│  - Two-Tier Grounded Search Service (intent router + citations)│
│  - CSV / JSON Panel & Metric Data Exporters                 │
└──────────────────────────────┬──────────────────────────────┘
                               │
       ┌───────────────────────┴───────────────────────┐
       ▼                                               ▼
┌─────────────────────────────┐         ┌─────────────────────────────┐
│  SQLite Local Database      │         │ Firebase Firestore + Storage│
│  (Zero-config out-of-the-   │   OR    │ (Production Cloud Storage;  │
│   box storage for local run)│         │  active when keys provided) │
└─────────────────────────────┘         └─────────────────────────────┘
```

### Key New Features
1. **El Niño Scenario Lab (`/scenario`)**: Interactive simulation workbench with 5 empirical presets (*Normal*, *Weak El Niño*, *Moderate El Niño*, *Strong El Niño*, *La Niña*) and real-time sliders with ensemble averaging.
2. **Two-Tier Grounded AI Search (`/search`)**: Zero-hallucination assistant classifying queries into *Factual*, *Historical*, *Prediction*, *Scenario*, or *Mixed* intents, returning exact metrics and verified citations (NOAA, IMD, RBI, MoSPI, DES).
3. **State Deep-Dive Profiles (`/states/[state]`)**: Granular climate-economy trajectories, climate vulnerability indices, and historical drought correlations.
4. **Academic Data & Metric Exporters**: Instant CSV and JSON downloads of the full cleaned panel and model evaluation benchmarks.

---

## 5. Quick Start & Execution Guide

### Step 1: Environment Setup

#### Backend Setup
```bash
# From repository root
cd backend
python -m venv venv

# Windows activate
.\venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

#### Frontend Setup
```bash
# In another terminal
cd frontend
npm install
```

---

### Step 2: Reproducible Pipeline Scripts

Execute the end-to-end data and modeling pipeline in sequence:

```bash
# 1. Download NOAA ONI & Open-Meteo ERA5 climate data (2009-2023)
python scripts/download_data.py

# 2. Clean panel, engineer anomaly features, and populate database
python scripts/preprocess_data.py

# 3. Train all 5 regression models with chronological time split
python scripts/train_models.py

# 4. Generate empirical evaluation and benchmarking report
python scripts/evaluate_models.py

# 5. Test interactive scenario prediction CLI
python scripts/run_prediction.py --state Maharashtra --preset "Moderate El Niño"

# 6. Run complete end-to-end automated verification suite
python scripts/test_system.py
```

---

### Step 3: Running the Application

```bash
# Terminal 1: Backend Server (FastAPI)
cd backend
.\venv\Scripts\activate
python -m uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend Server (Next.js)
cd frontend
npm run dev
```

Visit **`http://localhost:3000`** in your browser.

---

## 6. Project Directory Structure

```
pbl-agriculture-project/
├── backend/
│   ├── app/
│   │   ├── constants.py              # 5 Models, features, paths, citations
│   │   ├── main.py                   # FastAPI entrypoint & CORS
│   │   ├── models/schemas.py         # Pydantic v2 schemas
│   │   ├── routers/                  # Modular API routes (scenario, search, etc.)
│   │   └── services/
│   │       ├── db_storage.py         # Resilient Dual SQLite / Firebase adapter
│   │       ├── ml.py                 # 5 models, time-split, training & metrics
│   │       ├── scenario_service.py   # Simulation engine & economic attribution
│   │       └── search_service.py     # Two-tier search & citation synthesis
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── dashboard/                # Macro KPIs, charts, state table
│   │   ├── scenario/                 # Scenario Simulation Lab
│   │   ├── search/                   # AI Search & Knowledge Assistant
│   │   ├── methodology/              # Somaiya PBL Presentation & Data Dictionary
│   │   ├── models/                   # 5-Model Evaluation & Benchmark Table
│   │   ├── states/[state]/           # State-specific deep-dive profiles
│   │   └── data/                     # Panel Explorer & CSV/JSON Export
│   ├── components/                   # Recharts visualizations & Navigation
│   └── lib/api.ts                    # Strongly typed API client
├── data/
│   ├── raw/                          # Raw NOAA and Open-Meteo downloads
│   ├── processed/                    # Cleaned panel CSV & model evaluation JSON
│   ├── models/                       # Versioned .joblib ML model artifacts
│   ├── metadata/                     # sources_metadata.json with provenance
│   └── pbl_database.sqlite           # SQLite storage database
├── scripts/
│   ├── download_data.py              # Ingestion script
│   ├── preprocess_data.py            # Feature engineering script
│   ├── train_models.py               # 5-model training script
│   ├── evaluate_models.py            # Model benchmarking script
│   ├── run_prediction.py             # CLI scenario prediction utility
│   └── test_system.py                # Comprehensive test suite
└── README.md
```

---

## 7. Model Evaluation Results (Latest Empirical Run)

*Evaluated on out-of-sample held-out test data (Years: 2020–2023):*

| Model | MAE (₹ Cr) | RMSE (₹ Cr) | $R^2$ Score | MAPE (%) | Selected |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Linear Regression (OLS Baseline)** | 15.16 | 17.49 | 0.4058 | 14.0% | Baseline |
| **Random Forest Regressor** | 13.37 | 17.62 | 0.3969 | 12.6% | Non-Linear |
| **Gradient Boosting Regressor** | 13.74 | 18.33 | 0.3468 | 13.1% | Sequential |
| **XGBoost Regressor** | 14.02 | 19.03 | 0.2965 | 12.9% | Regularized |
| **Extra Trees Regressor** | **12.19** | **15.68** | **0.5224** | **11.2%** | **BEST PERFORMER** |

*Key Academic Finding:*
Extra Trees demonstrated the lowest RMSE (15.68) and highest out-of-sample $R^2$ (0.5224), indicating that extreme randomization of split thresholds mitigates multi-collinearity between rainfall anomalies and temperature deviations in Indian agricultural panel data.

---

## 8. Academic Viva Voce & Presentation Talking Points

When presenting this project to the evaluation committee:
1. **Explain the Target**: Clarify that state agricultural accounts compile **Agricultural GSVA** at constant 2011-12 prices, eliminating inflationary distortion.
2. **Justify Multi-Model Choice**: Emphasize that empirical data science tests multiple algorithmic inductive biases (OLS linearity vs. Tree ensembles vs. Gradient Boosting) on out-of-sample data rather than declaring one model without empirical proof.
3. **Address Data Leakage**: Explain why standard random K-Fold cross validation is invalid for panel data (it leaks future temporal shocks into past predictions), which is why we enforced a **chronological time-aware split** (2009–2019 train, 2020–2023 test).
4. **Explain Scenario Simulation**: Highlight how the scenario engine allows policymakers to test "what-if" monsoon deficits before sowing season begins.

---

## 9. Disclaimer
*This platform provides analytical estimates and simulation scenarios based on empirical panel machine learning models. It is designed for academic research, education, and policy decision support, and does not constitute an official government macroeconomic forecast.*
