import streamlit as st
import pandas as pd
import json
import difflib
import requests

st.set_page_config(page_title="SNAP-TO-SKU", layout="wide", page_icon="📦")

# Standard PIM Schema Definition (Image removed for stability)
SCHEMA_MAPPING = {
    "sku": ["sku", "item_code", "part_number", "product_id", "id"],
    "product_name": ["name", "product_name", "title", "item_name", "description"],
    "category": ["category", "dept", "group", "type", "class"],
    "brand": ["brand", "manufacturer", "mfg", "make", "vendor"],
    "dimensions": ["dimensions", "size", "dims", "measurement", "l_w_h"],
    "weight": ["weight", "wt", "mass", "net_weight"],
    "material": ["material", "composition", "fabric", "construction"],
    "color": ["color", "colour", "shade", "finish"],
    "compliance": ["compliance", "certifications", "standards", "safety"],
    "price": ["price", "cost", "msrp", "retail_price"]
}

def normalize_columns(df):
    """Maps dirty column names to canonical PIM attributes using strict and fuzzy matching."""
    normalized_cols = {}
    lower_cols = {str(col).strip().lower().replace(" ", "_"): col for col in df.columns}
    
    # 1. Strict Alias Matching
    for canonical_name, aliases in SCHEMA_MAPPING.items():
        for alias in aliases:
            if alias in lower_cols:
                normalized_cols[lower_cols[alias]] = canonical_name
                break
                
    # 2. Smart Fuzzy Matching (catches typos)
    unmapped_keys = [k for k in lower_cols.keys() if lower_cols[k] not in normalized_cols.keys()]
    for unmapped in unmapped_keys:
        matches = difflib.get_close_matches(unmapped, SCHEMA_MAPPING.keys(), n=1, cutoff=0.6)
        if matches:
            normalized_cols[lower_cols[unmapped]] = matches[0]
            
    # Apply mapping
    renamed_df = df.rename(columns=normalized_cols)
    
    # 3. Schema Enforcement
    for canonical_name in SCHEMA_MAPPING.keys():
        if canonical_name not in renamed_df.columns:
            renamed_df[canonical_name] = "N/A"
            
    return renamed_df, normalized_cols

def calculate_data_health(row):
    """Calculates completeness score for a product record."""
    total_fields = len(SCHEMA_MAPPING)
    filled_fields = sum(1 for k in SCHEMA_MAPPING.keys() if pd.notna(row.get(k)) and str(row.get(k)).strip() not in ["", "N/A", "nan", "None"])
    return int((filled_fields / total_fields) * 100)

# --- UI HEADER ---
st.title("📦 SNAP-TO-SKU")
st.caption("Automated ingestion, schema normalization, and technical spec sheet generation.")

# --- FILE UPLOADER ---
uploaded_file = st.file_uploader("Upload Raw Supplier Excel or CSV", type=["xlsx", "xls", "csv"])

if uploaded_file:
    # Read file
    if uploaded_file.name.endswith(".csv"):
        raw_df = pd.read_csv(uploaded_file)
    else:
        raw_df = pd.read_excel(uploaded_file)

    st.success(f"Loaded {len(raw_df)} raw records from `{uploaded_file.name}`")

    # Ingestion & Normalization
    clean_df, mapped_cols = normalize_columns(raw_df)
    clean_df["health_score"] = clean_df.apply(calculate_data_health, axis=1)

    # Top Metrics Bar
    col1, col2, col3, col4 = st.columns(4)
    avg_health = int(clean_df["health_score"].mean())
    col1.metric("Total Products", len(clean_df))
    col2.metric("Mapped Attributes", f"{len(mapped_cols)} / {len(SCHEMA_MAPPING)}")
    col3.metric("Catalog Health", f"{avg_health}%")
    col4.metric("Status", "PIM Ready" if avg_health >= 70 else "Needs Enrichment")

    st.divider()

    # --- MAIN VIEW: SELECT & RENDER SPEC SHEET ---
    left_panel, right_panel = st.columns([1, 2])

    with left_panel:
        st.subheader("Data Remediation Grid")
        st.caption("Edit missing or incorrect fields below. Changes update the spec sheet instantly.")
        
        # Interactive Grid
        edited_df = st.data_editor(clean_df, num_rows="dynamic", use_container_width=True, hide_index=True)
        
        # Recalculate health score dynamically after user edits
        edited_df["health_score"] = edited_df.apply(calculate_data_health, axis=1)

        st.write("---")
        st.subheader("Product Selector")
        
        product_options = [f"{row['sku']} - {row['product_name']}" for _, row in edited_df.iterrows()]
        selected_idx = st.selectbox("Select a product to preview:", range(len(product_options)), format_func=lambda x: product_options[x])
        selected_prod = edited_df.iloc[selected_idx]

    with right_panel:
        st.subheader("Standardized Technical Spec Sheet")
        
        # Rule-Based Compliance Flags
        critical_missing = []
        if str(selected_prod['weight']).strip() in ["N/A", "", "nan", "None"]: critical_missing.append("Weight (required for shipping)")
        if str(selected_prod['price']).strip() in ["N/A", "", "nan", "None"]: critical_missing.append("Base Price")
        
        if critical_missing:
            st.error(f"⚠️ **Syndication Blocked:** Missing critical fields: {', '.join(critical_missing)}")
        else:
            st.success("✅ **Cleared for Syndication:** All critical attributes present.")
        
        # Spec Sheet Card
        with st.container(border=True):
            head_col1, head_col2 = st.columns([3, 1])
            
            with head_col1:
                st.markdown(f"### {selected_prod['product_name']}")
                st.caption(f"**Brand:** {selected_prod['brand']} | **Category:** {selected_prod['category']}")
            
            with head_col2:
                # Dynamic QR Code
                sku_safe = str(selected_prod['sku']).replace(" ", "%20")
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data={sku_safe}"
                st.image(qr_url, caption="SKU QR Code", width=80)
                
                # Health Badge
                health = selected_prod['health_score']
                badge_color = "green" if health >= 80 else ("orange" if health >= 50 else "red")
                st.markdown(f"**Completeness:** :{badge_color}[**{health}%**]")

            st.write("---")

            # Technical Specifications Grid
            spec_col1, spec_col2 = st.columns(2)
            with spec_col1:
                st.markdown("**Identification & Pricing**")
                st.write(f"• **SKU / Model:** `{selected_prod['sku']}`")
                st.write(f"• **Base Price:** `${selected_prod['price']}`")
                st.write(f"• **Color / Finish:** {selected_prod['color']}")

            with spec_col2:
                st.markdown("**Physical & Regulatory Specs**")
                st.write(f"• **Dimensions:** {selected_prod['dimensions']}")
                st.write(f"• **Weight:** {selected_prod['weight']}")
                st.write(f"• **Primary Material:** {selected_prod['material']}")
                st.write(f"• **Compliance / Certs:** `{selected_prod['compliance']}`")

        # Export Actions
        export_col1, export_col2 = st.columns(2)
        with export_col1:
            prod_json = selected_prod[list(SCHEMA_MAPPING.keys())].to_dict()
            st.download_button(
                label="📥 Export Product JSON",
                data=json.dumps(prod_json, indent=2),
                file_name=f"{selected_prod['sku']}_spec_sheet.json",
                mime="application/json"
            )
        with export_col2:
            # Export the EDITED dataframe so manual fixes are saved
            csv_export = edited_df[list(SCHEMA_MAPPING.keys())].to_csv(index=False)
            st.download_button(
                label="📊 Export Full Catalog (CSV)",
                data=csv_export,
                file_name="remediated_pim_catalog.csv",
                mime="text/csv"
            )

        # --- LIVE WOOCOMMERCE API PUSH ---
        st.write("---")
        st.subheader("🚀 Live WooCommerce Syndication")
        
        # UI for API Credentials
        woo_url = st.text_input("Store URL", placeholder="https://your-site.tastewp.com")
        woo_key = st.text_input("Consumer Key", type="password")
        woo_secret = st.text_input("Consumer Secret", type="password")

        # Disable button if syndication is blocked (forces user to fix data first!)
        is_blocked = len(critical_missing) > 0
        
        if st.button("Push Product to Live Store", disabled=is_blocked):
            if not woo_url or not woo_key or not woo_secret:
                st.warning("⚠️ Enter your Store URL and API keys above.")
            else:
                # 1. Map our normalized PIM data to WooCommerce's exact JSON schema
                woo_payload = {
                    "name": selected_prod['product_name'],
                    "type": "simple",
                    "regular_price": str(selected_prod['price']),
                    "description": f"<strong>Material:</strong> {selected_prod['material']}<br><strong>Color:</strong> {selected_prod['color']}<br><strong>Compliance:</strong> {selected_prod['compliance']}",
                    "short_description": f"Brand: {selected_prod['brand']}",
                    "sku": selected_prod['sku'],
                    "weight": str(selected_prod['weight']).replace("kg", "").replace("g", "").strip()
                }

                # 2. Build the API Endpoint
                endpoint = f"{woo_url.rstrip('/')}/wp-json/wc/v3/products"
                
                # 3. Fire the request
                try:
                    with st.spinner("Syncing to WooCommerce..."):
                        # Send keys in the URL parameters instead of headers to bypass server blocks
                        response = requests.post(
                            endpoint,
                            json=woo_payload,
                            params={
                                "consumer_key": woo_key.strip(),
                                "consumer_secret": woo_secret.strip()
                            }
                        )
                    
                    # 4. Handle the response
                    if response.status_code in [200, 201]: 
                        st.success("✅ Successfully published to WooCommerce!")
                        st.balloons()
                        live_url = response.json().get('permalink')
                        st.markdown(f"[**👉 Click here to view the live product in the store!**]({live_url})")
                    else:
                        st.error(f"❌ WooCommerce API Error: {response.text}")
                except Exception as e:
                    st.error(f"❌ Connection Error: {e}")
else:
    st.info("👆 Upload an Excel or CSV file to view the live normalization pipeline.")