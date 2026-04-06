import pandas as pd
import numpy as np
import os
from datetime import timedelta, date

# Set random seed for reproducibility
np.random.seed(42)

def generate_datasets(output_dir='data/raw'):
    print("Generating synthetic datasets...")
    os.makedirs(output_dir, exist_ok=True)
    
    # ----------------------------------------------------
    # 1. Product Master (product_master.csv)
    # ----------------------------------------------------
    products = [
        {'product_id': 'P001', 'product_name': 'Wireless Earbuds', 'category': 'Electronics'},
        {'product_id': 'P002', 'product_name': 'Smart Watch', 'category': 'Electronics'},
        {'product_id': 'P003', 'product_name': 'Yoga Mat', 'category': 'Fitness'},
        {'product_id': 'P004', 'product_name': 'Dumbbells Set', 'category': 'Fitness'},
        {'product_id': 'P005', 'product_name': 'Coffee Maker', 'category': 'Home Appliances'},
        {'product_id': 'P006', 'product_name': 'Air Purifier', 'category': 'Home Appliances'}
    ]
    df_products = pd.DataFrame(products)
    df_products.to_csv(f"{output_dir}/product_master.csv", index=False)
    
    # ----------------------------------------------------
    # 2. Inventory Data (inventory_data.csv)
    # ----------------------------------------------------
    warehouses = ['WH_East', 'WH_West']
    inventory_records = []
    
    for p in products:
        for w in warehouses:
            # Base values tailored by category for realism
            if p['category'] == 'Electronics':
                holding_cost = np.round(np.random.uniform(5.0, 15.0), 2)
                ordering_cost = np.random.randint(50, 100)
                lead_time = np.random.randint(7, 21)
                current_stock = np.random.randint(100, 500)
            elif p['category'] == 'Fitness':
                holding_cost = np.round(np.random.uniform(1.0, 5.0), 2)
                ordering_cost = np.random.randint(20, 60)
                lead_time = np.random.randint(5, 14)
                current_stock = np.random.randint(200, 1000)
            else: # Home Appliances
                holding_cost = np.round(np.random.uniform(3.0, 10.0), 2)
                ordering_cost = np.random.randint(40, 80)
                lead_time = np.random.randint(10, 28)
                current_stock = np.random.randint(150, 600)
                
            inventory_records.append({
                'product_id': p['product_id'],
                'warehouse_id': w,
                'current_stock': current_stock,
                'holding_cost_per_unit': holding_cost,
                'ordering_cost': ordering_cost,
                'lead_time_days': lead_time
            })
    
    df_inventory = pd.DataFrame(inventory_records)
    df_inventory.to_csv(f"{output_dir}/inventory_data.csv", index=False)
    
    # ----------------------------------------------------
    # 3. Sales Data (sales_data.csv)
    # ----------------------------------------------------
    start_date = date(2023, 1, 1)
    end_date = date(2023, 12, 31)
    delta = end_date - start_date
    dates = [start_date + timedelta(days=i) for i in range(delta.days + 1)]
    
    sales_records = []
    
    for p in products:
        for w in warehouses:
            # Base price and demand by category
            if p['category'] == 'Electronics':
                base_price = np.random.choice([49.99, 199.99, 299.99])
                base_demand = np.random.randint(10, 30)
            elif p['category'] == 'Fitness':
                base_price = np.random.choice([19.99, 89.99])
                base_demand = np.random.randint(30, 80)
            else:
                base_price = np.random.choice([79.99, 149.99])
                base_demand = np.random.randint(15, 40)
            
            # Regional difference: East sells slightly more
            wh_factor = 1.2 if w == 'WH_East' else 0.8
            
            for d in dates:
                month = d.month
                day_of_week = d.weekday()
                
                # Seasonality: High demand in Nov/Dec (Holidays) and Jan (Resolutions for Fitness)
                seasonality_factor = 1.0
                if month in [11, 12]:
                    seasonality_factor = 1.5
                elif p['category'] == 'Fitness' and month == 1:
                    seasonality_factor = 1.8
                elif month in [2, 3]:
                    seasonality_factor = 0.8 # Post-holiday slump
                
                # Weekly pattern: Weekend (5,6) higher sales
                weekly_factor = 1.3 if day_of_week >= 5 else 0.9
                
                # Promotion: 5% chance of a random promotion day (e.g., flash sales)
                # Black Friday / Cyber Monday simulation (late Nov)
                is_promo = 0
                promo_factor = 1.0
                if month == 11 and d.day > 24:
                    is_promo = 1
                    promo_factor = 3.0
                elif np.random.random() > 0.95:
                    is_promo = 1
                    promo_factor = 2.0
                
                # Random Noise (White noise)
                noise = np.random.normal(1.0, 0.1)
                
                # Calculate synthetic Quantity
                demand = base_demand * wh_factor * seasonality_factor * weekly_factor * promo_factor * noise
                qty = max(0, int(np.round(demand)))
                
                # Assign to Channel
                channel_probabilities = [0.7, 0.3] if w == 'WH_East' else [0.5, 0.5]
                channel = np.random.choice(['Online', 'Offline'], p=channel_probabilities)
                
                sales_records.append({
                    'date': d.strftime('%Y-%m-%d'),
                    'product_id': p['product_id'],
                    'warehouse_id': w,
                    'sales_qty': qty,
                    'price': base_price,
                    'promotion_flag': is_promo,
                    'channel': channel
                })
                
    df_sales = pd.DataFrame(sales_records)
    
    # Sort sales data chronologically for neatness
    df_sales = df_sales.sort_values(by=['date', 'product_id', 'warehouse_id'])
    df_sales.to_csv(f"{output_dir}/sales_data.csv", index=False)
    
    print(f"Data generation complete!")
    print(f"--> Saved {len(df_products)} products to {output_dir}/product_master.csv")
    print(f"--> Saved {len(df_inventory)} inventory records to {output_dir}/inventory_data.csv")
    print(f"--> Saved {len(df_sales)} sales transaction records to {output_dir}/sales_data.csv")

if __name__ == '__main__':
    generate_datasets()
