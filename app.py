import streamlit as st
import pandas as pd
import plotly.express as px

# Dashboard Configuration
st.set_page_config(page_title="Customer Engagement & Retention", layout="wide", page_icon="🏦")

# Data loading function
@st.cache_data
def load_data():
    return pd.read_csv('processed_bank_data.csv')

df = load_data()

# CSS styling for KPIs
st.markdown("""
<style>
.kpi-card {
    background-color: #f8f9fa;
    border-left: 5px solid #004085;
    padding: 20px;
    border-radius: 5px;
    margin-bottom: 20px;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
}
.kpi-title {
    font-size: 1.1em;
    font-weight: bold;
    color: #6c757d;
}
.kpi-value {
    font-size: 2em;
    font-weight: bold;
    color: #004085;
}
</style>
""", unsafe_allow_html=True)

# Main Title
st.title("🏦 Customer Engagement & Product Utilization Analytics")
st.markdown("---")

# Navigation Sidebar
st.sidebar.header("Navigation & Filters")
menu = st.sidebar.radio("Go to:", ["Overview & KPIs", "Engagement vs Churn", "Product Utilization Impact", "High-Value Disengaged Customers", "Retention Strength Scoring"])

# Global Filters
st.sidebar.markdown('---')
st.sidebar.subheader('Global Filters')
geography_filter = st.sidebar.multiselect('Select Geography', df['Geography'].unique(), default=df['Geography'].unique())
gender_filter = st.sidebar.multiselect('Select Gender', df['Gender'].unique(), default=df['Gender'].unique())

filtered_df = df[(df['Geography'].isin(geography_filter)) & (df['Gender'].isin(gender_filter))]

if menu == "Overview & KPIs":
    st.header("Key Performance Indicators 📈")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # KPIs Calculation
    active_churn = filtered_df[filtered_df['IsActiveMember'] == 1]['Exited'].mean()
    inactive_churn = filtered_df[filtered_df['IsActiveMember'] == 0]['Exited'].mean()
    erb = inactive_churn / active_churn if active_churn > 0 else 0
    
    single_prod_churn = filtered_df[filtered_df['NumOfProducts'] == 1]['Exited'].mean()
    multi_prod_churn = filtered_df[filtered_df['NumOfProducts'] > 1]['Exited'].mean()
    pdi = single_prod_churn / multi_prod_churn if multi_prod_churn > 0 else 0
    
    non_zero_balance_median = filtered_df[filtered_df['Balance'] > 0]['Balance'].median()
    high_bal_inactive_churn = filtered_df[(filtered_df['Balance'] >= non_zero_balance_median) & (filtered_df['IsActiveMember'] == 0)]['Exited'].mean()
    
    cc_churn = filtered_df[filtered_df['HasCrCard'] == 1]['Exited'].mean()
    no_cc_churn = filtered_df[filtered_df['HasCrCard'] == 0]['Exited'].mean()
    cc_stickiness = no_cc_churn / cc_churn if cc_churn > 0 else 0
    
    with col1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Engagement Retention Ratio</div><div class="kpi-value">{erb:.2f}x</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Product Depth Index</div><div class="kpi-value">{pdi:.2f}x</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">High-Bal Disengagement Rate</div><div class="kpi-value">{high_bal_inactive_churn:.1%}</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Cards Stickiness Score</div><div class="kpi-value">{cc_stickiness:.2f}x</div></div>', unsafe_allow_html=True)
        
    st.markdown("---")
    st.subheader("Data Preview")
    st.dataframe(filtered_df.head(10))

elif menu == "Engagement vs Churn":
    st.header("Engagement vs Churn Analysis")
    st.markdown("Analyzing how active vs inactive behavior determines long-term customer retention.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_profile = px.pie(filtered_df, names='Profile', title="Customer Profile Distribution", hole=0.4, color_discrete_sequence=px.colors.sequential.Teal)
        st.plotly_chart(fig_profile, use_container_width=True)
        
    with col2:
        churn_by_profile = filtered_df.groupby('Profile')['Exited'].mean().reset_index()
        fig_profile_churn = px.bar(churn_by_profile, x='Profile', y='Exited', title="Churn Rate by Profile", labels={'Exited': 'Churn Rate'}, text_auto='.1%', color='Profile', color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_profile_churn.update_layout(showlegend=False)
        st.plotly_chart(fig_profile_churn, use_container_width=True)

    st.markdown("### Key Insight")
    st.info("Inactive Disengaged customers show the highest churn propensity. Interestingly, Inactive High-Balance customers also show significant churn risk, negating the assumption that balance alone drives loyalty.")

elif menu == "Product Utilization Impact":
    st.header("Product Depth vs Churn Relationship")
    st.markdown("Evaluating single-product vs multi-product consumer retention.")
    
    prod_filter = st.slider("Select Range of Products", min_value=1, max_value=4, value=(1, 4))
    
    temp_df = filtered_df[(filtered_df['NumOfProducts'] >= prod_filter[0]) & (filtered_df['NumOfProducts'] <= prod_filter[1])]
    
    col1, col2 = st.columns(2)
    
    with col1:
        churn_by_prod = temp_df.groupby('NumOfProducts')['Exited'].agg(['mean', 'count']).reset_index()
        fig_prod = px.bar(churn_by_prod, x='NumOfProducts', y='mean', title="Churn Rate by Number of Products", text_auto='.1%', labels={'mean': 'Churn Rate'})
        st.plotly_chart(fig_prod, use_container_width=True)
        
    with col2:
        fig_prod_count = px.bar(churn_by_prod, x='NumOfProducts', y='count', title="Customer Count by Number of Products", text_auto=True, color_discrete_sequence=['#5f9e8f'])
        st.plotly_chart(fig_prod_count, use_container_width=True)
        
    st.markdown("### Key Insight")
    st.info("Single-product customers represent the bulk of the churn. Transitioning customers to 2 products dramatically decreases churn vulnerability.")

elif menu == "High-Value Disengaged Customers":
    st.header("Financial Commitment vs Engagement Analysis")
    st.markdown("Detecting silent churn among premium but inactive consumers.")
    
    bal_threshold = st.number_input("Set Minimum Balance to Classify as 'Premium'", value=100000, step=10000)
    salary_threshold = st.number_input("Set Minimum Salary Default", value=100000, step=10000)
    
    hw_inactive = filtered_df[(filtered_df['Balance'] >= bal_threshold) & (filtered_df['IsActiveMember'] == 0)]
    hw_active = filtered_df[(filtered_df['Balance'] >= bal_threshold) & (filtered_df['IsActiveMember'] == 1)]
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total 'At-Risk' Premium Customers", hw_inactive.shape[0])
        st.metric("Churn Rate for 'At-Risk' Premium", f"{hw_inactive['Exited'].mean():.1%}" if not hw_inactive.empty else "N/A")
    with col2:
        st.metric("Total Active Premium Customers", hw_active.shape[0])
        st.metric("Churn Rate for Active Premium", f"{hw_active['Exited'].mean():.1%}" if not hw_active.empty else "N/A")

    st.markdown("---")
    st.subheader("Salary-Balance Mismatch Analysis")
    fig_scatter = px.scatter(
        filtered_df[filtered_df['EstimatedSalary'] >= salary_threshold].sample(min(1000, filtered_df.shape[0]), random_state=42), 
        x="EstimatedSalary", y="Balance", color="Exited", hover_data=['Profile'],
        title="Sample Overlay: Salary vs Balance (Colored by Churn)", opacity=0.7
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

elif menu == "Retention Strength Scoring":
    st.header("Retention Strength Assessment")
    st.markdown("Defining 'sticky customer' profiles based on combined engagement + product scores.")
    
    # Calculate a simple Activity score 
    filtered_df['RetentionScore'] = (filtered_df['IsActiveMember'] * 50) + (filtered_df['NumOfProducts'] * 25)
    
    fig_hist = px.histogram(filtered_df, x='RetentionScore', color='Exited', nbins=10, 
                            title="Churn Probability Across Retention Strength Score", 
                            barmode='group')
    st.plotly_chart(fig_hist, use_container_width=True)
    
    st.markdown("### Summary")
    st.success("Customers with High Retention Strength Scores (> 75) operate essentially as safe recurring assets. Customers scoring under 50 require immediate engagement initiatives via gamification or product upselling.")
