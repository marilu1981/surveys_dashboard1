"""Robust Streamlit-friendly client for the Sebenza backend."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

import pandas as pd
import requests
import streamlit as st

DEFAULT_TIMEOUT = 20
CACHE_HASH_FUNCS = {
    "backend_client.BackendClient": lambda client: (client.base_url, client.api_key or ""),
    "requests.sessions.Session": lambda _: None,
}


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

    @st.cache_data(ttl=300, show_spinner=False, hash_funcs=CACHE_HASH_FUNCS)
    def get_surveys_index(self) -> pd.DataFrame:
        response = self._request("GET", "/api/surveys")
        payload = self._safe_json(response)
        df = self._coerce_dataframe(payload)
        return df

    @st.cache_data(ttl=300, show_spinner=False, hash_funcs=CACHE_HASH_FUNCS)
    def get_responses(self, *, survey: str, limit: int = 1000, **filters: Any) -> pd.DataFrame:
        if not survey:
            raise ValueError("survey parameter is required for get_responses")
        params: Dict[str, Any] = {"survey": survey, "limit": limit}
        params.update({k: v for k, v in filters.items() if v not in (None, "")})

        response = self._request("GET", "/api/responses", params=params)
        payload = self._safe_json(response)
        df = self._coerce_dataframe(payload)
        return df

    @st.cache_data(ttl=300, show_spinner=False, hash_funcs=CACHE_HASH_FUNCS)
    def get_individual_survey(self, survey_id: str, *, limit: int = 100, full: bool = False) -> pd.DataFrame:
        path = f"/api/survey/{survey_id}"
        params: Dict[str, Any]
        if full:
            params = {"full": "true"}
        else:
            params = {"limit": limit}
        response = self._request("GET", path, params=params)
        payload = self._safe_json(response)
        return self._coerce_dataframe(payload)

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
    def get_filtered_responses(self, filters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        params = {k: v for k, v in (filters or {}).items() if v not in (None, "")}
        response = self._request("GET", "/api/responses", params=params)
        payload = self._safe_json(response)
        return self._coerce_dataframe(payload)

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
    base_url = None
    api_key = None

    if hasattr(st, "secrets") and "backend" in st.secrets:
        secrets_config = st.secrets["backend"]
        base_url = secrets_config.get("base_url")
        api_key = secrets_config.get("api_key")

    base_url = os.getenv("SEBENZA_BACKEND_BASE_URL", base_url)
    api_key = os.getenv("SEBENZA_BACKEND_API_KEY", api_key)

    if not base_url:
        return None
    return BackendConfig(base_url=base_url, api_key=api_key)


@st.cache_resource(show_spinner=False)
def get_backend_client() -> Optional[BackendClient]:
    config = _load_backend_config()
    if not config:
        st.error("Backend configuration is missing. Set SEBENZA_BACKEND_BASE_URL or update secrets.")
        return None
    try:
        client = BackendClient(config.base_url, config.api_key)
        if not client.test_connection():
            st.warning("Backend reachable but health check is not OK.")
        return client
    except Exception as exc:  # noqa: BLE001
        st.error(f"Unable to initialise backend client: {exc}")
        return None