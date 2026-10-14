# Jordan_Kilowott

📦 Excel-to-PIM Spec Sheet Generator
An automated inbound integration engine that ingests inconsistent supplier spreadsheets (Excel/CSV), normalizes attributes against canonical PIM schemas, calculates product data completeness, and renders standardized technical specification sheets with live WooCommerce REST API syndication.


🚀 Quick Start (Execute in 3 Minutes)
1. Prerequisites
Ensure you have Python 3.8+ installed.
2. Set Up Virtual Environment (Recommended)
On Windows (PowerShell / Command Prompt):

python -m venv venv

venv\Scripts\activate

On macOS/Linux:

python3 -m venv venv

source venv/bin/activate
3. Install Required Dependencies
The engine relies on Streamlit for the frontend, Pandas for data normalization, and Requests for API syndication.

pip install streamlit pandas requests openpyxl

(Note: openpyxl is required for Pandas to read Excel files).
4. Run the Engine
Execute the following command to launch the local Streamlit server:

streamlit run app.py

The interface will automatically open in your default browser at http://localhost:8501.


🏗️ Architecture & Features
1. Smart Schema Normalization
The engine utilizes a hybrid strict-alias and fuzzy-matching logic (difflib) to map chaotic supplier column headers (e.g., wt, shade, dept) to standardized canonical PIM schema attributes (e.g., weight, color, category).
2. Human-in-the-Loop Remediation Grid
Built-in rule validation blocks outbound syndication if critical fields (like Base Price or Weight) are missing. Users can instantly remediate errors via the live UI data grid, which recalculates catalog health dynamically.
3. Live E-Commerce Syndication
Fully integrated with the WooCommerce REST API. Once a product reaches 100% data health, the system packages the remediated data into a compliant JSON payload and pushes it instantly to a live storefront.
🧪 Testing the Pipeline
Generate test data using python generate_test_data.py.
Upload the resulting messy_supplier_data.xlsx into the UI.
Observe the "Syndication Blocked" error on incomplete products.
Add the missing data into the grid to clear the block.
Enter your WooCommerce Store URL, Consumer Key, and Consumer Secret, then click "Push Product to Live Store" to see the live deployment.

```bash
python -m venv venv
venv\Scripts\activate

Site name: Compile Carriage
URL: https://compilecarriage.s3-tastewp.com
Username: admin
Password: acR7vWUCB2E

Key: ck_06b90519219c7474a55515658e4fd3aa069264dc
Secret: cs_caf1773a0d1132831476cb5744d7e0ce3b254c8f