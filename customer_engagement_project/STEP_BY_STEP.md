# Step-by-Step Execution Guide

## Step 1: Load data
- Source file: `C:\Users\Rishi\Downloads\European_Bank.csv`
- Shape: 10,000 rows x 14 columns

## Step 2: Validate data quality
- Nulls: 0
- Duplicates: 0
- Outlier report generated using IQR method.
- Output files:
  - `01_data_validation.csv`
  - `02_outlier_report.csv`

## Step 3: Build engagement classification
- Formula used:
  - `EngagementScore = (IsActiveMember*3) + min(NumOfProducts,3) + HasCrCard + min(floor(Tenure/2),2)`
- Tiering:
  - Low: `0-3`
  - Medium: `4-6`
  - High: `7+`
- Output files:
  - `03_engagement_summary.csv`
  - `04_active_inactive_by_engagement.csv`

## Step 4: Analyze product utilization vs churn
- Churn analyzed by `NumOfProducts`
- Credit card effect included
- Product x engagement interaction included
- Output files:
  - `05_product_summary.csv`
  - `06_credit_card_impact.csv`
  - `07_product_engagement_combo.csv`

## Step 5: Financial commitment analysis
- Balance segments:
  - `Zero Balance`, `1-50K`, `50K-100K`, `100K-150K`, `150K+`
- Salary quartiles and geography-gender splits analyzed
- Output files:
  - `08_balance_segment_analysis.csv`
  - `09_salary_quartile_analysis.csv`
  - `10_geo_gender_financials.csv`

## Step 6: Retention strength assessment
- Formula used:
  - `RetentionScore = 0.4*EngagementScore + 0.6*ProductIndex`
  - `ProductIndex = NumOfProducts`
- Tiering:
  - At Risk: `0-3`
  - Moderate: `3-5`
  - Stable: `5-7`
  - Loyal: `7+`
- Output files:
  - `11_retention_summary.csv`
  - `12_retention_by_age.csv`

## Step 7: Identify high-risk value segments
- Segment 1: High-value disengaged
  - `Balance >= top 25%` and `IsActiveMember = 0`
- Segment 2: Silent premium churners
  - `EstimatedSalary >= top 25%` and `NumOfProducts <= 1` and `Exited = 1`
- Output file:
  - `13_hvd_country_profile.csv`

## Step 8: Build dashboard-ready dataset and final report
- Enriched master data:
  - `14_enriched_customer_data.csv`
- KPI and segment summary:
  - `15_summary.json`
- Final written report:
  - `16_final_report.md`

## Step 9: Re-run project
```powershell
python G:\Codex\customer_engagement_project\run_analysis.py
```
