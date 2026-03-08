# Customer Engagement & Product Utilization Analytics for Retention Strategy

## 1. Project Objective Coverage
- Evaluate relationship between engagement and churn: completed using EngagementScore + tier-wise churn comparison.
- Measure retention impact of product count and product mix: completed using product-level churn and engagement-product interaction tables.
- Identify disengaged yet high-value customers: completed via HVD segment and silent premium churner segment.

## 2. Data Validation
- Records: 10,000
- Features: 14
- Missing values: 0
- Duplicate rows: 0
- Year range: 2025 to 2025

## 3. Core KPIs
- Overall churn rate: 20.37%
- Average engagement score: 5.28/9
- Active member ratio: 51.51%
- High-value disengaged customers: 1,247
- Silent premium churners: 371
- Avg products per customer: 1.53
- Low vs high engagement churn gap: 18.69 percentage points
- Product-mix churn gap (max-min): 92.42 percentage points

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
- Segment 1 (High-Value Disengaged): 1,247 customers (12.47%), churn = 30.47%.
- Segment 2 (Silent Premium Churners): 371 customers, avg salary = EUR 175,475.

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

