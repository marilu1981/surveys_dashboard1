"""
Advanced Filtering Component for Survey Data
"""
import streamlit as st
import pandas as pd
from backend_client import get_backend_client
from typing import Dict, Any, Optional

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_filter_vocabulary():
    """Get vocabulary mappings for filter options"""
    client = get_backend_client()
    if not client:
        return {}
    
    try:
        vocab = client.get_vocabulary()
        if "error" not in vocab:
            return vocab
        else:
            return {}
    except Exception as e:
        st.warning(f"Could not load vocabulary: {str(e)}")
        return {}

def render_advanced_filters() -> Dict[str, Any]:
    """Render advanced filtering interface and return filter values"""
    
    # Get vocabulary for filter options
    vocab = get_filter_vocabulary()
    
    st.sidebar.header("🔍 Advanced Filters")
    
    # Initialize session state for filters
    if 'advanced_filters' not in st.session_state:
        st.session_state.advanced_filters = {}
    
    filters = {}
    
    # Survey filter
    with st.sidebar.expander("📋 Survey", expanded=False):
        survey_options = ["All Surveys", "SB055_Profile_Survey1", "FI027_1Life_Funeral_Cover_Survey", 
                         "FI028_1Life_Funeral_Cover_Survey2", "SB056_Cellphone_Survey", 
                         "TP005_Convinience_Store_Products_Survey_Briefing_Form"]
        selected_survey = st.selectbox(
            "Select Survey",
            options=survey_options,
            key="filter_survey"
        )
        if selected_survey != "All Surveys":
            filters['survey'] = selected_survey
    
    # Gender filter
    with st.sidebar.expander("Gender", expanded=False):
        gender_options = ["All Genders"] + (vocab.get('gender_values', ['Male', 'Female', 'Other']))
        selected_gender = st.selectbox(
            "Select Gender",
            options=gender_options,
            key="filter_gender"
        )
        if selected_gender != "All Genders":
            filters['gender'] = selected_gender
    
    # Age Group filter
    with st.sidebar.expander("Age Group", expanded=False):
        age_options = ["All Ages"] + (vocab.get('age_group_values', ['18-24', '25-34', '35-44', '45-54', '55+']))
        selected_age = st.selectbox(
            "Select Age Group",
            options=age_options,
            key="filter_age"
        )
        if selected_age != "All Ages":
            filters['age_group'] = selected_age
    
    # Employment filter
    with st.sidebar.expander("Employment", expanded=False):
        employment_options = ["All Employment"] + (vocab.get('employment_values', ['Employed', 'Unemployed', 'Student', 'Retired']))
        selected_employment = st.selectbox(
            "Select Employment Status",
            options=employment_options,
            key="filter_employment"
        )
        if selected_employment != "All Employment":
            filters['employment'] = selected_employment
    
    # Location filter
    with st.sidebar.expander("Location", expanded=False):
        location_options = ["All Locations"] + (vocab.get('home_province_values', ['Gauteng', 'Western Cape', 'KwaZulu-Natal', 'Eastern Cape', 'Free State', 'Limpopo', 'Mpumalanga', 'Northern Cape', 'North West']))
        selected_location = st.selectbox(
            "Select Location",
            options=location_options,
            key="filter_location"
        )
        if selected_location != "All Locations":
            filters['home_province'] = selected_location
    
    # Date range filter
    with st.sidebar.expander("📅 Date Range", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                key="filter_start_date"
            )
        with col2:
            end_date = st.date_input(
                "End Date",
                key="filter_end_date"
            )
        
        if start_date:
            filters['start_date'] = start_date.strftime('%Y-%m-%d')
        if end_date:
            filters['end_date'] = end_date.strftime('%Y-%m-%d')
    
    # Data limit
    with st.sidebar.expander("📊 Data Limit", expanded=False):
        limit_options = [100, 500, 1000, 5000, 10000]
        selected_limit = st.selectbox(
            "Max Responses",
            options=limit_options,
            index=2,  # Default to 1000
            key="filter_limit"
        )
        filters['limit'] = selected_limit
    
    # Clear filters button
    if st.sidebar.button("🗑️ Clear All Filters", key="clear_filters"):
        # Clear all filter session state
        for key in list(st.session_state.keys()):
            if key.startswith('filter_'):
                del st.session_state[key]
        st.rerun()
    
    # Show active filters
    if filters:
        st.sidebar.markdown("---")
        st.sidebar.markdown("**Active Filters:**")
        for key, value in filters.items():
            st.sidebar.markdown(f"• {key}: {value}")
    
    return filters

def get_filtered_data(filters: Dict[str, Any]) -> Optional[pd.DataFrame]:
    """Get filtered data using the advanced filters"""
    client = get_backend_client()
    if not client:
        return None
    
    try:
        # Ensure survey parameter is present
        if 'survey' not in filters:
            st.warning("⚠️ Survey parameter is required for filtered responses")
            return None
            
        # Use the get_responses method with filters
        params = {k: v for k, v in filters.items() if v not in (None, "")}
        survey_id = params.pop('survey', None)
        if not survey_id:
            st.warning('A survey must be selected before filtering.')
            return None
        data = client.get_responses(survey=survey_id, **params)
    except Exception as e:
        st.error(f"Error fetching filtered data: {str(e)}")
        return None

def render_filter_summary(filters: Dict[str, Any], data: Optional[Dict[str, Any]]):
    """Render a summary of applied filters and data"""
    if not filters:
        st.info("No filters applied - showing all data")
        return
    
    st.info(f"🔍 **Filters Applied:** {len(filters)} filter(s)")
    
    # Show filter details
    filter_details = []
    for key, value in filters.items():
        filter_details.append(f"**{key.replace('_', ' ').title()}:** {value}")
    
    st.markdown(" | ".join(filter_details))
    
    # Show data summary
    if data and 'pagination' in data:
        pagination = data['pagination']
        st.markdown(f"**Results:** {len(data.get('data', []))} of {pagination.get('total', 0)} responses")
        
        if pagination.get('has_more', False):
            st.warning("⚠️ Results are limited by the data limit filter. Increase the limit to see more data.")


def main():
    filters = render_advanced_filters()
    if filters:
        st.sidebar.success("Filters applied. Please navigate to the desired dashboard.")


if __name__ == "__main__":
    main()

