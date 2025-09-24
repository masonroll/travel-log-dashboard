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
        
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def connect_to_sheets(_self):
        """Connect to Google Sheets using service account credentials"""
        try:
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
                    st.stop()
                creds = Credentials.from_service_account_file(credentials_path, scopes=scope)
            
            _self.gc = gspread.authorize(creds)
            
            # Get sheet configuration
            try:
                # Try Streamlit secrets first
                sheet_name = st.secrets.get('GOOGLE_SHEET_NAME', 'Travel Log')
                worksheet_name = st.secrets.get('WORKSHEET_NAME', 'Raw Data')
            except:
                # Fallback to environment variables
                sheet_name = os.getenv('GOOGLE_SHEET_NAME', 'Travel Log')
                worksheet_name = os.getenv('WORKSHEET_NAME', 'Raw Data')
            
            # Open the sheet and worksheet
            _self.sheet = _self.gc.open(sheet_name)
            _self.worksheet = _self.sheet.worksheet(worksheet_name)
            
            return True
            
        except gspread.SpreadsheetNotFound:
            st.error(f"❌ Google Sheet '{sheet_name}' not found. Make sure it's shared with your service account.")
            return False
        except gspread.WorksheetNotFound:
            st.error(f"❌ Worksheet '{worksheet_name}' not found in the sheet.")
            return False
        except Exception as e:
            st.error(f"❌ Error connecting to Google Sheets: {str(e)}")
            return False
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def load_data(_self):
        """Load data from Google Sheets and return as DataFrame"""
        if not _self.connect_to_sheets():
            return None
            
        try:
            # Get all records
            records = _self.worksheet.get_all_records()
            
            if not records:
                st.warning("⚠️ No data found in the worksheet.")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(records)
            
            # Clean and process the data
            df = _self.clean_data(df)
            
            return df
            
        except Exception as e:
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