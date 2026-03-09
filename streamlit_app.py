import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bank Retention Analytics",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background-color: #F7F9FC; }

    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 20px 24px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #1F3B73;
        margin-bottom: 12px;
    }
    .metric-card.red   { border-left-color: #C0392B; }
    .metric-card.teal  { border-left-color: #0D8C8C; }
    .metric-card.orange{ border-left-color: #E8580A; }
    .metric-card.gold  { border-left-color: #D4AC0D; }

    .metric-val {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1F3B73;
        line-height: 1;
    }
    .metric-val.red    { color: #C0392B; }
    .metric-val.teal   { color: #0D8C8C; }
    .metric-val.orange { color: #E8580A; }
    .metric-val.gold   { color: #D4AC0D; }
    .metric-label { font-size: 0.78rem; color: #6B7280; margin-top: 4px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }

    .section-header {
        background: linear-gradient(135deg, #1F3B73 0%, #2E5FA3 100%);
        color: white;
        padding: 14px 20px;
        border-radius: 10px;
        font-size: 1.1rem;
        font-weight: 600;
        margin: 20px 0 14px 0;
        letter-spacing: 0.02em;
    }
    .risk-badge-critical { background: #FDECEA; color: #C0392B; padding: 3px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 700; }
    .risk-badge-high     { background: #FEF3E2; color: #E8580A; padding: 3px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 700; }
    .risk-badge-medium   { background: #EBF5FB; color: #2E5FA3; padding: 3px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 700; }

    .insight-box {
        background: #EBF5FB;
        border: 1px solid #AED6F1;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 8px 0;
        font-size: 0.85rem;
        color: #1A3A5C;
    }
    div[data-testid="stSidebar"] { background: #1F3B73; }
    div[data-testid="stSidebar"] * { color: white !important; }
    div[data-testid="stSidebar"] .stSelectbox > div { background: #2E5FA3; border: none; }
    div[data-testid="stSidebar"] h1, 
    div[data-testid="stSidebar"] h2,
    div[data-testid="stSidebar"] h3 { color: white !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 4px; background: #F0F4FF; padding: 4px; border-radius: 8px; }
    .stTabs [data-baseweb="tab"] { border-radius: 6px; padding: 8px 20px; font-weight: 500; }
    .stTabs [aria-selected="true"] { background: #1F3B73; color: white; }
</style>
""", unsafe_allow_html=True)

# ─── DATA LOAD & FEATURE ENGINEERING ─────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv('European_Bank.csv')

    def eng_score(row):
        return row['IsActiveMember'] * 3 + min(row['NumOfProducts'], 3) + (1 if row['HasCrCard'] else 0) + min(row['Tenure'] / 2, 2)

    df['EngagementScore'] = df.apply(eng_score, axis=1)
    df['EngagementTier']  = df['EngagementScore'].apply(lambda s: 'High' if s >= 7 else ('Medium' if s >= 4 else 'Low'))
    df['ProductIndex']    = df['NumOfProducts'] + df['HasCrCard'] * 0.5
    df['RetentionStrength'] = df['EngagementScore'] * 0.4 + df['ProductIndex'] * 0.6
    df['RetentionTier']   = pd.cut(df['RetentionStrength'], bins=[0,3,5,7,99], labels=['At Risk','Moderate','Stable','Loyal'])
    df['HighValueDisengaged'] = ((df['Balance'] > df['Balance'].quantile(0.75)) & (df['IsActiveMember'] == 0)).astype(int)
    df['SilentPremiumChurn']  = ((df['EstimatedSalary'] > df['EstimatedSalary'].quantile(0.75)) & (df['NumOfProducts'] <= 1) & (df['Exited'] == 1)).astype(int)
    df['BalanceBand'] = pd.cut(df['Balance'], bins=[-1,1,50000,100000,150000,999999], labels=['Zero','1–50K','50–100K','100–150K','150K+'])
    df['AgeGroup']    = pd.cut(df['Age'], bins=[17,25,35,45,55,65,100], labels=['18–25','26–35','36–45','46–55','56–65','65+'])
    df['ChurnLabel']  = df['Exited'].map({0:'Retained', 1:'Churned'})
    return df

df = load_data()

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏦 Bank Retention Analytics")
    st.markdown("**European Central Bank | 2025**")
    st.markdown("---")
    st.markdown("### Filters")

    geo_filter = st.multiselect("Geography", df['Geography'].unique().tolist(), default=df['Geography'].unique().tolist())
    gender_filter = st.multiselect("Gender", df['Gender'].unique().tolist(), default=df['Gender'].unique().tolist())
    eng_filter = st.multiselect("Engagement Tier", ['Low','Medium','High'], default=['Low','Medium','High'])
    age_range = st.slider("Age Range", int(df['Age'].min()), int(df['Age'].max()), (18, 92))
    active_filter = st.radio("Member Status", ["All", "Active Only", "Inactive Only"])

    st.markdown("---")
    st.markdown("### About")
    st.markdown("Customer engagement & retention analytics dashboard for strategic decision-making.")

# Apply filters
dff = df[
    (df['Geography'].isin(geo_filter)) &
    (df['Gender'].isin(gender_filter)) &
    (df['EngagementTier'].isin(eng_filter)) &
    (df['Age'] >= age_range[0]) & (df['Age'] <= age_range[1])
]
if active_filter == "Active Only":
    dff = dff[dff['IsActiveMember'] == 1]
elif active_filter == "Inactive Only":
    dff = dff[dff['IsActiveMember'] == 0]

# ─── COLORS ──────────────────────────────────────────────────────────────────
BLUE   = '#1F3B73'
MBLU   = '#2E5FA3'
TEAL   = '#0D8C8C'
ORANGE = '#E8580A'
RED    = '#C0392B'
GREEN  = '#1E8449'
GOLD   = '#D4AC0D'
LGRAY  = '#F2F2F2'

CHART_TEMPLATE = dict(
    plot_bgcolor='white',
    paper_bgcolor='white',
    font_family='Inter',
    title_font_color=BLUE,
    title_font_size=14,
    margin=dict(l=20, r=20, t=50, b=20),
)

# ─── HEADER ──────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="background: linear-gradient(135deg, #1F3B73 0%, #2E5FA3 100%); 
     padding: 24px 32px; border-radius: 14px; margin-bottom: 24px; color: white;">
  <h1 style="margin:0; font-size: 1.8rem; font-weight: 700;">
    🏦 Customer Engagement & Product Utilization Analytics
  </h1>
  <p style="margin: 6px 0 0 0; opacity: 0.85; font-size: 0.95rem;">
    The European Central Bank  ·  Retention Strategy Platform  ·  Dataset: {len(dff):,} customers shown
  </p>
</div>
""", unsafe_allow_html=True)

# ─── KPI ROW ─────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5, k6 = st.columns(6)

kpis = [
    (k1, f"{dff['Exited'].mean()*100:.1f}%", "Churn Rate", "red"),
    (k2, f"{dff['IsActiveMember'].mean()*100:.1f}%", "Active Members", "teal"),
    (k3, f"{dff['EngagementScore'].mean():.2f}", "Avg Engagement", "blue"),
    (k4, f"{dff['HighValueDisengaged'].sum():,}", "HV Disengaged", "orange"),
    (k5, f"{dff['SilentPremiumChurn'].sum():,}", "Silent Churners", "gold"),
    (k6, f"{dff['NumOfProducts'].mean():.2f}", "Avg Products", "blue"),
]

for col, val, label, style in kpis:
    with col:
        st.markdown(f"""
        <div class="metric-card {style}">
            <div class="metric-val {style}">{val}</div>
            <div class="metric-label">{label}</div>
        </div>""", unsafe_allow_html=True)

# ─── TABS ────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Overview", "👥 Engagement", "📦 Products", "💰 Financial", "⚠️ Risk Segments", "📝 Recommendations"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1: OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-header">Portfolio Overview & Churn Distribution</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        # Churn donut
        churn_counts = dff['ChurnLabel'].value_counts()
        fig = go.Figure(go.Pie(
            labels=churn_counts.index, values=churn_counts.values,
            hole=0.55, marker_colors=[GREEN, RED],
            textinfo='label+percent', textfont_size=13,
            pull=[0, 0.05]
        ))
        fig.update_layout(title_text='Overall Churn Distribution', **CHART_TEMPLATE,
                          showlegend=False, height=320)
        fig.add_annotation(text=f"<b>{dff['Exited'].mean()*100:.1f}%</b><br>Churned",
                           x=0.5, y=0.5, showarrow=False, font_size=16, font_color=RED)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        # Churn by Geography
        geo_churn = dff.groupby('Geography')['Exited'].mean().reset_index()
        geo_churn['Churn%'] = geo_churn['Exited'] * 100
        fig2 = px.bar(geo_churn, x='Geography', y='Churn%',
                      color='Churn%', color_continuous_scale=['#2ECC71','#F39C12','#C0392B'],
                      text=geo_churn['Churn%'].apply(lambda x: f'{x:.1f}%'))
        fig2.update_traces(textposition='outside', marker_line_width=0)
        fig2.update_layout(title_text='Churn Rate by Geography', **CHART_TEMPLATE,
                           coloraxis_showscale=False, height=320,
                           yaxis_title='Churn Rate (%)', xaxis_title='')
        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2)

    with c3:
        # Age group churn
        age_churn = dff.groupby('AgeGroup', observed=True)['Exited'].mean().reset_index()
        age_churn['Churn%'] = age_churn['Exited'] * 100
        fig3 = px.line(age_churn, x='AgeGroup', y='Churn%', markers=True,
                       color_discrete_sequence=[BLUE])
        fig3.add_scatter(x=age_churn['AgeGroup'], y=age_churn['Churn%'],
                         fill='tozeroy', fillcolor='rgba(31,59,115,0.1)', showlegend=False, line_color=BLUE)
        fig3.update_traces(marker=dict(size=10, color=ORANGE))
        fig3.update_layout(title_text='Churn Rate by Age Group', **CHART_TEMPLATE,
                           height=300, yaxis_title='Churn Rate (%)', xaxis_title='Age Group')
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        # Gender x Geography heatmap
        pivot = dff.pivot_table(values='Exited', index='Geography', columns='Gender', aggfunc='mean') * 100
        fig4 = px.imshow(pivot, color_continuous_scale='RdYlGn_r', text_auto='.1f',
                         aspect='auto', zmin=10, zmax=40)
        fig4.update_layout(title_text='Churn Heatmap: Geography × Gender', **CHART_TEMPLATE, height=300)
        st.plotly_chart(fig4, use_container_width=True)

    # Insight box
    peak_age = dff.groupby('AgeGroup', observed=True)['Exited'].mean().idxmax()
    st.markdown(f"""
    <div class="insight-box">
    💡 <b>Key Insight:</b> Germany's churn rate ({dff[dff['Geography']=='Germany']['Exited'].mean()*100:.1f}%) 
    is double France's ({dff[dff['Geography']=='France']['Exited'].mean()*100:.1f}%) despite holding the highest average balances. 
    The {peak_age} age group shows peak churn at {dff.groupby('AgeGroup', observed=True)['Exited'].mean().max()*100:.1f}%.
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2: ENGAGEMENT
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-header">Customer Engagement Classification Analysis</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        # Engagement tier distribution
        tier_dist = dff['EngagementTier'].value_counts().reindex(['Low','Medium','High'])
        fig = px.bar(x=tier_dist.index, y=tier_dist.values,
                     color=tier_dist.index,
                     color_discrete_map={'Low': RED, 'Medium': ORANGE, 'High': GREEN},
                     text=tier_dist.values)
        fig.update_traces(textposition='outside', marker_line_width=0)
        fig.update_layout(title_text='Customers by Engagement Tier', **CHART_TEMPLATE,
                          height=300, showlegend=False, yaxis_title='Count', xaxis_title='')
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        # Churn by tier
        tier_churn = dff.groupby('EngagementTier', observed=True)['Exited'].mean().reindex(['Low','Medium','High']) * 100
        fig2 = px.bar(x=tier_churn.index, y=tier_churn.values,
                      color=tier_churn.index,
                      color_discrete_map={'Low': RED, 'Medium': ORANGE, 'High': GREEN},
                      text=tier_churn.values.round(1))
        fig2.update_traces(texttemplate='%{text:.1f}%', textposition='outside', marker_line_width=0)
        fig2.update_layout(title_text='Churn Rate by Engagement Tier', **CHART_TEMPLATE,
                           height=300, showlegend=False, yaxis_title='Churn Rate (%)', xaxis_title='')
        st.plotly_chart(fig2, use_container_width=True)

    with c3:
        # Active vs Inactive
        active_data = dff.groupby('IsActiveMember')['Exited'].mean().reset_index()
        active_data['Label'] = active_data['IsActiveMember'].map({0: 'Inactive', 1: 'Active'})
        active_data['Churn%'] = active_data['Exited'] * 100
        fig3 = px.bar(active_data, x='Label', y='Churn%',
                      color='Label', color_discrete_map={'Active': TEAL, 'Inactive': RED},
                      text=active_data['Churn%'].apply(lambda x: f'{x:.1f}%'))
        fig3.update_traces(textposition='outside', marker_line_width=0)
        fig3.update_layout(title_text='Churn: Active vs Inactive', **CHART_TEMPLATE,
                           height=300, showlegend=False, yaxis_title='Churn Rate (%)', xaxis_title='')
        st.plotly_chart(fig3, use_container_width=True)

    # Engagement Score Distribution
    st.markdown('<div class="section-header">Engagement Score Distribution</div>', unsafe_allow_html=True)
    c4, c5 = st.columns([2,1])

    with c4:
        fig4 = px.histogram(dff, x='EngagementScore', color='ChurnLabel',
                            color_discrete_map={'Retained': GREEN, 'Churned': RED},
                            barmode='overlay', nbins=20, opacity=0.75)
        fig4.update_layout(title_text='Engagement Score Distribution by Churn Status', **CHART_TEMPLATE,
                           height=320, xaxis_title='Engagement Score', yaxis_title='Count',
                           legend_title='Status')
        st.plotly_chart(fig4, use_container_width=True)

    with c5:
        st.markdown("#### Engagement Tier Summary")
        for tier, color in [('Low', '#FDECEA'), ('Medium', '#FEF3E2'), ('High', '#EAFAF1')]:
            sub = dff[dff['EngagementTier'] == tier]
            if len(sub) == 0:
                continue
            st.markdown(f"""
            <div style="background:{color}; border-radius:8px; padding:12px 16px; margin:6px 0;">
                <b style="font-size:1rem;">{tier} Engagement</b><br>
                <span style="font-size:0.8rem;">
                {len(sub):,} customers &nbsp;|&nbsp; 
                Churn: <b>{sub['Exited'].mean()*100:.1f}%</b><br>
                Avg Balance: €{sub['Balance'].mean():,.0f} &nbsp;|&nbsp; 
                Avg Products: {sub['NumOfProducts'].mean():.1f}
                </span>
            </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3: PRODUCTS
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header">Product Utilization & Churn Impact</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        prod_churn = dff.groupby('NumOfProducts')['Exited'].agg(['mean','count']).reset_index()
        prod_churn['Churn%'] = prod_churn['mean'] * 100
        colors = [ORANGE, GREEN, RED, RED]
        fig = go.Figure()
        fig.add_bar(x=prod_churn['NumOfProducts'].astype(str),
                    y=prod_churn['Churn%'],
                    marker_color=colors[:len(prod_churn)],
                    text=prod_churn['Churn%'].apply(lambda x: f'{x:.1f}%'),
                    textposition='outside')
        fig.update_layout(title_text='Churn Rate by Number of Products', **CHART_TEMPLATE,
                          height=340, xaxis_title='Number of Products', yaxis_title='Churn Rate (%)')
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        # Product count distribution
        prod_dist = dff['NumOfProducts'].value_counts().sort_index()
        fig2 = px.pie(values=prod_dist.values, names=[f'{i} Product(s)' for i in prod_dist.index],
                      color_discrete_sequence=[BLUE, TEAL, ORANGE, RED])
        fig2.update_layout(title_text='Product Distribution', **CHART_TEMPLATE, height=340)
        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2)

    with c3:
        # Product x Engagement bubble
        combo = dff.groupby(['NumOfProducts','EngagementTier'], observed=True).agg(
            Count=('Exited','count'), Churn=('Exited','mean')).reset_index()
        combo['Churn%'] = combo['Churn'] * 100
        fig3 = px.scatter(combo, x='NumOfProducts', y='Churn%', size='Count', color='EngagementTier',
                          color_discrete_map={'Low': RED, 'Medium': ORANGE, 'High': GREEN},
                          size_max=50, hover_data=['Count'])
        fig3.update_layout(title_text='Churn: Products × Engagement (bubble = count)', **CHART_TEMPLATE, height=320)
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        # Credit card impact
        cc_churn = dff.groupby('HasCrCard')['Exited'].mean().reset_index()
        cc_churn['Label'] = cc_churn['HasCrCard'].map({0:'No Credit Card', 1:'Has Credit Card'})
        cc_churn['Churn%'] = cc_churn['Exited'] * 100
        fig4 = px.bar(cc_churn, x='Label', y='Churn%',
                      color='Label', color_discrete_map={'No Credit Card': ORANGE, 'Has Credit Card': TEAL},
                      text=cc_churn['Churn%'].apply(lambda x: f'{x:.1f}%'))
        fig4.update_traces(textposition='outside', marker_line_width=0)
        fig4.update_layout(title_text='Churn: Credit Card Ownership', **CHART_TEMPLATE,
                           height=320, showlegend=False, xaxis_title='', yaxis_title='Churn Rate (%)')
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown(f"""<div class="insight-box">
    💡 <b>Critical Finding:</b> Moving a customer from 1 to 2 products reduces churn from 
    {dff[dff['NumOfProducts']==1]['Exited'].mean()*100:.1f}% to {dff[dff['NumOfProducts']==2]['Exited'].mean()*100:.1f}% 
    — this single action is the most powerful retention lever in the portfolio. Conversely, customers with 3+ products 
    show abnormally high churn, suggesting over-selling without genuine engagement.
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4: FINANCIAL
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header">Financial Commitment & Balance Analysis</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        # Balance distribution
        fig = px.histogram(dff, x='Balance', color='ChurnLabel',
                           color_discrete_map={'Retained': TEAL, 'Churned': ORANGE},
                           nbins=50, barmode='overlay', opacity=0.7)
        fig.update_layout(title_text='Balance Distribution: Retained vs Churned', **CHART_TEMPLATE,
                          height=320, xaxis_title='Account Balance (€)', yaxis_title='Count')
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        # Balance band churn
        bal_churn = dff.groupby('BalanceBand', observed=True)['Exited'].mean().reset_index()
        bal_churn['Churn%'] = bal_churn['Exited'] * 100
        fig2 = px.bar(bal_churn, x='BalanceBand', y='Churn%',
                      color='Churn%', color_continuous_scale='RdYlGn_r',
                      text=bal_churn['Churn%'].apply(lambda x: f'{x:.1f}%'))
        fig2.update_traces(textposition='outside', marker_line_width=0)
        fig2.update_layout(title_text='Churn Rate by Balance Segment', **CHART_TEMPLATE,
                           height=320, coloraxis_showscale=False, xaxis_title='Balance Band', yaxis_title='Churn Rate (%)')
        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2)

    with c3:
        # Salary quartile
        dff2 = dff.copy()
        dff2['SalaryQ'] = pd.qcut(dff2['EstimatedSalary'], q=4, labels=['Q1 Bottom','Q2','Q3','Q4 Top'])
        sal_churn = dff2.groupby('SalaryQ', observed=True)['Exited'].mean().reset_index()
        sal_churn['Churn%'] = sal_churn['Exited'] * 100
        fig3 = px.bar(sal_churn, x='SalaryQ', y='Churn%',
                      color='Churn%', color_continuous_scale='Blues',
                      text=sal_churn['Churn%'].apply(lambda x: f'{x:.1f}%'))
        fig3.update_traces(textposition='outside', marker_line_width=0)
        fig3.update_layout(title_text='Churn Rate by Salary Quartile', **CHART_TEMPLATE,
                           height=310, coloraxis_showscale=False, xaxis_title='Salary Quartile', yaxis_title='Churn Rate (%)')
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        # Average balance by retention tier
        ret_bal = dff.groupby('RetentionTier', observed=True)['Balance'].mean().reset_index()
        fig4 = px.bar(ret_bal, x='RetentionTier', y='Balance',
                      color='RetentionTier',
                      color_discrete_map={'At Risk': RED, 'Moderate': ORANGE, 'Stable': TEAL, 'Loyal': GREEN},
                      text=ret_bal['Balance'].apply(lambda x: f'€{x:,.0f}'))
        fig4.update_traces(textposition='outside', marker_line_width=0)
        fig4.update_layout(title_text='Avg Balance by Retention Tier', **CHART_TEMPLATE,
                           height=310, showlegend=False, xaxis_title='', yaxis_title='Average Balance (€)')
        st.plotly_chart(fig4, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5: RISK SEGMENTS
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-header">Risk Segment Identification & Profiling</div>', unsafe_allow_html=True)

    col_hvd, col_spc = st.columns(2)

    with col_hvd:
        st.markdown(f"""
        <div style="background:#FDECEA; border: 2px solid #C0392B; border-radius:10px; padding:16px 20px; margin-bottom:14px;">
        <h3 style="color:#C0392B; margin:0 0 8px 0;">⚠️ High-Value Disengaged</h3>
        <b style="font-size:1.8rem; color:#C0392B;">{dff['HighValueDisengaged'].sum():,}</b> customers<br>
        <span style="font-size:0.85rem; color:#666;">Top-quartile balance + IsActiveMember = 0</span><br><br>
        <b>Churn Rate:</b> {dff[dff['HighValueDisengaged']==1]['Exited'].mean()*100:.1f}% vs {dff[dff['HighValueDisengaged']==0]['Exited'].mean()*100:.1f}% standard<br>
        <b>Avg Balance:</b> €{dff[dff['HighValueDisengaged']==1]['Balance'].mean():,.0f}<br>
        <b>Avg Age:</b> {dff[dff['HighValueDisengaged']==1]['Age'].mean():.1f} years
        </div>""", unsafe_allow_html=True)

        hvd_geo = dff[dff['HighValueDisengaged']==1]['Geography'].value_counts().reset_index()
        hvd_geo.columns = ['Geography', 'Count']
        fig = px.bar(hvd_geo, x='Geography', y='Count', color='Geography',
                     color_discrete_sequence=[BLUE, TEAL, ORANGE], text='Count')
        fig.update_traces(textposition='outside', marker_line_width=0)
        fig.update_layout(title_text='HVD by Country', **CHART_TEMPLATE, height=260, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col_spc:
        st.markdown(f"""
        <div style="background:#FEF3E2; border: 2px solid #E8580A; border-radius:10px; padding:16px 20px; margin-bottom:14px;">
        <h3 style="color:#E8580A; margin:0 0 8px 0;">🔕 Silent Premium Churners</h3>
        <b style="font-size:1.8rem; color:#E8580A;">{dff['SilentPremiumChurn'].sum():,}</b> customers<br>
        <span style="font-size:0.85rem; color:#666;">Top-salary quartile + ≤1 product + Exited = 1</span><br><br>
        <b>Avg Salary:</b> €{dff[dff['SilentPremiumChurn']==1]['EstimatedSalary'].mean():,.0f}<br>
        <b>Avg Balance:</b> €{dff[dff['SilentPremiumChurn']==1]['Balance'].mean():,.0f}<br>
        <b>Were Active at Exit:</b> {dff[dff['SilentPremiumChurn']==1]['IsActiveMember'].mean()*100:.1f}%
        </div>""", unsafe_allow_html=True)

        spc_geo = dff[dff['SilentPremiumChurn']==1]['Geography'].value_counts().reset_index()
        spc_geo.columns = ['Geography', 'Count']
        fig2 = px.bar(spc_geo, x='Geography', y='Count', color='Geography',
                      color_discrete_sequence=[ORANGE, TEAL, BLUE], text='Count')
        fig2.update_traces(textposition='outside', marker_line_width=0)
        fig2.update_layout(title_text='Silent Churners by Country', **CHART_TEMPLATE, height=260, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    # Retention Tier
    st.markdown('<div class="section-header">Retention Tier Breakdown</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        ret_summary = dff.groupby('RetentionTier', observed=True).agg(
            Count=('Exited','count'), Churn=('Exited','mean')).reset_index()
        ret_summary['Churn%'] = ret_summary['Churn'] * 100
        fig3 = px.bar(ret_summary, x='RetentionTier', y='Churn%',
                      color='RetentionTier',
                      color_discrete_map={'At Risk': RED, 'Moderate': ORANGE, 'Stable': TEAL, 'Loyal': GREEN},
                      text=ret_summary['Churn%'].apply(lambda x: f'{x:.1f}%'))
        fig3.update_traces(textposition='outside', marker_line_width=0)
        fig3.update_layout(title_text='Churn Rate by Retention Tier', **CHART_TEMPLATE,
                           height=300, showlegend=False, xaxis_title='', yaxis_title='Churn Rate (%)')
        st.plotly_chart(fig3, use_container_width=True)

    with c2:
        ret_dist = dff.groupby('RetentionTier', observed=True)['Exited'].count().reset_index()
        fig4 = px.pie(ret_dist, values='Exited', names='RetentionTier',
                      color='RetentionTier',
                      color_discrete_map={'At Risk': RED, 'Moderate': ORANGE, 'Stable': TEAL, 'Loyal': GREEN})
        fig4.update_layout(title_text='Portfolio by Retention Tier', **CHART_TEMPLATE, height=300)
        st.plotly_chart(fig4, use_container_width=True)

    # Scatter: Engagement vs Balance coloured by churn
    st.markdown('<div class="section-header">Engagement vs Balance: Churn Landscape</div>', unsafe_allow_html=True)
    sample = dff.sample(min(2000, len(dff)), random_state=42)
    fig5 = px.scatter(sample, x='EngagementScore', y='Balance', color='ChurnLabel',
                      color_discrete_map={'Retained': TEAL, 'Churned': RED},
                      opacity=0.5, hover_data=['Geography','Age','NumOfProducts'],
                      size_max=6)
    fig5.update_layout(title_text='Engagement Score vs Account Balance (sample of 2,000)', **CHART_TEMPLATE,
                       height=380, xaxis_title='Engagement Score', yaxis_title='Account Balance (€)')
    st.plotly_chart(fig5, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 6: RECOMMENDATIONS
# ══════════════════════════════════════════════════════════════════════════════
with tab6:
    st.markdown('<div class="section-header">Strategic Recommendations for Retention</div>', unsafe_allow_html=True)

    recs = [
        ('1', 'Emergency Re-engagement: High-Value Disengaged', 'CRITICAL', RED,
         f"{dff['HighValueDisengaged'].sum():,} customers with top-quartile balances are inactive — churning at {dff[dff['HighValueDisengaged']==1]['Exited'].mean()*100:.1f}%.",
         'Deploy dedicated relationship managers. Launch VIP reactivation programme with preferential rates and personalised wealth consultations within 30 days.'),

        ('2', 'Silent Premium Churn Prevention', 'CRITICAL', ORANGE,
         f"{dff['SilentPremiumChurn'].sum():,} high-salary customers left with only 1 product. {dff[dff['SilentPremiumChurn']==1]['IsActiveMember'].mean()*100:.0f}% were still active at departure.",
         'AI-driven Next Best Offer engine for top-salary customers. Launch private banking bundles. Mandate 90-day onboarding reviews for high-income customers.'),

        ('3', 'Germany Market Intervention', 'HIGH', BLUE,
         f"Germany churn ({dff[dff['Geography']=='Germany']['Exited'].mean()*100:.1f}%) is double France ({dff[dff['Geography']=='France']['Exited'].mean()*100:.1f}%) despite higher balances.",
         'Commission German market study: exit interviews, competitive fee benchmarking, digital service quality review, local product adjustments.'),

        ('4', 'Portfolio Activation Drive', 'HIGH', TEAL,
         f"Only {dff['IsActiveMember'].mean()*100:.1f}% of customers are active. Inactive members churn at {dff[dff['IsActiveMember']==0]['Exited'].mean()*100:.1f}% vs {dff[dff['IsActiveMember']==1]['Exited'].mean()*100:.1f}% active.",
         'Loyalty programme with reward points for digital actions. Personalised reactivation campaign for all 90-day inactive customers.'),

        ('5', 'Product Bundling Strategy', 'HIGH', GOLD,
         f"2-product customers churn at only {dff[dff['NumOfProducts']==2]['Exited'].mean()*100:.1f}% vs {dff[dff['NumOfProducts']==1]['Exited'].mean()*100:.1f}% for 1-product. This is the most powerful retention lever.",
         'Auto-suggest second product at 3-month milestone. Bundle savings with all new current accounts. Relationship reviews for 3+ product customers.'),

        ('6', 'Mid-Life Financial Planning (46–55)', 'MEDIUM', GREEN,
         f"The 46–55 age group has the highest churn rate ({dff[dff['AgeGroup']=='46–55']['Exited'].mean()*100:.1f}%) — unmet complex financial needs.",
         'Pension advisory and retirement planning service. Mortgage refinancing review programme. Wealth management consultation for high-balance mid-life customers.'),
    ]

    for num, title, priority, color, finding, action in recs:
        badge_class = 'critical' if priority == 'CRITICAL' else ('high' if priority == 'HIGH' else 'medium')
        st.markdown(f"""
        <div style="background:white; border-radius:10px; border-left: 5px solid {color}; 
             padding: 16px 20px; margin-bottom: 14px; box-shadow: 0 2px 6px rgba(0,0,0,0.07);">
            <div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
                <span style="background:{color}; color:white; border-radius:50%; width:28px; height:28px; 
                      display:inline-flex; align-items:center; justify-content:center; 
                      font-weight:700; font-size:0.9rem; flex-shrink:0;">{num}</span>
                <b style="font-size:1rem; color:#1F3B73;">{title}</b>
                <span class="risk-badge-{badge_class}">{priority}</span>
            </div>
            <div style="font-size:0.85rem; color:#555; margin-bottom:6px;">
                <b>Finding:</b> {finding}
            </div>
            <div style="font-size:0.85rem; color:#2E5FA3;">
                <b>Recommended Action:</b> {action}
            </div>
        </div>""", unsafe_allow_html=True)

    # Impact projection
    st.markdown('<div class="section-header">Projected Impact of Recommendations</div>', unsafe_allow_html=True)
    current_churn = dff['Exited'].mean() * 100
    target_churn  = max(current_churn - 5, 10)
    customers_saved = int((current_churn - target_churn) / 100 * len(dff))
    balance_saved   = customers_saved * dff['Balance'].mean()

    ci1, ci2, ci3 = st.columns(3)
    for col, val, label, color in [
        (ci1, f"{current_churn:.1f}% → {target_churn:.1f}%", "Churn Rate Improvement", RED),
        (ci2, f"+{customers_saved:,}", "Customers Retained", GREEN),
        (ci3, f"€{balance_saved/1e6:.1f}M", "Balance Preserved", BLUE),
    ]:
        with col:
            st.markdown(f"""
            <div class="metric-card" style="border-left-color:{color}; text-align:center;">
                <div class="metric-val" style="color:{color}; font-size:1.6rem;">{val}</div>
                <div class="metric-label">{label}</div>
            </div>""", unsafe_allow_html=True)

# ─── FOOTER ──────────────────────────────────────────────────────────────────
st.markdown("""
<hr style="margin: 40px 0 16px 0; border-color: #E5E7EB;">
<div style="text-align:center; color:#9CA3AF; font-size:0.78rem;">
    🏦 European Central Bank · Customer Engagement & Retention Analytics · 2025 · Confidential
</div>
""", unsafe_allow_html=True)
