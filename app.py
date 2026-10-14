import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="PIM SpecSheet Generator", layout="wide", page_icon="📦")

# Standard PIM Schema Definition with known supplier aliases
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
    """Maps dirty column names to canonical PIM attributes."""
    normalized_cols = {}
    lower_cols = {col.strip().lower().replace(" ", "_"): col for col in df.columns}
    
    for canonical_name, aliases in SCHEMA_MAPPING.items():
        for alias in aliases:
            if alias in lower_cols:
                normalized_cols[lower_cols[alias]] = canonical_name
                break
                
    renamed_df = df.rename(columns=normalized_cols)
    
    # Ensure all canonical fields exist even if missing from raw data
    for canonical_name in SCHEMA_MAPPING.keys():
        if canonical_name not in renamed_df.columns:
            renamed_df[canonical_name] = "N/A"
            
    return renamed_df, normalized_cols

def calculate_data_health(row):
    """Calculates completeness score for a product record."""
    total_fields = len(SCHEMA_MAPPING)
    filled_fields = sum(1 for k in SCHEMA_MAPPING.keys() if pd.notna(row.get(k)) and str(row.get(k)).strip() not in ["", "N/A", "nan"])
    return int((filled_fields / total_fields) * 100)

# --- UI HEADER ---
st.title("📦 Excel-to-PIM Spec Sheet Generator")
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
        st.subheader("Product Catalog")
        product_options = [f"{row['sku']} - {row['product_name']}" for _, row in clean_df.iterrows()]
        selected_idx = st.selectbox("Select a product to preview:", range(len(product_options)), format_func=lambda x: product_options[x])
        selected_prod = clean_df.iloc[selected_idx]

        st.write("---")
        st.subheader("Raw Data Preview")
        st.dataframe(raw_df.iloc[[selected_idx]], use_container_width=True)

    with right_panel:
        st.subheader("Standardized Technical Spec Sheet")
        
        # Spec Sheet Card
        with st.container(border=True):
            head_col1, head_col2 = st.columns([3, 1])
            head_col1.markdown(f"### {selected_prod['product_name']}")
            head_col1.caption(f"**Brand:** {selected_prod['brand']} | **Category:** {selected_prod['category']}")
            
            # Health Badge
            health = selected_prod['health_score']
            badge_color = "green" if health >= 80 else ("orange" if health >= 50 else "red")
            head_col2.markdown(f"**Data Completeness**")
            head_col2.markdown(f":{badge_color}[### {health}%]")

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
                label="📥 Export Product JSON (PIM API Payload)",
                data=json.dumps(prod_json, indent=2),
                file_name=f"{selected_prod['sku']}_spec_sheet.json",
                mime="application/json"
            )
        with export_col2:
            csv_export = clean_df[list(SCHEMA_MAPPING.keys())].to_csv(index=False)
            st.download_button(
                label="📊 Export Full Normalized Catalog (CSV)",
                data=csv_export,
                file_name="normalized_pim_catalog.csv",
                mime="text/csv"
            )
else:
    st.info("👆 Upload an Excel or CSV file to view the live normalization pipeline.")