"""Brands analysis dashboard backed by survey responses."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from backend_client import get_backend_client
from styles.card_style import apply_card_styles

RESPONSE_LIMIT = 20000


def _get_survey_options(client) -> list[str]:
    surveys: list[str] = []
    try:
        survey_index = client.get_surveys_index()
        if isinstance(survey_index, pd.DataFrame) and not survey_index.empty:
            if "survey" in survey_index.columns:
                surveys.extend(survey_index["survey"].dropna().astype(str).tolist())
            if "title" in survey_index.columns:
                surveys.extend(survey_index["title"].dropna().astype(str).tolist())
        summary = client.get_survey_summary()
        if isinstance(summary, dict):
            summary_surveys = summary.get("surveys", [])
            for item in summary_surveys:
                if isinstance(item, str):
                    surveys.append(item)
                elif isinstance(item, dict):
                    title = item.get("survey_title") or item.get("title")
                    if title:
                        surveys.append(str(title))
    except Exception:
        # Defer to backend error handlers already surfaced via Streamlit.
        pass

    unique_surveys = sorted({name for name in surveys if name})
    # Prefer funeral cover surveys for this dashboard.
    funeral_like = [name for name in unique_surveys if "funeral" in name.lower() or name.lower().startswith("fi027") or name.lower().startswith("fi028")]
    if funeral_like:
        return funeral_like
    return unique_surveys


def _load_responses(client, survey: str) -> pd.DataFrame:
    if not survey:
        return pd.DataFrame()
    try:
        responses = client.get_responses(survey=survey, limit=RESPONSE_LIMIT)
    except Exception as exc:  # noqa: BLE001
        st.error(f"Unable to load responses for {survey}: {exc}")
        return pd.DataFrame()
    return responses if isinstance(responses, pd.DataFrame) else pd.DataFrame()


def _render_filters(data: pd.DataFrame) -> pd.DataFrame:
    if data.empty:
        return data

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        genders = ["All"]
        if "gender" in data.columns:
            genders += sorted(data["gender"].dropna().unique())
        gender_choice = st.selectbox("Gender", genders)

    with col2:
        ages = ["All"]
        if "age_group" in data.columns:
            ages += sorted(data["age_group"].dropna().unique())
        age_choice = st.selectbox("Age group", ages)

    with col3:
        provinces = ["All"]
        if "home_province" in data.columns:
            provinces += sorted(data["home_province"].dropna().unique())
        province_choice = st.selectbox("Province", provinces)

    with col4:
        segments = ["All"]
        if "sem_segment" in data.columns:
            segments += sorted(data["sem_segment"].dropna().unique())
        segment_choice = st.selectbox("SEM segment", segments)

    filtered = data.copy()
    if gender_choice != "All" and "gender" in filtered.columns:
        filtered = filtered[filtered["gender"] == gender_choice]
    if age_choice != "All" and "age_group" in filtered.columns:
        filtered = filtered[filtered["age_group"] == age_choice]
    if province_choice != "All" and "home_province" in filtered.columns:
        filtered = filtered[filtered["home_province"] == province_choice]
    if segment_choice != "All" and "sem_segment" in filtered.columns:
        filtered = filtered[filtered["sem_segment"] == segment_choice]

    if len(filtered) < len(data):
        st.info(f"Showing {len(filtered):,} of {len(data):,} responses after filters.")

    return filtered


def _render_question_analysis(data: pd.DataFrame) -> None:
    if data.empty or "q" not in data.columns:
        return

    st.subheader("Question responses")
    questions = sorted(data["q"].dropna().unique())
    if not questions:
        st.info("No questions available in this dataset.")
        return

    selected_questions = st.multiselect("Select question(s)", questions, default=questions[:1])
    if not selected_questions:
        st.info("Select at least one question to view response distributions.")
        return

    for question in selected_questions:
        question_data = data[data["q"] == question]
        if question_data.empty:
            st.info(f"No responses for '{question}'.")
            continue

        if "resp" not in question_data.columns:
            st.info(f"Response column not present for '{question}'.")
            continue

        response_counts = question_data["resp"].fillna("Unknown").value_counts()
        total = int(response_counts.sum()) or 1
        distribution = pd.DataFrame(
            {
                "Response": response_counts.index,
                "Count": response_counts.values,
                "Percentage": (response_counts.values / total * 100).round(1),
            }
        )

        st.markdown(f"#### {question}")
        col1, col2 = st.columns([2, 1])

        with col1:
            st.dataframe(distribution, hide_index=True, use_container_width=True)
            st.download_button(
                "Download distribution (CSV)",
                distribution.to_csv(index=False),
                file_name=f"brand_distribution_{question[:40].replace(' ', '_')}.csv",
                key=f"download_{abs(hash(question))}",
            )

        with col2:
            fig = px.pie(
                distribution,
                values="Count",
                names="Response",
                title="Response share",
                color_discrete_sequence=px.colors.qualitative.Set3,
            )
            fig.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig, use_container_width=True)


def _render_demographics(data: pd.DataFrame) -> None:
    if data.empty:
        return

    st.subheader("Demographic insights")
    col1, col2 = st.columns(2)

    if "gender" in data.columns:
        with col1:
            counts = data["gender"].fillna("Unknown").value_counts()
            fig = px.pie(
                values=counts.values,
                names=counts.index,
                title="Gender distribution",
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            fig.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig, use_container_width=True)

    if "age_group" in data.columns:
        with col2:
            counts = data["age_group"].fillna("Unknown").value_counts().sort_index()
            fig = px.bar(
                x=counts.index,
                y=counts.values,
                title="Age group distribution",
                color=counts.values,
                color_continuous_scale="viridis",
            )
            fig.update_layout(showlegend=False, xaxis_title="Age group", yaxis_title="Responses")
            st.plotly_chart(fig, use_container_width=True)

    if "home_province" in data.columns:
        counts = data["home_province"].fillna("Unknown").value_counts()
        st.markdown("#### Province distribution")
        st.dataframe(
            pd.DataFrame({"Province": counts.index, "Responses": counts.values}),
            hide_index=True,
            use_container_width=True,
        )


def _render_metrics(data: pd.DataFrame, selected_surveys: list[str]) -> None:
    total = len(data)
    unique_profiles = data["pid"].nunique() if "pid" in data.columns else 0
    unique_questions = data["q"].nunique() if "q" in data.columns else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Selected surveys", len(selected_surveys))
    col2.metric("Responses", f"{total:,}")
    col3.metric("Unique participants", f"{unique_profiles:,}")

    st.caption(f"Questions covered: {unique_questions:,}")


def main() -> None:
    st.title("Brands analysis dashboard")
    st.markdown("---")
    apply_card_styles()

    client = get_backend_client()
    if not client:
        st.error("Backend connection unavailable for brands analysis.")
        return

    survey_options = _get_survey_options(client)
    if not survey_options:
        st.warning("No surveys available for analysis.")
        return

    selected_surveys = st.multiselect("Select survey(s)", survey_options, default=survey_options[:1])
    if not selected_surveys:
        st.info("Select at least one survey to load data.")
        return

    frames = []
    for survey in selected_surveys:
        df = _load_responses(client, survey)
        if not df.empty:
            if "title" not in df.columns:
                df["title"] = survey
            frames.append(df)
    if not frames:
        st.warning("No data returned for the selected survey(s).")
        return

    responses = pd.concat(frames, ignore_index=True, copy=False)

    st.success(f"Loaded {len(responses):,} responses across {len(selected_surveys)} survey(s).")

    filtered = _render_filters(responses)
    if filtered.empty:
        st.warning("No data available after applying filters.")
        return

    _render_metrics(filtered, selected_surveys)
    _render_question_analysis(filtered)
    _render_demographics(filtered)


if __name__ == "__main__":
    main()
