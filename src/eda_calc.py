import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Create outputs directory
os.makedirs('outputs', exist_ok=True)

# Load data
sales = pd.read_csv('data/raw/sales_data.csv')
inv = pd.read_csv('data/raw/inventory_data.csv')
prod = pd.read_csv('data/raw/product_master.csv')

# 1. DATA UNDERSTANDING
print("--- 1. DATA UNDERSTANDING ---")
print("Sales Shape:", sales.shape)
print("Sales Missing:", sales.isnull().sum().sum())
print("Inv Missing:", inv.isnull().sum().sum())

# 2. UNIVARIATE ANALYSIS
print("\n--- 2. UNIVARIATE ANALYSIS ---")
print(sales[['sales_qty', 'price']].describe(percentiles=[.25, .5, .75, .95]))
print("\nPromotion Flag Distribution:\n", sales['promotion_flag'].value_counts(normalize=True))

# 4. PRODUCT-LEVEL ANALYSIS
print("\n--- 4. PRODUCT-LEVEL ANALYSIS ---")
prod_sales = sales.groupby('product_id')['sales_qty'].sum().reset_index()
prod_sales = prod_sales.merge(prod, on='product_id').sort_values('sales_qty', ascending=False)
prod_sales['cum_perc'] = prod_sales['sales_qty'].cumsum() / prod_sales['sales_qty'].sum()
print(prod_sales[['product_name', 'category', 'sales_qty', 'cum_perc']])

# 5. WAREHOUSE ANALYSIS
print("\n--- 5. WAREHOUSE ANALYSIS ---")
wh_sales = sales.groupby('warehouse_id')['sales_qty'].sum().reset_index()
wh_sales['pct_total'] = wh_sales['sales_qty'] / wh_sales['sales_qty'].sum()
print(wh_sales)

# 6. PROMOTION IMPACT
print("\n--- 6. PROMOTION IMPACT ---")
promo = sales.groupby('promotion_flag')['sales_qty'].mean().reset_index()
promo['uplift'] = promo['sales_qty'] / promo.loc[promo['promotion_flag']==0, 'sales_qty'].values[0]
print(promo)

# 7. CHANNEL ANALYSIS
print("\n--- 7. CHANNEL ANALYSIS ---")
chan = sales.groupby('channel')['sales_qty'].sum().reset_index()
chan['pct_total'] = chan['sales_qty'] / chan['sales_qty'].sum()
print(chan)

# 8. INVENTORY INSIGHT
print("\n--- 8. INVENTORY INSIGHT ---")
avg_daily = sales.groupby(['product_id', 'warehouse_id'])['sales_qty'].mean().reset_index()
avg_daily.rename(columns={'sales_qty': 'avg_daily_demand'}, inplace=True)
inv_risk = inv.merge(avg_daily, on=['product_id', 'warehouse_id'])
inv_risk['days_of_stock'] = inv_risk['current_stock'] / inv_risk['avg_daily_demand']
print(inv_risk[['product_id', 'warehouse_id', 'current_stock', 'avg_daily_demand', 'days_of_stock']].sort_values('days_of_stock'))

# Generate Plots silently
sales['date'] = pd.to_datetime(sales['date'])
daily_sales = sales.groupby('date')['sales_qty'].sum().reset_index()

plt.figure(figsize=(12,5))
sns.lineplot(data=daily_sales, x='date', y='sales_qty', color='blue')
plt.title('Total Daily Sales Volume')
plt.tight_layout()
plt.savefig('outputs/daily_sales.png')
plt.close()

plt.figure(figsize=(10,5))
sns.barplot(data=prod_sales, x='product_name', y='sales_qty', palette='viridis')
plt.xticks(rotation=45)
plt.title('Total Sales by Product')
plt.tight_layout()
plt.savefig('outputs/product_sales.png')
plt.close()
