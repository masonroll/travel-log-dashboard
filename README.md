# Travel Log Dashboard

A Python dashboard application that connects to Google Sheets to analyze your travel expenses and provide interactive budgeting summaries.

## Features

- 📊 Interactive dashboard built with Streamlit
- 📈 Real-time data from Google Sheets
- 💰 Budget analysis by category, date, and trip
- 📱 Responsive visualizations with Plotly
- 🔍 Filter data by date ranges, categories, and trips
- 💳 Point spending vs cash spending analysis

## Setup

### 1. Google Sheets API Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API
4. Create credentials (Service Account)
5. Download the JSON key file and save it as `credentials.json` in the project root
6. Share your Google Sheet with the service account email

### 2. Environment Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your configuration:
```
GOOGLE_SHEET_NAME=Travel Log
WORKSHEET_NAME=Raw data
```

### 3. Run the Dashboard

```bash
streamlit run dashboard.py
```

## Project Structure

```
TravelLogSummary/
├── dashboard.py          # Main Streamlit dashboard
├── sheets_connector.py   # Google Sheets API integration
├── data_processor.py     # Data analysis functions
├── requirements.txt      # Python dependencies
├── credentials.json      # Google API credentials (add this)
├── .env                 # Environment variables (add this)
└── README.md            # This file
```

## Usage

1. Make sure your Google Sheet has the following columns:
   - Trip Name
   - Category
   - Date
   - Merchant
   - Cost
   - Point Spend
   - Notes
   - Location
   - Point Cash Value

2. Run the dashboard and explore your travel expenses with interactive filters and visualizations.

## Troubleshooting

- Make sure your Google Sheet is shared with the service account email
- Check that your credentials.json file is in the project root
- Verify that the sheet name and worksheet name match your configuration