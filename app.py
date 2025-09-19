
import streamlit as st
import pandas as pd
import sys
import os
from urllib.parse import urlparse

# Add the dashboard_pages directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'dashboard_pages'))

# Add the styles directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'styles'))

# Import our new modules
from card_style import apply_card_styles, create_metric_card
from chart_utils import create_chart
from styles.global_styles import inject_global_styles

# Image service removed

# Import the page functions (lazy loading to prevent startup crashes)
# from demographics import main as demographics_main
# from survey_questions import main as survey_questions_main
# from auth_config import get_authenticator

# Page configuration
st.set_page_config(
    page_title="Sebenza Surveys Dashboard",
    page_icon="🚕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Suppress some Streamlit warnings
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

# No need for CSS to hide pages since they're moved out of the pages/ directory

def main():
    # Apply global styles
    inject_global_styles()
    
    # Temporarily disable authentication for deployment testing
    # try:
    #     # Authentication
    #     authenticator = get_authenticator()
    #     
    #     # Check if user is authenticated
    #     if 'authentication_status' not in st.session_state:
    #         st.session_state.authentication_status = None
    #     
    #     # Show login form if not authenticated
    #     if st.session_state.authentication_status != True:
    #         st.title("🔐 Surveys Dashboard Login")
    #         st.markdown("Please log in to access the dashboard")
    #         
    #         name, authentication_status, username = authenticator.login('Login', 'main')
    #         
    #         if authentication_status == False:
    #             st.error('Username/password is incorrect')
    #         elif authentication_status == None:
    #             st.warning('Please enter your username and password')
    #         else:
    #             st.session_state.authentication_status = True
    #             st.session_state.name = name
    #             st.session_state.username = username
    #             st.rerun()
    #         
    #         return
    # except Exception as e:
    #     st.error(f"Authentication error: {str(e)}")
    #     st.info("Please check your authentication configuration")
    #     return
    
    # User is authenticated, show the dashboard
    # st.sidebar.write(f'Welcome *{st.session_state.name}*')
    
    # Add logout button
    # if st.sidebar.button('Logout'):
    #     authenticator.logout('Logout', 'sidebar')
    #     st.session_state.authentication_status = False
    #     st.rerun()
    
    # Initialize session state for navigation
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'
    
    # Sidebar navigation
    st.sidebar.title("Sebenza Surveys Dashboard")
    st.sidebar.markdown("---")
    
    # Data usage monitoring
    if 'data_usage' in st.session_state and st.session_state.data_usage:
        with st.sidebar.expander("💰 Data Usage", expanded=False):
            total_records = sum(usage['records'] for usage in st.session_state.data_usage)
            st.metric("Total Records Loaded", f"{total_records:,}")
            st.metric("Pages Visited", len(st.session_state.data_usage))
            
            # Show recent usage
            for usage in st.session_state.data_usage[-3:]:  # Show last 3
                st.write(f"📄 {usage['page']}: {usage['records']:,} records")
    
    st.sidebar.markdown("---")

    
    # Sidebar button styling is now handled by global_styles.py
    
    # Add navigation buttons with consistent styling
    nav_buttons = [
        ("🏠 Home", "home", "home"),
        ("Demographics", "demographics", "demographics"),
        ("Profile Surveys", "survey_questions", "survey_questions"),
        ("Health Surveys", "health", "health"),
        ("Brands Analysis", "brands", "brands"),
        ("Profile Survey", "profile", "profile"),
        ("Funeral Cover", "funeral", "funeral"),
        ("Cellphone Survey", "cellphone", "cellphone"),
        ("Convenience Store", "convenience", "convenience"),
        ("Comprehensive Analytics", "comprehensive", "comprehensive")
    ]
    
    for button_text, key, page in nav_buttons:
        if st.sidebar.button(button_text, key=key, use_container_width=True):
            st.session_state.current_page = page
            st.rerun()
    
    # Add Sebenza logo below navigation buttons
    st.sidebar.markdown("---")

    # Display content based on current page
    if st.session_state.current_page == 'home':
        show_home_page()
    elif st.session_state.current_page == 'demographics':
        show_demographics_page()
    elif st.session_state.current_page == 'survey_questions':
        show_survey_questions_page()
    elif st.session_state.current_page == 'health':
        show_health_page()
    elif st.session_state.current_page == 'brands':
        show_brands_page()
    elif st.session_state.current_page == 'funeral':
        show_funeral_page()
    elif st.session_state.current_page == 'cellphone':
        show_cellphone_page()
    elif st.session_state.current_page == 'convenience':
        show_convenience_page()
    elif st.session_state.current_page == 'comprehensive':
        show_comprehensive_page() 

def show_demographics_page():
    # Lazy import to prevent startup crashes
    try:
        from demographics import main as demographics_main
        demographics_main()
    except ImportError as e:
        st.error(f"Demographics module not available: {e}")
        st.info("This will be fixed in the next deployment")

def show_survey_questions_page():
    # Lazy import to prevent startup crashes
    try:
        from dashboard_pages.profile_surveys import main as profile_surveys_main
        profile_surveys_main()
    except ImportError as e:
        st.error(f"Profile surveys module not available: {e}")
        st.info("This will be fixed in the next deployment")

def show_health_page():
    # Lazy import to prevent startup crashes
    try:
        from dashboard_pages.health import main as health_main
        health_main()
    except ImportError as e:
        st.error(f"Health module not available: {e}")
        st.info("This will be fixed in the next deployment")

def show_brands_page():
    # Lazy import to prevent startup crashes
    try:
        from dashboard_pages.brands import main as brands_main
        brands_main()
    except ImportError as e:
        st.error(f"Brands module not available: {e}")
        st.info("This will be fixed in the next deployment")


def show_funeral_page():
    # Lazy import to prevent startup crashes
    try:
        from dashboard_pages.funeral_cover import main as funeral_main
        funeral_main()
    except ImportError as e:
        st.error(f"Funeral Cover module not available: {e}")
        st.info("This will be fixed in the next deployment")

def show_cellphone_page():
    # Lazy import to prevent startup crashes
    try:
        from dashboard_pages.cellphone_survey import main as cellphone_main
        cellphone_main()
    except ImportError as e:
        st.error(f"Cellphone Survey module not available: {e}")
        st.info("This will be fixed in the next deployment")

def show_convenience_page():
    # Lazy import to prevent startup crashes
    try:
        from dashboard_pages.convenience_store import main as convenience_main
        convenience_main()
    except ImportError as e:
        st.error(f"Convenience Store module not available: {e}")
        st.info("This will be fixed in the next deployment")

def show_comprehensive_page():
    # Lazy import to prevent startup crashes
    try:
        from dashboard_pages.comprehensive_analytics import main as comprehensive_main
        comprehensive_main()
    except ImportError as e:
        st.error(f"Comprehensive Analytics module not available: {e}")
        st.info("This will be fixed in the next deployment")

def show_home_page():
    st.title("📊 Dashboard Overview")
    
    st.markdown("---")
    
    # Apply card styles
    apply_card_styles()
    
    # Survey Selection
    st.markdown("### 📊 Survey Selection")
    try:
        from backend_client import get_backend_client
        client = get_backend_client()
        if client:
            # Get available surveys
            surveys_index = client.get_surveys_index()
            if not surveys_index.empty and 'survey' in surveys_index.columns:
                available_surveys = surveys_index['survey'].unique().tolist()
            else:
                # Fallback to known surveys
                available_surveys = [
                    "SB055_Profile_Survey1",
                    "SB056_Cellphone_Survey", 
                    "FI027_1Life_Funeral_Cover_Survey",
                    "FI028_1Life_Funeral_Cover_Survey2"
                ]
            
            selected_survey = st.selectbox(
                "Select Survey:",
                options=available_surveys,
                index=0,
                key="home_survey_selection"
            )
        else:
            raise Exception("No backend connection")
    except:
        # Fallback to default survey
        selected_survey = "SB055_Profile_Survey1"
        st.info("Using default survey: SB055_Profile_Survey1")
    
    # Try to get real metrics from backend, fallback to sample data
    responses = None
    try:
        from backend_client import get_backend_client
        client = get_backend_client()
        if client:
            # Try to get survey index first (lightweight)
            surveys_index = client.get_surveys_index()
            if not surveys_index.empty:
                # Get total responses from index
                total_responses = len(surveys_index)
                unique_users = surveys_index['pid'].nunique() if 'pid' in surveys_index.columns else total_responses
                
                metrics_data = [
                    {"title": "Total Responses", "value": f"{total_responses:,}"},
                    {"title": "Unique Users", "value": f"{unique_users:,}"},
                ]
            else:
                # Fallback to responses endpoint with limit and required survey parameter
                responses = client.get_responses(survey=selected_survey, limit=1000)
                if not responses.empty:
                    # Calculate real metrics
                    total_responses = len(responses)
                    unique_users = responses['pid'].nunique() if 'pid' in responses.columns else 0
                    
                    metrics_data = [
                        {"title": "Total Responses", "value": f"{total_responses:,}"},
                        {"title": "Unique Users", "value": f"{unique_users:,}"},
                    ]
                else:
                    metrics_data = [
                        {"title": "Total Responses", "value": "0"},
                        {"title": "Unique Users", "value": "0"},
                    ]
        else:
            raise Exception("No backend connection")
    except:
        # Fallback to sample metrics
        metrics_data = [
            {"title": "Total Responses", "value": "144k"},
            {"title": "Unique Users", "value": "325k"},
        ]
    st.markdown("""
    ## Welcome to the Sebenza Surveys Dashboard!
    This dashboard provides comprehensive insights into the preferences and preceptions of South African Taxi Commuters.
    """)

    # Add metrics cards
    st.markdown("### Key Metrics")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(create_metric_card(
            "Total Responses", 
            metrics_data[0]["value"],
            "Survey responses collected"
        ), unsafe_allow_html=True)

    with col2:
        st.markdown(create_metric_card(
            "Unique Users", 
            metrics_data[1]["value"],
            "Distinct participants"
        ), unsafe_allow_html=True)

    # Add dashboard features
    st.markdown("### Features")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        #### Demographics Dashboard
        - **Gender Distribution**
        - **Age Group Analysis** 
        - **Employment Status**
        - **Location Analysis**
        - **SEM Groups**
        """)

    with col2:
        st.markdown("""
        #### Profile Surveys Dashboard
        - **Shop Visitation Analysis**
        - **Money Source Analysis**
        - **Commuter Spending**

        #### Health Surveys Dashboard
        - **Health Status Analysis**
        - **Exercise & Lifestyle**
        - **Sleep Patterns**

        #### Brands Analysis Dashboard
        - **Brand Preference Analysis**
        - **Shopping Behavior**
        - **Customer Satisfaction**

        #### Profile Survey Dashboard
        - **Demographic Analysis**
        - **Age & Gender Distribution**
        - **Employment & Income**

        #### Funeral Cover Dashboard
        - **Coverage Analysis**
        - **Provider Preferences**
        - **Satisfaction Metrics**

        #### Cellphone Survey Dashboard
        - **Device Usage Analysis**
        - **Network Provider Preferences**
        - **Spending Patterns**

        #### Convenience Store Dashboard
        - **Shopping Behavior**
        - **Product Preferences**
        - **Store Satisfaction**

        #### Comprehensive Analytics Dashboard
        - **Advanced Filtering**
        - **Cross-Survey Analysis**
        - **System Health Monitoring**
        - **Data Schema Documentation**

        **Last Updated**: `15-Sept-2025`
        """)

    # Add date range filter and trend chart if data is available
    try:
        if responses is not None and hasattr(responses, 'empty') and not responses.empty and 'ts' in responses.columns:
            # Date Range Filter
            st.markdown("### 📅 Date Range Filter")
            
            # Convert ts column to datetime if it exists
            responses['ts'] = pd.to_datetime(responses['ts'], errors='coerce')
            valid_dates = responses['ts'].dropna()
            
            if not valid_dates.empty:
                min_date = valid_dates.min().date()
                max_date = valid_dates.max().date()
                
                # Create date slider
                date_range = st.date_input(
                    "Select date range:",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date,
                    key="home_date_range_filter"
                )
                
                # Apply date filter to responses
                if len(date_range) == 2:
                    start_date, end_date = date_range
                    # Convert to datetime for comparison
                    start_datetime = pd.to_datetime(start_date)
                    end_datetime = pd.to_datetime(end_date) + pd.Timedelta(days=1)  # Include end date
                    
                    # Filter responses by date range
                    filtered_responses = responses[
                        (responses['ts'] >= start_datetime) & 
                        (responses['ts'] < end_datetime)
                    ]
                    
                    st.info(f"📊 Showing data from {start_date} to {end_date} ({len(filtered_responses):,} responses)")
                    
                    # Create trend chart with filtered data
                    st.markdown("### Response Trends")
                    dates = filtered_responses['ts'].dropna()
                    if not dates.empty:
                        # Create daily response counts
                        daily_counts = dates.dt.date.value_counts().sort_index()
                        trend_data = pd.DataFrame({
                            'date': daily_counts.index.astype(str),
                            'responses': daily_counts.values
                        })
                        
                        # Create chart with proper data validation and standardized fonts
                        if len(trend_data) > 0 and trend_data['responses'].sum() > 0:
                            chart = create_chart(
                                trend_data, 
                                'line', 
                                'date', 
                                'responses', 
                                'Daily Response Trends',
                                width=800,
                                height=300,
                                font_size=14,
                                title_font_size=16,
                                axis_font_size=12
                            )
                            
                            if chart is not None:
                                # Check if it's a Plotly figure or Altair chart
                                if hasattr(chart, 'update_layout'):  # Plotly figure
                                    st.plotly_chart(chart, use_container_width=True)
                                else:  # Altair chart
                                    st.altair_chart(chart, use_container_width=True)
                            else:
                                st.info("Daily Response Counts (Chart library not available)")
                                st.dataframe(trend_data, use_container_width=True)
                        else:
                            st.info("No data available for the selected date range")
                            st.dataframe(trend_data, use_container_width=True)
                    else:
                        st.info("No valid date data available for trend analysis in selected range")
                else:
                    st.info("📊 Please select both start and end dates")
            else:
                st.warning("⚠️ No valid date data found in responses")
        else:
            st.info("No timestamp data available for trend analysis")
    except Exception as e:
        st.info("Unable to display response trends at this time")

    # Add Survey Questions Analysis
    try:
        if responses is not None and hasattr(responses, 'empty') and not responses.empty and 'q' in responses.columns:
            st.markdown("### Survey Questions Analysis")
            
            # Show unique questions count
            unique_questions = responses['q'].dropna().unique()
            st.markdown(f"**Total unique questions:** {len(unique_questions)}")
            
            # Show question distribution in a neat table
            question_counts = responses['q'].value_counts()
            st.markdown("**Top 10 most frequently asked questions:**")
            
            # Create a DataFrame for the table
            top_questions = question_counts.head(10)
            questions_data = []
            for i, (question, count) in enumerate(top_questions.items(), 1):
                questions_data.append({
                    "Question": question,
                    "Unique Responses": f"{count:,}"
                })
            
            questions_df = pd.DataFrame(questions_data)
            st.table(questions_df)
            
    except Exception as e:
        st.info("Unable to display survey questions analysis at this time")



 

if __name__ == "__main__":
    main()