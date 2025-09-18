"""
Client for connecting to your existing GCP backend
"""
import streamlit as st
import requests
import pandas as pd
import json
from typing import Optional, Dict, Any

class BackendClient:
    """Client for your existing GCP backend"""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        # Add authentication headers if API key provided
        if self.api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            })
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_surveys_index(_self) -> pd.DataFrame:
        """Get lightweight survey index (1.3KB) from your backend"""
        try:
            response = _self.session.get(f"{_self.base_url}/api/surveys")
            response.raise_for_status()
            
            # Try to parse JSON - handle multiple JSON objects
            try:
                data = response.json()
                if isinstance(data, list):
                    return pd.DataFrame(data)
                elif isinstance(data, dict) and 'data' in data:
                    return pd.DataFrame(data['data'])
                else:
                    return pd.DataFrame()
            except json.JSONDecodeError as json_err:
                # Handle multiple JSON objects like in get_responses
                response_text = response.text
                if '} {' in response_text:
                    json_objects = response_text.split('} {')
                    if len(json_objects) > 1:
                        json_objects[0] = json_objects[0] + '}'
                        json_objects[-1] = '{' + json_objects[-1]
                        
                        parsed_objects = []
                        for obj in json_objects:
                            try:
                                parsed_obj = json.loads(obj)
                                parsed_objects.append(parsed_obj)
                            except:
                                continue
                        
                        if parsed_objects:
                            return pd.DataFrame(parsed_objects)
                
                return pd.DataFrame()
                
        except Exception as e:
            st.error(f"Error fetching survey summary: {str(e)}")
            return pd.DataFrame()
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_responses(_self, limit: int = 100) -> pd.DataFrame:
        """Get cached responses with compression from your backend"""
        try:
            response = _self.session.get(f"{_self.base_url}/api/responses?limit={limit}")
            response.raise_for_status()
            
            # Get response text
            response_text = response.text
            
            # Try to parse JSON - handle multiple JSON objects
            try:
                # First try normal JSON parsing
                data = response.json()
                if isinstance(data, list):
                    return pd.DataFrame(data)
                elif isinstance(data, dict) and 'data' in data:
                    return pd.DataFrame(data['data'])
                else:
                    return pd.DataFrame()
            except json.JSONDecodeError as json_err:
                # If that fails, try to parse multiple JSON objects
                try:
                    # Try different approaches to parse concatenated JSON
                    
                    # Method 1: Split by '} {' pattern
                    if '} {' in response_text:
                        json_objects = response_text.split('} {')
                        
                        if len(json_objects) > 1:
                            # Fix the first and last objects
                            json_objects[0] = json_objects[0] + '}'
                            json_objects[-1] = '{' + json_objects[-1]
                            
                            # Parse each JSON object
                            parsed_objects = []
                            for i, obj in enumerate(json_objects):
                                try:
                                    parsed_obj = json.loads(obj)
                                    parsed_objects.append(parsed_obj)
                                except json.JSONDecodeError:
                                    continue
                            
                            if parsed_objects:
                                return pd.DataFrame(parsed_objects)
                    
                    # Method 2: Try to parse line by line (if each JSON is on a separate line)
                    lines = response_text.strip().split('\n')
                    parsed_objects = []
                    
                    for i, line in enumerate(lines):
                        line = line.strip()
                        if line:
                            try:
                                parsed_obj = json.loads(line)
                                parsed_objects.append(parsed_obj)
                            except json.JSONDecodeError:
                                # Try to find JSON objects within the line
                                # Look for complete JSON objects
                                start = 0
                                while start < len(line):
                                    try:
                                        # Find the next complete JSON object
                                        brace_count = 0
                                        end = start
                                        in_string = False
                                        escape_next = False
                                        
                                        for j, char in enumerate(line[start:], start):
                                            if escape_next:
                                                escape_next = False
                                                continue
                                                
                                            if char == '\\':
                                                escape_next = True
                                                continue
                                                
                                            if char == '"' and not escape_next:
                                                in_string = not in_string
                                                continue
                                                
                                            if not in_string:
                                                if char == '{':
                                                    brace_count += 1
                                                elif char == '}':
                                                    brace_count -= 1
                                                    if brace_count == 0:
                                                        end = j + 1
                                                        break
                                        
                                        if brace_count == 0 and end > start:
                                            json_str = line[start:end]
                                            parsed_obj = json.loads(json_str)
                                            parsed_objects.append(parsed_obj)
                                            start = end
                                        else:
                                            break
                                            
                                    except (json.JSONDecodeError, IndexError):
                                        break
                    
                    if parsed_objects:
                        return pd.DataFrame(parsed_objects)
                    
                    # Method 3: Try to extract JSON objects using regex-like approach
                    import re
                    
                    # Find all JSON objects in the text
                    json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
                    matches = re.findall(json_pattern, response_text)
                    
                    parsed_objects = []
                    for match in matches:
                        try:
                            parsed_obj = json.loads(match)
                            parsed_objects.append(parsed_obj)
                        except json.JSONDecodeError:
                            continue
                    
                    if parsed_objects:
                        return pd.DataFrame(parsed_objects)
                    
                    return pd.DataFrame()
                        
                except Exception as parse_err:
                    st.error(f"Failed to parse multiple JSON objects: {str(parse_err)}")
                    return pd.DataFrame()
                
        except Exception as e:
            st.error(f"Error fetching responses: {str(e)}")
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
            
            # Try to parse JSON - handle multiple JSON objects
            try:
                data = response.json()
                if isinstance(data, list):
                    return pd.DataFrame(data)
                elif isinstance(data, dict) and 'data' in data:
                    return pd.DataFrame(data['data'])
                else:
                    return pd.DataFrame()
            except json.JSONDecodeError as json_err:
                # Handle multiple JSON objects like in get_responses
                response_text = response.text
                if '} {' in response_text:
                    json_objects = response_text.split('} {')
                    if len(json_objects) > 1:
                        json_objects[0] = json_objects[0] + '}'
                        json_objects[-1] = '{' + json_objects[-1]
                        
                        parsed_objects = []
                        for json_str in json_objects:
                            try:
                                parsed_objects.append(json.loads(json_str))
                            except json.JSONDecodeError:
                                continue
                        
                        if parsed_objects:
                            return pd.DataFrame(parsed_objects)
                
                # If all else fails, try to parse as CSV
                try:
                    from io import StringIO
                    return pd.read_csv(StringIO(response_text))
                except:
                    pass
                
                return pd.DataFrame()
                
        except requests.exceptions.RequestException as e:
            return pd.DataFrame()
        except Exception as e:
            return pd.DataFrame()
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_survey_group(_self, group_id: str, full: bool = True) -> pd.DataFrame:
        """Get survey group data (combines all surveys in a group) from your backend"""
        try:
            response = _self.session.get(f"{_self.base_url}/api/survey-group/{group_id}?full={str(full).lower()}")
            response.raise_for_status()
            
            # Try to parse JSON - handle multiple JSON objects
            try:
                data = response.json()
                if isinstance(data, list):
                    return pd.DataFrame(data)
                elif isinstance(data, dict) and 'data' in data:
                    return pd.DataFrame(data['data'])
                else:
                    return pd.DataFrame()
            except json.JSONDecodeError as json_err:
                # Handle multiple JSON objects like in get_responses
                response_text = response.text
                if '} {' in response_text:
                    json_objects = response_text.split('} {')
                    if len(json_objects) > 1:
                        json_objects[0] = json_objects[0] + '}'
                        json_objects[-1] = '{' + json_objects[-1]
                        
                        parsed_objects = []
                        for json_str in json_objects:
                            try:
                                parsed_objects.append(json.loads(json_str))
                            except json.JSONDecodeError:
                                continue
                        
                        if parsed_objects:
                            return pd.DataFrame(parsed_objects)
                
                # If all else fails, try to parse as CSV
                try:
                    from io import StringIO
                    return pd.read_csv(StringIO(response_text))
                except:
                    pass
                
                return pd.DataFrame()
                
        except requests.exceptions.RequestException as e:
            return pd.DataFrame()
        except Exception as e:
            return pd.DataFrame()
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_health_surveys(_self, limit: int = 100) -> pd.DataFrame:
        """Get health surveys data using the individual survey endpoint"""
        try:
            # Try to get health survey data using the new individual survey endpoint
            response = _self.session.get(f"{_self.base_url}/api/survey/SB055_Profile_Survey1?limit={limit}")
            response.raise_for_status()
            
            # Try to parse JSON - handle multiple JSON objects
            try:
                data = response.json()
                if isinstance(data, list):
                    return pd.DataFrame(data)
                elif isinstance(data, dict) and 'data' in data:
                    return pd.DataFrame(data['data'])
                else:
                    return pd.DataFrame()
            except json.JSONDecodeError as json_err:
                # Handle multiple JSON objects like in get_responses
                response_text = response.text
                if '} {' in response_text:
                    json_objects = response_text.split('} {')
                    if len(json_objects) > 1:
                        json_objects[0] = json_objects[0] + '}'
                        json_objects[-1] = '{' + json_objects[-1]
                        
                        parsed_objects = []
                        for json_str in json_objects:
                            try:
                                parsed_objects.append(json.loads(json_str))
                            except json.JSONDecodeError:
                                continue
                        
                        if parsed_objects:
                            return pd.DataFrame(parsed_objects)
                
                # If all else fails, try to parse as CSV
                try:
                    from io import StringIO
                    return pd.read_csv(StringIO(response_text))
                except:
                    pass
                
                return pd.DataFrame()
                
        except requests.exceptions.RequestException as e:
            return pd.DataFrame()
        except Exception as e:
            return pd.DataFrame()

    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_brands_data(_self) -> pd.DataFrame:
        """Get processed survey data brands from your backend (.ndjson format)"""
        try:
            # Try different possible endpoint variations
            endpoints_to_try = [
                f"{_self.base_url}/api/brands-data",
                f"{_self.base_url}/api/processed-survey-data-brands",
                f"{_self.base_url}/api/brands",
                f"{_self.base_url}/api/processed_survey_data_brands",
                f"{_self.base_url}/processed-survey-data-brands",
                f"{_self.base_url}/brands"
            ]
            
            response = None
            for endpoint in endpoints_to_try:
                try:
                    response = _self.session.get(endpoint)
                    if response.status_code == 200:
                        break
                except:
                    continue
            
            if response is None or response.status_code != 200:
                raise Exception(f"No valid endpoint found. Tried: {endpoints_to_try}")
            
            response.raise_for_status()
            
            # Handle .ndjson format (JSON Lines)
            try:
                # Split by lines and parse each JSON object
                lines = response.text.strip().split('\n')
                data = []
                for line in lines:
                    if line.strip():  # Skip empty lines
                        try:
                            parsed_line = json.loads(line)
                            # Handle potential blank first column or empty keys
                            if isinstance(parsed_line, dict):
                                # Remove any keys with empty values or None
                                cleaned_line = {k: v for k, v in parsed_line.items() 
                                             if k is not None and k.strip() != '' and v is not None}
                                if cleaned_line:  # Only add if there's actual data
                                    data.append(cleaned_line)
                        except json.JSONDecodeError:
                            continue
                
                if data:
                    df = pd.DataFrame(data)
                    # Remove any columns that are completely empty or have no name
                    df = df.dropna(axis=1, how='all')  # Remove columns that are all NaN
                    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]  # Remove unnamed columns
                    return df
                else:
                    return pd.DataFrame()
                    
            except Exception as json_err:
                # Fallback: try to parse as regular JSON
                try:
                    data = response.json()
                    if isinstance(data, list):
                        return pd.DataFrame(data)
                    elif isinstance(data, dict) and 'data' in data:
                        return pd.DataFrame(data['data'])
                    else:
                        return pd.DataFrame()
                except:
                    return pd.DataFrame()
                
        except requests.exceptions.RequestException as e:
            return pd.DataFrame()
        except Exception as e:
            return pd.DataFrame()

    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_survey_questions(_self) -> pd.DataFrame:
        """Get survey questions from your backend"""
        try:
            response = _self.session.get(f"{_self.base_url}/api/survey-questions")
            response.raise_for_status()
            
            # Try to parse JSON - handle multiple JSON objects
            try:
                data = response.json()
                if isinstance(data, list):
                    return pd.DataFrame(data)
                elif isinstance(data, dict) and 'data' in data:
                    return pd.DataFrame(data['data'])
                else:
                    return pd.DataFrame()
            except json.JSONDecodeError as json_err:
                # Handle multiple JSON objects like in get_responses
                response_text = response.text
                if '} {' in response_text:
                    json_objects = response_text.split('} {')
                    if len(json_objects) > 1:
                        json_objects[0] = json_objects[0] + '}'
                        json_objects[-1] = '{' + json_objects[-1]
                        
                        parsed_objects = []
                        for obj in json_objects:
                            try:
                                parsed_obj = json.loads(obj)
                                parsed_objects.append(parsed_obj)
                            except:
                                continue
                        
                        if parsed_objects:
                            return pd.DataFrame(parsed_objects)
                
                return pd.DataFrame()
                
        except Exception as e:
            st.error(f"Error fetching survey questions: {str(e)}")
            return pd.DataFrame()
    
    @st.cache_data(ttl=60)  # Cache for 1 minute
    def get_health_check(_self) -> Dict[str, Any]:
        """Get health check with cache monitoring from your backend"""
        try:
            response = _self.session.get(f"{_self.base_url}/api/health", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_demographics(_self) -> Dict[str, Any]:
        """Get pre-computed demographics breakdown for dashboard"""
        try:
            response = _self.session.get(f"{_self.base_url}/api/demographics")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    @st.cache_data(ttl=3600)  # Cache for 1 hour (vocabulary doesn't change often)
    def get_vocabulary(_self) -> Dict[str, Any]:
        """Get vocabulary mappings for form dropdowns and filters"""
        try:
            response = _self.session.get(f"{_self.base_url}/api/vocab")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    @st.cache_data(ttl=3600)  # Cache for 1 hour (schema doesn't change often)
    def get_schema(_self) -> Dict[str, Any]:
        """Get data schema documentation with field descriptions"""
        try:
            response = _self.session.get(f"{_self.base_url}/api/schema")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_filtered_responses(_self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get filtered and paginated survey responses with advanced filtering options"""
        try:
            params = {}
            if filters:
                # Convert filters to query parameters
                for key, value in filters.items():
                    if value is not None and value != '':
                        params[key] = str(value)
            
            response = _self.session.get(f"{_self.base_url}/api/responses", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def export_profile_survey_csv(_self) -> str:
        """Export profile survey data as CSV"""
        try:
            response = _self.session.get(f"{_self.base_url}/api/reporting/profile-survey?format=csv")
            response.raise_for_status()
            return response.text
        except Exception as e:
            return f"Error exporting CSV: {str(e)}"
    
    def test_connection(self) -> bool:
        """Test if backend is accessible"""
        try:
            health_data = self.get_health_check()
            return health_data.get("status") != "error"
        except:
            try:
                # Try root endpoint if /api/health doesn't exist
                response = self.session.get(f"{self.base_url}/", timeout=10)
                return response.status_code == 200
            except:
                return False

# Global backend client
@st.cache_resource
def get_backend_client():
    """Get cached backend client with fallback configuration"""
    try:
        # Try to get configuration from secrets first
        try:
            if hasattr(st, 'secrets') and 'backend' in st.secrets:
                config = st.secrets['backend']
                base_url = config.get('base_url')
                api_key = config.get('api_key')
            else:
                raise Exception("Secrets not available")
        except Exception as secrets_error:
            # Fallback to hardcoded values for deployment
            base_url = "https://ansebmrsurveysv1.appspot.com"
            api_key = ""
        
        if not base_url:
            st.error("❌ Backend base_url not configured")
            return None
        
        client = BackendClient(base_url, api_key)
        
        # Test connection
        if client.test_connection():
            return client
        else:
            return None
            
    except Exception as e:
        st.error(f"❌ Error creating backend client: {str(e)}")
        return None
