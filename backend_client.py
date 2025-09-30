"""Robust Streamlit-friendly client for the Sebenza backend."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional
from io import BytesIO

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import requests
import streamlit as st

DEFAULT_TIMEOUT = 20
CACHE_HASH_FUNCS = {
    "backend_client.BackendClient": lambda client: (client.base_url, client.api_key or ""),
    "requests.sessions.Session": lambda _: None,
}

DEFAULT_BACKEND_BASE_URL = "https://ansebmrsurveysv1.oa.r.appspot.com"

class BackendClient:
    """Thin HTTP client with Streamlit-aware helpers."""

    def __init__(self, base_url: str, api_key: Optional[str] = None, timeout: int = DEFAULT_TIMEOUT) -> None:
        if not base_url:
            raise ValueError("base_url is required")
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()

        headers = {"Accept": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        self.session.headers.update(headers)

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
    ) -> requests.Response:
        url = f"{self.base_url}{path}" if path.startswith("/") else f"{self.base_url}/{path}"
        try:
            response = self.session.request(
                method,
                url,
                params=params,
                json=json_body,
                timeout=timeout or self.timeout,
            )
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as exc:
            status = exc.response.status_code if exc.response else "unknown"
            detail = exc.response.text[:400] if exc.response else str(exc)
            st.error(f"HTTP {status} calling {url}: {detail}")
            raise
        except requests.exceptions.RequestException as exc:
            st.error(f"Network error calling {url}: {exc}")
            raise

    @staticmethod
    def _coerce_dataframe(payload: Any) -> pd.DataFrame:
        if isinstance(payload, pd.DataFrame):
            return payload
        if isinstance(payload, list):
            return pd.DataFrame(payload)
        if isinstance(payload, dict):
            data = payload.get("data")
            if isinstance(data, list):
                return pd.DataFrame(data)
        return pd.DataFrame()

    @staticmethod
    def _safe_json(response: requests.Response) -> Any:
        try:
            return response.json()
        except json.JSONDecodeError:
            text = response.text.strip()
            if not text:
                return {}
            fragments = []
            buffer = ""
            depth = 0
            for char in text:
                buffer += char
                if char == "{":
                    depth += 1
                elif char == "}":
                    depth -= 1
                    if depth == 0:
                        fragments.append(buffer)
                        buffer = ""
            rows = []
            for fragment in fragments:
                try:
                    rows.append(json.loads(fragment))
                except json.JSONDecodeError:
                    continue
            return rows

    @staticmethod
    def _parse_parquet_response(response: requests.Response) -> pd.DataFrame:
        """Parse parquet binary response into a pandas DataFrame."""
        try:
            # Check if response content looks like JSON (error response)
            content = response.content
            if content.startswith(b'{') or content.startswith(b'['):
                # This is likely a JSON error response, not parquet
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', 'Unknown server error')
                    st.warning(f"Server returned JSON instead of Parquet: {error_msg}")
                except:
                    st.warning("Server returned non-parquet data. Falling back to JSON format.")
                return pd.DataFrame()
            
            parquet_data = BytesIO(content)
            df = pd.read_parquet(parquet_data, engine='pyarrow')
            return df
        except Exception as exc:
            st.warning(f"Parquet parsing failed: {exc}. Falling back to JSON format.")
            return pd.DataFrame()

    @st.cache_data(ttl=300, show_spinner=False, hash_funcs=CACHE_HASH_FUNCS)
    def get_surveys_index(self) -> pd.DataFrame:
        response = self._request("GET", "/api/surveys")
        payload = self._safe_json(response)
        df = self._coerce_dataframe(payload)
        return df

    @st.cache_data(ttl=300, show_spinner=False, hash_funcs=CACHE_HASH_FUNCS)
    def get_responses(self, *, survey: str, limit: int = 1000, format: str = "json", **filters: Any) -> pd.DataFrame:
        if not survey:
            raise ValueError("survey parameter is required for get_responses")
        params: Dict[str, Any] = {"survey": survey, "limit": limit}
        
        # Add format parameter if parquet is requested
        if format.lower() == "parquet":
            params["format"] = "parquet"
        
        params.update({k: v for k, v in filters.items() if v not in (None, "")})

        # Update Accept header for parquet requests
        headers = {}
        if format.lower() == "parquet":
            headers["Accept"] = "application/octet-stream"
        
        # Store original headers
        original_headers = self.session.headers.copy()
        
        try:
            if headers:
                self.session.headers.update(headers)
            
            response = self._request("GET", "/api/responses", params=params)
            
            # Parse response based on format
            if format.lower() == "parquet":
                df = self._parse_parquet_response(response)
                # If parquet parsing failed, fall back to JSON
                if df.empty:
                    st.info("Falling back to JSON format...")
                    payload = self._safe_json(response)
                    df = self._coerce_dataframe(payload)
            else:
                payload = self._safe_json(response)
                df = self._coerce_dataframe(payload)
            
            return df
        finally:
            # Restore original headers
            self.session.headers = original_headers

    @st.cache_data(ttl=300, show_spinner=False, hash_funcs=CACHE_HASH_FUNCS)
    def get_individual_survey(self, survey_id: str, *, limit: int = 100, full: bool = False, format: str = "json") -> pd.DataFrame:
        path = f"/api/survey/{survey_id}"
        params: Dict[str, Any]
        if full:
            params = {"full": "true"}
        else:
            params = {"limit": limit}
        
        # Add format parameter if parquet is requested
        if format.lower() == "parquet":
            params["format"] = "parquet"
        
        # Update Accept header for parquet requests
        headers = {}
        if format.lower() == "parquet":
            headers["Accept"] = "application/octet-stream"
        
        # Store original headers
        original_headers = self.session.headers.copy()
        
        try:
            if headers:
                self.session.headers.update(headers)
            
            response = self._request("GET", path, params=params)
            
            # Parse response based on format
            if format.lower() == "parquet":
                df = self._parse_parquet_response(response)
                # If parquet parsing failed, fall back to JSON
                if df.empty:
                    st.info("Falling back to JSON format...")
                    payload = self._safe_json(response)
                    df = self._coerce_dataframe(payload)
                return df
            else:
                payload = self._safe_json(response)
                return self._coerce_dataframe(payload)
        finally:
            # Restore original headers
            self.session.headers = original_headers

    @st.cache_data(ttl=300, show_spinner=False, hash_funcs=CACHE_HASH_FUNCS)
    def get_survey_group(self, group_id: str, *, full: bool = True) -> pd.DataFrame:
        params = {"full": str(full).lower()}
        response = self._request("GET", f"/api/survey-group/{group_id}", params=params)
        payload = self._safe_json(response)
        return self._coerce_dataframe(payload)

    @st.cache_data(ttl=300, show_spinner=False, hash_funcs=CACHE_HASH_FUNCS)
    def get_survey_questions(self) -> pd.DataFrame:
        response = self._request("GET", "/api/survey-questions")
        payload = self._safe_json(response)
        return self._coerce_dataframe(payload)

    @st.cache_data(ttl=60, show_spinner=False, hash_funcs=CACHE_HASH_FUNCS)
    def get_health_check(self) -> Dict[str, Any]:
        response = self._request("GET", "/api/health", timeout=10)
        payload = self._safe_json(response)
        return payload if isinstance(payload, dict) else {"status": "unknown"}

    @st.cache_data(ttl=300, show_spinner=False, hash_funcs=CACHE_HASH_FUNCS)
    def get_demographics(self) -> Dict[str, Any]:
        response = self._request("GET", "/api/demographics")
        payload = self._safe_json(response)
        return payload if isinstance(payload, dict) else {}

    @st.cache_data(ttl=3600, show_spinner=False, hash_funcs=CACHE_HASH_FUNCS)
    def get_vocabulary(self) -> Dict[str, Any]:
        response = self._request("GET", "/api/vocab")
        payload = self._safe_json(response)
        return payload if isinstance(payload, dict) else {}

    @st.cache_data(ttl=3600, show_spinner=False, hash_funcs=CACHE_HASH_FUNCS)
    def get_schema(self) -> Dict[str, Any]:
        response = self._request("GET", "/api/schema")
        payload = self._safe_json(response)
        return payload if isinstance(payload, dict) else {}

    @st.cache_data(ttl=300, show_spinner=False, hash_funcs=CACHE_HASH_FUNCS)
    def get_filtered_responses(self, filters: Optional[Dict[str, Any]] = None, format: str = "json") -> pd.DataFrame:
        params = {k: v for k, v in (filters or {}).items() if v not in (None, "")}
        
        # Add format parameter if parquet is requested
        if format.lower() == "parquet":
            params["format"] = "parquet"
        
        # Update Accept header for parquet requests
        headers = {}
        if format.lower() == "parquet":
            headers["Accept"] = "application/octet-stream"
        
        # Store original headers
        original_headers = self.session.headers.copy()
        
        try:
            if headers:
                self.session.headers.update(headers)
            
            response = self._request("GET", "/api/responses", params=params)
            
            # Parse response based on format
            if format.lower() == "parquet":
                df = self._parse_parquet_response(response)
                # If parquet parsing failed, fall back to JSON
                if df.empty:
                    st.info("Falling back to JSON format...")
                    payload = self._safe_json(response)
                    df = self._coerce_dataframe(payload)
                return df
            else:
                payload = self._safe_json(response)
                return self._coerce_dataframe(payload)
        finally:
            # Restore original headers
            self.session.headers = original_headers

    @st.cache_data(ttl=300, show_spinner=False, hash_funcs=CACHE_HASH_FUNCS)
    def get_survey_summary(self) -> Dict[str, Any]:
        response = self._request("GET", "/api/survey-summary")
        payload = self._safe_json(response)
        return payload if isinstance(payload, dict) else {}

    @st.cache_data(ttl=300, show_spinner=False, hash_funcs=CACHE_HASH_FUNCS)
    def get_legacy_survey_data(self, limit: int = 1000, **filters: Any) -> pd.DataFrame:
        params = {"limit": limit}
        params.update({k: v for k, v in filters.items() if v not in (None, "")})
        response = self._request("GET", "/api/legacy-survey-data", params=params)
        payload = self._safe_json(response)
        return self._coerce_dataframe(payload)

    def export_profile_survey_csv(self) -> str:
        response = self._request("GET", "/api/reporting/profile-survey", params={"format": "csv"})
        response.encoding = response.encoding or "utf-8"
        return response.text

    @st.cache_data(ttl=300, show_spinner=False, hash_funcs=CACHE_HASH_FUNCS)
    def get_responses_parquet(self) -> pd.DataFrame:
        """Get responses data from the staging Parquet file"""
        # Try multiple possible URLs for the Parquet file
        possible_urls = [
            "https://staging.ansebmrsurveysv1.appspot.com/processed/responses.parquet",
            f"{self.base_url}/processed/responses.parquet",  # Try main server
            f"{self.base_url}/api/responses.parquet",  # Try as API endpoint
        ]
        
        for i, url in enumerate(possible_urls):
            try:
                # Only show first attempt to reduce verbosity
                if i == 0:
                    st.info("🔍 Checking for Parquet file availability...")
                
                # Make direct request with SSL verification disabled for staging
                headers = {"Accept": "application/octet-stream"}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                
                # Disable SSL verification for staging environments
                verify_ssl = not ("staging" in url.lower())
                
                response = requests.get(
                    url, 
                    headers=headers, 
                    timeout=self.timeout,
                    verify=verify_ssl
                )
                response.raise_for_status()
                
                # Check if response is actually Parquet data
                content = response.content
                if len(content) < 1000:  # Too small to be a real Parquet file
                    st.info(f"Response too small ({len(content)} bytes), likely not a Parquet file")
                    continue
                
                # Check if response is HTML/JSON instead of Parquet
                content_start = content[:100].decode('utf-8', errors='ignore').strip().lower()
                if content_start.startswith(('<html', '<!doctype', '{', '[')):
                    st.info(f"Server returned HTML/JSON instead of Parquet file")
                    continue
                
                # Check for Parquet magic bytes (PAR1)
                if not content.startswith(b'PAR1') and b'PAR1' not in content[-8:]:
                    st.info(f"No Parquet magic bytes found, not a valid Parquet file")
                    continue
                    
                # Parse the Parquet file
                parquet_data = BytesIO(content)
                df = pd.read_parquet(parquet_data, engine='pyarrow')
                
                if not df.empty:
                    st.success(f"✅ Successfully loaded {len(df):,} records from Parquet file")
                    return df
                    
            except Exception as exc:
                # Only log detailed errors for debugging, not for user display
                continue
        
        st.info("📄 Parquet file not available, using API endpoint instead.")
        return pd.DataFrame()

    def test_connection(self) -> bool:
        try:
            health = self.get_health_check()
            return str(health.get("status", "")).lower() == "ok"
        except Exception:
            return False


@dataclass(frozen=True)
class BackendConfig:
    base_url: str
    api_key: Optional[str]


def _load_backend_config() -> Optional[BackendConfig]:
    base_url: Optional[str] = None
    api_key: Optional[str] = None

    if hasattr(st, "secrets"):
        backend_section = None
        if "backend" in st.secrets:
            backend_section = st.secrets["backend"]
        elif "connections" in st.secrets and isinstance(st.secrets["connections"], dict):
            backend_section = st.secrets["connections"].get("sebenza_backend")

        if isinstance(backend_section, dict):
            base_url = backend_section.get("base_url") or base_url
            api_key = backend_section.get("api_key") or api_key

    env_base = os.getenv("SEBENZA_BACKEND_BASE_URL")
    env_key = os.getenv("SEBENZA_BACKEND_API_KEY")
    if env_base:
        base_url = env_base
    if env_key:
        api_key = env_key

    base_url = (base_url or DEFAULT_BACKEND_BASE_URL or "").strip()
    api_key = (api_key or "").strip() or None

    if not base_url:
        return None
    return BackendConfig(base_url=base_url, api_key=api_key)


@st.cache_resource(show_spinner=False)
def _get_backend_client_cached(base_url: str, api_key: Optional[str]) -> BackendClient:
    client = BackendClient(base_url, api_key)
    if not client.test_connection():
        st.warning("Backend reachable but health check is not OK.")
    return client


def get_backend_client() -> Optional[BackendClient]:
    config = _load_backend_config()
    if not config:
        st.error("Backend configuration is missing. Set SEBENZA_BACKEND_BASE_URL or update secrets.")
        return None
    try:
        return _get_backend_client_cached(config.base_url, config.api_key)
    except Exception as exc:  # noqa: BLE001
        st.error(f"Unable to initialise backend client: {exc}")
        return None
