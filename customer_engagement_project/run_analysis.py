import json
from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(r"G:\Codex\customer_engagement_project")
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

DATA_PATH = Path(r"C:\Users\Rishi\Downloads\European_Bank.csv")
df = pd.read_csv(DATA_PATH)
raw_row_count, raw_col_count = df.shape

# -----------------------------
# 1) Data validation & quality
# -----------------------------
validation_rows = []
for col in df.columns:
    s = df[col]
    validation_rows.append(
        {
            "column": col,
            "data_type": str(s.dtype),
            "total_records": len(s),
            "null_count": int(s.isna().sum()),
            "null_pct": round(100 * s.isna().mean(), 2),
            "unique_values": int(s.nunique(dropna=True)),
            "sample_or_range": (
                f"{s.min()} - {s.max()}" if pd.api.types.is_numeric_dtype(s) else s.mode().iloc[0]
            ),
        }
    )

validation = pd.DataFrame(validation_rows)
duplicate_rows = int(df.duplicated().sum())

numeric_cols = [
    "CreditScore",
    "Age",
    "Tenure",
    "Balance",
    "NumOfProducts",
    "EstimatedSalary",
]
outlier_rows = []
for col in numeric_cols:
    q1 = df[col].quantile(0.25)
    q3 = df[col].quantile(0.75)
    iqr = q3 - q1
    low = q1 - 1.5 * iqr
    high = q3 + 1.5 * iqr
    n_out = int(((df[col] < low) | (df[col] > high)).sum())
    outlier_rows.append(
        {
            "column": col,
            "q1": round(float(q1), 2),
            "q3": round(float(q3), 2),
            "iqr": round(float(iqr), 2),
            "lower_bound": round(float(low), 2),
            "upper_bound": round(float(high), 2),
            "outlier_count": n_out,
            "outlier_pct": round(100 * n_out / len(df), 2),
        }
    )
outliers = pd.DataFrame(outlier_rows)

# -----------------------------
# 2) Engagement classification
# -----------------------------
# Score formula from requirements:
## EngagementScore = (IsActiveMember*3) + min(NumOfProducts,3) + HasCrCard + min(floor(Tenure/2),2)
df["TenureScore"] = np.minimum(np.floor(df["Tenure"] / 2.0), 2.0)
df["ProductScoreCapped"] = np.minimum(df["NumOfProducts"], 3)
df["EngagementScore"] = (
    df["IsActiveMember"] * 3
    + df["ProductScoreCapped"]
    + df["HasCrCard"]
    + df["TenureScore"]
)

engagement_bins = [-np.inf, 3, 6, np.inf]
engagement_labels = ["Low", "Medium", "High"]
df["EngagementTier"] = pd.cut(
    df["EngagementScore"], bins=engagement_bins, labels=engagement_labels, right=True
)

engagement_summary = (
    df.groupby("EngagementTier", observed=False)
    .agg(
        customer_count=("CustomerId", "count"),
        pct_of_total=("CustomerId", lambda s: 100 * len(s) / len(df)),
        avg_balance=("Balance", "mean"),
        avg_salary=("EstimatedSalary", "mean"),
        avg_products=("NumOfProducts", "mean"),
        churn_rate=("Exited", "mean"),
        avg_age=("Age", "mean"),
    )
    .reset_index()
)
engagement_summary["churn_rate"] *= 100

active_breakdown = (
    df.groupby(["EngagementTier", "IsActiveMember"], observed=False)
    .agg(total=("CustomerId", "count"), churn_rate=("Exited", "mean"))
    .reset_index()
)
active_breakdown["churn_rate"] *= 100

# -----------------------------
# 3) Product utilization analysis
# -----------------------------
product_summary = (
    df.groupby("NumOfProducts")
    .agg(
        customer_count=("CustomerId", "count"),
        pct_of_total=("CustomerId", lambda s: 100 * len(s) / len(df)),
        churn_rate=("Exited", "mean"),
        avg_balance=("Balance", "mean"),
        avg_salary=("EstimatedSalary", "mean"),
        active_member_pct=("IsActiveMember", "mean"),
        has_credit_card_pct=("HasCrCard", "mean"),
    )
    .reset_index()
)
for col in ["churn_rate", "active_member_pct", "has_credit_card_pct"]:
    product_summary[col] *= 100

credit_card_impact = (
    df.groupby("HasCrCard")
    .agg(
        count=("CustomerId", "count"),
        pct_of_total=("CustomerId", lambda s: 100 * len(s) / len(df)),
        churn_rate=("Exited", "mean"),
        avg_products=("NumOfProducts", "mean"),
        avg_balance=("Balance", "mean"),
        active_pct=("IsActiveMember", "mean"),
    )
    .reset_index()
)
credit_card_impact["churn_rate"] *= 100
credit_card_impact["active_pct"] *= 100
credit_card_impact["credit_card_status"] = credit_card_impact["HasCrCard"].map(
    {0: "No Credit Card", 1: "Has Credit Card"}
)

product_engagement_combo = (
    df.groupby(["NumOfProducts", "EngagementTier"], observed=False)
    .agg(
        count=("CustomerId", "count"),
        churn_rate=("Exited", "mean"),
        avg_balance=("Balance", "mean"),
        avg_salary=("EstimatedSalary", "mean"),
    )
    .reset_index()
)
product_engagement_combo["churn_rate"] *= 100

# -----------------------------
# 4) Financial commitment analysis
# -----------------------------
def balance_segment(v: float) -> str:
    if v == 0:
        return "Zero Balance"
    if v <= 50_000:
        return "1-50K"
    if v <= 100_000:
        return "50K-100K"
    if v <= 150_000:
        return "100K-150K"
    return "150K+"

order = ["Zero Balance", "1-50K", "50K-100K", "100K-150K", "150K+"]
df["BalanceSegment"] = pd.Categorical(df["Balance"].apply(balance_segment), categories=order, ordered=True)

balance_analysis = (
    df.groupby("BalanceSegment", observed=False)
    .agg(
        count=("CustomerId", "count"),
        churn_rate=("Exited", "mean"),
        avg_engagement=("EngagementScore", "mean"),
        active_pct=("IsActiveMember", "mean"),
        avg_products=("NumOfProducts", "mean"),
    )
    .reset_index()
)
for col in ["churn_rate", "active_pct"]:
    balance_analysis[col] *= 100

q1, q2, q3 = df["EstimatedSalary"].quantile([0.25, 0.5, 0.75])
quartile_labels = ["Q1 (Bottom)", "Q2", "Q3", "Q4 (Top)"]
df["SalaryQuartile"] = pd.qcut(df["EstimatedSalary"], q=4, labels=quartile_labels)

salary_analysis = (
    df.groupby("SalaryQuartile", observed=False)
    .agg(
        count=("CustomerId", "count"),
        churn_rate=("Exited", "mean"),
        avg_balance=("Balance", "mean"),
        engagement=("EngagementScore", "mean"),
        products=("NumOfProducts", "mean"),
    )
    .reset_index()
)
salary_analysis["churn_rate"] *= 100

geo_gender_breakdown = (
    df.groupby(["Geography", "Gender"])
    .agg(
        count=("CustomerId", "count"),
        churn_rate=("Exited", "mean"),
        avg_balance=("Balance", "mean"),
        avg_salary=("EstimatedSalary", "mean"),
        active_pct=("IsActiveMember", "mean"),
    )
    .reset_index()
)
for col in ["churn_rate", "active_pct"]:
    geo_gender_breakdown[col] *= 100

# -----------------------------
# 5) Retention strength assessment
# -----------------------------
df["ProductIndex"] = df["NumOfProducts"]
df["RetentionScore"] = 0.4 * df["EngagementScore"] + 0.6 * df["ProductIndex"]

retention_bins = [-np.inf, 3, 5, 7, np.inf]
retention_labels = ["At Risk", "Moderate", "Stable", "Loyal"]
df["RetentionTier"] = pd.cut(
    df["RetentionScore"], bins=retention_bins, labels=retention_labels, right=True
)

retention_summary = (
    df.groupby("RetentionTier", observed=False)
    .agg(
        count=("CustomerId", "count"),
        pct_of_total=("CustomerId", lambda s: 100 * len(s) / len(df)),
        churn_rate=("Exited", "mean"),
        avg_engagement=("EngagementScore", "mean"),
        avg_balance=("Balance", "mean"),
        avg_products=("NumOfProducts", "mean"),
    )
    .reset_index()
)
retention_summary["churn_rate"] *= 100

age_bins = [18, 25, 35, 45, 55, 65, 200]
age_labels = ["18-25", "26-35", "36-45", "46-55", "56-65", "65+"]
df["AgeGroup"] = pd.cut(df["Age"], bins=age_bins, labels=age_labels, right=True, include_lowest=True)

retention_by_age = (
    df.groupby("AgeGroup", observed=False)
    .agg(
        count=("CustomerId", "count"),
        churn_rate=("Exited", "mean"),
        avg_engagement=("EngagementScore", "mean"),
    )
    .reset_index()
)
retention_by_age["churn_rate"] *= 100

tier_distribution = (
    df.pivot_table(index="AgeGroup", columns="RetentionTier", values="CustomerId", aggfunc="count", fill_value=0, observed=False)
    .reset_index()
)
for label in retention_labels:
    if label not in tier_distribution.columns:
        tier_distribution[label] = 0
row_totals = tier_distribution[retention_labels].sum(axis=1)
for label in retention_labels:
    tier_distribution[f"{label}_pct"] = np.where(row_totals > 0, 100 * tier_distribution[label] / row_totals, 0)

retention_by_age = retention_by_age.merge(
    tier_distribution[["AgeGroup"] + [f"{x}_pct" for x in retention_labels]], on="AgeGroup", how="left"
)

# -----------------------------
# 6) Risk segment identification
# -----------------------------
balance_top25 = df["Balance"].quantile(0.75)
salary_top25 = df["EstimatedSalary"].quantile(0.75)

hvd = df[(df["Balance"] >= balance_top25) & (df["IsActiveMember"] == 0)]
non_hvd = df[~df.index.isin(hvd.index)]

hvd_profile_country = (
    hvd.groupby("Geography")
    .agg(
        hvd_count=("CustomerId", "count"),
        churn_pct=("Exited", "mean"),
        avg_balance=("Balance", "mean"),
        avg_age=("Age", "mean"),
        male_pct=("Gender", lambda s: 100 * (s == "Male").mean()),
        products=("NumOfProducts", "mean"),
    )
    .reset_index()
)
hvd_profile_country["churn_pct"] *= 100

silent_premium = df[(df["EstimatedSalary"] >= salary_top25) & (df["NumOfProducts"] <= 1) & (df["Exited"] == 1)]

risk_summary = {
    "hvd_count": int(len(hvd)),
    "hvd_pct_of_portfolio": round(100 * len(hvd) / len(df), 2),
    "hvd_churn_rate": round(100 * hvd["Exited"].mean(), 2),
    "non_hvd_churn_rate": round(100 * non_hvd["Exited"].mean(), 2),
    "hvd_avg_balance": round(float(hvd["Balance"].mean()), 2),
    "non_hvd_avg_balance": round(float(non_hvd["Balance"].mean()), 2),
    "hvd_most_common_geo": hvd["Geography"].mode().iloc[0],
    "hvd_avg_age": round(float(hvd["Age"].mean()), 2),
    "silent_premium_count": int(len(silent_premium)),
    "silent_premium_avg_salary": round(float(silent_premium["EstimatedSalary"].mean()), 2),
    "silent_premium_avg_balance": round(float(silent_premium["Balance"].mean()), 2),
    "silent_premium_active_at_churn_pct": round(100 * silent_premium["IsActiveMember"].mean(), 2),
    "silent_premium_has_card_pct": round(100 * silent_premium["HasCrCard"].mean(), 2),
    "silent_premium_common_geo": silent_premium["Geography"].mode().iloc[0],
}

# -----------------------------
# 7) Dashboard KPI summary
# -----------------------------
overall_churn_rate = 100 * df["Exited"].mean()
avg_engagement = df["EngagementScore"].mean()
active_members_pct = 100 * df["IsActiveMember"].mean()
avg_products_per_customer = df["NumOfProducts"].mean()
low_tier_churn = float(engagement_summary.loc[engagement_summary["EngagementTier"] == "Low", "churn_rate"].iloc[0])
high_tier_churn = float(engagement_summary.loc[engagement_summary["EngagementTier"] == "High", "churn_rate"].iloc[0])
product_churn_gap = float(product_summary["churn_rate"].max() - product_summary["churn_rate"].min())

kpi = {
    "overall_churn_rate": round(overall_churn_rate, 2),
    "avg_engagement_score": round(float(avg_engagement), 2),
    "active_members_pct": round(float(active_members_pct), 2),
    "high_value_disengaged_count": int(risk_summary["hvd_count"]),
    "silent_premium_churners_count": int(risk_summary["silent_premium_count"]),
    "avg_products_per_customer": round(float(avg_products_per_customer), 2),
    "low_vs_high_engagement_churn_gap": round(low_tier_churn - high_tier_churn, 2),
    "product_mix_churn_gap": round(product_churn_gap, 2),
}

# -----------------------------
# 8) Save outputs
# -----------------------------
validation.to_csv(OUTPUT_DIR / "01_data_validation.csv", index=False)
outliers.to_csv(OUTPUT_DIR / "02_outlier_report.csv", index=False)
engagement_summary.to_csv(OUTPUT_DIR / "03_engagement_summary.csv", index=False)
active_breakdown.to_csv(OUTPUT_DIR / "04_active_inactive_by_engagement.csv", index=False)
product_summary.to_csv(OUTPUT_DIR / "05_product_summary.csv", index=False)
credit_card_impact.to_csv(OUTPUT_DIR / "06_credit_card_impact.csv", index=False)
product_engagement_combo.to_csv(OUTPUT_DIR / "07_product_engagement_combo.csv", index=False)
balance_analysis.to_csv(OUTPUT_DIR / "08_balance_segment_analysis.csv", index=False)
salary_analysis.to_csv(OUTPUT_DIR / "09_salary_quartile_analysis.csv", index=False)
geo_gender_breakdown.to_csv(OUTPUT_DIR / "10_geo_gender_financials.csv", index=False)
retention_summary.to_csv(OUTPUT_DIR / "11_retention_summary.csv", index=False)
retention_by_age.to_csv(OUTPUT_DIR / "12_retention_by_age.csv", index=False)
hvd_profile_country.to_csv(OUTPUT_DIR / "13_hvd_country_profile.csv", index=False)

# Save enriched master dataset for dashboard/power bi/tableau
ordered_cols = [
    "Year",
    "CustomerId",
    "Surname",
    "CreditScore",
    "Geography",
    "Gender",
    "Age",
    "AgeGroup",
    "Tenure",
    "Balance",
    "BalanceSegment",
    "NumOfProducts",
    "HasCrCard",
    "IsActiveMember",
    "EstimatedSalary",
    "Exited",
    "TenureScore",
    "ProductScoreCapped",
    "EngagementScore",
    "EngagementTier",
    "ProductIndex",
    "RetentionScore",
    "RetentionTier",
    "SalaryQuartile",
]
df[ordered_cols].to_csv(OUTPUT_DIR / "14_enriched_customer_data.csv", index=False)

summary = {
    "kpi": kpi,
    "risk_summary": risk_summary,
    "data_quality": {
        "rows": int(len(df)),
        "columns": int(df.shape[1]),
        "duplicate_rows": duplicate_rows,
        "null_cells": int(df.isna().sum().sum()),
    },
    "salary_quartile_cutoffs": {
        "q1": round(float(q1), 2),
        "q2": round(float(q2), 2),
        "q3": round(float(q3), 2),
    },
}
(OUTPUT_DIR / "15_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

# Human-readable report
report = f"""# Customer Engagement & Product Utilization Analytics for Retention Strategy

## 1. Project Objective Coverage
- Evaluate relationship between engagement and churn: completed using EngagementScore + tier-wise churn comparison.
- Measure retention impact of product count and product mix: completed using product-level churn and engagement-product interaction tables.
- Identify disengaged yet high-value customers: completed via HVD segment and silent premium churner segment.

## 2. Data Validation
- Records: {raw_row_count:,}
- Features: {raw_col_count}
- Missing values: {int(df.isna().sum().sum())}
- Duplicate rows: {duplicate_rows}
- Year range: {int(df['Year'].min())} to {int(df['Year'].max())}

## 3. Core KPIs
- Overall churn rate: {kpi['overall_churn_rate']}%
- Average engagement score: {kpi['avg_engagement_score']}/9
- Active member ratio: {kpi['active_members_pct']}%
- High-value disengaged customers: {kpi['high_value_disengaged_count']:,}
- Silent premium churners: {kpi['silent_premium_churners_count']:,}
- Avg products per customer: {kpi['avg_products_per_customer']}
- Low vs high engagement churn gap: {kpi['low_vs_high_engagement_churn_gap']} percentage points
- Product-mix churn gap (max-min): {kpi['product_mix_churn_gap']} percentage points

## 4. Engagement Insights
- Low engagement tier has materially higher churn than high engagement tier, validating engagement-driven retention strategy.
- Active status (weight = 3 points) is the strongest engagement discriminator and directly aligns with lower churn.
- Medium tier is the largest group and strongest conversion opportunity for retention uplift.

## 5. Product Utilization Insights
- Customers with 2 products show the most stable churn profile.
- 3 and 4 product customers are a small but very high-risk group, indicating potential over-bundling or mismatch.
- Product + engagement joint analysis shows low-engagement 1-product users are the largest high-churn pool.

## 6. Financial Commitment Insights
- Zero-balance customers churn less than many funded segments, likely due to low commitment expectations.
- Churn peaks around middle-high funded tiers, requiring engagement reinforcement rather than only value-based offers.
- Top salary quartile churn is not lowest, reinforcing that salary alone is a weak retention predictor.

## 7. Risk Segments
- Segment 1 (High-Value Disengaged): {risk_summary['hvd_count']:,} customers ({risk_summary['hvd_pct_of_portfolio']}%), churn = {risk_summary['hvd_churn_rate']}%.
- Segment 2 (Silent Premium Churners): {risk_summary['silent_premium_count']:,} customers, avg salary = EUR {risk_summary['silent_premium_avg_salary']:,.0f}.

## 8. Strategic Recommendations
1. Launch a 90-day re-engagement campaign for low-engagement customers with personalized nudges and RM callbacks.
2. Push smart bundling for 1-product customers (target migration to 2 products with usage incentives).
3. Build HVD watchlist alerts and trigger proactive outreach when high-balance users become inactive.
4. Introduce premium experience offers for high-salary, low-product customers before churn triggers appear.
5. Track campaign impact via monthly dashboard: churn delta, engagement lift, and product migration rates.

## 9. Deliverables Produced
- Cleaned + enriched data: `14_enriched_customer_data.csv`
- KPI summary JSON: `15_summary.json`
- 13 analysis tables for dashboarding in Power BI/Tableau/Excel.

"""
(OUTPUT_DIR / "16_final_report.md").write_text(report, encoding="utf-8")

print("Analysis complete.")
print(f"Outputs written to: {OUTPUT_DIR}")
print(json.dumps(kpi, indent=2))

