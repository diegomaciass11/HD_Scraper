import streamlit as st
from scraper import scrape_product_info
import pandas as pd
import datetime

st.title("Home Depot Product Info by SKU")

# Initialize products_df if not present or cleared
if "products_df" not in st.session_state or st.session_state.get("clear_table", False):
    st.session_state.products_df = pd.DataFrame()
    st.session_state.clear_table = False  # reset the flag

# Clear table button sets the clear flag
if st.button("Clear Table"):
    st.session_state.clear_table = True

# SKU Input
sku_input = st.text_area("Enter SKUs (one per line):")

# Function to score product
def score_product(row):
    score = 0
    try:
        if row.get("Price", 0) < 500:
            score += 1
        if row.get("Rating", 0) > 4:
            score += 1
        if row.get("Availability", "").lower() == "in stock":
            score += 1
    except:
        pass
    return score

# Main Table Display
table_placeholder = st.empty()
if not st.session_state.products_df.empty:
    df = st.session_state.products_df.copy()
    
    # Add Product Score Column
    df["Score"] = df.apply(score_product, axis=1)
    
    table_placeholder.dataframe(df)

    # CSV Export Button
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Results as CSV", csv, "home_depot_products.csv", "text/csv")

    # Charts in Sidebar
    if st.sidebar.checkbox("📊 Show Price Chart"):
        if "Price" in df.columns:
            st.sidebar.bar_chart(df["Price"])

# Scraping Logic
if st.button("Get Info for All SKUs"):
    sku_list = [sku.strip() for sku in sku_input.splitlines() if sku.strip()]

    if not sku_list:
        st.warning("Please enter at least one valid SKU.")
    else:
        all_new_data = []

        for i, sku in enumerate(sku_list, start=1):
            with st.spinner(f"Scraping SKU {i}/{len(sku_list)}: {sku}"):
                try:
                    product_info = scrape_product_info(sku)
                    if isinstance(product_info, dict):
                        all_new_data.append(product_info)
                    else:
                        st.warning(f"⚠️ SKU {sku} returned invalid data.")
                except Exception as e:
                    st.error(f"❌ Error scraping {sku}: {e}")

        # Filter out invalid or empty results
        valid_data = [row for row in all_new_data if isinstance(row, dict) and row]

        if valid_data:
            new_df = pd.DataFrame(valid_data)
            st.session_state.products_df = pd.concat(
                [st.session_state.products_df, new_df], ignore_index=True
            )
        else:
            st.warning("No valid data was retrieved from the provided SKUs.")

