import streamlit as st
import pandas as pd
import numpy as np
import os
from io import BytesIO
import warnings
from datetime import datetime
import datetime
import openpyxl
import hashlib

# Suppress SettingWithCopyWarning
warnings.filterwarnings('ignore', category=pd.errors.SettingWithCopyWarning)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Valid credentials (for demo purposes; in production, use a secure database)
VALID_USERNAME = "Access_User"
VALID_PASSWORD_HASH = hash_password("Jainam@135")

def to_excel(df):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)
    return buffer.getvalue()

def main():
    # Set page configuration
    st.set_page_config(page_title="Jainam Data Processor", layout="centered", initial_sidebar_state="collapsed")

    # Initialize session state
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'
    if 'form_inputs' not in st.session_state:
        st.session_state.form_inputs = {'file1': None, 'file2': None, 'file3': None, 'sheet_name': '', 'date': None}
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'output' not in st.session_state:
        st.session_state.output = None

    # Theme-based CSS
    def get_css(theme):
        if theme == 'dark':
            background = "linear-gradient(135deg, #1F2937 0%, #374151 100%)"
            container_bg = "#2D3748"
            text_color = "#FFFFFF"
            input_bg = "#4B5563"
            input_border = "#6B7280"
            button_bg = "linear-gradient(90deg, #06B6D4, #3B82F6)"
            button_hover = "linear-gradient(90deg, #0E7490, #1E40AF)"
            header_gradient = "linear-gradient(to right, #34D399, #60A5FA)"
            error_bg = "#4B5563"
            error_border = "#EF4444"
            error_text = "#FECACA"
            success_bg = "#4B5563"
            success_border = "#10B981"
            success_text = "#D1FAE5"
            tooltip_bg = "#1E40AF"
            tooltip_text = "#FFFFFF"
            progress_bg = "#3B82F6"
            toggle_bg = "#4B5563"
            toggle_border = "#6B7280"
            login_bg = "linear-gradient(145deg, #374151, #1F2937)"
            login_border = "#4B5563"
            card_shadow = "0 12px 24px rgba(0, 0, 0, 0.3)"
        else:
            background = "linear-gradient(135deg, #E5E7EB 0%, #A5B4FC 100%)"
            container_bg = "#FFFFFF"
            text_color = "#1F2937"
            input_bg = "#F9FAFB"
            input_border = "#D1D5DB"
            button_bg = "linear-gradient(90deg, #10B981, #3B82F6)"
            button_hover = "linear-gradient(90deg, #047857, #1E40AF)"
            header_gradient = "linear-gradient(to right, #10B981, #3B82F6)"
            error_bg = "#FEE2E2"
            error_border = "#EF4444"
            error_text = "#B91C1C"
            success_bg = "#D1FAE5"
            success_border = "#10B981"
            success_text = "#065F46"
            tooltip_bg = "#1E40AF"
            tooltip_text = "#FFFFFF"
            progress_bg = "#10B981"
            toggle_bg = "#E5E7EB"
            toggle_border = "#D1D5DB"
            login_bg = "linear-gradient(145deg, #FFFFFF, #F3F4F6)"
            login_border = "#D1D5DB"
            card_shadow = "0 8px 16px rgba(0, 0, 0, 0.1)"

        return f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        .stApp {{
            background: {background};
            min-height: 100vh;
            padding: 2rem;
            font-family: 'Inter', sans-serif;
            transition: all 0.3s ease;
        }}
        .container {{
            background: {container_bg};
            border-radius: 0.75rem;
            box-shadow: {card_shadow};
            padding: 2rem;
            max-width: 550px;
            margin: auto;
            transition: transform 0.3s ease;
        }}
        .container:hover {{
            transform: translateY(-3px);
        }}
        .header h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            text-align: center;
            background: {header_gradient};
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
        }}
        .header p {{
            text-align: center;
            color: {text_color};
            font-size: 1rem;
            opacity: 0.8;
            margin-bottom: 1.5rem;
        }}
        .stFileUploader, .stTextInput, .stDateInput {{
            background: {input_bg};
            border-radius: 0.5rem;
            padding: 0.75rem;
            margin-bottom: 1rem;
            border: 1px solid {input_border};
            transition: all 0.3s ease;
            border-radius: 12px;
        }}
        .stFileUploader:hover, .stTextInput:hover, .stDateInput:hover {{
            border-color: #3B82F6;
            background: #E5E7EB;
            transform: scale(1.02);
        }}
        .stFileUploader label, .stTextInput label, .stDateInput label {{
            font-weight: 600;
            color: {text_color};
            margin-bottom: 0.5rem;
        }}
        .stButton>button {{
            background: {button_bg};
            border: none;
            border-radius: 0.5rem;
            padding: 0.75rem;
            font-size: 1rem;
            font-weight: 600;
            color: {text_color};
            width: 100%;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            border-radius: 12px;
        }}
        .stButton>button:hover {{
            background: {button_hover};
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }}
        .stButton>button:disabled {{
            background: #9CA3AF;
            cursor: not-allowed;
            transform: none;
        }}
        .reset-button {{
            background: linear-gradient(90deg, #F87171, #EF4444);
            border: none;
            border-radius: 0.5rem;
            padding: 0.75rem;
            font-size: 1rem;
            font-weight: 600;
            color: {text_color};
            width: 100%;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            border-radius: 12px;
        }}
        .reset-button:hover {{
            background: linear-gradient(90deg, #B91C1C, #991B1B);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }}
        .error-message {{
            background: {error_bg};
            border: 1px solid {error_border};
            border-radius: 0.5rem;
            padding: 0.75rem;
            color: {error_text};
            font-weight: 500;
            margin-top: 1rem;
            animation: slideIn 0.5s ease-out;
            border-radius: 12px;
        }}
        .success-message {{
            background: {success_bg};
            border: 1px solid {success_border};
            border-radius: 0.5rem;
            padding: 0.75rem;
            color: {success_text};
            font-weight: 500;
            margin-top: 1rem;
            animation: slideIn 0.5s ease-out;
            border-radius: 12px;
        }}
        .file-preview, .validation-message {{
            color: {text_color};
            font-size: 0.85rem;
            margin-top: 0.25rem;
            font-style: italic;
        }}
        .file-size-gauge {{
            width: 100%;
            height: 10px;
            background: #E5E7EB;
            border-radius: 5px;
            overflow: hidden;
            margin-top: 0.25rem;
        }}
        .file-size-gauge-bar {{
            height: 100%;
            background: {progress_bg};
            transition: width 0.3s ease;
        }}
        @keyframes slideIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        .loading-spinner {{
            border: 4px solid {text_color};
            border-top: 4px solid {progress_bg};
            border-radius: 50%;
            width: 24px;
            height: 24px;
            animation: spin 1s linear infinite;
            display: inline-block;
            margin-right: 0.5rem;
        }}
        .tooltip {{
            position: relative;
            display: inline-block;
            color: {text_color};
        }}
        .tooltip .tooltiptext {{
            visibility: hidden;
            width: 180px;
            background-color: {tooltip_bg};
            color: {tooltip_text};
            text-align: center;
            border-radius: 6px;
            padding: 6px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -90px;
            opacity: 0;
            transition: opacity 0.3s;
            font-size: 0.85rem;
        }}
        .tooltip:hover .tooltiptext {{
            visibility: visible;
            opacity: 1;
        }}
        .stExpander {{
            background: {input_bg};
            border: 1px solid {input_border};
            border-radius: 0.5rem;
        }}
        .stExpander summary {{
            color: {text_color};
            font-weight: 600;
        }}
        .footer {{
            text-align: center;
            color: {text_color};
            opacity: 0.6;
            font-size: 0.8rem;
            margin-top: 2rem;
            animation: fadeIn 1s ease-in;
        }}
        .theme-toggle {{
            position: fixed;
            top: 1rem;
            right: 1rem;
            background: {toggle_bg};
            border: 1px solid {toggle_border};
            border-radius: 50%;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }}
        .theme-toggle:hover {{
            background: {button_hover};
            transform: scale(1.1);
        }}
        .theme-toggle span {{
            font-size: 1.2rem;
        }}
        .login-container {{
            background: {login_bg};
            border-radius: 1rem;
            box-shadow: {card_shadow};
            padding: 2rem;
            max-width: 400px;
            margin: 5rem auto;
            border: 1px solid {login_border};
            animation: fadeIn 0.5s ease-in;
        }}
        .login-header {{
            font-size: 1.75rem;
            font-weight: 600;
            text-align: center;
            margin-bottom: 1.5rem;
            color: {text_color};
        }}
        .login-input {{
            background: {input_bg};
            border: 1px solid {input_border};
            border-radius: 12px;
            padding: 0.75rem;
            margin-bottom: 1rem;
            transition: all 0.3s ease;
        }}
        .login-input:hover {{
            border-color: #3B82F6;
            background: #E5E7EB;
            transform: scale(1.02);
        }}
        .login-button {{
            background: {button_bg};
            border: none;
            border-radius: 12px;
            padding: 0.75rem;
            font-size: 1rem;
            font-weight: 600;
            color: {text_color};
            width: 100%;
            transition: all 0.3s ease;
        }}
        .login-button:hover {{
            background: {button_hover};
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }}
        .input-icon {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            background: {input_bg};
            border: 1px solid {input_border};
            border-radius: 12px;
            padding: 0.5rem;
            margin-bottom: 1rem;
        }}
        .input-icon svg {{
            margin-left: 0.5rem;
            color: {text_color};
            opacity: 0.6;
        }}
        .input-icon input {{
            border: none;
            background: transparent;
            width: 100%;
            outline: none;
            color: {text_color};
            font-family: 'Inter', sans-serif;
        }}
        .input-icon input::placeholder {{
            color: {text_color};
            opacity: 0.6;
        }}
        .row-widget-stMarkdown {{
            margin-bottom: -15px; /* Adjust spacing between icon and input */
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        </style>
        """

    # Apply theme-based CSS
    st.markdown(get_css(st.session_state.theme), unsafe_allow_html=True)

    # Theme toggle button
    theme_icon = "🌙" if st.session_state.theme == 'light' else "☀️"
    if st.button(theme_icon, key="theme_toggle", help="Toggle theme"):
        st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'
        st.rerun()

    # Login Page
    if not st.session_state.logged_in:
        # st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<div class="login-header">Jainam Data Processor</div>', unsafe_allow_html=True)

        # Username input with icon
        col1, col2 = st.columns([0.1, 0.9])
        with col1:
            st.markdown('''<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>''', unsafe_allow_html=True)
        with col2:
            username = st.text_input("", placeholder="Username", key="username", label_visibility="collapsed")

        # Password input with icon
        col1, col2 = st.columns([0.1, 0.9])
        with col1:
            st.markdown('''<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect></svg>''', unsafe_allow_html=True)
        with col2:
            password = st.text_input("", type="password", placeholder="Password", key="password", label_visibility="collapsed")

        if st.button("Login", key="login_btn"):
            if username == VALID_USERNAME and hash_password(password) == VALID_PASSWORD_HASH:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.markdown('<div class="error-message">Invalid username or password</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # Main Interface
    st.markdown("""
    <div class="header">
        <h1>Jainam Data Processor</h1>
    </div>
    """, unsafe_allow_html=True)

    # File uploaders and input fields
    with st.container():
        st.markdown('<div class="tooltip">📁 Compiled MTM Sheet<span class="tooltiptext">Excel/CSV with MTM data.</span></div>', unsafe_allow_html=True)
        file1 = st.file_uploader("", type=["xlsx", "csv"], key="file1")
        if file1:
            st.session_state.form_inputs['file1'] = file1
            st.markdown(f'<div class="file-preview">Uploaded: {file1.name}</div>', unsafe_allow_html=True)

        st.markdown('<div class="tooltip">📁 Jainam Daily Allocation<span class="tooltiptext">Excel/CSV with allocation data.</span></div>', unsafe_allow_html=True)
        file2 = st.file_uploader("", type=["xlsx", "csv"], key="file2")
        if file2:
            st.session_state.form_inputs['file2'] = file2
            st.markdown(f'<div class="file-preview">Uploaded: {file2.name}</div>', unsafe_allow_html=True)

        st.markdown('<div class="tooltip">📁 Updated JAINAM DAILY<span class="tooltiptext">Excel/CSV with updated daily data.</span></div>', unsafe_allow_html=True)
        file3 = st.file_uploader("", type=["xlsx", "csv"], key="file3")
        if file3:
            st.session_state.form_inputs['file3'] = file3
            st.markdown(f'<div class="file-preview">Uploaded: {file3.name}</div>', unsafe_allow_html=True)

        st.markdown('<div class="tooltip">📝 Sheet Name<span class="tooltiptext">Enter the exact sheet name (e.g., JULY 2025).</span></div>', unsafe_allow_html=True)
        sheet_name = st.text_input("", value=st.session_state.form_inputs['sheet_name'], placeholder="Enter sheet name (e.g., JULY 2025)")
        if sheet_name:
            st.session_state.form_inputs['sheet_name'] = sheet_name

        st.markdown(
            f'<div class="tooltip">📅 Date<span class="tooltiptext">Select a date up to today ({datetime.date.today().strftime("%B %d, %Y")}).</span></div>',
            unsafe_allow_html=True
        )
        
        date = st.date_input(
            "",
            max_value=datetime.date.today(),  # limit till today
            value=st.session_state.form_inputs['date']
        )
        
        if date:
            st.session_state.form_inputs['date'] = date

    # Buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        process_clicked = st.button("⚙️ Process Files", key="process_btn")
    with col2:
        reset_clicked = st.button("🔄 Reset Form", key="reset_btn", help="Clear all inputs")

    # Handle reset
    if reset_clicked:
        st.session_state.form_inputs = {'file1': None, 'file2': None, 'file3': None, 'sheet_name': '', 'date': None}
        st.rerun()

    # Process button logic
    if process_clicked:
        if not all([file1, file2, file3, sheet_name, date]):
            st.markdown('<div class="error-message">All fields are required.</div>', unsafe_allow_html=True)
            return

        # Progress bar with loading animation
        progress_bar = st.progress(0)
        with st.spinner("Processing your files..."):
            st.markdown('<div class="loading-spinner"></div>Processing...', unsafe_allow_html=True)
            try:
                progress_bar.progress(10)
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
                progress_bar.progress(20)
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

                progress_bar.progress(30)
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

                progress_bar.progress(40)
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

                progress_bar.progress(50)
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

                progress_bar.progress(60)
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

                progress_bar.progress(70)
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

                progress_bar.progress(80)
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

                progress_bar.progress(90)
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

                # Rename columns for better readability
                capital_deployed_df = capital_deployed_df.rename(columns={
                    'IDs': 'User ID',
                    'Alias': 'Component',
                    'Allocation': 'Capital Deployed',
                    'MTM': 'MTM',
                    '  ': '|',
                    'IDs(1)': 'User ID (SL)',
                    'Alias(1)': 'Component (SL)',
                    'max_loss': 'Max Loss'
                })

                # Save to session state for display
                st.session_state.output = capital_deployed_df

                progress_bar.progress(100)
                st.markdown('<div class="success-message">✅ Files processed successfully! View the data below.</div>', unsafe_allow_html=True)

            except Exception as e:
                st.markdown(f'<div class="error-message">Error processing files: {str(e)}</div>', unsafe_allow_html=True)
            finally:
                progress_bar.empty()

    # Display processed data
    if st.session_state.output is not None:
        st.subheader("Processed Data")
        st.dataframe(
            st.session_state.output.style.format({
                'Capital Deployed': '{:,.2f}',
                'MTM': '{:,.2f}',
                'Max Loss': '{:,.2f}'
            }),
            use_container_width=True,
            hide_index=True
        )

        # Download button
        output_excel = to_excel(st.session_state.output)
        filename = f"jainam_{st.session_state.form_inputs['date'].strftime('%Y-%m-%d')}.xlsx"
        st.download_button("📥 Download Processed Data", data=output_excel, file_name=filename, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # Footer
    st.markdown('<div class="footer">Jainam Data Processor v1.0 | Developed By Sahil</div>', unsafe_allow_html=True)

if __name__ == '__main__':
    main()



