import streamlit as st
import pandas as pd
import glob
import os

st.set_page_config(page_title="BASIL Master RFI Search", layout="wide", page_icon="🏗️")

@st.cache_data
def load_all_data():
    all_files = glob.glob("*.xlsx")
    combined_list = []
    for file in all_files:
        try:
            all_sheets = pd.read_excel(file, sheet_name=None, header=None)
            for sheet_name, df in all_sheets.items():
                mask = df.isin(['Work Item']).any(axis=1)
                if mask.any():
                    header_idx = df[mask].index[0]
                    new_df = pd.read_excel(file, sheet_name=sheet_name, header=header_idx)
                    new_df.columns = new_df.columns.astype(str).str.strip()
                    new_df['Source File'] = file
                    new_df['Source Tab'] = sheet_name
                    combined_list.append(new_df)
        except Exception:
            continue
    return pd.concat(combined_list, ignore_index=True) if combined_list else pd.DataFrame()

st.title("BASIL PROJECT: RFI Dashboard")

try:
    full_df = load_all_data()
    
    if not full_df.empty:
        # --- NEW PROGRESS SECTION ---
        st.subheader("📊 Status by Tab")
        tabs_in_data = full_df['Source Tab'].unique()
        
        # Create a grid to show status for each tab
        for tab in tabs_in_data:
            with st.expander(f"Status for {tab}"):
                tab_data = full_df[full_df['Source Tab'] == tab]
                total = len(tab_data)
                
                # Count statuses (assumes you have a column named 'Status')
                # If your column is named differently, change 'Status' below
                if 'Status' in tab_data.columns:
                    acc = len(tab_data[tab_data['Status'].str.contains('Accepted', na=False, case=False)])
                    ong = len(tab_data[tab_data['Status'].str.contains('Ongoing', na=False, case=False)])
                    can = len(tab_data[tab_data['Status'].str.contains('Cancelled', na=False, case=False)])
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Accepted", f"{acc}")
                    col1.progress(acc/total if total > 0 else 0)
                    
                    col2.metric("Ongoing", f"{ong}")
                    col2.progress(ong/total if total > 0 else 0)
                    
                    col3.metric("Cancelled", f"{can}")
                    col3.progress(can/total if total > 0 else 0)
                else:
                    st.write("No 'Status' column found in this tab.")
        
        st.markdown("---")
        # --- SEARCH SECTION ---
        query = st.text_input("Search keywords (e.g., 'C300 concrete'):")
        if query:
            keywords = query.split()
            results = full_df.copy()
            for word in keywords:
                mask = results.apply(lambda row: row.astype(str).str.contains(word, case=False).any(), axis=1)
                results = results[mask]
            
            if not results.empty:
                st.dataframe(results[['RFI No.', 'Work Item', 'Status', 'Location', 'Source Tab']], use_container_width=True)
            else:
                st.warning("No matches found.")

except Exception as e:
    st.error(f"Error: {e}")
