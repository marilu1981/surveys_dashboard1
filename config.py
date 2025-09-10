"""
Configuration settings for the Surveys Dashboard
"""
import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SnowflakeConfig:
    """Snowflake connection configuration"""
    
    def __init__(self):
        # Try to get from Streamlit secrets first, then fall back to environment variables
        try:
            secrets = st.secrets["snowflake"]
            self.account = secrets["account"]
            self.user = secrets["user"]
            self.password = secrets["password"]
            self.warehouse = secrets["warehouse"]
            self.database = secrets["database"]
            self.schema = secrets["schema"]
            self.role = secrets["role"]
        except (KeyError, AttributeError):
            # Fall back to environment variables
            self.account = os.getenv('SNOWFLAKE_ACCOUNT')
            self.user = os.getenv('SNOWFLAKE_USER')
            self.password = os.getenv('SNOWFLAKE_PASSWORD')
            self.warehouse = os.getenv('SNOWFLAKE_WAREHOUSE')
            self.database = os.getenv('SNOWFLAKE_DATABASE')
            self.schema = os.getenv('SNOWFLAKE_SCHEMA')
            self.role = os.getenv('SNOWFLAKE_ROLE')
        
        self.private_key_path = os.getenv('SNOWFLAKE_PRIVATE_KEY_PATH')
        self.private_key_passphrase = os.getenv('SNOWFLAKE_PRIVATE_KEY_PASSPHRASE')
    
    def get_connection_string(self):
        """Get SQLAlchemy connection string for Snowflake"""
        if not all([self.account, self.user, self.warehouse, self.database]):
            raise ValueError("Missing required Snowflake configuration")
        
        # Use password authentication by default
        if self.password:
            # URL encode the password to handle special characters
            from urllib.parse import quote_plus
            encoded_password = quote_plus(self.password)
            return f"snowflake://{self.user}:{encoded_password}@{self.account}/{self.database}/{self.schema}?warehouse={self.warehouse}&role={self.role}"
        else:
            raise ValueError("Password or private key authentication required")
    
    def is_configured(self):
        """Check if Snowflake is properly configured"""
        return all([
            self.account,
            self.user,
            self.warehouse,
            self.database
        ]) and (self.password or self.private_key_path)

# Global configuration instance
config = SnowflakeConfig()
