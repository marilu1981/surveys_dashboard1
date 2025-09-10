"""
Check what data exists in your Snowflake table
"""
import streamlit as st
from database import get_database

def check_data():
    """Check what data exists in the table"""
    st.title("🔍 Data Check")
    
    # Get database connection
    db = get_database()
    
    if not db:
        st.error("❌ No database connection available")
        return
    
    st.success("✅ Database connection established")
    
    # Check total records
    st.markdown("### 📊 Total Records")
    try:
        result = db.execute_query("SELECT COUNT(*) as total FROM SURVEYS_DB.RAW.SEM_AND_PROFILE_SURVEYS_09092025")
        if not result.empty:
            total = result.iloc[0]['total']
            st.info(f"Total records in table: {total:,}")
            
            if total == 0:
                st.warning("⚠️ Table is empty - no data found")
                st.info("You need to import your survey data into this table")
            else:
                st.success(f"✅ Found {total:,} records")
        else:
            st.warning("⚠️ Could not count records")
    except Exception as e:
        st.error(f"❌ Error counting records: {str(e)}")
    
    # Check for survey IDs
    st.markdown("### 📋 Survey IDs")
    try:
        result = db.execute_query("""
            SELECT DISTINCT SURVEY_ID, COUNT(*) as count
            FROM SURVEYS_DB.RAW.SEM_AND_PROFILE_SURVEYS_09092025
            WHERE SURVEY_ID IS NOT NULL
            GROUP BY SURVEY_ID
            ORDER BY SURVEY_ID
        """)
        
        if not result.empty:
            st.success(f"✅ Found {len(result)} unique survey IDs")
            st.dataframe(result, use_container_width=True)
        else:
            st.warning("⚠️ No survey IDs found")
    except Exception as e:
        st.error(f"❌ Error getting survey IDs: {str(e)}")
    
    # Check sample data
    st.markdown("### 📝 Sample Data")
    try:
        result = db.execute_query("""
            SELECT *
            FROM SURVEYS_DB.RAW.SEM_AND_PROFILE_SURVEYS_09092025
            LIMIT 5
        """)
        
        if not result.empty:
            st.success(f"✅ Retrieved {len(result)} sample records")
            st.dataframe(result, use_container_width=True)
        else:
            st.warning("⚠️ No sample data found")
    except Exception as e:
        st.error(f"❌ Error getting sample data: {str(e)}")
    
    # Check column structure
    st.markdown("### 🏗️ Table Structure")
    try:
        result = db.execute_query("""
            SELECT COLUMN_NAME, DATA_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'SEM_AND_PROFILE_SURVEYS_09092025'
            AND TABLE_SCHEMA = 'RAW'
            ORDER BY ORDINAL_POSITION
        """)
        
        if not result.empty:
            st.success(f"✅ Table has {len(result)} columns")
            st.dataframe(result, use_container_width=True)
        else:
            st.warning("⚠️ Could not get table structure")
    except Exception as e:
        st.error(f"❌ Error getting table structure: {str(e)}")

if __name__ == "__main__":
    check_data()
