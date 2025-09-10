"""
Simple test with basic queries
"""
import streamlit as st
from database import get_database

def simple_test():
    """Simple test with basic queries"""
    st.title("🔍 Simple Data Test")
    
    db = get_database()
    if not db:
        st.error("❌ No database connection")
        return
    
    st.success("✅ Connected to Snowflake")
    
    # Test 1: Simple count without alias
    st.markdown("### Test 1: Simple Count")
    try:
        result = db.execute_query("SELECT COUNT(*) FROM SURVEYS_DB.RAW.SEM_AND_PROFILE_SURVEYS_09092025")
        if not result.empty:
            st.success(f"✅ Count query works: {result.iloc[0, 0]} records")
        else:
            st.warning("⚠️ Count query returned no results")
    except Exception as e:
        st.error(f"❌ Count query failed: {str(e)}")
    
    # Test 2: Get survey IDs
    st.markdown("### Test 2: Survey IDs")
    try:
        result = db.execute_query("SELECT DISTINCT SURVEY_ID FROM SURVEYS_DB.RAW.SEM_AND_PROFILE_SURVEYS_09092025 WHERE SURVEY_ID IS NOT NULL")
        if not result.empty:
            st.success(f"✅ Found {len(result)} survey IDs")
            survey_ids = result.iloc[:, 0].tolist()  # Get first column
            st.info(f"Survey IDs: {survey_ids}")
        else:
            st.warning("⚠️ No survey IDs found")
    except Exception as e:
        st.error(f"❌ Survey ID query failed: {str(e)}")
    
    # Test 3: Sample data
    st.markdown("### Test 3: Sample Data")
    try:
        result = db.execute_query("SELECT * FROM SURVEYS_DB.RAW.SEM_AND_PROFILE_SURVEYS_09092025 LIMIT 3")
        if not result.empty:
            st.success(f"✅ Retrieved {len(result)} sample records")
            st.dataframe(result)
        else:
            st.warning("⚠️ No sample data")
    except Exception as e:
        st.error(f"❌ Sample data query failed: {str(e)}")
    
    # Test 4: Column names
    st.markdown("### Test 4: Column Names")
    try:
        result = db.execute_query("SELECT * FROM SURVEYS_DB.RAW.SEM_AND_PROFILE_SURVEYS_09092025 LIMIT 1")
        if not result.empty:
            st.success(f"✅ Table has {len(result.columns)} columns")
            st.info(f"Column names: {list(result.columns)}")
        else:
            st.warning("⚠️ Could not get column info")
    except Exception as e:
        st.error(f"❌ Column query failed: {str(e)}")

if __name__ == "__main__":
    simple_test()
