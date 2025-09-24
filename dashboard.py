import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from sheets_connector import SheetsConnector
from data_processor import DataProcessor

# Configure Streamlit page
st.set_page_config(
    page_title="Travel Log Dashboard",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling and readability
st.markdown("""
<style>
    /* Improve metric card readability */
    .metric-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 0.75rem;
        border: 2px solid #e1e5e9;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Better contrast for metric labels */
    .stMetric > label {
        font-size: 16px !important;
        color: #1f1f1f !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Stronger text for metric values */
    .stMetric > div {
        font-size: 28px !important;
        font-weight: 800 !important;
        color: #0f1419 !important;
    }
    
    /* Improve sidebar text */
    .css-1d391kg {
        color: #1f1f1f !important;
    }
    
    /* Better button contrast */
    .stButton > button {
        background-color: #0066cc;
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 0.5rem;
    }
    
    /* Improve dataframe text */
    .stDataFrame {
        background-color: white;
    }
    
    /* Better chart backgrounds */
    .plotly-graph-div {
        background-color: white !important;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.title("✈️ Travel Log Dashboard")
    st.markdown("### Analyze your travel expenses and budgeting insights")
    
    # Initialize session state
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    if 'df' not in st.session_state:
        st.session_state.df = pd.DataFrame()
    
    # Sidebar for controls
    st.sidebar.header("🔧 Controls")
    
    # Load data section
    st.sidebar.subheader("📊 Data Connection")
    
    if st.sidebar.button("🔄 Load/Refresh Data", type="primary"):
        with st.spinner("Loading data from Google Sheets..."):
            connector = SheetsConnector()
            df = connector.load_data()
            
            if df is not None and not df.empty:
                st.session_state.df = df
                st.session_state.data_loaded = True
                st.sidebar.success(f"✅ Loaded {len(df)} records!")
            else:
                st.sidebar.error("❌ Failed to load data")
                st.session_state.data_loaded = False
    
    # Show connection status
    if st.session_state.data_loaded:
        st.sidebar.success("🟢 Connected to Google Sheets")
        st.sidebar.info(f"📈 {len(st.session_state.df)} records loaded")
    else:
        st.sidebar.warning("🟡 No data loaded")
        st.info("👆 Click 'Load/Refresh Data' in the sidebar to connect to your Google Sheets")
        return
    
    # Data filtering section
    if st.session_state.data_loaded and not st.session_state.df.empty:
        df = st.session_state.df
        processor = DataProcessor(df)
        
        st.sidebar.subheader("🔍 Filters")
        
        # Date range filter
        if 'Date' in df.columns and not df['Date'].isna().all():
            min_date = df['Date'].min().date()
            max_date = df['Date'].max().date()
            
            date_range = st.sidebar.date_input(
                "📅 Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
            
            if len(date_range) == 2:
                start_date, end_date = date_range
            else:
                start_date, end_date = min_date, max_date
        else:
            start_date, end_date = None, None
        
        # Category filter
        if 'Category' in df.columns:
            available_categories = df['Category'].dropna().unique().tolist()
            selected_categories = st.sidebar.multiselect(
                "🏷️ Categories",
                options=available_categories,
                default=available_categories
            )
        else:
            selected_categories = None
        
        # Trip filter
        if 'Trip Name' in df.columns:
            available_trips = df['Trip Name'].dropna().unique().tolist()
            selected_trips = st.sidebar.multiselect(
                "✈️ Trips",
                options=available_trips,
                default=available_trips
            )
        else:
            selected_trips = None
        
        # Apply filters
        filtered_processor = processor.filter_data(
            start_date=pd.Timestamp(start_date) if start_date else None,
            end_date=pd.Timestamp(end_date) if end_date else None,
            categories=selected_categories if selected_categories else None,
            trips=selected_trips if selected_trips else None
        )
        
        # Main dashboard content
        display_dashboard(filtered_processor)

def display_dashboard(processor):
    """Display the main dashboard content"""
    
    # Summary metrics
    st.subheader("📊 Summary Metrics")
    metrics = processor.get_summary_metrics()
    
    if metrics:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "💰 Total Cash Spent",
                f"${metrics['total_cost']:,.2f}",
                help="Total amount spent in cash"
            )
        
        with col2:
            st.metric(
                "🪙 Points Spent",
                f"{metrics['total_point_spend']:,.0f}",
                help="Total points/miles spent"
            )
        
        with col3:
            st.metric(
                "💎 Point Value",
                f"${metrics['total_point_value']:,.2f}",
                help="Cash value of points spent"
            )
        
        with col4:
            st.metric(
                "🧾 Transactions",
                f"{metrics['total_transactions']:,}",
                help="Total number of transactions"
            )
        
        # Second row of metrics
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            st.metric(
                "✈️ Unique Trips",
                f"{metrics['unique_trips']:,}",
                help="Number of different trips"
            )
        
        with col6:
            st.metric(
                "🏷️ Categories",
                f"{metrics['unique_categories']:,}",
                help="Number of spending categories"
            )
        
        with col7:
            st.metric(
                "📊 Avg Transaction",
                f"${metrics['avg_transaction']:,.2f}",
                help="Average transaction amount"
            )
        
        with col8:
            total_value = metrics['total_cost'] + metrics['total_point_value']
            st.metric(
                "🎯 Total Value",
                f"${total_value:,.2f}",
                help="Total cash + point value"
            )
    
    st.divider()
    
    # Charts section
    st.subheader("📈 Visual Analysis")
    
    # Create two columns for charts
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        # Category pie chart
        cat_chart = processor.create_category_pie_chart()
        if cat_chart:
            st.plotly_chart(cat_chart, use_container_width=True)
        else:
            st.info("No category data available for chart")
    
    with chart_col2:
        # Monthly trend chart
        trend_chart = processor.create_monthly_trend_chart()
        if trend_chart:
            st.plotly_chart(trend_chart, use_container_width=True)
        else:
            st.info("No date data available for trend chart")
    
    # Trip comparison chart (full width)
    trip_chart = processor.create_trip_comparison_chart()
    if trip_chart:
        st.plotly_chart(trip_chart, use_container_width=True)
    else:
        st.info("No trip data available for comparison chart")
    
    st.divider()
    
    # Data tables section
    st.subheader("📋 Detailed Breakdowns")
    
    tab1, tab2, tab3, tab4 = st.tabs(["By Category", "By Trip", "By Month", "Top Merchants"])
    
    with tab1:
        category_data = processor.get_spending_by_category()
        if not category_data.empty:
            st.dataframe(category_data, use_container_width=True)
        else:
            st.info("No category data available")
    
    with tab2:
        trip_data = processor.get_spending_by_trip()
        if not trip_data.empty:
            st.dataframe(trip_data, use_container_width=True)
        else:
            st.info("No trip data available")
    
    with tab3:
        monthly_data = processor.get_monthly_spending()
        if not monthly_data.empty:
            st.dataframe(monthly_data, use_container_width=True)
        else:
            st.info("No monthly data available")
    
    with tab4:
        merchant_data = processor.get_top_merchants()
        if not merchant_data.empty:
            st.dataframe(merchant_data, use_container_width=True)
        else:
            st.info("No merchant data available")
    
    # Raw data section
    with st.expander("🔍 View Raw Data", expanded=False):
        if not processor.df.empty:
            st.dataframe(processor.df, use_container_width=True)
            
            # Download button for filtered data
            csv = processor.df.to_csv(index=False)
            st.download_button(
                label="📥 Download Filtered Data as CSV",
                data=csv,
                file_name=f"travel_log_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No raw data available")

if __name__ == "__main__":
    main()