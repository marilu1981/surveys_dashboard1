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
    def get_survey_summary(_self) -> pd.DataFrame:
        """Get survey summary from your backend"""
        try:
            response = _self.session.get(f"{_self.base_url}/api/survey-summary")
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
    def get_responses(_self) -> pd.DataFrame:
        """Get survey responses from your backend"""
        try:
            response = _self.session.get(f"{_self.base_url}/api/responses")
            response.raise_for_status()
            
            # Debug: Show raw response
            st.info(f"Response status: {response.status_code}")
            st.info(f"Response headers: {dict(response.headers)}")
            
            # Try to get text first to debug
            response_text = response.text
            st.info(f"Response text (first 500 chars): {response_text[:500]}")
            
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
                st.warning(f"Standard JSON parsing failed: {str(json_err)}")
                st.info("Attempting to parse multiple JSON objects...")
                
                try:
                    # Try different approaches to parse concatenated JSON
                    st.info(f"Full response length: {len(response_text)} characters")
                    
                    # Method 1: Split by '} {' pattern
                    if '} {' in response_text:
                        st.info("Found '} {' pattern - splitting concatenated JSON objects")
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
                                except json.JSONDecodeError as obj_err:
                                    st.warning(f"Failed to parse object {i}: {str(obj_err)}")
                                    continue
                            
                            if parsed_objects:
                                st.success(f"Successfully parsed {len(parsed_objects)} JSON objects")
                                return pd.DataFrame(parsed_objects)
                    
                    # Method 2: Try to parse line by line (if each JSON is on a separate line)
                    st.info("Trying line-by-line parsing...")
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
                        st.success(f"Successfully parsed {len(parsed_objects)} JSON objects using line parsing")
                        return pd.DataFrame(parsed_objects)
                    
                    # Method 3: Try to extract JSON objects using regex-like approach
                    st.info("Trying regex-like JSON extraction...")
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
                        st.success(f"Successfully parsed {len(parsed_objects)} JSON objects using regex")
                        return pd.DataFrame(parsed_objects)
                    
                    st.error("All parsing methods failed")
                    return pd.DataFrame()
                        
                except Exception as parse_err:
                    st.error(f"Failed to parse multiple JSON objects: {str(parse_err)}")
                    return pd.DataFrame()
                
        except Exception as e:
            st.error(f"Error fetching responses: {str(e)}")
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
    
    def test_connection(self) -> bool:
        """Test if backend is accessible"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            return response.status_code == 200
        except:
            try:
                # Try root endpoint if /health doesn't exist
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
        if 'backend' in st.secrets:
            config = st.secrets['backend']
            base_url = config.get('base_url')
            api_key = config.get('api_key')
            st.info("✅ Using secrets configuration")
        else:
            # Fallback to hardcoded values for deployment
            st.warning("⚠️ Using fallback backend configuration")
            base_url = "https://ansebmrsurveysv1.oa.r.appspot.com"
            api_key = ""
        
        if not base_url:
            st.error("❌ Backend base_url not configured")
            return None
        
        client = BackendClient(base_url, api_key)
        
        # Test connection
        if client.test_connection():
            st.success("✅ Backend connection successful")
            return client
        else:
            st.error("❌ Backend connection failed")
            return None
            
    except Exception as e:
        st.error(f"❌ Error creating backend client: {str(e)}")
        return None
