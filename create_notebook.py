import json

notebook = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Customer Engagement & Product Utilization Analytics\n",
    "## Phase 2: Data Preprocessing & Exploratory Data Analysis"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "import pandas as pd\n",
    "import numpy as np\n",
    "import warnings\n",
    "warnings.filterwarnings('ignore')"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 1. Data Ingestion & Validation"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Load dataset\n",
    "df = pd.read_csv('European_Bank.csv')\n",
    "\n",
    "print(\"=== Dataset Info ===\")\n",
    "df.info()\n",
    "print(\"\\n=== Missing Values ===\")\n",
    "print(df.isnull().sum())\n",
    "print(\"\\n=== Head ===\")\n",
    "display(df.head())\n",
    "print(\"\\n=== Summary Stats ===\")\n",
    "display(df.describe())"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 2. Engagement Classification\n",
    "Creating engagement profiles:\n",
    "- Active engaged customers\n",
    "- Inactive disengaged customers\n",
    "- Active but low-product customers\n",
    "- Inactive high-balance customers"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "non_zero_balance_median = df[df['Balance'] > 0]['Balance'].median()\n",
    "df['Profile'] = 'Other'\n",
    "df.loc[(df['IsActiveMember'] == 1) & (df['NumOfProducts'] > 1), 'Profile'] = 'Active Engaged'\n",
    "df.loc[(df['IsActiveMember'] == 0) & (df['NumOfProducts'] == 1), 'Profile'] = 'Inactive Disengaged'\n",
    "df.loc[(df['IsActiveMember'] == 1) & (df['NumOfProducts'] <= 1), 'Profile'] = 'Active Low-Product'\n",
    "df.loc[(df['IsActiveMember'] == 0) & (df['Balance'] >= non_zero_balance_median), 'Profile'] = 'Inactive High-Balance'\n",
    "\n",
    "print(\"=== Profile Distribution ===\")\n",
    "display(df['Profile'].value_counts().to_frame())\n",
    "\n",
    "print(\"\\n=== Profile Churn Rate ===\")\n",
    "display(df.groupby('Profile')['Exited'].mean().to_frame().sort_values(by='Exited', ascending=False))"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 3. Product Utilization Analysis"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "print(\"=== Churn by NumOfProducts ===\")\n",
    "display(df.groupby('NumOfProducts')['Exited'].agg(['count', 'mean']))"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 4. Financial Commitment vs Engagement Analysis"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Salary-balance mismatch (high salary, low balance)\n",
    "high_salary_threshold = df['EstimatedSalary'].median()\n",
    "low_balance_threshold = 0 # Mostly zero\n",
    "    \n",
    "df['Salary_Balance_Mismatch'] = np.where((df['EstimatedSalary'] > high_salary_threshold) & (df['Balance'] == 0), 1, 0)\n",
    "print(\"=== Salary-Balance Mismatch Churn ===\")\n",
    "display(df.groupby('Salary_Balance_Mismatch')['Exited'].agg(['count', 'mean']))"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 5. Retention Strength Assessment & KPIs"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Engagement Retention Ratio: active vs inactive churn comparison\n",
    "active_churn = df[df['IsActiveMember'] == 1]['Exited'].mean()\n",
    "inactive_churn = df[df['IsActiveMember'] == 0]['Exited'].mean()\n",
    "print(f\"Engagement Retention Ratio (Inactive / Active Churn): {inactive_churn / active_churn:.2f}x\")\n",
    "\n",
    "# Product Depth Index: ratio of products used vs loyalty\n",
    "single_prod_churn = df[df['NumOfProducts'] == 1]['Exited'].mean()\n",
    "multi_prod_churn = df[df['NumOfProducts'] > 1]['Exited'].mean()\n",
    "print(f\"Product Depth Index (Single Prod / Multi Prod Churn): {single_prod_churn / multi_prod_churn:.2f}x\")\n",
    "\n",
    "# High-Balance Disengagement Rate: premium inactive churn\n",
    "high_bal_inactive_churn = df[(df['Balance'] >= non_zero_balance_median) & (df['IsActiveMember'] == 0)]['Exited'].mean()\n",
    "print(f\"High-Balance Disengagement Rate: {high_bal_inactive_churn:.2%}\")\n",
    "\n",
    "# Credit Card Stickiness Score\n",
    "cc_churn = df[df['HasCrCard'] == 1]['Exited'].mean()\n",
    "no_cc_churn = df[df['HasCrCard'] == 0]['Exited'].mean()\n",
    "print(f\"Credit Card Stickiness Score (No CC / CC Churn): {no_cc_churn / cc_churn:.2f}x\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Save the processed data for Streamlit\n",
    "df.to_csv('processed_bank_data.csv', index=False)\n",
    "print(\"Saved 'processed_bank_data.csv' for the Streamlit dashboard.\")"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "name": "python",
   "version": "3.10.0"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}

with open('DA_project.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=1)
