import streamlit as st
import sys
import os

# Add the dashboard_pages directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'dashboard_pages'))

# Import the page functions
from demographics import main as demographics_main
from survey_questions import main as survey_questions_main

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
    # Initialize session state for navigation
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'
    
    # Sidebar navigation
    st.sidebar.title("📊 Navigation")
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
    # Call the demographics main function but skip its sidebar navigation
    demographics_main()

def show_survey_questions_page():
    # Call the survey questions main function but skip its sidebar navigation
    survey_questions_main()

def show_home_page():
    st.title("📊 Sebenza Surveys Dashboard")
    st.markdown("---")
    
    st.markdown("""
    ## Welcome to the Sebenza Surveys Dashboard!
    
    This dashboard provides comprehensive insights into your survey data from Snowflake.
    
    ### 📊 Available Pages:
    
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
    
    ### 🔍 **Key Features:**
    - **Interactive Filters**: Age, Gender, and SEM segment filtering
    - **Real-time Data**: Direct connection to Snowflake database
    - **Responsive Design**: Optimized for different screen sizes
    - **Export Capabilities**: Download data as CSV or JSON
    
    ### 🚀 **Getting Started:**
    1. **Choose a page** from the sidebar navigation
    2. **Apply filters** to focus on specific demographics
    3. **Explore charts** and interactive visualizations
    4. **Export data** for further analysis
    
    ### 📈 **Data Source:**
    - **Database**: Snowflake
    - **Table**: `SURVEYS_DB.RAW.NEW_DASBOARD_DATA1`
    - **Real-time**: Live connection to your data warehouse
    
    ### 💡 **Tips:**
    - Use the **SEM segment filters** to analyze different customer tiers
    - **Combine filters** for detailed demographic analysis
    - **Export data** to create custom reports
    - **Switch between pages** to explore different aspects of your data
    """)
    
    # Add some styling
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .feature-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #1f77b4;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Add some key metrics on the home page
    st.markdown("### 📊 Quick Stats")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h4>👥 Demographics</h4>
            <p>Gender, Age, Employment, Location, and SEM analysis with interactive filtering</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h4>📋 Survey Questions</h4>
            <p>Shop visits, trip costs, money sources, and spending patterns analysis</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h4>🔍 Advanced Filters</h4>
            <p>Age, Gender, and SEM segment filtering for detailed demographic analysis</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()