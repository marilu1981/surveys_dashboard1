"""
Simple diagnostic script to check what data exists
"""
import streamlit as st
from database import get_database

def diagnose():
    """Diagnose what data exists"""
    st.title("🔍 Data Diagnosis")
    
    db = get_database()
    if not db:
        st.error("❌ No database connection")
        return
    
    st.success("✅ Connected to Snowflake")
    
    # Check total records
    try:
        total = db.execute_query("SELECT COUNT(*) as count FROM SURVEYS_DB.RAW.SEM_AND_PROFILE_SURVEYS_09092025")
        if not total.empty:
            st.info(f"📊 Total records: {total.iloc[0]['count']:,}")
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return
    
    # Check survey IDs
    try:
        surveys = db.execute_query("""
            SELECT DISTINCT SURVEY_ID, COUNT(*) as count
            FROM SURVEYS_DB.RAW.SEM_AND_PROFILE_SURVEYS_09092025
            WHERE SURVEY_ID IS NOT NULL
            GROUP BY SURVEY_ID
            ORDER BY SURVEY_ID
        """)
        
        if not surveys.empty:
            st.success(f"✅ Found {len(surveys)} survey IDs:")
            st.dataframe(surveys)
            
            # Test with first survey ID
            first_survey = surveys.iloc[0]['SURVEY_ID']
            st.info(f"🧪 Testing with survey ID: {first_survey}")
            
            # Test survey data query
            survey_data = db.get_survey_data(first_survey)
            if not survey_data.empty:
                st.success("✅ Survey data query works!")
                st.dataframe(survey_data)
            else:
                st.warning("⚠️ Survey data query returned empty")
            
            # Test survey responses query
            responses = db.get_survey_responses(first_survey)
            if not responses.empty:
                st.success(f"✅ Survey responses query works! Found {len(responses)} responses")
                st.dataframe(responses.head())
            else:
                st.warning("⚠️ Survey responses query returned empty")
                
        else:
            st.warning("⚠️ No survey IDs found")
    except Exception as e:
        st.error(f"❌ Error: {e}")

if __name__ == "__main__":
    diagnose()
