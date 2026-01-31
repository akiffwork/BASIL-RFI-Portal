import streamlit as st
import pandas as pd
import glob
import os

# 1. Page Setup
st.set_page_config(page_title="BASIL Master RFI Search", layout="wide", page_icon="🏗️")

@st.cache_data
def load_all_data():
    # Finds all Excel files in the current folder
    all_files = glob.glob("*.xlsx")
    combined_list = []
    
    for file in all_files:
        try:
            # Read every tab in the file
            all_sheets = pd.read_excel(file, sheet_name=None, header=None)
            for sheet_name, df in all_sheets.items():
                # Locate 'Work Item' to find the header row
                mask = df.isin(['Work Item']).any(axis=1)
                if mask.any():
                    header_idx = df[mask].index[0]
                    new_df = pd.read_excel(file, sheet_name=sheet_name, header=header_idx)
                    
                    # Clean column names
                    new_df.columns = new_df.columns.astype(str).str.strip()
                    new_df['Source File'] = file
                    new_df['Source Tab'] = sheet_name
                    combined_list.append(new_df)
        except Exception:
            continue
            
    return pd.concat(combined_list, ignore_index=True) if combined_list else pd.DataFrame()

# 2. UI Header
st.title("BASIL PROJECT: Master RFI Portal")
st.markdown("Search across all files using **multiple keywords** (e.g., *'C300 concrete'*).")

try:
    full_df = load_all_data()
    
    if not full_df.empty:
        # 3. Multi-Keyword Search Bar
        query = st.text_input("Enter keywords (separated by spaces):")
        
        if query:
            keywords = query.split()
            results = full_df.copy()
            
            # Narrow down results for each keyword
            for word in keywords:
                mask = results.apply(lambda row: row.astype(str).str.contains(word, case=False).any(), axis=1)
                results = results[mask]
            
            if not results.empty:
                st.success(f"Found {len(results)} matches.")
                # Customize which columns to display
                cols = ['RFI No.', 'Work Item', 'Detail Item', 'Location', 'Source File']
                st.dataframe(results[cols], use_container_width=True, hide_index=True)
            else:
                st.warning("No records contain all those keywords.")
    else:
        st.error("No valid Excel files found. Check your folder!")
except Exception as e:
    st.error(f"Error: {e}")