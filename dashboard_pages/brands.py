"""Brands analysis dashboard page."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from backend_client import get_backend_client
from styles.card_style import apply_card_styles


LEGACY_LIMIT = 2000


def _load_legacy_data() -> pd.DataFrame:
    """Fetch legacy survey data from the backend if available."""
    client = get_backend_client()
    if not client:
        return pd.DataFrame()

    if not hasattr(client, "get_legacy_survey_data"):
        st.error("Legacy survey data method not available on backend client.")
        return pd.DataFrame()

    try:
        return client.get_legacy_survey_data(limit=LEGACY_LIMIT)
    except Exception as exc:  # noqa: BLE001
        st.error(f"Unable to load legacy survey data: {exc}")
        return pd.DataFrame()


def _render_filters(data: pd.DataFrame) -> pd.DataFrame:
    """Render filter controls and return the filtered dataframe."""
    if data.empty:
        return data

    col1, col2, col3 = st.columns(3)

    with col1:
        genders = ["All"] + sorted(data["gender"].dropna().unique()) if "gender" in data.columns else ["All"]
        gender_choice = st.selectbox("Gender", genders)

    with col2:
        ages = ["All"] + sorted(data["age_group"].dropna().unique()) if "age_group" in data.columns else ["All"]
        age_choice = st.selectbox("Age group", ages)

    with col3:
        employment_values = ["All"]
        if "employment_status" in data.columns:
            values = data["employment_status"].dropna().astype(str).unique()
            employment_values += sorted(values)
        employment_choice = st.selectbox("Employment status", employment_values)

    filtered = data.copy()
    if gender_choice != "All":
        filtered = filtered[filtered["gender"] == gender_choice]
    if age_choice != "All":
        filtered = filtered[filtered["age_group"] == age_choice]
    if employment_choice != "All":
        filtered = filtered[filtered["employment_status"].astype(str) == employment_choice]

    return filtered


def _render_question_analysis(data: pd.DataFrame) -> None:
    if data.empty or "survey_question" not in data.columns:
        return

    st.subheader("Survey question analysis")
    question_options = sorted(data["survey_question"].dropna().unique())
    if not question_options:
        st.info("No questions available in the filtered dataset.")
        return

    selected_question = st.selectbox("Select a question", question_options)
    question_data = data[data["survey_question"] == selected_question]
    if question_data.empty:
        st.info("No responses for the selected question.")
        return

    if "response" in question_data.columns:
        response_counts = question_data["response"].fillna("Unknown").value_counts()
        total = int(response_counts.sum()) or 1
        distribution = pd.DataFrame(
            {
                "Response": response_counts.index,
                "Count": response_counts.values,
                "Percentage": (response_counts.values / total * 100).round(1),
            }
        )

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("#### Response distribution")
            st.dataframe(distribution, hide_index=True, use_container_width=True)
            st.download_button(
                "Download distribution (CSV)",
                distribution.to_csv(index=False),
                file_name=f"legacy_distribution_{selected_question[:40].replace(' ', '_')}.csv",
            )

        with col2:
            st.markdown("#### Visualisation")
            fig = px.pie(
                distribution,
                values="Count",
                names="Response",
                title="Responses",
                color_discrete_sequence=px.colors.qualitative.Set3,
            )
            fig.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig, use_container_width=True)


def _render_demographics(data: pd.DataFrame) -> None:
    if data.empty:
        return

    st.subheader("Demographics")
    col1, col2 = st.columns(2)

    if "gender" in data.columns:
        gender_counts = data["gender"].fillna("Unknown").value_counts()
        with col1:
            fig_gender = px.pie(
                values=gender_counts.values,
                names=gender_counts.index,
                title="Gender distribution",
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            fig_gender.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig_gender, use_container_width=True)

    if "age_group" in data.columns:
        age_counts = data["age_group"].fillna("Unknown").value_counts().sort_index()
        with col2:
            fig_age = px.bar(
                x=age_counts.index,
                y=age_counts.values,
                title="Age group distribution",
                color=age_counts.values,
                color_continuous_scale="viridis",
            )
            fig_age.update_layout(showlegend=False, xaxis_title="Age group", yaxis_title="Responses")
            st.plotly_chart(fig_age, use_container_width=True)


def _render_survey_summary(data: pd.DataFrame) -> None:
    if data.empty or "survey_title" not in data.columns:
        return

    st.subheader("Survey summary")
    counts = data["survey_title"].value_counts()
    col1, col2 = st.columns([2, 1])

    with col1:
        fig = px.bar(
            x=counts.values,
            y=counts.index,
            orientation="h",
            title="Responses by survey",
            color=counts.values,
            color_continuous_scale="Blues",
        )
        fig.update_layout(showlegend=False, xaxis_title="Responses", yaxis_title="Survey title")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        table = pd.DataFrame({"Survey title": counts.index, "Responses": counts.values})
        st.dataframe(table, hide_index=True, use_container_width=True)


def _render_metrics(data: pd.DataFrame) -> None:
    total = len(data)
    surveys = data["survey_title"].nunique() if "survey_title" in data.columns else 0
    questions = data["survey_question"].nunique() if "survey_question" in data.columns else 0
    profiles = data["profile_id"].nunique() if "profile_id" in data.columns else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total responses", f"{total:,}")
    col2.metric("Unique surveys", f"{surveys:,}")
    col3.metric("Unique questions", f"{questions:,}")
    col4.metric("Unique profiles", f"{profiles:,}")


def main() -> None:
    st.title("Brands analysis dashboard")
    st.markdown("---")
    apply_card_styles()

    legacy_data = _load_legacy_data()
    if legacy_data.empty:
        st.warning("No legacy survey data available for brands analysis.")
        return

    st.success(f"Loaded {len(legacy_data):,} legacy survey responses.")

    filtered = _render_filters(legacy_data)
    if filtered.empty:
        st.warning("No data available after applying filters.")
        return

    _render_metrics(filtered)
    _render_question_analysis(filtered)
    _render_demographics(filtered)
    _render_survey_summary(filtered)


if __name__ == "__main__":
    main()
