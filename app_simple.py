"""
Simplified version of the app for testing deployment
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
    
    st.success("✅ App is running successfully!")
    
    st.markdown("""
    ## Welcome to the Sebenza Surveys Dashboard!
    
    This is a simplified version to test deployment.
    
    ### 🚀 **Features:**
    - ✅ **Authentication**: Login required
    - ✅ **BigQuery Integration**: Connected to your data
    - ✅ **Interactive Charts**: Plotly Express visualizations
    - ✅ **Advanced Tables**: st-aggrid for better UX
    - ✅ **Caching**: Optimized performance
    - ✅ **Dark Theme**: Modern UI
    
    ### 📊 **Available Pages:**
    - **Demographics Dashboard**: Gender, Age, Employment, Location analysis
    - **Survey Questions Dashboard**: Shop visits, trip costs, money sources
    
    ### 🔐 **Login Credentials:**
    - Username: `admin` / Password: `password`
    - Username: `marilu` / Password: `password`
    """)
    
    # Test imports
    st.markdown("### 🧪 **System Status:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        try:
            import pandas as pd
            st.success("✅ Pandas")
        except:
            st.error("❌ Pandas")
        
        try:
            import plotly.express as px
            st.success("✅ Plotly")
        except:
            st.error("❌ Plotly")
    
    with col2:
        try:
            from google.cloud import bigquery
            st.success("✅ BigQuery")
        except:
            st.error("❌ BigQuery")
        
        try:
            from st_aggrid import AgGrid
            st.success("✅ st-aggrid")
        except:
            st.error("❌ st-aggrid")

if __name__ == "__main__":
    main()
