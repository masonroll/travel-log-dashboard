import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar

class DataProcessor:
    def __init__(self, df):
        self.df = df
    
    def get_summary_metrics(self):
        """Calculate key summary metrics"""
        if self.df.empty:
            return {}
        
        total_cost = self.df['Cost'].sum()
        total_point_spend = self.df['Point Spend'].sum()
        total_point_value = self.df['Point Cash Value'].sum()
        total_transactions = len(self.df)
        unique_trips = self.df['Trip Name'].nunique() if 'Trip Name' in self.df.columns else 0
        unique_categories = self.df['Category'].nunique() if 'Category' in self.df.columns else 0
        
        avg_transaction = total_cost / total_transactions if total_transactions > 0 else 0
        
        return {
            'total_cost': total_cost,
            'total_point_spend': total_point_spend,
            'total_point_value': total_point_value,
            'total_transactions': total_transactions,
            'unique_trips': unique_trips,
            'unique_categories': unique_categories,
            'avg_transaction': avg_transaction,
            'total_savings_from_points': total_point_value
        }
    
    def get_spending_by_category(self):
        """Get spending breakdown by category"""
        if self.df.empty or 'Category' not in self.df.columns:
            return pd.DataFrame()
        
        category_summary = self.df.groupby('Category').agg({
            'Cost': 'sum',
            'Point Spend': 'sum',
            'Point Cash Value': 'sum',
            'Trip Name': 'count'
        }).rename(columns={'Trip Name': 'Transaction Count'})
        
        category_summary['Total Value'] = category_summary['Cost'] + category_summary['Point Cash Value']
        
        return category_summary.sort_values('Total Value', ascending=False)
    
    def get_spending_by_trip(self):
        """Get spending breakdown by trip"""
        if self.df.empty or 'Trip Name' not in self.df.columns:
            return pd.DataFrame()
        
        trip_summary = self.df.groupby('Trip Name').agg({
            'Cost': 'sum',
            'Point Spend': 'sum',
            'Point Cash Value': 'sum',
            'Category': 'count',
            'Date': ['min', 'max']
        })
        
        # Flatten column names
        trip_summary.columns = ['Cash Spent', 'Points Spent', 'Point Value', 'Transactions', 'Start Date', 'End Date']
        trip_summary['Total Value'] = trip_summary['Cash Spent'] + trip_summary['Point Value']
        trip_summary['Duration (Days)'] = (trip_summary['End Date'] - trip_summary['Start Date']).dt.days + 1
        
        return trip_summary.sort_values('Total Value', ascending=False)
    
    def get_monthly_spending(self):
        """Get spending breakdown by month"""
        if self.df.empty or 'Date' not in self.df.columns:
            return pd.DataFrame()
        
        # Create month-year column
        self.df['Month_Year'] = self.df['Date'].dt.to_period('M')
        
        monthly_summary = self.df.groupby('Month_Year').agg({
            'Cost': 'sum',
            'Point Spend': 'sum',
            'Point Cash Value': 'sum',
            'Trip Name': 'count'
        }).rename(columns={'Trip Name': 'Transaction Count'})
        
        monthly_summary['Total Value'] = monthly_summary['Cost'] + monthly_summary['Point Cash Value']
        
        return monthly_summary
    
    def get_top_merchants(self, top_n=10):
        """Get top merchants by spending"""
        if self.df.empty or 'Merchant' not in self.df.columns:
            return pd.DataFrame()
        
        merchant_summary = self.df.groupby('Merchant').agg({
            'Cost': 'sum',
            'Point Spend': 'sum',
            'Point Cash Value': 'sum',
            'Trip Name': 'count'
        }).rename(columns={'Trip Name': 'Transaction Count'})
        
        merchant_summary['Total Value'] = merchant_summary['Cost'] + merchant_summary['Point Cash Value']
        
        return merchant_summary.sort_values('Total Value', ascending=False).head(top_n)
    
    def create_category_pie_chart(self):
        """Create pie chart for spending by category"""
        category_data = self.get_spending_by_category()
        if category_data.empty:
            return None
        
        # Reset index to make category names a column
        chart_data = category_data.reset_index()
        
        fig = px.pie(
            chart_data,
            values='Total Value',
            names='Category',
            title="Spending by Category"
        )
        
        # Add custom hover information with transaction count
        customdata = chart_data['Transaction Count'].values
        fig.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            customdata=customdata,
            hovertemplate='<b>%{label}</b><br>' +
                         'Amount: $%{value:,.2f}<br>' +
                         'Transactions: %{customdata}<br>' +
                         'Percentage: %{percent}<br>' +
                         '<extra></extra>'
        )
        return fig
    
    def create_monthly_trend_chart(self):
        """Create line chart for monthly spending trends"""
        monthly_data = self.get_monthly_spending()
        if monthly_data.empty:
            return None
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=monthly_data.index.astype(str),
            y=monthly_data['Cost'],
            mode='lines+markers',
            name='Cash Spending',
            line=dict(color='#1f77b4')
        ))
        
        fig.add_trace(go.Scatter(
            x=monthly_data.index.astype(str),
            y=monthly_data['Point Cash Value'],
            mode='lines+markers',
            name='Point Value',
            line=dict(color='#ff7f0e')
        ))
        
        fig.add_trace(go.Scatter(
            x=monthly_data.index.astype(str),
            y=monthly_data['Total Value'],
            mode='lines+markers',
            name='Total Value',
            line=dict(color='#2ca02c', width=3)
        ))
        
        fig.update_layout(
            title="Monthly Spending Trends",
            xaxis_title="Month",
            yaxis_title="Amount ($)",
            hovermode='x unified'
        )
        
        return fig
    
    def create_trip_comparison_chart(self):
        """Create bar chart comparing trips"""
        trip_data = self.get_spending_by_trip()
        if trip_data.empty:
            return None
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=trip_data.index,
            y=trip_data['Cash Spent'],
            name='Cash Spent',
            marker_color='#1f77b4'
        ))
        
        fig.add_trace(go.Bar(
            x=trip_data.index,
            y=trip_data['Point Value'],
            name='Point Value',
            marker_color='#ff7f0e'
        ))
        
        fig.update_layout(
            title="Spending Comparison by Trip",
            xaxis_title="Trip",
            yaxis_title="Amount ($)",
            barmode='stack',
            xaxis_tickangle=-45
        )
        
        return fig
    
    def filter_data(self, start_date=None, end_date=None, categories=None, trips=None):
        """Filter data based on date range, categories, and trips"""
        filtered_df = self.df.copy()
        
        # Date filtering
        if start_date and end_date and 'Date' in filtered_df.columns:
            filtered_df = filtered_df[
                (filtered_df['Date'] >= start_date) & 
                (filtered_df['Date'] <= end_date)
            ]
        
        # Category filtering
        if categories and 'Category' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['Category'].isin(categories)]
        
        # Trip filtering
        if trips and 'Trip Name' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['Trip Name'].isin(trips)]
        
        return DataProcessor(filtered_df)