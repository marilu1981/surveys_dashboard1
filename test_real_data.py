"""
Test script to verify connection with real Snowflake data
"""
import streamlit as st
from database import get_database

def test_real_data():
    """Test the real Snowflake data connection"""
    st.title("🔍 Real Data Connection Test")
    
    # Get database connection
    db = get_database()
    
    if not db:
        st.error("❌ No database connection available")
        return
    
    st.success("✅ Database connection established")
    
    # Test basic table access
    st.markdown("### 📊 Table Information")
    
    try:
        # Get table info
        table_info = db.execute_query("""
            SELECT COUNT(*) as total_records
            FROM SURVEYS_DB.RAW.SEM_AND_PROFILE_SURVEYS_09092025
        """)
        
        if not table_info.empty:
            total_records = table_info.iloc[0]['total_records']
            st.success(f"✅ Table accessible - {total_records:,} total records")
        else:
            st.warning("⚠️ Table accessible but no records found")
            
    except Exception as e:
        st.error(f"❌ Table access failed: {str(e)}")
        return
    
    # Test survey data
    st.markdown("### 📋 Survey Data")
    
    try:
        # Get unique surveys
        surveys = db.execute_query("""
            SELECT DISTINCT 
                SURVEY_ID,
                SURVEY_CATEGORY,
                SURVEY_TITLE,
                COUNT(*) as response_count
            FROM SURVEYS_DB.RAW.SEM_AND_PROFILE_SURVEYS_09092025
            GROUP BY SURVEY_ID, SURVEY_CATEGORY, SURVEY_TITLE
            ORDER BY SURVEY_ID
        """)
        
        if not surveys.empty:
            st.success(f"✅ Found {len(surveys)} unique surveys")
            st.dataframe(surveys, use_container_width=True)
        else:
            st.warning("⚠️ No survey data found")
            
    except Exception as e:
        st.error(f"❌ Survey data query failed: {str(e)}")
    
    # Test sample responses
    st.markdown("### 📝 Sample Responses")
    
    try:
        # Get sample responses
        sample_responses = db.execute_query("""
            SELECT 
                SURVEY_ID,
                SURVEY_TITLE,
                SURVEY_QUESTION,
                RESPONSE,
                SEM_SCORE,
                GENDER,
                AGEGROUP,
                LOCATION,
                CREATED_AT
            FROM SURVEYS_DB.RAW.SEM_AND_PROFILE_SURVEYS_09092025
            WHERE SURVEY_ID IS NOT NULL
            ORDER BY CREATED_AT DESC
            LIMIT 10
        """)
        
        if not sample_responses.empty:
            st.success(f"✅ Retrieved {len(sample_responses)} sample responses")
            st.dataframe(sample_responses, use_container_width=True)
        else:
            st.warning("⚠️ No response data found")
            
    except Exception as e:
        st.error(f"❌ Response data query failed: {str(e)}")
    
    # Test analytics
    st.markdown("### 📈 Analytics Test")
    
    try:
        # Get analytics for first survey
        first_survey = db.execute_query("""
            SELECT MIN(SURVEY_ID) as first_survey_id
            FROM SURVEYS_DB.RAW.SEM_AND_PROFILE_SURVEYS_09092025
            WHERE SURVEY_ID IS NOT NULL
        """)
        
        if not first_survey.empty:
            survey_id = first_survey.iloc[0]['first_survey_id']
            
            analytics = db.execute_query("""
                SELECT 
                    COUNT(*) as total_responses,
                    COUNT(DISTINCT PROFILEUUID) as unique_respondents,
                    COUNT(CASE WHEN SURVEY_COMPLETED = TRUE THEN 1 END) as completed_surveys,
                    AVG(SEM_SCORE) as avg_sem_score,
                    MIN(SEM_SCORE) as min_sem_score,
                    MAX(SEM_SCORE) as max_sem_score
                FROM SURVEYS_DB.RAW.SEM_AND_PROFILE_SURVEYS_09092025 
                WHERE SURVEY_ID = :survey_id
            """, {'survey_id': survey_id})
            
            if not analytics.empty:
                st.success(f"✅ Analytics calculated for Survey ID {survey_id}")
                st.dataframe(analytics, use_container_width=True)
            else:
                st.warning("⚠️ No analytics data found")
                
    except Exception as e:
        st.error(f"❌ Analytics query failed: {str(e)}")
    
    st.markdown("### 🎉 Test Complete!")
    st.info("If all tests passed, your dashboard should work with real data!")

if __name__ == "__main__":
    test_real_data()
