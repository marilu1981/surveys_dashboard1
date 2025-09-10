"""
Debug script to help identify Snowflake connection issues
"""
import streamlit as st
from config import config
import urllib.parse

def debug_connection():
    """Debug Snowflake connection issues"""
    st.title("🔍 Snowflake Connection Debug")
    
    # Display configuration (masked password)
    st.markdown("### Current Configuration")
    config_info = {
        "Account": config.account,
        "User": config.user,
        "Password": f"{config.password[:3]}***{config.password[-3:]}" if config.password else "Not set",
        "Warehouse": config.warehouse,
        "Database": config.database,
        "Schema": config.schema,
        "Role": config.role
    }
    
    for key, value in config_info.items():
        if value:
            st.success(f"✅ {key}: {value}")
        else:
            st.error(f"❌ {key}: Not configured")
    
    # Test password encoding
    st.markdown("### Password Encoding Test")
    if config.password:
        original_password = config.password
        encoded_password = urllib.parse.quote_plus(original_password)
        
        st.info(f"Original password: `{original_password}`")
        st.info(f"URL encoded: `{encoded_password}`")
        
        # Check for problematic characters
        problematic_chars = ['@', '!', '#', '$', '%', '^', '&', '*', '(', ')', '+', '=', '[', ']', '{', '}', '|', '\\', ':', ';', '"', "'", '<', '>', ',', '.', '?', '/']
        found_chars = [char for char in problematic_chars if char in original_password]
        
        if found_chars:
            st.warning(f"⚠️ Password contains special characters: {found_chars}")
            st.info("These characters may cause connection issues and need URL encoding.")
        else:
            st.success("✅ Password doesn't contain problematic special characters")
    
    # Test connection string generation
    st.markdown("### Connection String Test")
    try:
        connection_string = config.get_connection_string()
        # Mask the password in the displayed string
        masked_string = connection_string.replace(encoded_password, "***MASKED***")
        st.code(masked_string, language="text")
        st.success("✅ Connection string generated successfully")
    except Exception as e:
        st.error(f"❌ Failed to generate connection string: {str(e)}")
    
    # Manual connection test
    st.markdown("### Manual Connection Test")
    if st.button("Test Native Snowflake Connection"):
        try:
            import snowflake.connector
            
            st.info("Attempting native Snowflake connection...")
            conn = snowflake.connector.connect(
                user=config.user,
                password=config.password,
                account=config.account,
                warehouse=config.warehouse,
                database=config.database,
                schema=config.schema,
                role=config.role
            )
            
            cursor = conn.cursor()
            cursor.execute("SELECT CURRENT_VERSION(), CURRENT_USER(), CURRENT_DATABASE()")
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            st.success("🎉 Native connection successful!")
            st.info(f"Version: {result[0]}")
            st.info(f"User: {result[1]}")
            st.info(f"Database: {result[2]}")
            
        except Exception as e:
            st.error(f"❌ Native connection failed: {str(e)}")
            
            # Provide specific troubleshooting
            error_str = str(e).lower()
            if "incorrect username or password" in error_str:
                st.error("🔑 Username or password issue:")
                st.info("• Check if the password contains special characters")
                st.info("• Verify the username is correct")
                st.info("• Ensure the account name is in the correct format")
            elif "failed to connect" in error_str:
                st.error("🌐 Network/connection issue:")
                st.info("• Check your internet connection")
                st.info("• Verify the account name format (should include region if applicable)")
                st.info("• Check if your IP is whitelisted in Snowflake")
            elif "warehouse" in error_str:
                st.error("🏭 Warehouse issue:")
                st.info("• Verify the warehouse name is correct")
                st.info("• Check if the warehouse is running")
                st.info("• Ensure you have access to the warehouse")

if __name__ == "__main__":
    debug_connection()
