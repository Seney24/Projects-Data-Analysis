import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')
# Load the provided Excel files
revenue = pd.read_excel('/Users/senelisiwemuradzikwa/Desktop/Projects-Data Analysis/Assessment (1) (1)/Revenue_extract.xlsx')
salaries = pd.read_excel('/Users/senelisiwemuradzikwa/Desktop/Projects-Data Analysis/Assessment (1) (1)/Staff_list.xlsx')

# Ensure the CreateDate column is in datetime format and convert it to month
revenue['CreateDate'] = pd.to_datetime(revenue['CreateDate'], errors='coerce')
revenue['Month'] = revenue['CreateDate'].dt.to_period('M')

# Filter for January 2021
total_sales_by_agent = revenue.groupby(['SaleAgent', 'Month', 'Product', 'BillingCycle'])['RecurringServiceAmount_IncVat'].sum().reset_index()
total_sales_by_agent = total_sales_by_agent[total_sales_by_agent['Month'] == '2021-01']
df_clean = total_sales_by_agent[total_sales_by_agent['SaleAgent'] != 'Local API User']

# Merge with salary data
merged_data = pd.merge(total_sales_by_agent, salaries[['Employee Name', 'Total Earnings']], 
                       left_on='SaleAgent', right_on='Employee Name', how='left')
merged_data.rename(columns={'Total Earnings': 'Salaries'}, inplace=True)

# Remove unwanted agents
merged_data = merged_data[merged_data['SaleAgent'] != 'Local API User']
merged_data = merged_data[merged_data['SaleAgent'] != 'Client']
merged_data = merged_data.drop(columns=['Employee Name'])

# Commission policy dictionary
commission_rates = {
    'Application Hosting': [0.10, 0.30, 0.50, 1.00],
    'Domain': [0.15, 0.40, 0.60, 1.00],  # Assuming Domain falls under Web Services
    'Infrastructure Hosting': [0.07, 0.20, 0.35, 0.50]
}

# Calculate total sales and salary cover per agent/product
df_sales = merged_data.groupby(['SaleAgent', 'Product']).agg({
    'RecurringServiceAmount_IncVat': 'sum',
    'Salaries': 'first'
}).reset_index()

df_sales['SalaryCover'] = df_sales['RecurringServiceAmount_IncVat'] / df_sales['Salaries']

# Commission calculation function
def apply_commission(product, salary_cover, recurring_amount):
    if salary_cover < 1:
        return commission_rates[product][0] * recurring_amount
    elif 1 <= salary_cover < 1.1:
        return commission_rates[product][1] * recurring_amount
    elif 1.1 <= salary_cover < 2:
        return commission_rates[product][2] * recurring_amount
    else:
        return commission_rates[product][3] * recurring_amount

# Apply commission
df_sales['CommissionEarned'] = df_sales.apply(lambda row: apply_commission(row['Product'], row['SalaryCover'], row['RecurringServiceAmount_IncVat']), axis=1)

# Summing commissions per Sales Agent
df_report = df_sales.groupby('SaleAgent').agg({
    'RecurringServiceAmount_IncVat': 'sum',
    'CommissionEarned': 'sum'
}).reset_index()

# Streamlit Dashboard
def create_dashboard():
    st.title("Sales and Commission Dashboard - January 2021")

    # Display cleaned sales data
    st.subheader("Agent Sales")
    st.dataframe(df_clean)

    # Plot: Total Sales by Agent
    st.subheader("Total Sales by Agent")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(df_clean['SaleAgent'], df_clean['RecurringServiceAmount_IncVat'], color='skyblue')
    ax.set_title('Total Sales by Each Agent - January 2021')
    ax.set_xlabel('Agent')
    ax.set_ylabel('Total Sales (Inc. VAT)')
    ax.set_xticklabels(df_clean['SaleAgent'], rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)

    # Display calculated salary cover
    st.subheader("Salary Cover Calculated")
    st.dataframe(df_sales)

    # Display commission report
    st.subheader("Commission Earned")
    st.dataframe(df_report)

    # Plot: Commission Earned by Agent
    st.subheader("Commission Earned by Agent")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(df_report['SaleAgent'], df_report['CommissionEarned'], color='lightgreen')
    ax.set_title('Commission Earned by Each Agent - January 2021')
    ax.set_xlabel('Agent')
    ax.set_ylabel('Commission Earned')
    ax.set_xticklabels(df_report['SaleAgent'], rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)

       # **New** Plot: Total Sales by Product
    st.subheader("Total Sales by Product")
    # Aggregate sales by product
    product_sales = df_clean.groupby('Product')['RecurringServiceAmount_IncVat'].sum().reset_index()

    # Plot the sales by product
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(product_sales['Product'], product_sales['RecurringServiceAmount_IncVat'], color='orange')
    ax.set_title('Total Sales by Product - January 2021')
    ax.set_xlabel('Product')
    ax.set_ylabel('Total Sales (Inc. VAT)')
    ax.set_xticklabels(product_sales['Product'], rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)
    
if __name__ == '__main__':
    create_dashboard()
