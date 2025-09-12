"""
BigQuery database utilities for connecting to Google Cloud BigQuery and executing queries
"""
import streamlit as st
import pandas as pd
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
import os
import logging
from typing import Optional, Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BigQueryConnection:
    """Handle BigQuery database connections and operations"""
    
    def __init__(self):
        self.client = None
        self.project_id = None
        self.dataset_id = None
        self.table_id = None
    
    def connect(self):
        """Establish connection to BigQuery"""
        try:
            # Get configuration from secrets
            if 'bigquery' not in st.secrets:
                logger.warning("BigQuery configuration not found in secrets")
                return False
            
            config = st.secrets['bigquery']
            self.project_id = config.get('project_id')
            self.dataset_id = config.get('dataset_id')
            self.table_id = config.get('table_id')
            
            if not all([self.project_id, self.dataset_id, self.table_id]):
                st.error("❌ Missing required BigQuery configuration fields.")
                return False
            
            # Initialize BigQuery client
            # Check if we have service account credentials in secrets
            if 'type' in config and config['type'] == 'service_account':
                # Use credentials from secrets.toml directly
                import json
                credentials_info = {
                    'type': config['type'],
                    'project_id': config['project_id'],
                    'private_key_id': config['private_key_id'],
                    'private_key': config['private_key'],
                    'client_email': config['client_email'],
                    'client_id': config['client_id'],
                    'auth_uri': config['auth_uri'],
                    'token_uri': config['token_uri'],
                    'auth_provider_x509_cert_url': config['auth_provider_x509_cert_url'],
                    'client_x509_cert_url': config['client_x509_cert_url'],
                    'universe_domain': config['universe_domain']
                }
                
                from google.oauth2 import service_account
                credentials = service_account.Credentials.from_service_account_info(credentials_info)
                self.client = bigquery.Client(credentials=credentials, project=self.project_id)
            else:
                # Fall back to environment variable or default credentials
                self.client = bigquery.Client(project=self.project_id)
            
            # Test connection by checking if dataset exists
            dataset_ref = self.client.dataset(self.dataset_id)
            try:
                self.client.get_dataset(dataset_ref)
                logger.info(f"Successfully connected to BigQuery project: {self.project_id}")
                return True
            except NotFound:
                st.error(f"❌ Dataset '{self.dataset_id}' not found in project '{self.project_id}'")
                return False
            
        except Exception as e:
            logger.error(f"Failed to connect to BigQuery: {str(e)}")
            st.error(f"❌ Failed to connect to BigQuery: {str(e)}")
            st.info("Please verify your BigQuery credentials and project configuration")
            return False
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def execute_query(_self, query: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """Execute a SQL query and return results as DataFrame with caching"""
        try:
            if not _self.client:
                if not _self.connect():
                    return pd.DataFrame()
            
            # Execute query
            if params:
                job_config = bigquery.QueryJobConfig(
                    query_parameters=[
                        bigquery.ScalarQueryParameter(key, "STRING", value) 
                        for key, value in params.items()
                    ]
                )
                query_job = _self.client.query(query, job_config=job_config)
            else:
                query_job = _self.client.query(query)
            
            # Convert to DataFrame
            df = query_job.to_dataframe()
            logger.info(f"Query executed successfully, returned {len(df)} rows")
            return df
            
        except Exception as e:
            st.error(f"Query execution failed: {str(e)}")
            logger.error(f"Query execution error: {str(e)}")
            return pd.DataFrame()
    
    @st.cache_data(ttl=600)  # Cache for 10 minutes
    def get_survey_data(_self, survey_id: Optional[str] = None) -> pd.DataFrame:
        """Get survey data from BigQuery"""
        if survey_id:
            query = f"""
            SELECT DISTINCT 
                SURVEY_ID,
                SURVEY_CATEGORY,
                SURVEY_TITLE,
                COUNT(*) as total_responses,
                COUNT(DISTINCT PROFILEUUID) as unique_respondents
            FROM `{_self.project_id}.{_self.dataset_id}.{_self.table_id}`
            WHERE SURVEY_ID = @survey_id
            GROUP BY SURVEY_ID, SURVEY_CATEGORY, SURVEY_TITLE
            ORDER BY SURVEY_ID
            """
            return _self.execute_query(query, {'survey_id': survey_id})
        else:
            query = f"""
            SELECT DISTINCT 
                SURVEY_ID,
                SURVEY_CATEGORY,
                SURVEY_TITLE,
                COUNT(*) as total_responses,
                COUNT(DISTINCT PROFILEUUID) as unique_respondents
            FROM `{_self.project_id}.{_self.dataset_id}.{_self.table_id}`
            WHERE SURVEY_ID IS NOT NULL
            GROUP BY SURVEY_ID, SURVEY_CATEGORY, SURVEY_TITLE
            ORDER BY SURVEY_ID
            """
            return _self.execute_query(query)
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_survey_responses(_self, survey_id: str) -> pd.DataFrame:
        """Get responses for a specific survey"""
        query = f"""
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
            `salary per month`,
            SEM_SEGMENT,
            SEM_SCORE,
            `Side Hustles`
        FROM `{_self.project_id}.{_self.dataset_id}.{_self.table_id}`
        WHERE SURVEY_ID = @survey_id
        ORDER BY CREATED_DATE DESC
        """
        return _self.execute_query(query, {'survey_id': survey_id})
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_survey_analytics(_self, survey_id: str) -> pd.DataFrame:
        """Get analytics data for a survey"""
        query = f"""
        SELECT 
            COUNT(*) as total_responses,
            COUNT(DISTINCT PROFILEUUID) as unique_respondents,
            COUNT(CASE WHEN SURVEY_COMPLETED = TRUE THEN 1 END) as completed_surveys,
            COUNT(CASE WHEN SURVEY_COMPLETED = FALSE THEN 1 END) as incomplete_surveys,
            AVG(SEM_SCORE) as avg_sem_score,
            MIN(SEM_SCORE) as min_sem_score,
            MAX(SEM_SCORE) as max_sem_score
        FROM `{_self.project_id}.{_self.dataset_id}.{_self.table_id}`
        WHERE SURVEY_ID = @survey_id
        """
        return _self.execute_query(query, {'survey_id': survey_id})
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_rating_distribution(_self, survey_id: str) -> pd.DataFrame:
        """Get SEM score distribution for a survey"""
        query = f"""
        SELECT 
            SEM_SCORE as score,
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
        FROM `{_self.project_id}.{_self.dataset_id}.{_self.table_id}`
        WHERE SURVEY_ID = @survey_id AND SEM_SCORE IS NOT NULL
        GROUP BY SEM_SCORE
        ORDER BY SEM_SCORE
        """
        return _self.execute_query(query, {'survey_id': survey_id})
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_time_series_data(_self, survey_id: str, days: int = 30) -> pd.DataFrame:
        """Get time series data for survey responses"""
        query = f"""
        SELECT 
            DATE(CREATED_DATE) as date,
            COUNT(*) as daily_responses,
            AVG(SEM_SCORE) as daily_avg_sem_score,
            COUNT(DISTINCT PROFILEUUID) as daily_unique_respondents
        FROM `{_self.project_id}.{_self.dataset_id}.{_self.table_id}`
        WHERE SURVEY_ID = @survey_id
        AND CREATED_DATE >= DATE_SUB(CURRENT_DATE(), INTERVAL @days DAY)
        GROUP BY DATE(CREATED_DATE)
        ORDER BY date
        """
        return _self.execute_query(query, {'survey_id': survey_id, 'days': days})
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_monthly_travel_costs(_self, survey_id: str) -> pd.DataFrame:
        """Get monthly travel cost data for analysis"""
        query = f"""
        SELECT 
            DATE_TRUNC(CREATED_DATE, MONTH) as month,
            COUNT(*) as monthly_responses,
            COUNT(DISTINCT PROFILEUUID) as unique_respondents
        FROM `{_self.project_id}.{_self.dataset_id}.{_self.table_id}`
        WHERE SURVEY_ID = @survey_id
        AND SURVEY_QUESTION = 'How much did you pay for this trip?'
        AND RESPONSE_X IS NOT NULL
        GROUP BY DATE_TRUNC(CREATED_DATE, MONTH)
        ORDER BY month
        """
        return _self.execute_query(query, {'survey_id': survey_id})
    
    def close(self):
        """Close BigQuery client connection"""
        if self.client:
            self.client.close()
            logger.info("BigQuery client connection closed")

# Global database instance
@st.cache_resource
def get_database():
    """Get cached BigQuery database connection"""
    db = BigQueryConnection()
    if db.connect():
        return db
    return None

# Utility functions for common operations
def get_sample_data():
    """Return sample data when BigQuery is not available"""
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
