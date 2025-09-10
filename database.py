"""
Database utilities for connecting to Snowflake and executing queries
"""
import streamlit as st
import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from sqlalchemy import create_engine, text
from config import config
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SnowflakeConnection:
    """Handle Snowflake database connections and operations"""
    
    def __init__(self):
        self.connection = None
        self.engine = None
    
    def connect(self):
        """Establish connection to Snowflake"""
        try:
            if not config.is_configured():
                st.error("❌ Snowflake configuration is incomplete. Please check your secrets.toml file.")
                st.info("Required fields: account, user, password, warehouse, database, schema, role")
                return False
            
            # Try native Snowflake connector first (better for special characters)
            try:
                self.connection = snowflake.connector.connect(
                    user=config.user,
                    password=config.password,
                    account=config.account,
                    warehouse=config.warehouse,
                    database=config.database,
                    schema=config.schema,
                    role=config.role
                )
                
                # Test connection
                cursor = self.connection.cursor()
                cursor.execute("SELECT CURRENT_VERSION()")
                version = cursor.fetchone()[0]
                cursor.close()
                
                logger.info("Successfully connected to Snowflake using native connector")
                return True
                
            except Exception as native_error:
                logger.warning(f"Native connector failed: {str(native_error)}")
                logger.info("Trying SQLAlchemy connector...")
                
                # Fall back to SQLAlchemy
                connection_string = config.get_connection_string()
                self.engine = create_engine(connection_string)
                
                # Test connection
                with self.engine.connect() as conn:
                    result = conn.execute(text("SELECT CURRENT_VERSION()"))
                    version = result.fetchone()[0]
                
                logger.info("Successfully connected to Snowflake using SQLAlchemy")
                return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Snowflake: {str(e)}")
            # Only show error in UI if it's a critical error, not connection warnings
            if "Incorrect username or password" in str(e) or "does not exist" in str(e):
                st.error(f"❌ Failed to connect to Snowflake: {str(e)}")
                st.info("Please verify your Snowflake credentials in .streamlit/secrets.toml")
            logger.error(f"Snowflake connection error: {str(e)}")
            return False
    
    def execute_query(self, query, params=None):
        """Execute a SQL query and return results as DataFrame"""
        try:
            # Try native connection first
            if self.connection:
                cursor = self.connection.cursor()
                
                # Handle parameterized queries by replacing placeholders
                if params:
                    # Replace parameter placeholders with actual values
                    formatted_query = query
                    for key, value in params.items():
                        if isinstance(value, str):
                            formatted_query = formatted_query.replace(f":{key}", f"'{value}'")
                        else:
                            formatted_query = formatted_query.replace(f":{key}", str(value))
                    cursor.execute(formatted_query)
                else:
                    cursor.execute(query)
                
                # Get column names - handle potential issues with column names
                if cursor.description:
                    columns = []
                    for desc in cursor.description:
                        col_name = desc[0]
                        # Clean column names to avoid issues
                        if col_name and col_name.strip():
                            columns.append(col_name.strip())
                        else:
                            columns.append(f"COL_{len(columns)}")
                else:
                    columns = []
                
                # Get data
                data = cursor.fetchall()
                cursor.close()
                
                # Create DataFrame with proper column handling
                if data and columns:
                    return pd.DataFrame(data, columns=columns)
                elif data:
                    # If no column names, create generic ones
                    return pd.DataFrame(data, columns=[f"COL_{i}" for i in range(len(data[0]) if data else 0)])
                else:
                    return pd.DataFrame()
            
            # Fall back to SQLAlchemy
            elif self.engine:
                with self.engine.connect() as conn:
                    result = conn.execute(text(query), params or {})
                    df = pd.DataFrame(result.fetchall(), columns=result.keys())
                    return df
            
            # No connection available
            else:
                if not self.connect():
                    return pd.DataFrame()
                return self.execute_query(query, params)
                
        except Exception as e:
            st.error(f"Query execution failed: {str(e)}")
            logger.error(f"Query execution error: {str(e)}")
            return pd.DataFrame()
    
    def get_survey_data(self, survey_id=None):
        """Get survey data from Snowflake"""
        if survey_id:
            query = """
            SELECT DISTINCT 
                SURVEY_ID,
                SURVEY_CATEGORY,
                SURVEY_TITLE,
                COUNT(*) as total_responses,
                COUNT(DISTINCT PROFILEUUID) as unique_respondents
            FROM SURVEYS_DB.RAW.NEW_DASBOARD_DATA1 
            WHERE SURVEY_ID = :survey_id
            GROUP BY SURVEY_ID, SURVEY_CATEGORY, SURVEY_TITLE
            ORDER BY SURVEY_ID
            """
            result = self.execute_query(query, {'survey_id': survey_id})
            # If no results, try to get any data for this survey_id
            if result.empty:
                query_fallback = """
                SELECT 
                    SURVEY_ID,
                    SURVEY_CATEGORY,
                    SURVEY_TITLE,
                    COUNT(*) as total_responses,
                    COUNT(DISTINCT PROFILEUUID) as unique_respondents
                FROM SURVEYS_DB.RAW.SEM_AND_PROFILE_SURVEYS_09092025 
                WHERE SURVEY_ID = :survey_id
                GROUP BY SURVEY_ID, SURVEY_CATEGORY, SURVEY_TITLE
                ORDER BY SURVEY_ID
                """
                result = self.execute_query(query_fallback, {'survey_id': survey_id})
            return result
        else:
            query = """
            SELECT DISTINCT 
                SURVEY_ID,
                SURVEY_CATEGORY,
                SURVEY_TITLE,
                COUNT(*) as total_responses,
                COUNT(DISTINCT PROFILEUUID) as unique_respondents
            FROM SURVEYS_DB.RAW.SEM_AND_PROFILE_SURVEYS_09092025 
            WHERE SURVEY_ID IS NOT NULL
            GROUP BY SURVEY_ID, SURVEY_CATEGORY, SURVEY_TITLE
            ORDER BY SURVEY_ID
            """
            return self.execute_query(query)
    
    def get_survey_responses(self, survey_id):
        """Get responses for a specific survey"""
        query = """
        SELECT 
            PROFILEUUID,
            PROFIE_ID,
            TRACKING_SESSION_UUID,
            SERIAL,
            CREATED_DATE as CREATED_AT,
            SURVEY_ID,
            SURVEY_CATEGORY,
            SURVEY_TITLE,
            SURVEY_QUESTION_ORDER,
            SURVEY_LAST_QUESTION_ORDER,
            SURVEY_COMPLETED,
            SURVEY_QUESTION,
            RESPONSE_X as RESPONSE,
            GENDER,
            AGE_GROUP as AGEGROUP,
            EMPLOYMENT as "Emloyment Status",
            LOCATION,
            "salary per month",
            SEM_SEGMENT,
            SEM_SCORE,
            "Side Hustles"
        FROM SURVEYS_DB.RAW.NEW_DASBOARD_DATA1
        WHERE SURVEY_ID = :survey_id
        ORDER BY CREATED_DATE DESC
        """
        return self.execute_query(query, {'survey_id': survey_id})
    
    def get_survey_analytics(self, survey_id):
        """Get analytics data for a survey"""
        query = """
        SELECT 
            COUNT(*) as total_responses,
            COUNT(DISTINCT PROFILEUUID) as unique_respondents,
            COUNT(CASE WHEN SURVEY_COMPLETED = TRUE THEN 1 END) as completed_surveys,
            COUNT(CASE WHEN SURVEY_COMPLETED = FALSE THEN 1 END) as incomplete_surveys,
            AVG(SEM_SCORE) as avg_sem_score,
            MIN(SEM_SCORE) as min_sem_score,
            MAX(SEM_SCORE) as max_sem_score
        FROM SURVEYS_DB.RAW.NEW_DASBOARD_DATA1 
        WHERE SURVEY_ID = :survey_id
        """
        result = self.execute_query(query, {'survey_id': survey_id})
        
        # If no results, try without the survey_id filter to get overall stats
        if result.empty:
            query_fallback = """
            SELECT 
                COUNT(*) as total_responses,
                COUNT(DISTINCT PROFILEUUID) as unique_respondents,
                COUNT(CASE WHEN SURVEY_COMPLETED = TRUE THEN 1 END) as completed_surveys,
                COUNT(CASE WHEN SURVEY_COMPLETED = FALSE THEN 1 END) as incomplete_surveys,
                AVG(SEM_SCORE) as avg_sem_score,
                MIN(SEM_SCORE) as min_sem_score,
                MAX(SEM_SCORE) as max_sem_score
            FROM SURVEYS_DB.RAW.NEW_DASBOARD_DATA1
            """
            result = self.execute_query(query_fallback)
        
        return result
    
    def get_rating_distribution(self, survey_id):
        """Get SEM score distribution for a survey"""
        query = """
        SELECT 
            SEM_SCORE as score,
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
        FROM SURVEYS_DB.RAW.NEW_DASBOARD_DATA1 
        WHERE SURVEY_ID = :survey_id AND SEM_SCORE IS NOT NULL
        GROUP BY SEM_SCORE
        ORDER BY SEM_SCORE
        """
        return self.execute_query(query, {'survey_id': survey_id})
    
    def get_time_series_data(self, survey_id, days=30):
        """Get time series data for survey responses"""
        query = """
        SELECT 
            DATE(CREATED_DATE) as date,
            COUNT(*) as daily_responses,
            AVG(SEM_SCORE) as daily_avg_sem_score,
            COUNT(DISTINCT PROFILEUUID) as daily_unique_respondents
        FROM SURVEYS_DB.RAW.NEW_DASBOARD_DATA1 
        WHERE SURVEY_ID = :survey_id
        AND CREATED_DATE >= DATEADD(day, -:days, CURRENT_DATE())
        GROUP BY DATE(CREATED_DATE)
        ORDER BY date
        """
        return self.execute_query(query, {'survey_id': survey_id, 'days': days})
    
    def get_monthly_travel_costs(self, survey_id):
        """Get monthly travel cost data for analysis"""
        query = """
        SELECT 
            DATE_TRUNC('month', CREATED_DATE) as month,
            COUNT(*) as monthly_responses,
            AVG(CAST(REGEXP_REPLACE(REGEXP_REPLACE(RESPONSE_X, '[^0-9.]', ''), '^$', '0') AS FLOAT)) as avg_monthly_cost,
            COUNT(DISTINCT PROFILEUUID) as unique_respondents
        FROM SURVEYS_DB.RAW.NEW_DASBOARD_DATA1 
        WHERE SURVEY_ID = :survey_id
        AND SURVEY_QUESTION = 'How much did you pay for this trip?'
        AND RESPONSE_X IS NOT NULL
        AND REGEXP_REPLACE(REGEXP_REPLACE(RESPONSE_X, '[^0-9.]', ''), '^$', '0') != '0'
        GROUP BY DATE_TRUNC('month', CREATED_DATE)
        ORDER BY month
        """
        return self.execute_query(query, {'survey_id': survey_id})
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Snowflake native connection closed")
        if self.engine:
            self.engine.dispose()
            logger.info("Snowflake SQLAlchemy connection closed")

# Global database instance
@st.cache_resource
def get_database():
    """Get cached database connection"""
    db = SnowflakeConnection()
    if db.connect():
        return db
    return None

# Utility functions for common operations
def get_sample_data():
    """Return sample data when Snowflake is not available"""
    return {
        'surveys': pd.DataFrame({
            'survey_id': [1, 2, 3],
            'survey_name': ['Customer Satisfaction', 'Employee Engagement', 'Product Feedback'],
            'survey_type': ['CSAT', 'NPS', 'Product'],
            'created_at': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'status': ['Active', 'Active', 'Active']
        }),
        'responses': pd.DataFrame({
            'response_id': range(1, 101),
            'survey_id': [1] * 40 + [2] * 35 + [3] * 25,
            'user_id': range(1, 101),
            'rating': [4, 5, 3, 4, 5, 2, 4, 5, 3, 4] * 10,
            'submitted_at': pd.date_range('2024-01-01', periods=100, freq='H'),
            'comments': ['Great service!'] * 50 + ['Needs improvement'] * 30 + ['Excellent!'] * 20
        })
    }
