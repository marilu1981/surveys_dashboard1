import streamlit as st
import requests
import pandas as pd
import json
from typing import Dict, Any, Optional

class BackendClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        # Set reasonable timeout
        self.session.timeout = 30

    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_responses(_self, survey: str, limit: int = 1000, **filters) -> pd.DataFrame:
        """Get cached responses with compression from your backend - REQUIRES survey parameter"""
        try:
            # Build query parameters
            params = {'survey': survey, 'limit': limit}
            params.update(filters)
            
            # Use optimized endpoint with specific survey (REQUIRED)
            response = _self.session.get(f"{_self.base_url}/api/responses", params=params)
            
            if response.status_code == 500:
                st.warning(f"⚠️ Backend server error (500) for /api/responses. Survey parameter is required.")
                return pd.DataFrame()
            elif response.status_code == 400:
                st.warning(f"⚠️ Bad request (400) for /api/responses. Check survey parameter: {survey}")
                return pd.DataFrame()
            
            response.raise_for_status()
            
            # Parse the new API response structure
            data = response.json()
            
            # Handle the new API format with data and pagination
            if isinstance(data, dict) and 'data' in data:
                df = pd.DataFrame(data['data'])
                # Store pagination info for potential future use
                if 'pagination' in data:
                    st.session_state[f'pagination_{survey}'] = data['pagination']
                return df
            elif isinstance(data, list):
                # Fallback for direct list format
                return pd.DataFrame(data)
            else:
                st.warning(f"⚠️ Unexpected response format from /api/responses")
                return pd.DataFrame()
                
        except json.JSONDecodeError as json_err:
            st.warning(f"⚠️ Could not parse JSON response: {str(json_err)}")
            return pd.DataFrame()
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching responses: {str(e)}")
            return pd.DataFrame()
        except Exception as e:
            st.error(f"Error parsing responses: {str(e)}")
            return pd.DataFrame()

    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_survey_group(_self, group_id: str, full: bool = True) -> pd.DataFrame:
        """Get survey group data (combines all surveys in a group) from your backend"""
        try:
            response = _self.session.get(f"{_self.base_url}/api/survey-group/{group_id}?full={str(full).lower()}")
            response.raise_for_status()
            
            # Parse the new API response structure
            data = response.json()
            
            # Handle the new API format with data and pagination
            if isinstance(data, dict) and 'data' in data:
                df = pd.DataFrame(data['data'])
                # Store pagination info for potential future use
                if 'pagination' in data:
                    st.session_state[f'pagination_group_{group_id}'] = data['pagination']
                return df
            elif isinstance(data, list):
                # Fallback for direct list format
                return pd.DataFrame(data)
            else:
                st.warning(f"⚠️ Unexpected response format from /api/survey-group/{group_id}")
                return pd.DataFrame()
                
        except requests.exceptions.RequestException as e:
            return pd.DataFrame()
        except Exception as e:
            return pd.DataFrame()

    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_individual_survey(_self, survey_id: str, limit: int = 100, full: bool = False) -> pd.DataFrame:
        """Get individual survey data from your backend"""
        try:
            if full:
                response = _self.session.get(f"{_self.base_url}/api/survey/{survey_id}?full=true")
            else:
                response = _self.session.get(f"{_self.base_url}/api/survey/{survey_id}?limit={limit}")
            response.raise_for_status()
            
            # Parse the new API response structure
            data = response.json()
            
            # Handle the new API format with data and pagination
            if isinstance(data, dict) and 'data' in data:
                df = pd.DataFrame(data['data'])
                # Store pagination info for potential future use
                if 'pagination' in data:
                    st.session_state[f'pagination_survey_{survey_id}'] = data['pagination']
                return df
            elif isinstance(data, list):
                # Fallback for direct list format
                return pd.DataFrame(data)
            else:
                st.warning(f"⚠️ Unexpected response format from /api/survey/{survey_id}")
                return pd.DataFrame()
                
        except Exception as e:
            st.error(f"Error fetching individual survey: {str(e)}")
            return pd.DataFrame()

    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_health_surveys(_self, limit: int = 100) -> pd.DataFrame:
        """Get health survey data from your backend"""
        try:
            # Use the individual survey endpoint for Profile Survey
            return _self.get_individual_survey("SB055_Profile_Survey1", limit=limit)
        except Exception as e:
            st.error(f"Error fetching health surveys: {str(e)}")
            return pd.DataFrame()

    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_surveys_index(_self) -> pd.DataFrame:
        """Get lightweight survey index from your backend"""
        try:
            response = _self.session.get(f"{_self.base_url}/api/surveys")
            response.raise_for_status()
            
            data = response.json()
            if isinstance(data, dict) and 'surveys' in data:
                return pd.DataFrame(data['surveys'])
            elif isinstance(data, list):
                return pd.DataFrame(data)
            else:
                return pd.DataFrame()
                
        except Exception as e:
            st.error(f"Error fetching surveys index: {str(e)}")
            return pd.DataFrame()

    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_health_check(_self) -> dict:
        """Get health check from your backend"""
        try:
            response = _self.session.get(f"{_self.base_url}/api/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Error fetching health check: {str(e)}")
            return {}

    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_demographics(_self) -> dict:
        """Get demographics from your backend"""
        try:
            response = _self.session.get(f"{_self.base_url}/api/demographics")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Error fetching demographics: {str(e)}")
            return {}

    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_vocabulary(_self) -> dict:
        """Get vocabulary from your backend"""
        try:
            response = _self.session.get(f"{_self.base_url}/api/vocab")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Error fetching vocabulary: {str(e)}")
            return {}

    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_schema(_self) -> dict:
        """Get schema from your backend"""
        try:
            response = _self.session.get(f"{_self.base_url}/api/schema")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Error fetching schema: {str(e)}")
            return {}

    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_filtered_responses(_self, filters: Dict[str, Any] = None) -> pd.DataFrame:
        """Get filtered responses from your backend"""
        try:
            if not filters:
                filters = {}
            
            # Ensure survey parameter is present
            if 'survey' not in filters:
                st.warning("⚠️ Survey parameter is required for filtered responses")
                return pd.DataFrame()
            
            response = _self.session.get(f"{_self.base_url}/api/responses", params=filters)
            response.raise_for_status()
            
            data = response.json()
            if isinstance(data, dict) and 'data' in data:
                return pd.DataFrame(data['data'])
            elif isinstance(data, list):
                return pd.DataFrame(data)
            else:
                return pd.DataFrame()
                
        except Exception as e:
            st.error(f"Error fetching filtered responses: {str(e)}")
            return pd.DataFrame()

    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def export_profile_survey_csv(_self) -> str:
        """Export profile survey as CSV from your backend"""
        try:
            response = _self.session.get(f"{_self.base_url}/api/reporting/profile-survey?format=csv")
            response.raise_for_status()
            return response.text
        except Exception as e:
            st.error(f"Error exporting profile survey CSV: {str(e)}")
            return ""

    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_survey_summary(_self) -> dict:
        """Get survey summary from your backend"""
        try:
            response = _self.session.get(f"{_self.base_url}/api/survey-summary")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching survey summary: {str(e)}")
            return {}
        except Exception as e:
            st.error(f"Error parsing survey summary: {str(e)}")
            return {}

    def test_connection(_self) -> bool:
        """Test connection to backend"""
        try:
            health_data = _self.get_health_check()
            return bool(health_data and health_data.get('status') == 'ok')
        except:
            return False

def get_backend_client() -> Optional[BackendClient]:
    """Get backend client with configuration from secrets"""
    try:
        # Try to get base URL from secrets
        base_url = st.secrets.get("backend_url", "https://ansebmrsurveysv1.oa.r.appspot.com")
        
        if not base_url:
            st.warning("⚠️ Backend URL not configured in secrets.toml")
            return None
            
        client = BackendClient(base_url)
        
        # Test connection
        if client.test_connection():
            return client
        else:
            st.warning("⚠️ Backend connection test failed")
            return None
            
    except Exception as e:
        st.error(f"Error creating backend client: {str(e)}")
        return None
