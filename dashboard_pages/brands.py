"""
Brands Analysis Dashboard Page - Using Legacy Survey Data
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'styles'))
from card_style import apply_card_styles

def main():
    st.title("🏷️ Brands Analysis Dashboard")
    st.markdown("---")
    apply_card_styles()
    
    # Get backend client
    try:
        from backend_client import get_backend_client
        client = get_backend_client()
        
        if not client:
            st.error("❌ Backend connection failed")
            return
            
        st.info("📊 Loading legacy survey data for brands analysis...")
        
        # Load legacy survey data
        legacy_data = client.get_legacy_survey_data(limit=5000)
        
        if legacy_data.empty:
            st.warning("No legacy survey data available")
            return
            
        st.success(f"✅ Loaded {len(legacy_data):,} legacy survey responses")
        
        # Show data structure info
        with st.expander("🔍 Data Structure", expanded=False):
            st.write("**Available columns:**", list(legacy_data.columns))
            st.write("**Sample data:**")
            st.dataframe(legacy_data.head(3), width='stretch')
        
        # Filters section
        st.markdown("### 🔍 Filters")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Gender filter
            if 'gender' in legacy_data.columns:
                genders = ['All'] + list(legacy_data['gender'].unique())
                selected_gender = st.selectbox("Gender", genders, index=0)
            else:
                selected_gender = 'All'
        
        with col2:
            # Age group filter
            if 'age_group' in legacy_data.columns:
                age_groups = ['All'] + list(legacy_data['age_group'].unique())
                selected_age = st.selectbox("Age Group", age_groups, index=0)
            else:
                selected_age = 'All'
        
        with col3:
            # Employment status filter
            if 'employment_status' in legacy_data.columns:
                employment_options = ['All'] + [str(x) for x in legacy_data['employment_status'].unique() if pd.notna(x)]
                selected_employment = st.selectbox("Employment Status", employment_options, index=0)
            else:
                selected_employment = 'All'
        
        # Apply filters
        filtered_data = legacy_data.copy()
        
        if selected_gender != 'All':
            filtered_data = filtered_data[filtered_data['gender'] == selected_gender]
        
        if selected_age != 'All':
            filtered_data = filtered_data[filtered_data['age_group'] == selected_age]
        
        if selected_employment != 'All':
            filtered_data = filtered_data[filtered_data['employment_status'] == selected_employment]
        
        # Show filter results
        if len(filtered_data) < len(legacy_data):
            st.info(f"📊 Showing {len(filtered_data):,} of {len(legacy_data):,} responses")
        
        # Analysis sections
        if not filtered_data.empty:
            # Survey Questions Analysis
            st.markdown("### 📋 Survey Questions Analysis")
            
            if 'survey_question' in filtered_data.columns:
                # Question selection
                questions = filtered_data['survey_question'].unique()
                selected_question = st.selectbox("Select a question to analyze:", questions)
                
                if selected_question:
                    question_data = filtered_data[filtered_data['survey_question'] == selected_question]
                    
                    if not question_data.empty:
                        # Response analysis
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.markdown("#### Response Distribution")
                            
                            if 'response' in question_data.columns:
                                response_counts = question_data['response'].value_counts()
                                
                                # Create response distribution table
                                dist_data = []
                                total_responses = len(question_data)
                                for response, count in response_counts.items():
                                    percentage = (count / total_responses) * 100
                                    dist_data.append({
                                        'Response': response,
                                        'Count': f"{count:,}",
                                        'Percentage': f"{percentage:.1f}%"
                                    })
                                
                                dist_df = pd.DataFrame(dist_data)
                                st.dataframe(dist_df, width='stretch')
                                
                                # Download button
                                csv_data = dist_df.to_csv(index=False)
                                st.download_button(
                                    "Download Response Distribution (CSV)",
                                    csv_data,
                                    f"legacy_response_distribution_{selected_question.replace(' ', '_')[:50]}.csv",
                                    "text/csv"
                                )
                        
                        with col2:
                            st.markdown("#### Visualization")
                            
                            if 'response' in question_data.columns and len(response_counts) > 0:
                                # Create pie chart
                                fig = px.pie(
                                    values=response_counts.values,
                                    names=response_counts.index,
                                    title=f"Response Distribution",
                                    color_discrete_sequence=px.colors.qualitative.Set3
                                )
                                fig.update_traces(textposition='inside', textinfo='percent+label')
                                st.plotly_chart(fig, width='stretch')
            
            # Demographics Analysis
            st.markdown("### 👥 Demographics Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Gender distribution
                if 'gender' in filtered_data.columns:
                    gender_counts = filtered_data['gender'].value_counts()
                    fig_gender = px.pie(
                        values=gender_counts.values,
                        names=gender_counts.index,
                        title="Gender Distribution",
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    st.plotly_chart(fig_gender, width='stretch')
            
            with col2:
                # Age group distribution
                if 'age_group' in filtered_data.columns:
                    age_counts = filtered_data['age_group'].value_counts()
                    fig_age = px.bar(
                        x=age_counts.index,
                        y=age_counts.values,
                        title="Age Group Distribution",
                        color=age_counts.values,
                        color_continuous_scale='viridis'
                    )
                    fig_age.update_layout(showlegend=False)
                    st.plotly_chart(fig_age, width='stretch')
            
            # Survey Titles Analysis
            st.markdown("### 📊 Survey Titles Analysis")
            
            if 'survey_title' in filtered_data.columns:
                survey_counts = filtered_data['survey_title'].value_counts()
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # Survey titles bar chart
                    fig_surveys = px.bar(
                        x=survey_counts.values,
                        y=survey_counts.index,
                        orientation='h',
                        title="Survey Titles Distribution",
                        color=survey_counts.values,
                        color_continuous_scale='blues'
                    )
                    fig_surveys.update_layout(height=400, showlegend=False)
                    st.plotly_chart(fig_surveys, width='stretch')
                
                with col2:
                    # Survey titles table
                    survey_table = pd.DataFrame({
                        'Survey Title': survey_counts.index,
                        'Responses': survey_counts.values
                    })
                    st.dataframe(survey_table, width='stretch')
            
            # Summary metrics
            st.markdown("### 📈 Summary Metrics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Responses", f"{len(filtered_data):,}")
            
            with col2:
                unique_surveys = filtered_data['survey_title'].nunique() if 'survey_title' in filtered_data.columns else 0
                st.metric("Unique Surveys", f"{unique_surveys:,}")
            
            with col3:
                unique_questions = filtered_data['survey_question'].nunique() if 'survey_question' in filtered_data.columns else 0
                st.metric("Unique Questions", f"{unique_questions:,}")
            
            with col4:
                unique_profiles = filtered_data['profile_id'].nunique() if 'profile_id' in filtered_data.columns else 0
                st.metric("Unique Profiles", f"{unique_profiles:,}")
        
        else:
            st.warning("No data available after applying filters")
    
    except Exception as e:
        st.error(f"Error loading brands data: {str(e)}")
        st.info("This page requires backend connection to function properly.")

if __name__ == "__main__":
    main()