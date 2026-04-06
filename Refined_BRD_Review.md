# BRD Review & Refinement Report

## 1. Key Issues Identified in the Original BRD

*   **Missing MVP Boundaries:** The original BRD treated everything as an equal priority. Jumping straight into advanced time-series analysis while simultaneously building a Streamlit optimization engine is a major risk for a 2-to-4 week timeline.
*   **Data Feasibility Risks:** The original document assumed the availability of accurate "Holding Costs" and "Ordering Costs." Publicly available retail datasets (like Kaggle’s UCI Retail or Brazilian E-Commerce) rarely include these. The BRD must account for industry-standard assumptions or proxy values.
*   **Overly Broad "What-If" Interactivity:** Allowing users to change too many variables at once makes the UI cluttered and the backend logic brittle. The scenarios should be constrained to the most impactful business levers.
*   **Lack of Testable Functional Requirements:** Stating the system "displays visual charts" is too vague. Requirements must specify exactly what actions the user takes and what specific output the system generates.

---

## 2. Refined BRD (Improved Version)

### **Project Title:** Interactive Inventory Optimization & Decision Support System

### **1. Executive Summary**
This project delivers a web-based decision-support tool that helps E-commerce supply chain planners balance stock availability with inventory holding costs. By combining historical demand baseline calculations with an interactive "What-If" simulation engine, the tool empowers users to set data-driven targets for Safety Stock and Reorder Points (ROP), ensuring readiness for demand spikes while mitigating excess working capital tie-up.

### **2. Business Problem**
Inventory planners often rely on static historical averages that fail during high-volatility events (e.g., flash sales, supplier delays). This leads to two costly extremes:
1.  **Stockouts:** Lost revenue and damaged customer trust during demand surges.
2.  **Overstock:** Excessive warehousing costs and dead capital after peak periods subside.

### **3. Objectives**
*   **Provide visibility:** Visualize baseline historical demand patterns.
*   **Enable agility:** Allow planners to simulate how unexpected changes (e.g., +20% demand, +5 days lead time) impact required stock levels.
*   **Automate calculation:** Dynamically generate precise Safety Stock and Reorder Point targets based on simulated parameters.

### **4. Scope**
**In-Scope:**
*   Ingestion of historical sales transaction data (CSV).
*   Calculation of baseline daily demand and standard deviation.
*   Interactive UI (Streamlit) featuring adjustable simulation sliders (e.g., Lead Time, Demand Multiplier, Target Service Level).
*   Dynamic calculation of Safety Stock and Reorder Point.

**Out-of-Scope:**
*   Complex machine learning forecasting models (e.g., Prophet, LSTM).
*   Live ERP/WMS database integration; financial accounting workflows.

### **5. Target Audience**
*   **Primary:** Inventory Planners & Supply Chain Analysts (Users of the tool).
*   **Secondary:** E-commerce Operations Leadership (Consumers of the insights).

### **6. Functional Requirements**
*   **FR1 - Data Ingestion:** The system shall accept a standard CSV file of historical sales (Date, Item ID, Quantity).
*   **FR2 - Parameter Controls:** The user interface shall provide sliders to adjust:
    *   Target Service Level (e.g., 90% - 99%)
    *   Supplier Lead Time (Days)
    *   Demand Multiplier (e.g., 1.0x baseline, 1.5x promo spike)
*   **FR3 - Engine Calculation:** Upon parameter adjustment, the system shall instantly (< 1 second) recalculate the required Safety Stock and Reorder Point.
*   **FR4 - Visualization:** The dashboard shall render a line chart comparing "Current Inventory Position" against the "Simulated Reorder Point" to highlight stockout risks.

### **7. Non-Functional Requirements**
*   **Usability:** Clean, single-page Streamlit application requiring zero coding knowledge from the end-user.
*   **Performance:** Calculations and visualizations must execute with low latency to support an interactive "what-if" experience.

### **8. Data Requirements & Assumptions**
*   **Data Structure:** Requires transactional grain (Date, Item, Quantity).
*   **Assumption - Standardized Cost Proxies:** If holding/ordering cost data is completely absent from the public dataset, the system will assume an industry-standard holding cost of 20% of item value annually, or exclude EOQ from the MVP entirely to focus on Safety Stock/ROP.

### **9. Success Metrics (Portfolio Validation)**
*   **Scenario Coverage:** The app successfully simulates at least 3 distinct business scenarios (e.g., Holiday Spike, Supplier Delay, Normal Operations).
*   **Performance:** Dashboard responds to slider inputs in under 1 second.
*   **Actionability:** Outputs are clear enough that a non-technical recruiter can understand the business recommendation.

---

## 3. MVP Definition

To ensure this project is achievable and high-impact within a 2-4 week sprint, it is divided strictly into MVP and Future Enhancements.

### **Core Features (Must-Have / MVP)**
1.  **Static Data Load:** Hand-picked, pre-cleaned dummy dataset (e.g., standard retail sales CSV) loaded directly into Pandas.
2.  **Baseline Statistics:** Simple calculation of Average Daily Demand and Demand Standard Deviation (historical baseline).
3.  **The "Big Three" Sliders:** Interactivity limited strictly to Target Service Level (Z-score), Lead Time (Days), and Demand Multiplier (%).
4.  **Core Outputs:** Dynamic display of **Safety Stock** and **Reorder Point (ROP)** formulas.
5.  **Vizualization:** A clear, interactive Plotly/Altair chart showing the demand distribution and where the ROP sits.

### **Optional Enhancements (Nice-to-Have / Post-MVP)**
1.  **EOQ (Economic Order Quantity) Calculation:** Only if unit cost and holding cost data can be accurately sourced or simulated.
2.  **Advanced ML Forecasting:** Replacing "Average Daily Demand" with an ARIMA or Prophet time-series prediction.
3.  **Multi-Item Selection:** A dropdown allowing the user to switch the simulation between different SKUs.

---

## 4. Recommendations for Portfolio Positioning

When publishing this to LinkedIn or discussing it in an interview, do not just say "I built a Python dashboard." Frame it around **business impact and strategic decision-making**.

**Angle 1: "Bridging the Gap Between Data and Operations"**
*   *Pitch:* "Data is useless if operators can't interact with it. I built this Streamlit application to hand the power of statistical modeling directly to Inventory Planners, allowing them to simulate supply chain shocks without needing to write a single line of Python."

**Angle 2: "Proactive Risk Mitigation over Reactive Reporting"**
*   *Pitch:* "Most dashboards just show what happened yesterday. I designed this tool to look forward. By allowing planners to simulate a 30% surge in demand or a 5-day supplier delay, the system acts as an early warning system to prevent revenue-killing stockouts."

**Angle 3: "Agile Supply Chain Optimization"**
*   *Pitch:* "In volatile e-commerce environments, static 'Safety Stock' numbers get businesses into trouble. I engineered a robust what-if engine using Python to dynamically recalculate inventory targets, directly targeting working capital efficiency."
