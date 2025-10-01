"""Funeral Cover Survey Analysis Dashboard - Clean and Simple"""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from backend_client import get_backend_client
from styles.card_style import apply_card_styles


def load_funeral_surveys_data(client) -> pd.DataFrame:
    """Load funeral survey data with fallback strategies"""
    funeral_surveys = [
        "FI027_1Life_Funeral_Cover_Survey",
        "FI027_1Life_Funeral_Cover_Survey-02",
        "FI027_1Life_Funeral_Cover_Survey-03",
        "FI028_1Life_Funeral_Cover_Survey2",
        "FI028_1Life_Funeral_Cover_Survey2-02",
        "FI028_1Life_Funeral_Cover_Survey2-03"
       
        
    ]
    
    all_responses = []
    
    for survey in funeral_surveys:
        st.info(f"📊 Loading {survey}...")
        
        # Try loading strategies
        strategies = [
            ("Parquet format", lambda s=survey: client.get_responses_parquet(survey=s, limit=20000)),
            ("JSON format", lambda s=survey: client.get_responses(survey=s, limit=20000, format="json")),
            ("Individual survey", lambda s=survey: client.get_individual_survey(s, limit=20000, format="json")),
        ]
        
        survey_loaded = False
        for strategy_name, strategy_func in strategies:
            try:
                responses = strategy_func()
                if isinstance(responses, pd.DataFrame) and not responses.empty:
                    st.success(f"✅ Loaded {len(responses)} responses from {survey} using {strategy_name}")
                    all_responses.append(responses)
                    survey_loaded = True
                    break
            except Exception as e:
                if "500" in str(e):
                    continue  # Try next strategy
                st.warning(f"⚠️ {strategy_name} failed: {str(e)[:50]}...")
                continue
        
        if not survey_loaded:
            st.warning(f"❌ Could not load {survey}")
    
    if all_responses:
        combined_data = pd.concat(all_responses, ignore_index=True)
        st.success(f"🎉 Total loaded: {len(combined_data)} responses from {len(all_responses)} funeral surveys")
        return combined_data
    else:
        st.error("❌ No funeral survey data could be loaded")
        return pd.DataFrame()


def create_demographic_filters(data: pd.DataFrame) -> pd.DataFrame:
    """Create demographic filter sidebar and return filtered data"""
    st.sidebar.markdown("### 🎯 Demographic Filters")
    
    # Gender filter
    if 'gender' in data.columns:
        gender_options = ['All'] + sorted(data['gender'].dropna().unique().tolist())
        selected_gender = st.sidebar.selectbox("Gender", gender_options)
        if selected_gender != 'All':
            data = data[data['gender'] == selected_gender]
    
    # Age group filter
    if 'age_group' in data.columns:
        age_options = ['All'] + sorted(data['age_group'].dropna().unique().tolist())
        selected_age = st.sidebar.selectbox("Age Group", age_options)
        if selected_age != 'All':
            data = data[data['age_group'] == selected_age]
    
    # Province filter
    if 'home_province' in data.columns:
        province_options = ['All'] + sorted(data['home_province'].dropna().unique().tolist())
        selected_province = st.sidebar.selectbox("Province", province_options)
        if selected_province != 'All':
            data = data[data['home_province'] == selected_province]
    
    # Employment filter
    if 'employment' in data.columns:
        employment_options = ['All'] + sorted(data['employment'].dropna().unique().tolist())
        selected_employment = st.sidebar.selectbox("Employment Status", employment_options)
        if selected_employment != 'All':
            data = data[data['employment'] == selected_employment]
    
    # Show filter results
    if len(data) > 0:
        st.sidebar.success(f"📊 Filtered to {len(data):,} responses")
        if 'pid' in data.columns:
            unique_respondents = data['pid'].nunique()
            st.sidebar.info(f"👥 {unique_respondents:,} unique respondents")
    else:
        st.sidebar.error("❌ No data matches filters")
    
    return data


def create_question_chart(data: pd.DataFrame, question: str, chart_type: str = "bar") -> None:
    """Create a chart for a specific question"""
    if data.empty or 'q' not in data.columns or 'resp' not in data.columns:
        return
    
    # Filter data for this question
    question_data = data[data['q'] == question].copy()
    if question_data.empty:
        st.warning(f"No data found for question: {question}")
        return
    
    # Count unique respondents per response
    if 'pid' in question_data.columns:
        response_counts = question_data.groupby('resp')['pid'].nunique().sort_values(ascending=False)
        total_respondents = question_data['pid'].nunique()
        metric_label = "Unique Respondents"
    else:
        response_counts = question_data['resp'].value_counts()
        total_respondents = len(question_data)
        metric_label = "Responses"
    
    if response_counts.empty:
        st.warning(f"No valid responses for: {question}")
        return
    
    # Create chart
    if chart_type == "pie":
        fig = px.pie(
            values=response_counts.values,
            names=response_counts.index,
            title=f"{question}<br><sub>{metric_label}: {total_respondents:,}</sub>",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_layout(height=500)
    else:  # bar chart
        fig = px.bar(
            x=response_counts.values,
            y=response_counts.index,
            orientation='h',
            title=f"{question}<br><sub>{metric_label}: {total_respondents:,}</sub>",
            labels={'x': metric_label, 'y': 'Response'},
            color=response_counts.values,
            color_continuous_scale='viridis'
        )
        fig.update_layout(
            height=max(300, len(response_counts) * 30),
            yaxis={'categoryorder': 'total ascending'}
        )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    # Show data table
    with st.expander(f"📊 Data Table for: {question}"):
        table_data = pd.DataFrame({
            'Response': response_counts.index,
            'Count': response_counts.values,
            'Percentage': [f"{(count/total_respondents*100):.1f}%" for count in response_counts.values]
        })
        st.dataframe(table_data, use_container_width=True)


def show_survey_overview(data: pd.DataFrame) -> None:
    """Show overview metrics and info"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_responses = len(data)
        st.metric("Total Responses", f"{total_responses:,}")
    
    with col2:
        if 'pid' in data.columns:
            unique_respondents = data['pid'].nunique()
            st.metric("Unique Respondents", f"{unique_respondents:,}")
        else:
            st.metric("Unique Respondents", "N/A")
    
    with col3:
        if 'q' in data.columns:
            unique_questions = data['q'].nunique()
            st.metric("Survey Questions", f"{unique_questions:,}")
        else:
            st.metric("Survey Questions", "N/A")
    
    with col4:
        if 'title' in data.columns:
            surveys = data['title'].nunique()
            st.metric("Funeral Surveys", f"{surveys:,}")
        else:
            st.metric("Funeral Surveys", "N/A")


def main():
    """Main funeral cover survey dashboard"""
    st.set_page_config(page_title="Funeral Cover Surveys", page_icon="⚰️", layout="wide")
    
    apply_card_styles()
    
    st.title("⚰️ Funeral Cover Survey Analysis")
    st.markdown("---")
    
    # Load backend client
    client = get_backend_client()
    if not client:
        st.error("❌ Backend connection not available")
        return
    
    # Load data
    with st.spinner("Loading funeral survey data..."):
        data = load_funeral_surveys_data(client)
    
    if data.empty:
        st.error("❌ No funeral survey data available")
        return
    
    # Apply demographic filters
    filtered_data = create_demographic_filters(data)
    
    if filtered_data.empty:
        st.error("❌ No data matches the selected filters")
        return
    
    # Show overview
    st.markdown("### 📊 Survey Overview")
    show_survey_overview(filtered_data)
    st.markdown("---")
    
    # Get all questions
    if 'q' not in filtered_data.columns:
        st.error("❌ Question column not found in data")
        return
    
    questions = filtered_data['q'].dropna().unique()
    if len(questions) == 0:
        st.error("❌ No questions found in filtered data")
        return
    
    st.markdown(f"### 📋 Survey Questions ({len(questions)} found)")
    
    # Chart type selector
    chart_type = st.radio("Chart Type", ["bar", "pie"], horizontal=True, key="chart_type")
    
    # Display each question
    for i, question in enumerate(questions, 1):
        st.markdown(f"#### Question {i}")
        create_question_chart(filtered_data, question, chart_type)
        
        if i < len(questions):  # Don't add separator after last question
            st.markdown("---")
    
    # Show raw data option
    with st.expander("🔍 View Raw Data"):
        st.dataframe(filtered_data, use_container_width=True)


if __name__ == "__main__":
    main()