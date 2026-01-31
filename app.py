import streamlit as st
import pandas as pd
import glob
import os

st.set_page_config(page_title="BASIL RFI Dashboard", layout="wide", page_icon="🏗️")

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

st.title("🏗️ BASIL PROJECT: RFI Dashboard")

try:
    full_df = load_all_data()
    
    if not full_df.empty:
        st.subheader("📊 Status by Tab")
        tabs_in_data = full_df['Source Tab'].unique()
        
        for tab in tabs_in_data:
            with st.expander(f"Status for {tab}"):
                tab_data = full_df[full_df['Source Tab'] == tab].copy()
                total = len(tab_data)
                
                if 'Status' in tab_data.columns:
                    # FIX: Force Status to string to avoid the ".str accessor" error
                    status_col = tab_data['Status'].astype(str)
                    
                    acc = len(tab_data[status_col.str.contains('Accepted', na=False, case=False)])
                    ong = len(tab_data[status_col.str.contains('Ongoing', na=False, case=False)])
                    can = len(tab_data[status_col.str.contains('Cancelled', na=False, case=False)])
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Accepted", acc)
                    c1.progress(acc/total if total > 0 else 0)
                    c2.metric("Ongoing", ong)
                    c2.progress(ong/total if total > 0 else 0)
                    c3.metric("Cancelled", can)
                    c3.progress(can/total if total > 0 else 0)
                else:
                    st.warning("Column 'Status' not found.")

        st.markdown("---")
        query = st.text_input("Search keywords (e.g., 'C300 concrete'):")
        if query:
            keywords = query.split()
            results = full_df.copy()
            for word in keywords:
                # FIX: Force entire row to string for universal search
                mask = results.apply(lambda row: row.astype(str).str.contains(word, case=False).any(), axis=1)
                results = results[mask]
            
            if not results.empty:
                st.success(f"Found {len(results)} matches.")
                display_cols = ['RFI No.', 'Work Item', 'Status', 'Location', 'Source Tab']
                st.dataframe(results[display_cols], use_container_width=True, hide_index=True)
            else:
                st.warning("No matches found.")
    else:
        st.error("No Excel files found in the repository. Please upload your .xlsx files to GitHub.")

except Exception as e:
    st.error(f"Unexpected Error: {e}")
