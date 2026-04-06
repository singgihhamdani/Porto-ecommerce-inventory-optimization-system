import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from scipy.stats import norm
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Inventory Optimization System", page_icon="📦", layout="wide")

# --- CUSTOM CSS FOR MODERN AESTHETICS ---
st.markdown("""
    <style>
    .stMetric { background-color: #f8f9fb; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #e0e0e0; }
    .status-safe { color: #28a745; font-size: 32px; font-weight: 800; text-transform: uppercase; }
    .status-risk { color: #dc3545; font-size: 32px; font-weight: 800; text-transform: uppercase; }
    .status-over { color: #ffc107; font-size: 32px; font-weight: 800; text-transform: uppercase; }
    </style>
""", unsafe_allow_html=True)

# --- LOAD DATA ---
@st.cache_data
def load_data():
    # Supports running from /app folder or /root directory
    path_prefix = "" if os.path.exists('data/processed/simulation_baseline.csv') else "../"
    
    base_df = pd.read_csv(f'{path_prefix}data/processed/simulation_baseline.csv')
    sales_df = pd.read_csv(f'{path_prefix}data/raw/sales_data.csv')
    return base_df, sales_df

df, sales = load_data()

# --- B. SIDEBAR (USER INPUT PANEL) ---
st.sidebar.title("⚙️ Simulation Controls")
st.sidebar.markdown("Adjust parameters to stress-test your supply chain.")

selected_product = st.sidebar.selectbox("Select Product", df['product_name'].unique())
selected_wh = st.sidebar.selectbox("Select Warehouse", df['warehouse_id'].unique())

# Filter static baseline segment
segment_df = df[(df['product_name'] == selected_product) & (df['warehouse_id'] == selected_wh)].iloc[0]

st.sidebar.markdown("---")
st.sidebar.subheader("What-If Shocks")

demand_multiplier = st.sidebar.slider("Demand Multiplier (1.0 = Normal)", min_value=0.5, max_value=3.0, value=1.0, step=0.1, help="Simulate a massive promotional spike or market downturn.")

current_lead_time = int(segment_df['lead_time_days'])
sim_lead_time = st.sidebar.number_input("Override Lead Time (Days)", min_value=1, max_value=90, value=current_lead_time, help="Simulate port strikes or supplier delays.")

service_level = st.sidebar.selectbox("Target Service Level (%)", [0.90, 0.95, 0.99], index=1, format_func=lambda x: f"{int(x*100)}%", help="Higher service level guarantees availability but inflates Safety Stock.")

# --- C. SIMULATION LOGIC ---
def calculate_z_score(sl):
    return norm.ppf(sl)

# Baseline Variables
base_demand = segment_df['avg_daily_demand']
base_std = segment_df['std_demand']
base_rop = segment_df['reorder_point']
base_ss = segment_df['safety_stock']
current_stock = segment_df['current_stock']

# Simulated Variables
sim_demand = base_demand * demand_multiplier
sim_std = base_std * (demand_multiplier if demand_multiplier > 1 else 1)
z_score = calculate_z_score(service_level)

# Core Optimization Math
sim_ss = np.round(z_score * sim_std * np.sqrt(sim_lead_time))
sim_rop = np.round((sim_demand * sim_lead_time) + sim_ss)
sim_eoq = np.round(np.sqrt((2 * (sim_demand * 365) * segment_df['ordering_cost']) / segment_df['holding_cost_per_unit']))

# Rules Engine (Status Evaluation)
if current_stock < sim_rop:
    status = "REORDER NEEDED"
    status_class = "status-risk"
    rec = f"🚨 **CRITICAL ACTION:** Issue Purchase Order for **{int(sim_eoq)} units**. The simulated shock breached the Reorder Point by {int(sim_rop - current_stock)} units. You will stock out if demand sustains."
elif current_stock > (sim_rop + sim_eoq):
    status = "OVERSTOCK RISK"
    status_class = "status-over"
    rec = f"🛑 **HOLD PURCHASES:** You have excessive inventory. Bleed down **{int(current_stock - (sim_rop + sim_eoq))} units** to free up working capital. Run marketing campaigns if necessary."
else:
    status = "SAFE (OPTIMAL)"
    status_class = "status-safe"
    rec = "✅ **SAFE:** Current inventory volume perfectly supports the simulated conditions. No intervention required."

# --- A. HEADER SECTION ---
st.title("📦 Interactive Inventory Optimization System")
st.markdown("A decision-support dashboard unifying Demand Forecasting, Safety Stock, and Scenario Simulation.")
st.markdown("---")

# --- 📊 SECTION 1: DEMAND FORECAST & HISTORY ---
st.subheader("📊 1. Historical Velocity vs Projected Demand Shock")

hist_sales = sales[(sales['product_id'] == segment_df['product_id']) & (sales['warehouse_id'] == selected_wh)].copy()
hist_sales['date'] = pd.to_datetime(hist_sales['date'])
daily_hist = hist_sales.groupby('date')['sales_qty'].sum().reset_index()

fig = px.line(daily_hist, x='date', y='sales_qty', title='12-Month Historical Sales', template='plotly_white', color_discrete_sequence=['#8c92ac'])
fig.add_hline(y=base_demand, line_dash="dot", line_color="blue", annotation_text=f"Base Demand: {base_demand:.0f} units/day", annotation_position="top left")
fig.add_hline(y=sim_demand, line_dash="dash", line_color="red", annotation_text=f"Simulated Demand: {sim_demand:.0f} units/day", annotation_position="bottom right")

st.plotly_chart(fig, use_container_width=True)

# --- ⚙️ SECTION 2 & 3: INVENTORY METRICS & RESULTS ---
st.subheader("⚙️ 2. Dynamic Inventory Targets (Real-Time Output)")
st.markdown("Watch how the mathematical targets shift based on your sidebar simulation parameters.")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Simulated Avg Demand", value=f"{sim_demand:.0f}/day", delta=f"{sim_demand - base_demand:.0f} (shock)", delta_color="inverse")
with col2:
    st.metric(label="Target Safety Stock", value=f"{sim_ss:.0f}", delta=f"{sim_ss - base_ss:.0f} (buffer)", delta_color="inverse")
with col3:
    st.metric(label="Reorder Point (ROP)", value=f"{sim_rop:.0f}", delta=f"{sim_rop - base_rop:.0f} (tripwire)", delta_color="inverse")
with col4:
    st.metric(label="Actual Current Stock", value=f"{current_stock:.0f}", delta=None)

st.markdown("---")

# --- ⚠️ SECTION 4 & 5: STATUS & AUTOMATED RECOMMENDATIONS ---
st.subheader("⚠️ 3. Executive Decision Support")

status_col, rec_col = st.columns([1, 2])
with status_col:
    st.markdown("<p style='color:gray; font-size:14px; margin-bottom:0px;'>Inventory Health Status:</p>", unsafe_allow_html=True)
    st.markdown(f"<span class='{status_class}'>{status}</span>", unsafe_allow_html=True)
    
with rec_col:
    st.info(rec)
