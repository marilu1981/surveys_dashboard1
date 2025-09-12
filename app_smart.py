"""
Smart app that only imports what it needs
"""
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Sebenza Surveys Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title("📊 Sebenza Surveys Dashboard")
    st.markdown("---")
    
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

def show_home_page():
    st.markdown("""
    ## Welcome to the Sebenza Surveys Dashboard!
    
    This dashboard provides comprehensive insights into your survey data.
    
    ### 📊 **Currently Available Pages:**
    
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

def show_demographics_page():
    st.title("📊 Demographics Dashboard")
    st.info("🔧 Demographics page - BigQuery connection will be added step by step")
    
    # Only import when needed
    try:
        import pandas as pd
        import plotly.express as px
        
        # Create sample data for testing
        sample_data = pd.DataFrame({
            'Gender': ['Male', 'Female', 'Other'] * 100,
            'Age': ['18-25', '26-35', '36-45', '46-55', '55+'] * 60,
            'Location': ['Cape Town', 'Johannesburg', 'Durban', 'Pretoria'] * 75
        })
        
        col1, col2 = st.columns(2)
        
        with col1:
            gender_counts = sample_data['Gender'].value_counts()
            fig = px.pie(values=gender_counts.values, names=gender_counts.index, title="Gender Distribution")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            age_counts = sample_data['Age'].value_counts()
            fig = px.bar(x=age_counts.index, y=age_counts.values, title="Age Group Distribution")
            st.plotly_chart(fig, use_container_width=True)
        
        st.success("✅ Charts are working! BigQuery connection will be added next.")
        
    except ImportError as e:
        st.error(f"Missing dependency: {e}")
        st.info("This page requires pandas and plotly. They will be added in the next deployment.")

def show_survey_questions_page():
    st.title("📋 Survey Questions Dashboard")
    st.info("🔧 Survey questions page - BigQuery connection will be added step by step")
    
    # Only import when needed
    try:
        import pandas as pd
        import plotly.express as px
        
        # Create sample data for testing
        sample_data = pd.DataFrame({
            'Shop': ['Shoprite', 'Pick n Pay', 'Woolworths', 'Checkers'] * 50,
            'Cost': [25, 35, 45, 30, 20, 40, 50, 15] * 25,
            'Source': ['Salary', 'Business', 'Side Hustle', 'Other'] * 50
        })
        
        col1, col2 = st.columns(2)
        
        with col1:
            shop_counts = sample_data['Shop'].value_counts()
            fig = px.bar(x=shop_counts.values, y=shop_counts.index, orientation='h', title="Shop Visits")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.histogram(sample_data, x='Cost', title="Trip Cost Distribution")
            st.plotly_chart(fig, use_container_width=True)
        
        st.success("✅ Charts are working! BigQuery connection will be added next.")
        
    except ImportError as e:
        st.error(f"Missing dependency: {e}")
        st.info("This page requires pandas and plotly. They will be added in the next deployment.")

if __name__ == "__main__":
    main()
