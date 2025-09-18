"""
Comprehensive Analytics Dashboard using all available endpoints
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from backend_client import get_backend_client
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from chart_utils import create_altair_chart
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'styles'))
from card_style import apply_card_styles
from dashboard_pages.advanced_filters import render_advanced_filters, get_filtered_data, render_filter_summary

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_comprehensive_data():
    """Get comprehensive data from multiple endpoints"""
    client = get_backend_client()
    if not client:
        return None
    
    try:
        # Get data from multiple endpoints
        data = {
            'demographics': client.get_demographics(),
            'survey_index': client.get_surveys_index(),
            'health_check': client.get_health_check(),
            'vocabulary': client.get_vocabulary(),
            'schema': client.get_schema()
        }
        
        # Check for errors
        for key, value in data.items():
            if isinstance(value, dict) and "error" in value:
                st.warning(f"Could not load {key}: {value['error']}")
                data[key] = None
        
        return data
    except Exception as e:
        st.error(f"Error loading comprehensive data: {str(e)}")
        return None

def render_overview_metrics(data):
    """Render overview metrics from demographics data"""
    if not data or 'demographics' not in data:
        st.warning("No demographics data available")
        return
    
    demographics = data['demographics']
    overview = demographics.get('overview', {})
    
    st.markdown("### 📊 Overview Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_responses = overview.get('total_responses', 0)
        st.metric("Total Responses", f"{total_responses:,}")
    
    with col2:
        total_surveys = overview.get('total_surveys', 0)
        st.metric("Total Surveys", f"{total_surveys:,}")
    
    with col3:
        date_range = overview.get('date_range', {})
        if date_range:
            earliest = date_range.get('earliest', 'N/A')
            latest = date_range.get('latest', 'N/A')
            st.metric("Date Range", f"{earliest} to {latest}")
        else:
            st.metric("Date Range", "N/A")
    
    with col4:
        # Calculate average responses per survey
        if total_surveys > 0:
            avg_responses = total_responses / total_surveys
            st.metric("Avg Responses/Survey", f"{avg_responses:,.0f}")
        else:
            st.metric("Avg Responses/Survey", "N/A")

def render_demographics_charts(data):
    """Render demographics charts"""
    if not data or 'demographics' not in data:
        return
    
    demographics = data['demographics']
    overall_demographics = demographics.get('overall_demographics', {})
    
    if not overall_demographics:
        return
    
    st.markdown("### 👥 Demographics Analysis")
    
    col1, col2 = st.columns(2)
    
    # Gender distribution
    with col1:
        gender_data = overall_demographics.get('gender', {})
        if gender_data:
            fig = px.pie(
                values=list(gender_data.values()),
                names=list(gender_data.keys()),
                title="Gender Distribution",
                color_discrete_sequence=px.colors.qualitative.Vivid
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, width='stretch')
    
    # Age group distribution
    with col2:
        age_data = overall_demographics.get('age_groups', {})
        if age_data:
            fig = px.bar(
                x=list(age_data.keys()),
                y=list(age_data.values()),
                title="Age Group Distribution",
                color=list(age_data.values()),
                color_continuous_scale=px.colors.sequential.Viridis
            )
            fig.update_layout(height=400, xaxis_title="Age Group", yaxis_title="Count")
            st.plotly_chart(fig, width='stretch')
    
    # Employment distribution
    employment_data = overall_demographics.get('employment', {})
    if employment_data:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = px.bar(
                x=list(employment_data.keys()),
                y=list(employment_data.values()),
                title="Employment Status Distribution",
                color=list(employment_data.values()),
                color_continuous_scale=px.colors.sequential.Plasma
            )
            fig.update_layout(height=400, xaxis_title="Employment Status", yaxis_title="Count")
            st.plotly_chart(fig, width='stretch')
        
        with col2:
            # Employment summary table
            st.markdown("#### Employment Summary")
            employment_df = pd.DataFrame([
                {"Status": k, "Count": v, "Percentage": f"{(v/sum(employment_data.values())*100):.1f}%"}
                for k, v in employment_data.items()
            ])
            st.dataframe(employment_df, width='stretch')

def render_survey_analysis(data):
    """Render survey analysis from survey index"""
    if not data or 'survey_index' not in data:
        return
    
    survey_index = data['survey_index']
    if survey_index is None or survey_index.empty:
        return
    
    st.markdown("### 📋 Survey Analysis")
    
    # Survey response counts
    if 'response_count' in survey_index.columns:
        fig = px.bar(
            survey_index,
            x='title',
            y='response_count',
            title="Response Count by Survey",
            color='response_count',
            color_continuous_scale=px.colors.sequential.Blues
        )
        fig.update_layout(
            height=500,
            xaxis_title="Survey Title",
            yaxis_title="Response Count",
            xaxis_tickangle=45
        )
        st.plotly_chart(fig, width='stretch')
    
    # Survey summary table
    st.markdown("#### Survey Summary")
    summary_columns = ['title', 'response_count']
    if 'file_size_mb' in survey_index.columns:
        summary_columns.append('file_size_mb')
    
    summary_df = survey_index[summary_columns].copy()
    if 'file_size_mb' in summary_df.columns:
        summary_df['file_size_mb'] = summary_df['file_size_mb'].round(2)
    
    st.dataframe(summary_df, width='stretch')

def render_health_status(data):
    """Render health check status"""
    if not data or 'health_check' not in data:
        return
    
    health_data = data['health_check']
    
    st.markdown("### 🔧 System Health")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status = health_data.get('status', 'unknown')
        status_color = "🟢" if status == "healthy" else "🔴"
        st.metric("Status", f"{status_color} {status.title()}")
    
    with col2:
        uptime = health_data.get('uptime', 'N/A')
        st.metric("Uptime", uptime)
    
    with col3:
        cache_size = health_data.get('cache_size', 0)
        st.metric("Cache Size", f"{cache_size} items")
    
    with col4:
        memory_usage = health_data.get('memory_usage', 'N/A')
        st.metric("Memory Usage", memory_usage)

def render_data_schema(data):
    """Render data schema information"""
    if not data or 'schema' not in data:
        return
    
    schema = data['schema']
    
    st.markdown("### 📋 Data Schema")
    
    for table_name, fields in schema.items():
        with st.expander(f"📄 {table_name}", expanded=False):
            schema_df = pd.DataFrame([
                {"Field": field, "Description": description}
                for field, description in fields.items()
            ])
            st.dataframe(schema_df, width='stretch')

def main():
    st.title("🔍 Comprehensive Analytics Dashboard")
    st.markdown("---")
    apply_card_styles()
    
    # Load comprehensive data
    with st.spinner("Loading comprehensive data..."):
        data = get_comprehensive_data()
    
    if not data:
        st.error("❌ Could not load comprehensive data. Please check your backend connection.")
        return
    
    # Render overview metrics
    render_overview_metrics(data)
    
    st.markdown("---")
    
    # Render demographics charts
    render_demographics_charts(data)
    
    st.markdown("---")
    
    # Render survey analysis
    render_survey_analysis(data)
    
    st.markdown("---")
    
    # Render health status
    render_health_status(data)
    
    st.markdown("---")
    
    # Advanced filtering section
    st.markdown("### 🔍 Advanced Data Filtering")
    
    # Render advanced filters
    filters = render_advanced_filters()
    
    # Get filtered data if filters are applied
    if filters:
        with st.spinner("Loading filtered data..."):
            filtered_data = get_filtered_data(filters)
        
        if filtered_data:
            render_filter_summary(filters, filtered_data)
            
            # Display filtered data
            if 'data' in filtered_data and filtered_data['data']:
                st.markdown("#### Filtered Data Preview")
                df = pd.DataFrame(filtered_data['data'])
                st.dataframe(df.head(100), width='stretch')
                
                # Download button for filtered data
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Filtered Data as CSV",
                    data=csv,
                    file_name="filtered_survey_data.csv",
                    mime="text/csv"
                )
    
    st.markdown("---")
    
    # Render data schema
    render_data_schema(data)

if __name__ == "__main__":
    main()
