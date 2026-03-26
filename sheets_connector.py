import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SheetsConnector:
    def __init__(self):
        self.gc = None
        self.sheet = None
        self.worksheet = None

    def _get_sheet_config(self):
        """Resolve sheet and worksheet names from secrets or environment."""
        sheet_name = os.getenv('GOOGLE_SHEET_NAME', 'Travel Log')
        worksheet_name = os.getenv('WORKSHEET_NAME', 'Raw Data')

        try:
            sheet_name = st.secrets.get('GOOGLE_SHEET_NAME', sheet_name)
            worksheet_name = st.secrets.get('WORKSHEET_NAME', worksheet_name)
        except Exception:
            # Streamlit secrets are optional in local development.
            pass

        return sheet_name, worksheet_name

    def _make_unique_headers(self, headers):
        """Return sanitized, unique headers for DataFrame construction."""
        seen = {}
        unique_headers = []

        for idx, header in enumerate(headers, start=1):
            name = str(header).strip()
            if not name:
                name = f"Column_{idx}"

            count = seen.get(name, 0) + 1
            seen[name] = count

            if count == 1:
                unique_headers.append(name)
            else:
                unique_headers.append(f"{name}_{count}")

        return unique_headers
        
    def connect_to_sheets(_self):
        """Connect to Google Sheets using service account credentials"""
        sheet_name, worksheet_name = _self._get_sheet_config()

        try:
            # Reset connection state each attempt to avoid stale object references.
            _self.gc = None
            _self.sheet = None
            _self.worksheet = None

            # Define the scope
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive"
            ]
            
            # Try to load credentials from Streamlit secrets first (for cloud deployment)
            creds = None
            try:
                credentials_dict = st.secrets["gcp_service_account"]
                creds = Credentials.from_service_account_info(credentials_dict, scopes=scope)
            except:
                # Fallback to local credentials.json file (for local development)
                credentials_path = "credentials.json"
                if not os.path.exists(credentials_path):
                    st.error("❌ credentials.json file not found and no Streamlit secrets configured. Please add your Google API credentials.")
                    return None
                creds = Credentials.from_service_account_file(credentials_path, scopes=scope)
            
            _self.gc = gspread.authorize(creds)
            
            # Open the sheet and worksheet
            _self.sheet = _self.gc.open(sheet_name)
            _self.worksheet = _self.sheet.worksheet(worksheet_name)

            if _self.worksheet is None:
                st.error(f"❌ Worksheet '{worksheet_name}' was not returned by Google Sheets API.")
                return None
            
            return _self.worksheet
            
        except gspread.SpreadsheetNotFound:
            st.error(f"❌ Google Sheet '{sheet_name}' not found. Make sure it's shared with your service account.")
            return None
        except gspread.WorksheetNotFound:
            st.error(f"❌ Worksheet '{worksheet_name}' not found in the sheet.")
            return None
        except Exception as e:
            st.error(f"❌ Error connecting to Google Sheets: {str(e)}")
            return None
    
    def load_data(_self):
        """Load data from Google Sheets and return as DataFrame"""
        worksheet = _self.connect_to_sheets()
        if worksheet is None or not hasattr(worksheet, 'get_all_records'):
            st.error("❌ Could not connect to a valid worksheet. Check credentials, sheet name, worksheet name, and sharing permissions.")
            return None
            
        try:
            # Get all records
            records = worksheet.get_all_records()
            
            if not records:
                st.warning("⚠️ No data found in the worksheet.")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(records)
            
            # Clean and process the data
            df = _self.clean_data(df)
            
            return df

        except Exception as e:
            # gspread raises when header names are duplicated; recover by building a DataFrame manually.
            if "header row in the worksheet is not unique" in str(e):
                try:
                    all_values = worksheet.get_all_values()
                    if not all_values:
                        st.warning("⚠️ Worksheet is empty.")
                        return pd.DataFrame()

                    headers = _self._make_unique_headers(all_values[0])
                    rows = all_values[1:]

                    normalized_rows = []
                    header_count = len(headers)
                    for row in rows:
                        if len(row) < header_count:
                            normalized_rows.append(row + [""] * (header_count - len(row)))
                        else:
                            normalized_rows.append(row[:header_count])

                    df = pd.DataFrame(normalized_rows, columns=headers)
                    df = _self.clean_data(df)

                    st.warning("⚠️ Duplicate column names detected in the worksheet header. Loaded data using auto-renamed columns.")
                    return df
                except Exception as fallback_error:
                    st.error(f"❌ Error loading data after header recovery attempt: {str(fallback_error)}")
                    return None
            
            st.error(f"❌ Error loading data: {str(e)}")
            return None
    
    def clean_data(self, df):
        """Clean and process the raw data"""
        # Convert Date column to datetime
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        # Convert numeric columns
        numeric_columns = ['Cost', 'Point Spend', 'Point Cash Value']
        for col in numeric_columns:
            if col in df.columns:
                # Remove any currency symbols and convert to numeric
                df[col] = df[col].astype(str).str.replace('$', '').str.replace(',', '')
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Remove empty rows
        df = df.dropna(how='all')
        
        # Fill empty strings with None for better filtering
        df = df.replace('', None)
        
        return df
    
    def refresh_data(self):
        """Clear cache and reload data"""
        st.cache_data.clear()
        return self.load_data()