"""
Test script to verify backend connection
"""
import streamlit as st
from backend_client import get_backend_client

st.title("🧪 Backend Connection Test")

# Test backend connection
client = get_backend_client()

if client:
    st.success("✅ Backend client created successfully")
    
    # Test connection
    if client.test_connection():
        st.success("✅ Backend is accessible")
        
        # Test data endpoints
        st.markdown("### 📊 Testing Data Endpoints:")
        
        # Test survey summary
        st.markdown("**Survey Summary:**")
        summary_data = client.get_survey_summary()
        if not summary_data.empty:
            st.success(f"✅ Survey summary loaded: {len(summary_data)} rows")
            st.dataframe(summary_data.head())
        else:
            st.warning("⚠️ No survey summary data returned")
        
        # Test responses data
        st.markdown("**Survey Responses:**")
        responses_data = client.get_responses()
        if not responses_data.empty:
            st.success(f"✅ Survey responses loaded: {len(responses_data)} rows")
            st.dataframe(responses_data.head())
        else:
            st.warning("⚠️ No survey responses data returned")
        
        # Test survey questions data
        st.markdown("**Survey Questions:**")
        questions_data = client.get_survey_questions()
        if not questions_data.empty:
            st.success(f"✅ Survey questions loaded: {len(questions_data)} rows")
            st.dataframe(questions_data.head())
        else:
            st.warning("⚠️ No survey questions data returned")
    
    else:
        st.error("❌ Backend is not accessible")
        st.info("Please check your backend URL and make sure it's running")

else:
    st.error("❌ Backend client creation failed")
    st.info("Please check your secrets.toml configuration")
