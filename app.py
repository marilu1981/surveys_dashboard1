
import streamlit as st
import pandas as pd
import sys
import os

# Add the dashboard_pages directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'dashboard_pages'))

# Add the styles directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'styles'))

# Import our new modules
from card_style import apply_card_styles, create_metric_card
from dashboard import create_metrics_dashboard
from chart_utils import create_altair_chart

# Import the page functions (lazy loading to prevent startup crashes)
# from demographics import main as demographics_main
# from survey_questions import main as survey_questions_main
# from auth_config import get_authenticator

# Page configuration
st.set_page_config(
    page_title="Sebenza Surveys Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Suppress some Streamlit warnings
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

# No need for CSS to hide pages since they're moved out of the pages/ directory

def main():
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
    st.sidebar.title("📊 Sebenza Surveys Dashboard")
    st.sidebar.markdown("---")

    
    # Add navigation buttons
    if st.sidebar.button("🏠 Home", key="home", width="stretch"):
        st.session_state.current_page = 'home'
        st.rerun()
    
    if st.sidebar.button("Demographics", key="demographics", width="stretch"):
        st.session_state.current_page = 'demographics'
        st.rerun()
    
    if st.sidebar.button("Survey Questions", key="survey_questions", width="stretch"):
        st.session_state.current_page = 'survey_questions'
        st.rerun()
    
    if st.sidebar.button("🏥 Health Surveys", key="health", width="stretch"):
        st.session_state.current_page = 'health'
        st.rerun()
    
    if st.sidebar.button("🏷️ Brands Analysis", key="brands", width="stretch"):
        st.session_state.current_page = 'brands'
        st.rerun()
    
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
        from survey_questions import main as survey_questions_main
        survey_questions_main()
    except ImportError as e:
        st.error(f"Survey questions module not available: {e}")
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

def show_home_page():
    st.title("📊 Dashboard Overview")
    st.markdown("---")
    
    # Apply card styles
    apply_card_styles()
    
    
    # Try to get real metrics from backend, fallback to sample data
    responses = None
    try:
        from backend_client import get_backend_client
        client = get_backend_client()
        if client:
            responses = client.get_responses()
            if not responses.empty:
                # Calculate real metrics
                total_responses = len(responses)
                unique_users = responses['pid'].nunique() if 'pid' in responses.columns else 0
                date_range = "Live Data"
                
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
    st.markdown("### 📊 Key Metrics")
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
    st.markdown("### 📋 Features")
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
            #### Survey Questions Dashboard
            - **Shop Visitation Analysis**
            - **Money Source Analysis**
            - **Commuter Spending**

                #### 🏥 Health Surveys Dashboard
                - **Health Status Analysis**
                - **Exercise & Lifestyle**
                - **Sleep Patterns**

                #### 🏷️ Brands Analysis Dashboard
                - **Brand Preference Analysis**
                - **Shopping Behavior**
                - **Customer Satisfaction**

                **Last Updated**: `15-Sept-2025`
            """)

    # Add trend chart if data is available
    try:
        if responses is not None and hasattr(responses, 'empty') and not responses.empty and 'ts' in responses.columns:
            st.markdown("### 📈 Response Trends")
            dates = pd.to_datetime(responses['ts'], errors='coerce').dropna()
            if not dates.empty:
                # Create daily response counts
                daily_counts = dates.dt.date.value_counts().sort_index()
                trend_data = pd.DataFrame({
                    'date': daily_counts.index.astype(str),
                    'responses': daily_counts.values
                })
                
                # Create Altair chart
                altair_chart = create_altair_chart(
                    trend_data, 
                    'line', 
                    'date', 
                    'responses', 
                    'Daily Response Trends',
                    width=800,
                    height=300
                )
                
                if altair_chart is not None:
                    st.altair_chart(altair_chart, use_container_width=True)
                else:
                    st.info("📊 Daily Response Counts (Altair not available)")
                    st.dataframe(trend_data, use_container_width=True)
            else:
                st.info("No valid date data available for trend analysis")
        else:
            st.info("No timestamp data available for trend analysis")
    except Exception as e:
        st.info("Unable to display response trends at this time")

    # Add Survey Questions Analysis
    try:
        if responses is not None and hasattr(responses, 'empty') and not responses.empty and 'q' in responses.columns:
            st.markdown("### 📝 Survey Questions Analysis")
            
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