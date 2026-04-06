# 🌐 Google Sheets Data Integration Guide
**Interactive Inventory Optimization System**

---

## 1. Integration Concept
**Data Integration** in this context means connecting our Streamlit dashboard to an external, live database rather than reading a static `.csv` file saved on your computer. 
*   **Static CSV:** Fast, locally stored, but requires a Data Engineer to manually export, run Python scripts, and overwrite the file every time a new sale occurs.
*   **Dynamic Data (Google Sheets):** Acts as a cloud database. An Inventory Manager can manually type a new stock level into a Google Sheet from their phone, and the Streamlit Dashboard will automatically pull that new data and recalculate the Reorder Point (ROP) instantly.

**Why it adds value:** It transforms the portfolio piece from a "dead" mathematical notebook into a "live" Software-as-a-Service (SaaS) tool. Recruiters look for candidates who understand data pipelines, not just isolated algorithms.

---

## 2. Data Source Options
When scaling a portfolio project to seem "real-world", you have three options:
1.  **Google Sheets (Primary Strategy):** Exceptionally visual, free, and completely usable by non-technical business stakeholders (like an Operations Manager).
2.  **CSV (Fallback System):** Good for testing and initial development. Zero latency.
3.  **API / SQL Database (Advanced):** Connecting to PostgreSQL or simulating REST APIs. Very impressive but requires extensive setup (AWS/GCP infrastructure) that distracts from the core Supply Chain logic.

*We will use Google Sheets as it perfectly simulates an interactive ERP/WMS database without the heavy server costs.*

---

## 3. The Data Flow Design

Here is the topological map of how data moves through the new system:

```text
[Operations Manager]
         │
         ▼ (Updates Stock manually)
[ 📊 Google Sheets Cloud Database ]
         │
         ▼ (API Fetch via gspread)
[ 🐍 Python Data Processing (Pandas) ]
         │
         ▼ (Dynamic ROP/Safety Stock Math)
[ ⚙️ Inventory Simulation Engine ]
         │
         ▼ (Real-time Render)
[ 🖥️ Streamlit Interactive Dashboard ]
```

---

## 4. Google Sheets Integration (Step-by-Step Setup)

Before touching the code, we must give Python the "keys" to your Google Drive.

### Step 1: Create the Google Sheet
1. Open Google Sheets and create a new sheet named `Inventory_Master_Data`.
2. Copy the contents of your `simulation_baseline.csv` and paste it into this sheet.

### Step 2: Get the API Keys (Service Account)
1. Go to the **Google Cloud Console** (console.cloud.google.com).
2. Create a new Project (e.g., "Inventory Dashboard").
3. Search for **Google Drive API** and **Google Sheets API**. Click "Enable" for both.
4. Go to **APIs & Services > Credentials**.
5. Click **Create Credentials > Service Account**.
6. Once created, click on the Service Account, go to the **Keys** tab, and click **Add Key > Create New Key > JSON**.
7. *A `.json` file will download to your computer. This is your master password!*

### Step 3: Connect the Sheet
1. Open the `.json` file you just downloaded. Find the `client_email` address (it looks like a long robot email ending in `gserviceaccount.com`).
2. Go back to your `Inventory_Master_Data` Google Sheet, click the "Share" button, and paste this email. Give it "Editor" access.
3. Rename your downloaded JSON file to `credentials.json` and move it into your `u:\Project\Porto suplaychain` folder. **(Do NOT upload this file to GitHub!)**

---

## 5. Python Implementation

First, install the required library:
```bash
pip install gspread oauth2client
```

Here is the exact Python code snippet you need to add to `app/app.py` to seamlessly replace the CSV loader:

```python
import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Define the scope of the API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

@st.cache_data(ttl=600)  # Caches the data for 10 minutes to prevent API rate limits
def load_data_from_sheets():
    # 1. Authenticate with Google
    creds = ServiceAccountCredentials.from_json_keyfile_name('../credentials.json', scope)
    client = gspread.authorize(creds)
    
    # 2. Open the Sheet and pull data
    sheet = client.open("Inventory_Master_Data").sheet1
    data = sheet.get_all_records()
    
    # 3. Convert directly to Pandas DataFrame
    base_df = pd.DataFrame(data)
    
    # 4. Optional: Still load raw sales from CSV for speed if it's very large
    sales_df = pd.read_csv('../data/raw/sales_data.csv')
    
    return base_df, sales_df

# Replace the old df, sales = load_data() with:
df, sales = load_data_from_sheets()
```

---

## 6. Streamlit Integration (The Refresh Button)

Because we use `@st.cache_data`, Streamlit remembers the Google Sheet to keep the app lightning fast. But what if the manager updates the sheet right now? We add a "Refresh" button at the bottom of the Streamlit Sidebar!

Add this code to your **Sidebar section** in `app.py`:

```python
st.sidebar.markdown('---')
st.sidebar.subheader("📡 Live Database Sync")

if st.sidebar.button("🔄 Refresh Data from Google Sheets"):
    # This clears the Streamlit cache and forces a fresh API call
    st.cache_data.clear()
    st.success("Database Successfully Synced!")
```

---

## 7. Business Use Case Scenarios

When demonstrating this project to a recruiter, tell them this story:
1. **The Phantom Stockout:** "Let's say a warehouse worker notices that 50 units of *Wireless Earbuds* were damaged by a forklift. In a static system, the dashboard wouldn't know."
2. **The Live Update:** "The worker opens the Google Sheet from an iPad on the warehouse floor and changes `current_stock` from 300 to 250."
3. **The Automatic Pivot:** "The Supply Chain Planner clicks 'Refresh' on this Streamlit Dashboard. The system instantly ingests the new 250 stock level, mathematically realizes it has breached the Reorder Point, and flashes a CRITICAL ACTION alert to immediately issue a Purchase Order. **Risk averted.**"

---

## 8. Performance & Limitations

Be prepared to answer technical questions about this architecture:
*   **Latency Cost:** Google Sheets API takes ~1-2 seconds to respond. This is slower than a local CSV.
*   **Capacity Limit:** Google Sheets maxes out at 10 million cells (or ~500,000 rows depending on columns). For standard Enterprise inventory dimensions (thousands of SKUs aggregated daily), this is perfectly fine. If transactional log data exceeds 1 million rows, we must migrate to a Cloud SQL Warehouse (Snowflake / BigQuery).
*   **Rate Limits:** Google restricts API reads to 60 per minute per user. This is why we use Streamlit's `@st.cache_data` feature—it buffers the data locally so the app remains blazing fast as the user moves local simulation sliders.
