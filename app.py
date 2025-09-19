from __future__ import annotations

import importlib
import os
import sys
from dataclasses import dataclass
from typing import Callable, Optional

import pandas as pd
import streamlit as st

from backend_client import get_backend_client
from chart_utils import create_altair_chart
from styles.card_style import apply_card_styles, create_metric_card
from styles.global_styles import inject_global_styles

BASE_DIR = os.path.dirname(__file__)
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)
DASHBOARD_DIR = os.path.join(BASE_DIR, "dashboard_pages")
if DASHBOARD_DIR not in sys.path:
    sys.path.append(DASHBOARD_DIR)

st.set_page_config(
    page_title="Sebenza Surveys Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_global_styles()


@dataclass(frozen=True)
class Page:
    label: str
    page_id: str
    render: Callable[[], None]


def lazy_page(module_path: str, attribute: str) -> Callable[[], None]:
    """Return a renderer that imports the module on demand."""

    def _renderer() -> None:
        try:
            module = importlib.import_module(module_path)
            getattr(module, attribute)()
        except ModuleNotFoundError as exc:
            st.error(f"Page module '{module_path}' is not available.")
            st.exception(exc)
        except Exception as exc:  # noqa: BLE001 - show useful details in UI
            st.error("The page failed to load.")
            st.exception(exc)

    return _renderer


def get_navigation() -> tuple[Page, ...]:
    return (
        Page("Home", "home", show_home_page),
        Page("Demographics", "demographics", lazy_page("dashboard_pages.demographics", "main")),
        Page("Profile Surveys", "profile", lazy_page("dashboard_pages.profile_surveys", "main")),
        Page("Health Surveys", "health", lazy_page("dashboard_pages.health", "main")),
        Page("Brands", "brands", lazy_page("dashboard_pages.brands", "main")),
        Page("Funeral Cover", "funeral", lazy_page("dashboard_pages.funeral_cover", "main")),
        Page("Cellphone", "cellphone", lazy_page("dashboard_pages.cellphone_survey", "main")),
        Page("Convenience Store", "convenience", lazy_page("dashboard_pages.convenience_store", "main")),
        Page("Advanced Filters", "advanced_filters", lazy_page("dashboard_pages.advanced_filters", "main")),
        Page("Comprehensive Analytics", "comprehensive", lazy_page("dashboard_pages.comprehensive_analytics", "main")),
    )


def init_session_state() -> None:
    if "current_page" not in st.session_state:
        st.session_state.current_page = "home"
    if "data_usage" not in st.session_state:
        st.session_state.data_usage = []


def record_data_usage(page: str, endpoint: str, records: int) -> None:
    st.session_state.data_usage.append(
        {
            "page": page,
            "endpoint": endpoint,
            "records": records,
            "timestamp": pd.Timestamp.utcnow(),
        }
    )


def render_sidebar(active_page_id: str, navigation: tuple[Page, ...]) -> None:
    st.sidebar.title("Sebenza Surveys Dashboard")
    st.sidebar.markdown("---")

    page_lookup = {page.label: page for page in navigation}
    selection = st.sidebar.radio(
        "Navigate",
        options=[page.label for page in navigation],
        index=[page.page_id for page in navigation].index(active_page_id),
    )
    if page_lookup[selection].page_id != active_page_id:
        st.session_state.current_page = page_lookup[selection].page_id
        st.rerun()

    render_backend_status()
    render_data_usage_sidebar()


def render_backend_status() -> None:
    client = get_backend_client()
    if not client:
        st.sidebar.error("Backend connection unavailable")
        return

    try:
        health = client.get_health_check()
    except Exception as exc:
        st.sidebar.error(f"Health check failed: {exc}")
        return

    status = str(health.get("status", "unknown")).lower()
    message = health.get("message") or health.get("detail") or ""
    if status == "ok":
        st.sidebar.success("Backend healthy")
    else:
        st.sidebar.warning(f"Backend degraded ({message or status})")
        with st.sidebar.expander("View health payload", expanded=False):
            st.json(health)

def render_data_usage_sidebar() -> None:
    usage = st.session_state.get("data_usage", [])
    if not usage:
        return

    total_records = sum(item["records"] for item in usage)
    with st.sidebar.expander("Recent data usage", expanded=False):
        st.metric("Rows loaded", f"{total_records:,}")
        recent = usage[-5:]
        for item in reversed(recent):
            st.caption(
                f"{item['timestamp']:%Y-%m-%d %H:%M UTC} â€” {item['page']} ({item['records']:,} rows via {item['endpoint']})"
            )


@st.cache_data(ttl=60, show_spinner=False)
def _get_survey_options() -> list[str]:
    client = get_backend_client()
    if not client:
        return []
    index = client.get_surveys_index()
    if not index.empty:
        if "survey" in index.columns:
            return sorted(index["survey"].dropna().unique().tolist())
        if "title" in index.columns:
            return sorted(index["title"].dropna().unique().tolist())
    summary = client.get_survey_summary()
    if isinstance(summary, dict):
        return sorted(summary.get("surveys", []))
    return []


def show_home_page() -> None:
    st.title("Sebenza Surveys Dashboard")
    st.caption("Insightful, trusted intelligence for the South African commuter market.")
    st.markdown("---")

    apply_card_styles()

    client = get_backend_client()
    survey_options = _get_survey_options()
    default_survey = survey_options[0] if survey_options else "SB055_Profile_Survey1"
    selected_survey = st.selectbox(
        "Select survey to analyse",
        options=survey_options or [default_survey],
        index=0,
    )

    metrics, responses = load_metrics_and_responses(client, selected_survey)
    render_metrics(metrics)
    render_feature_highlights()
    render_response_trends(responses, selected_survey)
    render_question_summary(responses)


@st.cache_data(ttl=300, show_spinner=False)
def load_metrics_and_responses(client, survey: str) -> tuple[dict[str, str], pd.DataFrame]:
    fallback = {
        "total_responses": "0",
        "unique_respondents": "0",
        "last_updated": "Unknown",
    }
    if not client:
        return fallback, pd.DataFrame()

    summary = client.get_survey_summary()
    if isinstance(summary, dict):
        total = summary.get("total_responses")
        unique = summary.get("unique_respondents")
        updated = summary.get("last_refreshed") or summary.get("generated_at")
    else:
        total = unique = updated = None

    responses = client.get_responses(survey=survey, limit=1000)
    if not isinstance(responses, pd.DataFrame):
        responses = pd.DataFrame()

    if total is None and not responses.empty:
        total = len(responses)
    if unique is None and not responses.empty and "pid" in responses.columns:
        unique = responses["pid"].nunique()
    metrics = {
        "total_responses": _format_number(total) if total is not None else "0",
        "unique_respondents": _format_number(unique) if unique is not None else "0",
        "last_updated": str(updated or pd.Timestamp.utcnow().strftime("%Y-%m-%d")),
    }

    try:
        record_data_usage("Home", "/api/responses", len(responses) if not responses.empty else 0)
    except Exception:
        pass

    return metrics, responses


def _format_number(value) -> str:
    if value is None:
        return "0"
    if isinstance(value, (int, float)) and pd.notna(value):
        return f"{int(value):,}"
    return str(value)


def render_metrics(metrics: dict[str, str]) -> None:
    st.subheader("Key metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            create_metric_card(
                "Total responses",
                metrics["total_responses"],
                "Rows available for analysis",
            ),
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            create_metric_card(
                "Unique respondents",
                metrics["unique_respondents"],
                "Distinct participant IDs",
            ),
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            create_metric_card(
                "Last refreshed",
                metrics["last_updated"],
                "Source: Sebenza data services",
            ),
            unsafe_allow_html=True,
        )


def render_feature_highlights() -> None:
    st.subheader("What you can explore")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
            **Audience intelligence**
            - Demographic depth across gender, age and province
            - Household economics with SEM and income lenses
            - Lifestyle indicators with commuter behaviour insights
            """
        )
    with col2:
        st.markdown(
            """
            **Engagement dashboards**
            - Campaign-ready segments in Brands, Health and Profile views
            - Funnel perspectives for Funeral Cover and Cellphone surveys
            - Operations suite with data quality and schema documentation
            """
        )


def render_response_trends(responses: pd.DataFrame, survey: str) -> None:
    if responses.empty or "ts" not in responses.columns:
        st.info("Response trend data is not available for the selected survey yet.")
        return

    st.subheader("Response trends")

    responses = responses.copy()
    responses["ts"] = pd.to_datetime(responses["ts"], errors="coerce")
    responses = responses.dropna(subset=["ts"])
    if responses.empty:
        st.info("No timestamped data available after cleaning.")
        return

    min_date = responses["ts"].min().date()
    max_date = responses["ts"].max().date()
    start, end = st.date_input(
        "Filter by date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key=f"range_{survey}",
    )
    mask = (responses["ts"].dt.date >= start) & (responses["ts"].dt.date <= end)
    filtered = responses.loc[mask]

    if filtered.empty:
        st.warning("No responses fall within the selected range.")
        return

    daily_counts = (
        filtered["ts"]
        .dt.to_period("D")
        .value_counts()
        .sort_index()
        .rename_axis("date")
        .reset_index(name="responses")
    )
    daily_counts["date"] = daily_counts["date"].dt.to_timestamp()

    chart = create_altair_chart(
        daily_counts,
        chart_type="line",
        x_col="date",
        y_col="responses",
        title="Daily response volume",
        width=780,
        height=320,
        font_size=14,
        title_font_size=18,
        axis_font_size=12,
    )
    if chart is not None:
        st.altair_chart(chart, use_container_width=True)
    else:
        st.dataframe(daily_counts, use_container_width=True)


def render_question_summary(responses: pd.DataFrame) -> None:
    if responses.empty or "q" not in responses.columns:
        return

    st.subheader("Top survey questions")
    question_counts = (
        responses["q"].dropna().value_counts().head(10).reset_index().rename(columns={"index": "Question", "q": "Responses"})
    )
    if question_counts.empty:
        return

    st.dataframe(question_counts, use_container_width=True)


def main() -> None:
    init_session_state()
    navigation = get_navigation()
    render_sidebar(st.session_state.current_page, navigation)

    active_page: Optional[Page] = next(
        (page for page in navigation if page.page_id == st.session_state.current_page),
        navigation[0],
    )
    active_page.render()


if __name__ == "__main__":
    main()
