import streamlit as st
import pandas as pd
import numpy as np
import os
from io import BytesIO
import warnings

# Suppress SettingWithCopyWarning
warnings.filterwarnings('ignore', category=pd.errors.SettingWithCopyWarning)

def main():
    # Set page configuration
    st.set_page_config(page_title="Jainam Data Processor", layout="centered")

    # Custom CSS for styling
    st.markdown("""
    <style>
    body {
        font-family: 'Poppins', sans-serif;
    }
    .stApp {
        background: linear-gradient(135deg, #6b7280 0%, #1e3a8a 100%);
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 1rem;
    }
    .container {
        background: white;
        border-radius: 1.5rem;
        box-shadow: 0 15px 30px rgba(0, 0, 0, 0.2);
        padding: 2.5rem;
        max-width: 28rem;
        width: 100%;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .header h1 {
        font-size: 2rem;
        font-weight: 700;
        color: #1e40af;
        background: linear-gradient(to right, #1e40af, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        background: linear-gradient(90deg, #3b82f6, #1e40af);
        border: none;
        border-radius: 0.75rem;
        padding: 0.75rem 1.5rem;
        font-size: 1rem;
        font-weight: 600;
        color: white;
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #1e40af, #1e3a8a);
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    }
    .stButton>button:disabled {
        background: #9ca3af;
        cursor: not-allowed;
        transform: none;
        box-shadow: none;
    }
    .stFileUploader>div>div>input {
        background: #f8fafc;
        border: 2px dashed #d1d5db;
        border-radius: 0.75rem;
        padding: 1rem;
        transition: all 0.3s ease;
    }
    .stFileUploader>div>div>input:hover {
        border-color: #3b82f6;
        background: #eff6ff;
    }
    .stTextInput>div>input, .stDateInput>div>input {
        background: #f8fafc;
        border: 2px solid #d1d5db;
        border-radius: 0.75rem;
        padding: 1rem;
        transition: all 0.3s ease;
    }
    .stTextInput>div>input:hover, .stDateInput>div>input:hover {
        border-color: #3b82f6;
        background: #eff6ff;
    }
    .error-message {
        background: #fee2e2;
        border: 1px solid #ef4444;
        border-radius: 0.5rem;
        padding: 1rem;
        color: #b91c1c;
        font-weight: 500;
        margin-top: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # UI Layout
    st.markdown('<div class="container">', unsafe_allow_html=True)
    st.markdown('<div class="header"><h1>Jainam Data Processor</h1></div>', unsafe_allow_html=True)

    # File uploaders and input fields
    file1 = st.file_uploader("Compiled MTM Sheet (Excel)", type=["xlsx", "csv"])
    file2 = st.file_uploader("Jainam Daily Allocation (Excel)", type=["xlsx", "csv"])
    file3 = st.file_uploader("Updated JAINAM DAILY (Excel)", type=["xlsx", "csv"])
    sheet_name = st.text_input("Sheet Name (e.g., JULY 2025)")
    date = st.date_input("Date")

    # Process button
    if st.button("Process Files", key="process_btn"):
        if not all([file1, file2, file3, sheet_name, date]):
            st.markdown('<div class="error-message">All fields are required.</div>', unsafe_allow_html=True)
            return

        with st.spinner("Processing your files..."):
            try:
                # Determine file type and read accordingly
                def read_file(file, sheet=None):
                    ext = os.path.splitext(file.name)[1].lower()
                    try:
                        if ext in ['.xlsx', '.xls']:
                            if sheet is None:
                                return pd.read_excel(file, sheet_name=0, engine='openpyxl')
                            return pd.read_excel(file, sheet_name=sheet, engine='openpyxl')
                        elif ext == '.csv':
                            return pd.read_csv(file)
                        else:
                            return f"Invalid file format for {file.name}. Please upload CSV or Excel files."
                    except Exception as e:
                        return f"Error reading file {file.name}: {str(e)}"

                # Read the files
                df1 = read_file(file1)
                df2 = read_file(file2, sheet='Record')
                df3 = read_file(file3, sheet=sheet_name)

                # Check for file reading errors
                for df, name in [(df1, 'file1'), (df2, 'file2'), (df3, 'file3')]:
                    if isinstance(df, str):
                        st.markdown(f'<div class="error-message">{df}</div>', unsafe_allow_html=True)
                        return
                    if df is None:
                        st.markdown(f'<div class="error-message">Invalid file format for {name}. Please upload CSV or Excel files.</div>', unsafe_allow_html=True)
                        return
                    if not isinstance(df, pd.DataFrame):
                        st.markdown(f'<div class="error-message">Error: {name} did not load as a DataFrame. Got type {type(df)}.</div>', unsafe_allow_html=True)
                        return
                    if df.empty:
                        st.markdown(f'<div class="error-message">File {name} is empty.</div>', unsafe_allow_html=True)
                        return

                # Process df3 to extract mtm_df, capital_deployed_df, max_loss_df
                try:
                    mtm_row_index = df3[df3["Unnamed: 0"] == "MTM"].index[0]
                    capital_deployed_row_index = df3[df3["Unnamed: 0"] == "Capital Deployed"].index[0]
                    max_loss_row_index = df3[df3["Unnamed: 0"] == "Max SL"].index[0]
                    AVG_row_index = df3[df3["Unnamed: 0"] == "AVG %"].index[0]
                except IndexError:
                    st.markdown('<div class="error-message">Error: Required sections (MTM, Capital Deployed, Max SL, AVG %) not found in file3.</div>', unsafe_allow_html=True)
                    return

                mtm_df = df3.iloc[mtm_row_index:capital_deployed_row_index + 1]
                capital_deployed_df = df3.iloc[capital_deployed_row_index:max_loss_row_index + 1]
                max_loss_df = df3.iloc[max_loss_row_index:AVG_row_index + 1]

                # Process mtm_df
                mtm_df = mtm_df.drop(index=mtm_df.index[0]).reset_index(drop=True)
                mtm_df.columns = mtm_df.iloc[0]
                mtm_df = mtm_df.drop(index=0).reset_index(drop=True)
                mtm_df = mtm_df[:-1]
                if 'IDs' not in mtm_df.columns:
                    st.markdown('<div class="error-message">Error: \'IDs\' column not found in MTM section of file3.</div>', unsafe_allow_html=True)
                    return
                non_null_ids = mtm_df['IDs'].dropna().tolist()

                # Process capital_deployed_df
                capital_deployed_df = capital_deployed_df.drop(index=capital_deployed_df.index[0]).reset_index(drop=True)
                capital_deployed_df.columns = capital_deployed_df.iloc[0]
                capital_deployed_df = capital_deployed_df.drop(index=0).reset_index(drop=True)
                capital_deployed_df = capital_deployed_df[:-1]
                if 'IDs' not in capital_deployed_df.columns:
                    st.markdown('<div class="error-message">Error: \'IDs\' column not found in Capital Deployed section of file3.</div>', unsafe_allow_html=True)
                    return

                # Process max_loss_df
                max_loss_df = max_loss_df.drop(index=max_loss_df.index[0]).reset_index(drop=True)
                max_loss_df.columns = max_loss_df.iloc[0]
                max_loss_df = max_loss_df.drop(index=0).reset_index(drop=True)
                max_loss_df = max_loss_df[:-1]
                if 'IDs' not in max_loss_df.columns:
                    st.markdown('<div class="error-message">Error: \'IDs\' column not found in Max SL section of file3.</div>', unsafe_allow_html=True)
                    return

                # Filter df1 based on non_null_ids
                if 'UserID' not in df1.columns:
                    st.markdown('<div class="error-message">Error: \'UserID\' column not found in file1.</div>', unsafe_allow_html=True)
                    return
                df_new = df1[df1["UserID"].isin(non_null_ids)]
                try:
                    df_new['Date'] = pd.to_datetime(df_new['Date'])
                except Exception as e:
                    st.markdown(f'<div class="error-message">Error converting Date column in file1: {str(e)}</div>', unsafe_allow_html=True)
                    return

                # Filter by date
                try:
                    match_date = pd.to_datetime(date)
                except Exception as e:
                    st.markdown(f'<div class="error-message">Invalid date format: {date}. Please use YYYY-MM-DD.</div>', unsafe_allow_html=True)
                    return
                matched_rows = df_new[df_new['Date'].dt.date == match_date.date()]
                if matched_rows.empty:
                    st.markdown(f'<div class="error-message">No data found for date {date} in file1.</div>', unsafe_allow_html=True)
                    return

                # Drop unnecessary columns
                cols_to_drop = ['Date', 'SNO', 'Enabled', 'LoggedIn', 'SqOff Done',
                                'Broker', 'Qty Multiplier', 'Available Margin', 'Total Orders',
                                'Total Lots', 'SERVER', 'Unnamed: 16', 'Unnamed: 17',
                                'Unnamed: 18', 'Unnamed: 19', 'Unnamed: 20']
                matched_rows = matched_rows.drop(columns=[col for col in cols_to_drop if col in matched_rows.columns])

                # Map values to dataframes
                if 'MTM (All)' not in matched_rows.columns:
                    st.markdown('<div class="error-message">Error: \'MTM (All)\' column not found in file1.</div>', unsafe_allow_html=True)
                    return
                mtm_df['mtm'] = mtm_df['IDs'].map(matched_rows.set_index('UserID')['MTM (All)'])
                if 'ALLOCATION' not in matched_rows.columns:
                    st.markdown('<div class="error-message">Error: \'ALLOCATION\' column not found in file1.</div>', unsafe_allow_html=True)
                    return
                capital_deployed_df['Allocation'] = (capital_deployed_df['IDs'].map(matched_rows.set_index('UserID')['ALLOCATION']) * 100)
                if 'MAX LOSS' not in matched_rows.columns:
                    st.markdown('<div class="error-message">Error: \'MAX LOSS\' column not found in file1.</div>', unsafe_allow_html=True)
                    return
                max_loss_df['max_loss'] = max_loss_df['IDs'].map(matched_rows.set_index('UserID')['MAX LOSS'])

                # Filter out invalid rows
                mtm_df = mtm_df[mtm_df['IDs'].notna() & (mtm_df['IDs'] != '')]
                capital_deployed_df = capital_deployed_df[capital_deployed_df['IDs'].notna() & (capital_deployed_df['IDs'] != '')]

                # Expand mtm_df with alias rows
                alias_values = ['PS', 'VT', 'GB', 'RD', 'RM']
                new_rows = []
                for _, row in mtm_df.iterrows():
                    new_rows.append(row.to_dict())
                    for alias in alias_values:
                        empty_row = {col: np.nan for col in mtm_df.columns}
                        empty_row['Alais'] = alias
                        new_rows.append(empty_row)
                mtm_df = pd.DataFrame(new_rows).reset_index(drop=True)
                mtm_df['Alias'] = mtm_df['Alias'].fillna(mtm_df['Alais'])
                mtm_df = mtm_df.drop(columns=['Alais'])

                # Expand capital_deployed_df with alias rows
                new_rows = []
                for _, row in capital_deployed_df.iterrows():
                    new_rows.append(row.to_dict())
                    for alias in alias_values:
                        empty_row = {col: np.nan for col in capital_deployed_df.columns}
                        empty_row['Alais'] = alias
                        new_rows.append(empty_row)
                capital_deployed_df = pd.DataFrame(new_rows).reset_index(drop=True)
                capital_deployed_df['Alias'] = capital_deployed_df['Alias'].fillna(capital_deployed_df['Alais'])
                capital_deployed_df = capital_deployed_df.drop(columns=['Alais'])

                # Process df2
                custom_header = ['UserID', 'User Alias', 'Algo', 'VT', 'GB', 'PS', 'RD', 'RM', 'ALLOCATION', 'MAX LOSS']
                all_data = []
                i = 0
                user_id_found = False
                while i < len(df2):
                    row = df2.iloc[i]
                    try:
                        if row.astype(str).str.contains("UserID", case=False, na=False).any():
                            user_id_found = True
                            header_row_idx = i
                            data_start_idx = i + 1
                            date_val = None
                            if header_row_idx > 0:
                                date_row = df2.iloc[header_row_idx - 1]
                                for val in date_row:
                                    try:
                                        dt = pd.to_datetime(val, dayfirst=True, errors='raise')
                                        if dt.year >= 2020:
                                            date_val = dt
                                            break
                                    except:
                                        continue
                            if date_val is None:
                                date_val = pd.NaT
                            data_rows = []
                            j = data_start_idx
                            while j < len(df2):
                                row_j = df2.iloc[j]
                                if row_j.isnull().all() or row_j.astype(str).str.contains("UserID", case=False, na=False).any():
                                    break
                                data_rows.append(row_j.tolist())
                                j += 1
                            if data_rows:
                                block_df = pd.DataFrame(data_rows, columns=custom_header)
                                block_df["Date"] = date_val
                                all_data.append(block_df)
                            i = j
                        else:
                            i += 1
                    except Exception as e:
                        st.markdown(f'<div class="error-message">Error processing file2 at row {i}: {str(e)}</div>', unsafe_allow_html=True)
                        return
                if not user_id_found:
                    st.markdown('<div class="error-message">Error: \'UserID\' column not found in file2 (Jainam Daily Allocation). Please ensure the \'Record\' sheet contains a \'UserID\' header.</div>', unsafe_allow_html=True)
                    return
                if not all_data:
                    st.markdown('<div class="error-message">Error: No valid data blocks found in file2.</div>', unsafe_allow_html=True)
                    return
                df2 = pd.concat(all_data, ignore_index=True)
                df2 = df2.drop(columns=['Algo', 'MAX LOSS'])
                try:
                    target_date = pd.to_datetime(date).normalize()
                except Exception as e:
                    st.markdown(f'<div class="error-message">Invalid date format: {date}. Please use YYYY-MM-DD.</div>', unsafe_allow_html=True)
                    return
                df2 = df2[df2['Date'] == target_date]
                if df2.empty:
                    st.markdown(f'<div class="error-message">No data found for {target_date.date()} in file2.</div>', unsafe_allow_html=True)
                    return
                df2 = df2.iloc[:-1].reset_index(drop=True)

                # Fill component allocations
                component_cols = ['PS', 'VT', 'GB', 'RD', 'RM']
                current_userid = None
                for i, row in capital_deployed_df.iterrows():
                    if pd.notna(row['IDs']):
                        current_userid = row['IDs']
                    elif current_userid and row['Alias'] in component_cols:
                        alias = row['Alias']
                        matching_row = df2[df2['UserID'] == current_userid]
                        if not matching_row.empty:
                            value = matching_row.iloc[0][alias]
                            capital_deployed_df.at[i, 'Allocation'] = value * 10_000_000

                # Handle unnamed column
                try:
                    nan_column_name = capital_deployed_df.columns[capital_deployed_df.columns.isna()][0]
                    capital_deployed_df['Allocation'] = capital_deployed_df['Allocation'].fillna(capital_deployed_df[nan_column_name])
                    capital_deployed_df = capital_deployed_df.drop(columns=[nan_column_name])
                except IndexError:
                    st.markdown('<div class="error-message">Error: No unnamed column found in capital_deployed_df.</div>', unsafe_allow_html=True)
                    return

                # Finalize mtm_df
                mtm_df = mtm_df[["IDs", "Alias", "mtm"]]

                # Map MTM to capital_deployed_df
                unique_mtm_df = mtm_df.drop_duplicates(subset='IDs', keep='first')
                capital_deployed_df['MTM'] = capital_deployed_df['IDs'].map(unique_mtm_df.set_index('IDs')['mtm'])

                # Proportional MTM allocation
                df = capital_deployed_df.copy()
                i = 0
                while i < len(df):
                    if pd.notna(df.at[i, 'IDs']):
                        main_mtm = df.at[i, 'MTM']
                        component_indices = []
                        j = i + 1
                        while j < len(df) and pd.isna(df.at[j, 'IDs']):
                            if not pd.isna(df.at[j, 'Allocation']):
                                component_indices.append(j)
                            j += 1
                        total_allocation = df.loc[component_indices, 'Allocation'].sum()
                        if total_allocation > 0 and pd.notna(main_mtm):
                            for idx in component_indices:
                                allocation = df.at[idx, 'Allocation']
                                proportion = allocation / total_allocation
                                df.at[idx, 'MTM'] = round(main_mtm * proportion, 2)
                        i = j
                    else:
                        i += 1
                capital_deployed_df = df
                capital_deployed_df["  "]="|"
                capital_deployed_df["IDs(1)"]=max_loss_df["IDs"]
                capital_deployed_df["Alias(1)"]=max_loss_df["Alias"]
                capital_deployed_df["max_loss"]=max_loss_df["max_loss"]

                # Save to CSV in memory
                output = BytesIO()
                capital_deployed_df.to_csv(output, index=False)
                output.seek(0)

                # Provide download button
                st.download_button(
                    label="Download Processed File",
                    data=output,
                    file_name=f'jainam_{date}.csv',
                    mime='text/csv'
                )

            except Exception as e:
                st.markdown(f'<div class="error-message">Error processing files: {str(e)}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == '__main__':
    main()
