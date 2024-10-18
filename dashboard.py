import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load the provided Excel files
policy_commission_path = '/Users/senelisiwemuradzikwa/Desktop/Projects-Data Analysis/Assessment (1) (1)/Policy_commission.xlsx'
staff_list_path = '/Users/senelisiwemuradzikwa/Desktop/Projects-Data Analysis/Assessment (1) (1)/Staff_list.xlsx'
revenue_extract_path = '/Users/senelisiwemuradzikwa/Desktop/Projects-Data Analysis/Assessment (1) (1)/Revenue_extract.xlsx'

# Reading the files
policy_commission_df = pd.read_excel(policy_commission_path)
staff_list_df = pd.read_excel(staff_list_path)
revenue_extract_df = pd.read_excel(revenue_extract_path)

# Display the first few rows of each dataframe to understand their structure
(policy_commission_df.head(), staff_list_df.head(), revenue_extract_df.head())
policy_commission_clean = policy_commission_df.dropna(how='all').iloc[3:].reset_index(drop=True)
policy_commission_clean.columns = ['Category', 'Sub Category', '< 1', '1 < 1.1', '1.1 < 2', '> 2 X', 'Unused']
policy_commission_clean = policy_commission_clean[['Category', 'Sub Category', '< 1', '1 < 1.1', '1.1 < 2', '> 2 X']]
# Cleaning revenue extract
revenue_clean = revenue_extract_df[['CreateDate', 'ServiceType', 'RecurringServiceAmount_IncVat', 'SaleAgent']].copy()
revenue_clean['CreateDate'] = pd.to_datetime(revenue_clean['CreateDate'])
# Filter by the month of interest
revenue_clean['Month'] = revenue_clean['CreateDate'].dt.to_period('M')
# Group by agent and calculate total sales for the month
total_sales_by_agent = revenue_clean.groupby(['SaleAgent', 'Month'])['RecurringServiceAmount_IncVat'].sum().reset_index()
total_sales_by_agent = total_sales_by_agent[total_sales_by_agent['Month'] == '2021-01']  # Example for January 2021
# Merging with staff list
staff_sales = total_sales_by_agent.merge(staff_list_df[['Employee Name', 'Employee Surname']], left_on='SaleAgent', right_on='Employee Name', how='left')
def create_dashboard():
    st.title("Sales and Commission Dashboard - January 2021")

    # Display the dataset
    st.subheader("Agent Sales and Commission Data")
    st.dataframe(staff_sales)

    # Plotting a bar chart for total sales by agent
    st.subheader("Total Sales by Agent")
    fig, ax = plt.subplots()
    ax.bar(staff_sales['SaleAgent'], staff_sales['RecurringServiceAmount_IncVat'], color='skyblue')
    ax.set_xlabel("Agent")
    ax.set_ylabel("Total Sales (Inc. VAT)")
    ax.set_title("Total Sales by Agent")
    st.pyplot(fig)

    # Plotting a bar chart for commission earned by agent
    st.subheader("Commission Earned by Agent")
    fig, ax = plt.subplots()
    ax.bar(staff_sales['SaleAgent'], staff_sales['Commission Earned'], color='green')
    ax.set_xlabel("Agent")
    ax.set_ylabel("Commission Earned")
    ax.set_title("Commission Earned by Agent")
    st.pyplot(fig)

if __name__ == '__main__':
    create_dashboard()
