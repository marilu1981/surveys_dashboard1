
import streamlit as st
import sys
import os

# Add the dashboard_pages directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'dashboard_pages'))

# Add the styles directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'styles'))

# Import our new modules
from card_style import apply_card_styles, create_metric_card
from dashboard import create_metrics_dashboard

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
    st.sidebar.title("Navigation")
    st.sidebar.markdown("---")
    
    # Add navigation buttons
    if st.sidebar.button("🏠 Home", key="home"):
        st.session_state.current_page = 'home'
        st.rerun()
    
    if st.sidebar.button("👥 Demographics", key="demographics"):
        st.session_state.current_page = 'demographics'
        st.rerun()
    
    if st.sidebar.button("📋 Survey Questions", key="survey_questions"):
        st.session_state.current_page = 'survey_questions'
        st.rerun()
    
    # Display content based on current page
    if st.session_state.current_page == 'home':
        show_home_page()
    elif st.session_state.current_page == 'demographics':
        show_demographics_page()
    elif st.session_state.current_page == 'survey_questions':
        show_survey_questions_page()

def show_demographics_page():
    st.title("📊 Demographics Dashboard")
    st.info("🔧 Demographics page - will be enabled step by step")
    
    # Lazy import to prevent startup crashes
    try:
        from demographics import main as demographics_main
        demographics_main()
    except ImportError as e:
        st.error(f"Demographics module not available: {e}")
        st.info("This will be fixed in the next deployment")

def show_survey_questions_page():
    st.title("📋 Survey Questions Dashboard")
    st.info("🔧 Survey questions page - will be enabled step by step")
    
    # Lazy import to prevent startup crashes
    try:
        from survey_questions import main as survey_questions_main
        survey_questions_main()
    except ImportError as e:
        st.error(f"Survey questions module not available: {e}")
        st.info("This will be fixed in the next deployment")

def show_home_page():
    st.title("📊 Sebenza Surveys Dashboard")
    st.markdown("---")
    
    # Apply card styles
    apply_card_styles()
    
    # Add key metrics dashboard
    st.markdown("### 📊 Dashboard Overview")
    
    # Try to get real metrics from backend, fallback to sample data
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
                    {"title": "Data Status", "value": date_range}
                ]
            else:
                metrics_data = [
                    {"title": "Total Responses", "value": "0"},
                    {"title": "Unique Users", "value": "0"},
                    {"title": "Data Status", "value": "No Data"}
                ]
        else:
            raise Exception("No backend connection")
    except:
        # Fallback to sample metrics
        metrics_data = [
            {"title": "Total Responses", "value": "144k"},
            {"title": "Unique Users", "value": "325k"},
            {"title": "Data Status", "value": "Sample Data"}
        ]
    
    # Create metrics dashboard
    create_metrics_dashboard(metrics_data)
    
    st.markdown("""
    ## Welcome to the Sebenza Surveys Dashboard!
    
    This dashboard provides comprehensive insights into your survey data from Snowflake.
    
    ### 📊Currently Available Pages:
    
    #### 👥 **Demographics Dashboard**
    - **Gender Distribution**: Interactive pie charts with filtering
    - **Age Group Analysis**: Bar charts with demographic breakdowns
    - **Employment Status**: Employment distribution across segments
    - **Location Analysis**: South African province mapping and rankings
    - **SEM Groups**: Socio-Economic Measure segmentation analysis
    
    #### 📋 **Survey Questions Dashboard**
    - **Shop Visitation Analysis**: Which shops respondents visit most often
    - **Trip Cost Analysis**: Travel spending patterns and cost distributions
    - **Money Source Analysis**: Main income sources and side hustles
    - **Commuter Spending**: Monthly and weekly spending analysis
       
    ### 🚀 **Getting Started:**
    1. **Choose a page** from the sidebar navigation
    2. **Apply filters** to focus on specific demographics
    3. **Explore charts** and interactive visualizations
    4. **Export data** for further analysis
    
    ### 📈 **Data Source:**
    - **Database**: Google Cloud BigQuery
    - **Table**: `surveys_db.new_dashboard_data1`
    - **Real-time**: Live connection to your data warehouse with caching
    """)
    
    # Add feature cards with new styling
    st.markdown("### 🎯 Key Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(create_metric_card(
            "👥 Demographics", 
            "Advanced Analysis", 
            "Gender, Age, Employment, Location, and SEM analysis with interactive filtering"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_metric_card(
            "📋 Survey Questions", 
            "Comprehensive", 
            "Shop visits, trip costs, money sources, and spending patterns analysis"
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_metric_card(
            "🔍 Advanced Filters", 
            "Multi-dimensional", 
            "Age, Gender, and SEM segment filtering for detailed demographic analysis"
        ), unsafe_allow_html=True)

if __name__ == "__main__":
    main()