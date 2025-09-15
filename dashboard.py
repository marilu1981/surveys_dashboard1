import streamlit as st
import sys
import os

# Add the styles directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'styles'))
from card_style import apply_card_styles, create_metric_card, create_dashboard_container, end_dashboard_container

def create_metrics_dashboard(metrics_data=None):
    """
    Create a metrics dashboard with styled cards
    
    Parameters:
    - metrics_data: List of dictionaries with 'title' and 'value' keys
    """
    
    # Apply card styles
    apply_card_styles()
    
    # Default metrics if none provided
    if metrics_data is None:
        metrics_data = [
            {"title": "Total Responses", "value": "144k"},
            {"title": "Unique Users", "value": "325k"},
            {"title": "Active Surveys", "value": "200k"}
        ]
    
    # Create dashboard container
    create_dashboard_container()
    
    # Display metrics
    for metric in metrics_data:
        st.markdown(f'''
        <div class="card" style="min-width:200px;max-width:260px;flex:1">
            <div class="card-title">{metric["title"]}</div>
            <div class="metric-value">{metric["value"]}</div>
        </div>
        ''', unsafe_allow_html=True)
    
    # End dashboard container
    end_dashboard_container()

def create_sample_dashboard():
    """Create a sample dashboard for demonstration"""
    st.title("📊 Sample Metrics Dashboard")
    
    # Sample metrics
    sample_metrics = [
        {"title": "Users", "value": "144k"},
        {"title": "Conversions", "value": "325k"},
        {"title": "Event count", "value": "200k"}
    ]
    
    create_metrics_dashboard(sample_metrics)

# For direct execution
if __name__ == "__main__":
    create_sample_dashboard()