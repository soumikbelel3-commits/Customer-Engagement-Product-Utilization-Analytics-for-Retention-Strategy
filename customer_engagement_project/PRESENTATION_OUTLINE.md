# Customer Engagement & Product Utilization Analytics for Retention Strategy
## Presentation Deck Outline (10 Slides)

### Slide 1: Title
- Customer Engagement & Product Utilization Analytics for Retention Strategy
- Dataset: European_Bank.csv (10,000 customers, 14 core fields)
- Analyst: Rishi

Speaker notes:
- This project evaluates churn behavior using engagement and product usage signals.
- The goal is to translate analysis into retention actions that are measurable.

### Slide 2: Business Problem
- Banks often use generic retention messaging that ignores customer behavior patterns.
- Churn can be reduced by identifying: disengaged customers, poor product fit, and high-value risk groups.
- Core challenge: find who is most likely to churn and why.

Speaker notes:
- The focus is not only predicting churn, but identifying actionable segments.

### Slide 3: Objectives (From Requirement)
- Evaluate relationship between engagement and churn.
- Measure retention impact of product count and product mix.
- Identify disengaged yet high-value customers.
- Support strategy design for engagement-led retention.

Speaker notes:
- These directly map to the methodology and KPI framework used.

### Slide 4: Dataset & Data Validation
- Source rows: 10,000
- Source columns: 14
- Missing values: 0
- Duplicate rows: 0
- Data year: 2025
- Validation artifacts generated: nulls, uniqueness, outlier checks

Speaker notes:
- Data quality was strong, so modeling and segmentation did not require imputation.

### Slide 5: Methodology
- Step 1: Data quality validation.
- Step 2: Engagement scoring and tiering.
- Step 3: Product utilization and churn impact analysis.
- Step 4: Financial commitment analysis (balance/salary).
- Step 5: Retention score and retention tiers.
- Step 6: Risk segment extraction for targeted action.

Speaker notes:
- The approach is sequential and interpretable for business teams.

### Slide 6: Engagement Framework
- EngagementScore formula:
  - (IsActiveMember * 3)
  - + min(NumOfProducts, 3)
  - + HasCrCard
  - + min(floor(Tenure/2), 2)
- Engagement tiers:
  - Low: 0-3
  - Medium: 4-6
  - High: 7+

Key result:
- Low-tier churn is significantly higher than high-tier churn (18.69 pp gap).

Speaker notes:
- Engagement is a strong practical lever for retention interventions.

### Slide 7: Product Utilization Insights
- Product-level churn:
  - 1 product: 27.7%
  - 2 products: 7.6% (most stable)
  - 3 products: 82.7%
  - 4 products: 100.0% (very small cohort)
- Interpretation:
  - 2-product customers show strongest retention behavior.
  - 3-4 product cohorts indicate severe product fit/experience issues.

Speaker notes:
- Product count alone is not enough; quality of product mix matters.

### Slide 8: Retention and Risk Segments
- Overall churn rate: 20.37%
- Active members: 51.51%
- Avg products/customer: 1.53

Risk Segment 1: High-Value Disengaged
- Definition: top-25% balance + inactive
- Count: 1,247
- Churn: 30.47%

Risk Segment 2: Silent Premium Churners
- Definition: top-25% salary + <=1 product + exited
- Count: 371

Speaker notes:
- These segments are operationally actionable for CRM and relationship managers.

### Slide 9: Recommendations
- Launch 90-day low-engagement reactivation campaign.
- Move 1-product customers toward high-utility 2-product bundles.
- Build HVD (high-value disengaged) watchlist with proactive outreach triggers.
- Design premium retention journeys for high-salary low-product users.
- Track campaign impact monthly via churn and engagement lift KPIs.

Speaker notes:
- Prioritize HVD and low-engagement 1-product customers for immediate ROI.

### Slide 10: Implementation Plan & KPI Tracking
- Month 1: Segment activation + campaign design.
- Month 2: Pilot campaigns in top geographies.
- Month 3: Scale and optimize.

Success KPIs:
- Churn reduction in low-engagement tier.
- Increase in active-member percentage.
- Migration rate from 1 product to 2 products.
- HVD churn reduction.

Speaker notes:
- Governance: weekly KPI review and monthly strategy corrections.

## Appendix: Artifacts
- Analysis script: `run_analysis.py`
- Step-by-step: `STEP_BY_STEP.md`
- Final report: `output/16_final_report.md`
- Enriched data: `output/14_enriched_customer_data.csv`
- KPI JSON: `output/15_summary.json`
- Charts: `output/charts/*.png`
