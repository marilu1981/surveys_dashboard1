"""
Simple test to verify parameter binding works
"""
import streamlit as st
from database import get_database

def test_simple():
    """Simple test for parameter binding"""
    st.title("🔍 Simple Parameter Test")
    
    # Get database connection
    db = get_database()
    
    if not db:
        st.error("❌ No database connection available")
        return
    
    st.success("✅ Database connection established")
    
    # Test 1: Simple query without parameters
    st.markdown("### Test 1: Simple Query")
    try:
        result = db.execute_query("SELECT COUNT(*) as total FROM SURVEYS_DB.RAW.SEM_AND_PROFILE_SURVEYS_09092025")
        if not result.empty:
            st.success(f"✅ Simple query works: {result.iloc[0]['total']} records")
        else:
            st.warning("⚠️ Simple query returned no results")
    except Exception as e:
        st.error(f"❌ Simple query failed: {str(e)}")
    
    # Test 2: Query with parameters
    st.markdown("### Test 2: Parameterized Query")
    try:
        result = db.execute_query("""
            SELECT COUNT(*) as count 
            FROM SURVEYS_DB.RAW.SEM_AND_PROFILE_SURVEYS_09092025 
            WHERE SURVEY_ID = :survey_id
        """, {'survey_id': 1})
        
        if not result.empty:
            st.success(f"✅ Parameterized query works: {result.iloc[0]['count']} records for survey_id=1")
        else:
            st.warning("⚠️ Parameterized query returned no results")
    except Exception as e:
        st.error(f"❌ Parameterized query failed: {str(e)}")
    
    # Test 3: Get available survey IDs
    st.markdown("### Test 3: Available Survey IDs")
    try:
        result = db.execute_query("""
            SELECT DISTINCT SURVEY_ID 
            FROM SURVEYS_DB.RAW.SEM_AND_PROFILE_SURVEYS_09092025 
            WHERE SURVEY_ID IS NOT NULL 
            ORDER BY SURVEY_ID
        """)
        
        if not result.empty:
            survey_ids = result['SURVEY_ID'].tolist()
            st.success(f"✅ Found survey IDs: {survey_ids}")
            
            # Test with first available survey ID
            if survey_ids:
                first_id = survey_ids[0]
                st.info(f"Testing with survey ID: {first_id}")
                
                test_result = db.execute_query("""
                    SELECT COUNT(*) as count 
                    FROM SURVEYS_DB.RAW.SEM_AND_PROFILE_SURVEYS_09092025 
                    WHERE SURVEY_ID = :survey_id
                """, {'survey_id': first_id})
                
                if not test_result.empty:
                    st.success(f"✅ Test with survey ID {first_id}: {test_result.iloc[0]['count']} records")
        else:
            st.warning("⚠️ No survey IDs found")
    except Exception as e:
        st.error(f"❌ Survey ID query failed: {str(e)}")

if __name__ == "__main__":
    test_simple()
