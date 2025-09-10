"""
Find what survey IDs exist in your data
"""
import streamlit as st
from database import get_database

def find_surveys():
    """Find available survey IDs"""
    st.title("🔍 Find Your Survey Data")
    
    db = get_database()
    if not db:
        st.error("❌ No database connection")
        return
    
    st.success("✅ Connected to Snowflake")
    
    # Get all survey IDs
    try:
        surveys = db.execute_query("""
            SELECT DISTINCT SURVEY_ID, COUNT(*) as record_count
            FROM SURVEYS_DB.RAW.SEM_AND_PROFILE_SURVEYS_09092025
            WHERE SURVEY_ID IS NOT NULL
            GROUP BY SURVEY_ID
            ORDER BY SURVEY_ID
        """)
        
        if not surveys.empty:
            st.success(f"✅ Found {len(surveys)} survey IDs:")
            st.dataframe(surveys)
            
            # Show the survey IDs as a list
            survey_ids = surveys['SURVEY_ID'].tolist()
            st.info(f"Available Survey IDs: {survey_ids}")
            
            # Test with the first survey ID
            if survey_ids:
                test_id = survey_ids[0]
                st.markdown(f"### 🧪 Testing with Survey ID: {test_id}")
                
                # Test survey data
                survey_data = db.get_survey_data(test_id)
                if not survey_data.empty:
                    st.success("✅ Survey data found!")
                    st.dataframe(survey_data)
                else:
                    st.warning("⚠️ No survey data found")
                
                # Test responses
                responses = db.get_survey_responses(test_id)
                if not responses.empty:
                    st.success(f"✅ Found {len(responses)} responses!")
                    st.dataframe(responses.head())
                else:
                    st.warning("⚠️ No responses found")
                
                # Test analytics
                analytics = db.get_survey_analytics(test_id)
                if not analytics.empty:
                    st.success("✅ Analytics calculated!")
                    st.dataframe(analytics)
                else:
                    st.warning("⚠️ No analytics data")
                    
        else:
            st.warning("⚠️ No survey IDs found")
            
    except Exception as e:
        st.error(f"❌ Error: {e}")
    
    # Show sample data structure
    st.markdown("### 📋 Sample Data Structure")
    try:
        sample = db.execute_query("""
            SELECT *
            FROM SURVEYS_DB.RAW.SEM_AND_PROFILE_SURVEYS_09092025
            LIMIT 3
        """)
        
        if not sample.empty:
            st.success("✅ Sample data retrieved")
            st.dataframe(sample)
        else:
            st.warning("⚠️ No sample data")
    except Exception as e:
        st.error(f"❌ Error getting sample: {e}")

if __name__ == "__main__":
    find_surveys()
