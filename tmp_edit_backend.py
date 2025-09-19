from pathlib import Path

path = Path("backend_client.py")
raw_text = path.read_text()
text = raw_text.replace("\r\n", "\n")

if "DEFAULT_BACKEND_BASE_URL" not in text:
    marker = "CACHE_HASH_FUNCS = {\n    \"backend_client.BackendClient\": lambda client: (client.base_url, client.api_key or \"\"),\n    \"requests.sessions.Session\": lambda _: None,\n}\n\n\nclass BackendClient:"
    replacement = "CACHE_HASH_FUNCS = {\n    \"backend_client.BackendClient\": lambda client: (client.base_url, client.api_key or \"\"),\n    \"requests.sessions.Session\": lambda _: None,\n}\n\nDEFAULT_BACKEND_BASE_URL = \"https://ansebmrsurveysv1.oa.r.appspot.com\"\n\n\nclass BackendClient:"
    if marker not in text:
        raise SystemExit("Marker for inserting DEFAULT_BACKEND_BASE_URL not found")
    text = text.replace(marker, replacement)

old_load = '''def _load_backend_config() -> Optional[BackendConfig]:
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
'''

new_load = '''def _load_backend_config() -> Optional[BackendConfig]:
    base_url: Optional[str] = None
    api_key: Optional[str] = None

    if hasattr(st, "secrets") and "backend" in st.secrets:
        secrets_config = st.secrets["backend"]
        base_url = secrets_config.get("base_url") or base_url
        api_key = secrets_config.get("api_key") or api_key

    base_url = os.getenv("SEBENZA_BACKEND_BASE_URL", base_url)
    api_key = os.getenv("SEBENZA_BACKEND_API_KEY", api_key)

    base_url = (base_url or DEFAULT_BACKEND_BASE_URL or "").strip()
    api_key = (api_key or "").strip() or None

    if not base_url:
        return None
    return BackendConfig(base_url=base_url, api_key=api_key)


@st.cache_resource(show_spinner=False)
def _get_cached_backend_client(base_url: str, api_key: Optional[str]) -> BackendClient:
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
        return _get_cached_backend_client(config.base_url, config.api_key)
    except Exception as exc:  # noqa: BLE001
        st.error(f"Unable to initialise backend client: {exc}")
        return None
'''

if old_load not in text:
    raise SystemExit("Expected backend config block not found")

text = text.replace(old_load, new_load)
path.write_text(text.replace("\n", "\r\n"))
