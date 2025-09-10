"""
Simplified dashboard with basic queries to avoid column alias issues
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from database import get_database

# Page configuration
st.set_page_config(
    page_title="Surveys Dashboard - Simple",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_simple_data():
    """Get data using simple queries"""
    db = get_database()
    if not db:
        return None, None, None
    
    try:
        # Get survey IDs
        surveys = db.execute_query("SELECT DISTINCT SURVEY_ID FROM SURVEYS_DB.RAW.SEM_AND_PROFILE_SURVEYS_09092025 WHERE SURVEY_ID IS NOT NULL")
        
        if surveys.empty:
            return None, None, None
        
        survey_id = surveys.iloc[0, 0]  # Get first survey ID
        
        # Get responses for this survey
        responses = db.execute_query(f"""
            SELECT 
                SURVEY_ID,
                SURVEY_TITLE,
                SURVEY_QUESTION,
                RESPONSE,
                SEM_SCORE,
                GENDER,
                AGEGROUP,
                LOCATION,
                CREATED_AT
            FROM SURVEYS_DB.RAW.SEM_AND_PROFILE_SURVEYS_09092025
            WHERE SURVEY_ID = {survey_id}
        """)
        
        # Get basic analytics
        analytics = db.execute_query(f"""
            SELECT 
                COUNT(*) as total_responses,
                COUNT(DISTINCT PROFILEUUID) as unique_respondents,
                AVG(SEM_SCORE) as avg_sem_score
            FROM SURVEYS_DB.RAW.SEM_AND_PROFILE_SURVEYS_09092025
            WHERE SURVEY_ID = {survey_id}
        """)
        
        return survey_id, responses, analytics
        
    except Exception as e:
        st.error(f"Error getting data: {str(e)}")
        return None, None, None

def main():
    st.title("📊 Surveys Dashboard - Simple Version")
    st.markdown("---")
    
    # Get data
    survey_id, responses, analytics = get_simple_data()
    
    if survey_id and not responses.empty:
        st.success(f"✅ Connected to Snowflake - Using Survey ID: {survey_id}")
        
        # Key metrics
        st.markdown("### 📊 Key Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_responses = len(responses)
            st.metric("Total Responses", f"{total_responses:,}")
        
        with col2:
            unique_respondents = responses['PROFILEUUID'].nunique() if 'PROFILEUUID' in responses.columns else total_responses
            st.metric("Unique Respondents", f"{unique_respondents:,}")
        
        with col3:
            if 'SEM_SCORE' in responses.columns:
                avg_score = responses['SEM_SCORE'].mean()
                st.metric("Avg SEM Score", f"{avg_score:.1f}")
            else:
                st.metric("Avg Score", "N/A")
        
        with col4:
            if 'SEM_SCORE' in responses.columns:
                high_scores = (responses['SEM_SCORE'] >= 4).sum()
                satisfaction_rate = (high_scores / total_responses) * 100
                st.metric("Satisfaction Rate", f"{satisfaction_rate:.1f}%")
            else:
                st.metric("Satisfaction Rate", "N/A")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            if 'SEM_SCORE' in responses.columns:
                st.markdown("#### SEM Score Distribution")
                score_dist = responses['SEM_SCORE'].value_counts().sort_index()
                fig = px.bar(x=score_dist.index, y=score_dist.values, title="SEM Score Distribution")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'GENDER' in responses.columns:
                st.markdown("#### Gender Distribution")
                gender_dist = responses['GENDER'].value_counts()
                fig = px.pie(values=gender_dist.values, names=gender_dist.index, title="Gender Distribution")
                st.plotly_chart(fig, use_container_width=True)
        
        # Demographics
        if 'AGEGROUP' in responses.columns:
            st.markdown("#### Age Group Distribution")
            age_dist = responses['AGEGROUP'].value_counts()
            fig = px.bar(x=age_dist.index, y=age_dist.values, title="Age Group Distribution")
            st.plotly_chart(fig, use_container_width=True)
        
        # Recent responses
        st.markdown("#### Recent Responses")
        display_cols = ['CREATED_AT', 'SURVEY_QUESTION', 'RESPONSE']
        if 'SEM_SCORE' in responses.columns:
            display_cols.insert(-1, 'SEM_SCORE')
        
        recent = responses[display_cols].head(10)
        if 'CREATED_AT' in recent.columns:
            recent['CREATED_AT'] = pd.to_datetime(recent['CREATED_AT']).dt.strftime('%Y-%m-%d %H:%M')
        
        st.dataframe(recent, use_container_width=True)
        
    else:
        st.warning("⚠️ No data found or connection failed")
        st.info("The dashboard is working but couldn't retrieve data from your Snowflake table.")

if __name__ == "__main__":
    main()
