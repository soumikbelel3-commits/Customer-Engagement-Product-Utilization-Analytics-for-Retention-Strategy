# 🏦 Customer Engagement & Product Utilization Analytics for Retention Strategy

> **The European Central Bank · Data Analytics Project · 2025**  
> A full-stack data analytics project examining customer churn through the lens of behavioral engagement, product utilization, and financial commitment — with actionable retention strategy recommendations.

---

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Dataset](#-dataset)
- [Project Structure](#-project-structure)
- [Analytical Methodology](#-analytical-methodology)
- [Key Findings](#-key-findings)
- [Deliverables](#-deliverables)
- [How to Run](#-how-to-run)
- [Dashboard Preview](#-dashboard-preview)
- [Tech Stack](#-tech-stack)
- [Strategic Recommendations](#-strategic-recommendations)
- [Author](#-author)

---

## 🎯 Project Overview

Banks recognize that customer behavior — not just demographics — determines long-term retention. Customers may appear financially stable (high balance, high salary) while remaining fundamentally disengaged, creating a hidden churn risk that standard retention strategies fail to address.

This project evaluates customer churn through three analytical lenses:

- **Engagement Classification** — scoring and tiering customers by behavioral depth
- **Product Utilization Analysis** — understanding how product mix drives or destroys loyalty  
- **Financial Commitment Assessment** — correlating balance and salary with churn risk

### Problem Statement
Despite having data on customer engagement and product usage, banks often lack:
- Quantified insight into which behaviors drive retention
- Clarity on which product mixes reduce churn
- Evidence on whether high balances alone ensure loyalty

### Objectives

| Primary | Secondary |
|---------|-----------|
| Evaluate the relationship between engagement and churn | Support engagement-driven retention strategies |
| Measure retention impact of product count and product mix | Improve product bundling decisions |
| Identify disengaged yet high-value customers | Reduce silent churn among premium customers |

---

## 📊 Dataset

**Source:** The European Central Bank  
**Records:** 10,000 customers · **Year:** 2025 · **Target Variable:** `Exited` (churn indicator)

| Column | Type | Description |
|--------|------|-------------|
| `CustomerId` | Integer | Unique customer identifier |
| `Surname` | String | Customer surname |
| `CreditScore` | Integer | Creditworthiness score (350–850) |
| `Geography` | String | France / Spain / Germany |
| `Gender` | String | Male / Female |
| `Age` | Integer | Customer age in years |
| `Tenure` | Integer | Years with the bank (0–10) |
| `Balance` | Float | Account balance in Euros |
| `NumOfProducts` | Integer | Number of bank products held (1–4) |
| `HasCrCard` | Binary | Credit card ownership (1 = Yes) |
| `IsActiveMember` | Binary | Active membership status (1 = Active) |
| `EstimatedSalary` | Float | Annual estimated salary in Euros |
| `Exited` | Binary | **TARGET** — Churn indicator (1 = Churned) |

> **Data Quality:** Zero null values across all 14 columns. No duplicates. Production-ready without imputation.

---

## 📁 Project Structure

```
├── European_Bank.csv              # Raw dataset
│
├── streamlit_app.py               # 🚀 Interactive Streamlit dashboard
│
├── Research_Paper.docx            # 📄 Full EDA research paper (8 sections)
├── Executive_Summary.docx         # 📋 Government stakeholder summary
├── European_Bank_Analysis.xlsx    # 📊 9-sheet Excel analytics workbook
│
└── README.md                      # This file
```

---

## 🔬 Analytical Methodology

### 1. Engagement Scoring Framework

A composite **Engagement Score (0–9)** was engineered from behavioral features:

```
Engagement Score = (IsActiveMember × 3)
                 + min(NumOfProducts, 3)
                 + HasCrCard
                 + min(Tenure ÷ 2, 2)
```

| Tier | Score Range | Interpretation |
|------|-------------|----------------|
| 🔴 Low | 0 – 3 | Disengaged, high churn risk |
| 🟡 Medium | 4 – 6 | Moderate engagement |
| 🟢 High | 7 – 9 | Deeply engaged, loyal |

### 2. Retention Strength Index

```
Retention Strength = (Engagement Score × 0.4) + (Product Index × 0.6)
Product Index      = NumOfProducts + (HasCrCard × 0.5)
```

Customers are classified into: **At Risk → Moderate → Stable → Loyal**

### 3. Risk Segment Identification

**High-Value Disengaged (HVD)**
```python
HVD = (Balance > 75th percentile) AND (IsActiveMember == 0)
```

**Silent Premium Churners (SPC)**
```python
SPC = (EstimatedSalary > 75th percentile) AND (NumOfProducts <= 1) AND (Exited == 1)
```

---

## 🔍 Key Findings

### Portfolio Summary

| KPI | Value |
|-----|-------|
| Overall Churn Rate | **20.4%** |
| Active Members | **51.5%** |
| Average Engagement Score | **5.38 / 9.0** |
| High-Value Disengaged Customers | **1,247** |
| Silent Premium Churners | **371** |
| At-Risk Customers (Retention Tier) | **3,701** |

### Finding 1 — Engagement is the Primary Retention Driver

| Tier | Churn Rate |
|------|-----------|
| 🔴 Low Engagement | 30.95% |
| 🟡 Medium Engagement | 22.01% |
| 🟢 High Engagement | 12.27% |

> High-engagement customers churn at **less than half the rate** of low-engagement customers.

### Finding 2 — Product Count Has a Non-Linear Churn Effect

| Products | Churn Rate | Risk |
|----------|-----------|------|
| 1 | 27.71% | Medium |
| 2 | **7.58%** | ✅ Lowest |
| 3 | 82.71% | 🚨 Critical |
| 4 | 100.00% | 🚨 Critical |

> Moving a customer from **1 → 2 products** is the single most powerful retention lever in the portfolio.

### Finding 3 — Germany is a Structural Risk

| Country | Customers | Churn Rate | Avg Balance |
|---------|-----------|-----------|-------------|
| France | 5,014 | 16.15% | €62,091 |
| Germany | 2,509 | **32.44%** | €119,730 |
| Spain | 2,477 | 16.67% | €61,803 |

> Germany's churn rate is **double** other markets — despite holding the highest average balances.

### Finding 4 — Age 46–55 is the Peak Churn Cohort

The 46–55 age bracket shows a **50.57% churn rate** — the highest of any age group — indicating unmet complex financial needs (pensions, mortgages, investment planning).

### Finding 5 — High-Value Disengaged Customers

**1,247 customers** with top-quartile balances (above €127,644) are completely inactive.  
Churn rate: **30.47%** vs 18.93% for standard customers.  
Estimated balance-flight risk if unaddressed: **€47M+**

---

## 📦 Deliverables

### 1. 📊 Interactive Streamlit Dashboard (`streamlit_app.py`)
Live analytics platform with 6 interactive tabs:

| Tab | Content |
|-----|---------|
| 📊 Overview | Churn distribution, geography, age group, heatmaps |
| 👥 Engagement | Tier analysis, active vs inactive, score distributions |
| 📦 Products | Product-churn relationship, credit card impact, combo analysis |
| 💰 Financial | Balance segments, salary quartiles, retention tier by balance |
| ⚠️ Risk Segments | HVD & SPC profiles, retention scatter plots |
| 📝 Recommendations | 6 prioritized actions + impact projections |

Full sidebar filters: Geography · Gender · Age Range · Engagement Tier · Member Status

### 2. 📄 Research Paper (`Research_Paper.docx`)
Full academic-style EDA document covering:
- Executive Abstract
- Background & Context
- Dataset Description & Validation
- Analytical Methodology
- 7-section EDA Findings
- Strategic Recommendations
- KPI Summary Table

### 3. 📋 Executive Summary (`Executive_Summary.docx`)
Government-stakeholder-ready brief with:
- Situation overview with KPI dashboard
- 3 critical findings in plain language
- 5 prioritized recommendations with investment case
- Financial impact projection (€38M+ balance preservation scenario)

### 4. 📈 Excel Analytics Workbook (`European_Bank_Analysis.xlsx`)
9-sheet professional workbook:

| Sheet | Content |
|-------|---------|
| 📋 Cover | KPIs + workbook index |
| 🔍 Data Validation | Quality audit + descriptive statistics |
| 👥 Engagement | Tier classification + methodology |
| 📦 Product Analysis | Utilization + combo matrix |
| 💰 Financial Commit | Balance/salary segments + geography breakdown |
| 🛡️ Retention | Strength tiers + age group profiles |
| ⚠️ Risk Segments | HVD & SPC full profiles |
| 📊 Dashboard | 10 embedded charts |
| 📝 Recommendations | 7 strategic recommendations |

---

## 🚀 How to Run

### Prerequisites

```bash
pip install streamlit plotly pandas numpy openpyxl
```

### Run the Streamlit Dashboard

```bash
# Place streamlit_app.py and European_Bank.csv in the same directory
streamlit run streamlit_app.py
```

The dashboard opens at `http://localhost:8501`

### Run Analysis in Python

```python
import pandas as pd
import numpy as np

df = pd.read_csv('European_Bank.csv')

# Engagement Score
def engagement_score(row):
    return (row['IsActiveMember'] * 3
            + min(row['NumOfProducts'], 3)
            + row['HasCrCard']
            + min(row['Tenure'] / 2, 2))

df['EngagementScore'] = df.apply(engagement_score, axis=1)
df['EngagementTier']  = df['EngagementScore'].apply(
    lambda s: 'High' if s >= 7 else ('Medium' if s >= 4 else 'Low')
)

# High-Value Disengaged
df['HighValueDisengaged'] = (
    (df['Balance'] > df['Balance'].quantile(0.75)) &
    (df['IsActiveMember'] == 0)
).astype(int)

print(f"Churn Rate: {df['Exited'].mean()*100:.1f}%")
print(f"HVD Count:  {df['HighValueDisengaged'].sum()}")
```

---

## 🖥️ Dashboard Preview

```
┌─────────────────────────────────────────────────────────────────┐
│  🏦 Customer Engagement & Product Utilization Analytics         │
│  The European Central Bank · Retention Strategy Platform        │
├───────────┬──────────┬───────────┬──────────┬──────────┬───────┤
│  20.4%    │  51.5%   │  5.38     │  1,247   │  371     │ 1.53  │
│  Churn    │  Active  │  Eng Score│  HV Disg │ Silent   │ Prods │
├───────────┴──────────┴───────────┴──────────┴──────────┴───────┤
│  [Overview] [Engagement] [Products] [Financial] [Risk] [Recs]  │
│                                                                  │
│  Sidebar Filters: Geography · Gender · Age · Tier · Status      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| **Python 3** | Core analysis and feature engineering |
| **Pandas / NumPy** | Data manipulation and statistical analysis |
| **Streamlit** | Interactive web dashboard |
| **Plotly** | Interactive charts and visualizations |
| **Matplotlib / Seaborn** | Static chart generation for Excel |
| **OpenPyXL** | Excel workbook generation |
| **docx (Node.js)** | Word document generation |

---

## 💡 Strategic Recommendations

| # | Initiative | Priority | Expected Impact |
|---|-----------|----------|-----------------|
| 1 | Re-engage High-Value Disengaged segment | 🚨 CRITICAL | Prevent €47M+ balance outflow |
| 2 | Silent Premium Churn prevention programme | 🚨 CRITICAL | Recover 371 premium accounts |
| 3 | Germany market investigation & fix | 🔴 HIGH | Halve Germany's churn rate |
| 4 | Portfolio activation drive | 🔴 HIGH | Convert 4,855 inactive → active |
| 5 | 1→2 product bundling strategy | 🔴 HIGH | Reduce churn by ~20pp per customer |
| 6 | Mid-life financial planning (46–55) | 🟡 MEDIUM | Address peak-churn cohort |
| 7 | Gender-differentiated retention offers | 🟡 MEDIUM | Close 8.6pp gender churn gap |

> A 5 percentage point reduction in portfolio churn would retain ~500 additional customers annually — preserving approximately **€38.2 million in deposits**.

---

## 👤 Author

**Senior Data Analytics Division**  
The European Central Bank · 2025  

> *"The path to retention excellence in European banking runs through behavioural engagement, not product complexity."*

---

## 📄 License

This project is for academic and analytical purposes. Dataset sourced from The European Central Bank public analytics programme.

---

<div align="center">
  <sub>Built with Python · Streamlit · Plotly · OpenPyXL · docx.js</sub>
</div>
