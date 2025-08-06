from flask import Flask, request, send_file, Response, render_template
import pandas as pd
import numpy as np
import os
from io import BytesIO
import warnings

app = Flask(__name__)

# Suppress SettingWithCopyWarning
warnings.filterwarnings('ignore', category=pd.errors.SettingWithCopyWarning)

@app.route('/')
def index():
    return render_template('index.html')  # Assumes index.html is in templates/

@app.route('/process', methods=['POST'])
def process_files():
    try:
        # Retrieve files and form inputs
        file1 = request.files['file1']
        file2 = request.files['file2']
        file3 = request.files['file3']
        sheet_name = request.form['sheet_name']
        date = request.form['date']

        # Validate inputs
        if not all([file1, file2, file3, sheet_name, date]):
            return "All fields are required.", 400

        # Determine file type and read accordingly
        def read_file(file, sheet=None):
            ext = os.path.splitext(file.filename)[1].lower()
            try:
                if ext in ['.xlsx', '.xls']:
                    # If no sheet specified, use the first sheet
                    if sheet is None:
                        return pd.read_excel(file, sheet_name=0, engine='openpyxl')
                    return pd.read_excel(file, sheet_name=sheet, engine='openpyxl')
                elif ext == '.csv':
                    return pd.read_csv(file)
                else:
                    return f"Invalid file format for {file.filename}. Please upload CSV or Excel files."
            except Exception as e:
                return f"Error reading file {file.filename}: {str(e)}"

        # Read the files
        df1 = read_file(file1)  # Default to first sheet for file1
        df2 = read_file(file2, sheet='Record')
        df3 = read_file(file3, sheet=sheet_name)

        # Check for file reading errors
        for df, name in [(df1, 'file1'), (df2, 'file2'), (df3, 'file3')]:
            if isinstance(df, str):
                return df, 400
            if df is None:
                return f"Invalid file format for {name}. Please upload CSV or Excel files.", 400
            if not isinstance(df, pd.DataFrame):
                return f"Error: {name} did not load as a DataFrame. Got type {type(df)}.", 400
            if df.empty:
                return f"File {name} is empty.", 400

        # Process df3 to extract mtm_df, capital_deployed_df, max_loss_df
        try:
            mtm_row_index = df3[df3["Unnamed: 0"] == "MTM"].index[0]
            capital_deployed_row_index = df3[df3["Unnamed: 0"] == "Capital Deployed"].index[0]
            max_loss_row_index = df3[df3["Unnamed: 0"] == "Max SL"].index[0]
            AVG_row_index = df3[df3["Unnamed: 0"] == "AVG %"].index[0]
        except IndexError:
            return "Error: Required sections (MTM, Capital Deployed, Max SL, AVG %) not found in file3.", 400

        mtm_df = df3.iloc[mtm_row_index:capital_deployed_row_index + 1]
        capital_deployed_df = df3.iloc[capital_deployed_row_index:max_loss_row_index + 1]
        max_loss_df = df3.iloc[max_loss_row_index:AVG_row_index + 1]

        # Process mtm_df
        mtm_df = mtm_df.drop(index=mtm_df.index[0]).reset_index(drop=True)
        mtm_df.columns = mtm_df.iloc[0]
        mtm_df = mtm_df.drop(index=0).reset_index(drop=True)
        mtm_df = mtm_df[:-1]
        if 'IDs' not in mtm_df.columns:
            return "Error: 'IDs' column not found in MTM section of file3.", 400
        non_null_ids = mtm_df['IDs'].dropna().tolist()

        # Process capital_deployed_df
        capital_deployed_df = capital_deployed_df.drop(index=capital_deployed_df.index[0]).reset_index(drop=True)
        capital_deployed_df.columns = capital_deployed_df.iloc[0]
        capital_deployed_df = capital_deployed_df.drop(index=0).reset_index(drop=True)
        capital_deployed_df = capital_deployed_df[:-1]
        if 'IDs' not in capital_deployed_df.columns:
            return "Error: 'IDs' column not found in Capital Deployed section of file3.", 400

        # Process max_loss_df
        max_loss_df = max_loss_df.drop(index=max_loss_df.index[0]).reset_index(drop=True)
        max_loss_df.columns = max_loss_df.iloc[0]
        max_loss_df = max_loss_df.drop(index=0).reset_index(drop=True)
        max_loss_df = max_loss_df[:-1]
        if 'IDs' not in max_loss_df.columns:
            return "Error: 'IDs' column not found in Max SL section of file3.", 400

        # Filter df1 based on non_null_ids
        if 'UserID' not in df1.columns:
            return "Error: 'UserID' column not found in file1.", 400
        df_new = df1[df1["UserID"].isin(non_null_ids)]
        try:
            df_new['Date'] = pd.to_datetime(df_new['Date'])
        except Exception as e:
            return f"Error converting Date column in file1: {str(e)}", 400

        # Filter by date
        try:
            match_date = pd.to_datetime(date)
        except Exception as e:
            return f"Invalid date format: {date}. Please use YYYY-MM-DD.", 400
        matched_rows = df_new[df_new['Date'].dt.date == match_date.date()]
        if matched_rows.empty:
            return f"No data found for date {date} in file1.", 400

        # Drop unnecessary columns
        cols_to_drop = ['Date', 'SNO', 'Enabled', 'LoggedIn', 'SqOff Done',
                        'Broker', 'Qty Multiplier', 'Available Margin', 'Total Orders',
                        'Total Lots', 'SERVER', 'Unnamed: 16', 'Unnamed: 17',
                        'Unnamed: 18', 'Unnamed: 19', 'Unnamed: 20']
        matched_rows = matched_rows.drop(columns=[col for col in cols_to_drop if col in matched_rows.columns])

        # Map values to dataframes
        if 'MTM (All)' not in matched_rows.columns:
            return "Error: 'MTM (All)' column not found in file1.", 400
        mtm_df['mtm'] = mtm_df['IDs'].map(matched_rows.set_index('UserID')['MTM (All)'])
        if 'ALLOCATION' not in matched_rows.columns:
            return "Error: 'ALLOCATION' column not found in file1.", 400
        capital_deployed_df['Allocation'] = (capital_deployed_df['IDs'].map(matched_rows.set_index('UserID')['ALLOCATION']) * 100)
        if 'MAX LOSS' not in matched_rows.columns:
            return "Error: 'MAX LOSS' column not found in file1.", 400
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
                    if data_rows:  # Only create block if data_rows exist
                        block_df = pd.DataFrame(data_rows, columns=custom_header)
                        block_df["Date"] = date_val
                        all_data.append(block_df)
                    i = j
                else:
                    i += 1
            except Exception as e:
                return f"Error processing file2 at row {i}: {str(e)}", 400
        if not user_id_found:
            return "Error: 'UserID' column not found in file2 (Jainam Daily Allocation). Please ensure the 'Record' sheet contains a 'UserID' header.", 400
        if not all_data:
            return "Error: No valid data blocks found in file2.", 400
        df2 = pd.concat(all_data, ignore_index=True)
        df2 = df2.drop(columns=['Algo', 'MAX LOSS'])
        try:
            target_date = pd.to_datetime(date).normalize()
        except Exception as e:
            return f"Invalid date format: {date}. Please use YYYY-MM-DD.", 400
        df2 = df2[df2['Date'] == target_date]
        if df2.empty:
            return f"No data found for {target_date.date()} in file2.", 400
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
            return "Error: No unnamed column found in capital_deployed_df.", 400

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

        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'jainam_{date}.csv'
        )

    except Exception as e:
        return f"Error processing files: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)