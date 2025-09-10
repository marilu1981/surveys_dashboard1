"""
Test script to verify Snowflake connection
"""
import streamlit as st
from config import config
from database import SnowflakeConnection

def test_snowflake_connection():
    """Test the Snowflake connection"""
    st.title("🔍 Snowflake Connection Test")
    
    # Display configuration (without password)
    st.markdown("### Configuration Status")
    config_status = {
        "Account": config.account,
        "User": config.user,
        "Password": "***" if config.password else "Not set",
        "Warehouse": config.warehouse,
        "Database": config.database,
        "Schema": config.schema,
        "Role": config.role
    }
    
    for key, value in config_status.items():
        if value:
            st.success(f"✅ {key}: {value}")
        else:
            st.error(f"❌ {key}: Not configured")
    
    # Test connection
    st.markdown("### Connection Test")
    if st.button("Test Snowflake Connection"):
        db = SnowflakeConnection()
        if db.connect():
            st.success("🎉 Connection successful!")
            
            # Test a simple query
            try:
                result = db.execute_query("SELECT CURRENT_DATABASE(), CURRENT_SCHEMA(), CURRENT_USER()")
                if not result.empty:
                    st.markdown("### Connection Details")
                    st.dataframe(result, use_container_width=True)
            except Exception as e:
                st.error(f"Query test failed: {str(e)}")
        else:
            st.error("❌ Connection failed!")
    
    # Check if tables exist
    st.markdown("### Database Schema Check")
    if st.button("Check Required Tables"):
        db = SnowflakeConnection()
        if db.connect():
            try:
                # Check for surveys table
                surveys_check = db.execute_query("""
                    SELECT COUNT(*) as table_exists 
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_NAME = 'SURVEYS' AND TABLE_SCHEMA = UPPER('{}')
                """.format(config.schema))
                
                if not surveys_check.empty and surveys_check.iloc[0]['table_exists'] > 0:
                    st.success("✅ SURVEYS table exists")
                else:
                    st.warning("⚠️ SURVEYS table not found")
                
                # Check for survey_responses table
                responses_check = db.execute_query("""
                    SELECT COUNT(*) as table_exists 
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_NAME = 'SURVEY_RESPONSES' AND TABLE_SCHEMA = UPPER('{}')
                """.format(config.schema))
                
                if not responses_check.empty and responses_check.iloc[0]['table_exists'] > 0:
                    st.success("✅ SURVEY_RESPONSES table exists")
                else:
                    st.warning("⚠️ SURVEY_RESPONSES table not found")
                
                # Show available tables
                tables = db.execute_query("""
                    SELECT TABLE_NAME, TABLE_TYPE 
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_SCHEMA = UPPER('{}')
                    ORDER BY TABLE_NAME
                """.format(config.schema))
                
                if not tables.empty:
                    st.markdown("### Available Tables")
                    st.dataframe(tables, use_container_width=True)
                else:
                    st.info("No tables found in the schema")
                    
            except Exception as e:
                st.error(f"Schema check failed: {str(e)}")

if __name__ == "__main__":
    test_snowflake_connection()
