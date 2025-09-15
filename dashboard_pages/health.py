import streamlit as st
import pandas as pd
import plotly.express as px
from backend_client import get_backend_client
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from chart_utils import create_altair_chart
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'styles'))
from card_style import apply_card_styles

def main():
    st.title("Health Surveys Dashboard")
    st.markdown("---")
    apply_card_styles()
    
    # Date range filter at the top
    st.markdown("### Date Range Filter")
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input("Start Date", value=None, key="health_start_date")
    with col2:
        end_date = st.date_input("End Date", value=None, key="health_end_date")
    
    # Fetch health data
    health_data = None
    try:
        from backend_client import get_backend_client
        client = get_backend_client()
        if client:
            health_data = client.get_health_surveys()
            if health_data.empty:
                st.warning("No health survey data available from backend")
                health_data = None
        else:
            raise Exception("No backend connection")
    except Exception as e:
        st.info("Using sample health data for demonstration")
        health_data = None
    
    # Create sample data if no backend data available
    if health_data is None or health_data.empty:
        st.info("Creating sample health data for demonstration")
        # Create sample health data
        n_records = 1000
        
        # Create arrays with exactly n_records elements
        profile_ids = list(range(1, n_records + 1))
        survey_titles = ['Health Survey 2024'] * n_records
        
        # Survey questions: 4 different questions, 250 each
        survey_questions = (['How is your overall health?'] * 250 + 
                          ['Do you exercise regularly?'] * 250 + 
                          ['How many hours do you sleep?'] * 250 + 
                          ['What is your stress level?'] * 250)
        
        # Responses: 4 response types for each question, 250 each
        responses = (['Excellent'] * 250 + ['Good'] * 250 + ['Fair'] * 250 + ['Poor'] * 250)
        
        # Demographics: ensure exactly n_records
        genders = ['Male', 'Female'] * 500
        age_groups = ['18-25', '26-35', '36-45', '46-55', '56+'] * 200
        monthly_salaries = ['0-5000', '5001-10000', '10001-20000', '20001+'] * 250
        employment_statuses = ['Employed', 'Unemployed', 'Student', 'Retired'] * 250
        timestamps = pd.date_range('2024-01-01', periods=n_records, freq='H')
        
        health_data = pd.DataFrame({
            'profile_id': profile_ids,
            'survey_title': survey_titles,
            'survey_question': survey_questions,
            'response': responses,
            'gender': genders,
            'age_group': age_groups,
            'monthly_salary': monthly_salaries,
            'employment_status': employment_statuses,
            'timestamp': timestamps
        })
    
    if health_data is None or health_data.empty:
        st.error("No health data available")
        return
    
    # Apply date filter if provided
    if 'timestamp' in health_data.columns and (start_date or end_date):
        health_data['date'] = pd.to_datetime(health_data['timestamp']).dt.date
        if start_date:
            health_data = health_data[health_data['date'] >= start_date]
        if end_date:
            health_data = health_data[health_data['date'] <= end_date]
    
    # Key metrics
    st.markdown("### Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_responses = len(health_data)
        st.metric("Total Responses", f"{total_responses:,}")
    
    with col2:
        unique_profiles = health_data['profile_id'].nunique() if 'profile_id' in health_data.columns else 0
        st.metric("Unique Profiles", f"{unique_profiles:,}")
    
    with col3:
        unique_questions = health_data['survey_question'].nunique() if 'survey_question' in health_data.columns else 0
        st.metric("Questions", f"{unique_questions:,}")
    
    with col4:
        # Show date range
        if 'timestamp' in health_data.columns:
            dates = pd.to_datetime(health_data['timestamp'], errors='coerce').dropna()
            if not dates.empty:
                date_range = f"{dates.min().strftime('%Y-%m-%d')} to {dates.max().strftime('%Y-%m-%d')}"
                st.metric("Date Range", date_range)
            else:
                st.metric("Date Range", "No Data")
        else:
            st.metric("Date Range", "No Data")
    
    st.markdown("---")
        
    # Sidebar filters
    with st.sidebar:
        st.header("Health Filters")
        
        # Survey title filter
        if 'survey_title' in health_data.columns:
            titles = health_data['survey_title'].unique()
            selected_titles = st.multiselect("Choose surveys", options=titles, default=titles)
        else:
            selected_titles = []
        
        # Demographics filters
        if 'gender' in health_data.columns:
            genders = health_data['gender'].unique()
            selected_genders = st.multiselect("Gender", genders, default=genders)
        else:
            selected_genders = []
        
        if 'age_group' in health_data.columns:
            ages = health_data['age_group'].unique()
            selected_ages = st.multiselect("Age group", ages, default=ages)
        else:
            selected_ages = []
        
        if 'monthly_salary' in health_data.columns:
            salaries = health_data['monthly_salary'].unique()
            selected_salaries = st.multiselect("Monthly salary", salaries, default=salaries)
        else:
            selected_salaries = []
        
        if 'employment_status' in health_data.columns:
            employs = health_data['employment_status'].unique()
            selected_employs = st.multiselect("Employment status", employs, default=employs)
        else:
            selected_employs = []
    
    # Apply filters
    filtered_data = health_data.copy()
    
    if selected_titles and 'survey_title' in health_data.columns:
        filtered_data = filtered_data[filtered_data['survey_title'].isin(selected_titles)]
    
    if selected_genders and 'gender' in health_data.columns:
        filtered_data = filtered_data[filtered_data['gender'].isin(selected_genders)]
    
    if selected_ages and 'age_group' in health_data.columns:
        filtered_data = filtered_data[filtered_data['age_group'].isin(selected_ages)]
    
    if selected_salaries and 'monthly_salary' in health_data.columns:
        filtered_data = filtered_data[filtered_data['monthly_salary'].isin(selected_salaries)]
    
    if selected_employs and 'employment_status' in health_data.columns:
        filtered_data = filtered_data[filtered_data['employment_status'].isin(selected_employs)]
    
    # Show filter info
    if len(filtered_data) < len(health_data):
        st.info(f"Showing {len(filtered_data):,} of {len(health_data):,} responses")
    
    # Question selection
    if 'survey_question' in filtered_data.columns:
        questions = filtered_data['survey_question'].unique()
        if len(questions) > 0:
            selected_question = st.selectbox("Select a question to analyze:", questions)
            
            if selected_question:
                # Filter data for selected question
                question_data = filtered_data[filtered_data['survey_question'] == selected_question]
                
                if not question_data.empty:
                    # Response distribution
                    response_counts = question_data['response'].value_counts()
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.subheader("Response Distribution")
                        
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
                        st.table(dist_df)
                        
                        # Download button
                        csv_data = dist_df.to_csv(index=False)
            st.download_button(
                            "Download Response Distribution (CSV)",
                            csv_data,
                            f"health_response_distribution_{selected_question.replace(' ', '_')}.csv",
                            "text/csv"
                        )
                    
                    with col2:
                        st.subheader("Visualization")
                        
                        # Create pie chart
                        fig = px.pie(
                            values=response_counts.values,
                            names=response_counts.index,
                            title=f"Response Distribution",
                            color_discrete_sequence=px.colors.qualitative.Set3
                        )
                        fig.update_traces(textposition='inside', textinfo='percent+label')
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Crosstab analysis
                    st.subheader("Crosstab Analysis")
                    
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        # Available columns for crosstab
                        available_cols = ['response', 'gender', 'age_group', 'monthly_salary', 'employment_status']
                        available_cols = [col for col in available_cols if col in question_data.columns]
                        row_col = st.selectbox("Rows", available_cols, index=0, key="health_row_col")
                    
                    with col2:
                        col_col = st.selectbox("Columns", available_cols, index=1, key="health_col_col")
                    
                    with col3:
                        show_mode = st.radio("Show", ["Counts", "% by column"], index=0, key="health_show_mode")
                    
                    # Create crosstab
                    if row_col != col_col:
                        try:
                            crosstab_data = pd.crosstab(
                                question_data[row_col], 
                                question_data[col_col], 
                                margins=True
                            )
                            
                            if show_mode == "% by column":
                                # Convert to percentages by column
                                crosstab_data = crosstab_data.div(crosstab_data.iloc[-1], axis=1) * 100
                                crosstab_data = crosstab_data.round(1)
                                st.dataframe(crosstab_data.style.format("{:.1f}%"), use_container_width=True)
                            else:
                                st.dataframe(crosstab_data.style.format("{:,}"), use_container_width=True)
                            
                            # Download crosstab
                            csv_data = crosstab_data.to_csv()
            st.download_button(
                                "Download Crosstab (CSV)",
                                csv_data,
                                f"health_crosstab_{row_col}_vs_{col_col}.csv",
                                "text/csv"
                            )
                            
                        except Exception as e:
                            st.error(f"Error creating crosstab: {str(e)}")
                    else:
                        st.warning("Please select different columns for rows and columns")
                else:
                    st.info("No responses found for the selected question with current filters")
        else:
            st.info("No questions available with current filters")
    else:
        st.info("No survey question data available")
    
    # Response trends over time
    if 'timestamp' in filtered_data.columns:
        st.markdown("### Response Trends Over Time")
        
        # Group by date and count responses
        filtered_data['date'] = pd.to_datetime(filtered_data['timestamp']).dt.date
        daily_counts = filtered_data.groupby('date').size().reset_index(name='responses')
        
        if not daily_counts.empty:
            # Create trend chart
            trend_data = pd.DataFrame({
                'date': daily_counts['date'].astype(str),
                'responses': daily_counts['responses']
            })
            
            altair_chart = create_altair_chart(
                trend_data,
                'line',
                'date',
                'responses',
                'Daily Health Survey Responses',
                width=800,
                height=300
            )
            
            if altair_chart is not None:
                st.altair_chart(altair_chart, use_container_width=True)
            else:
                st.info("Daily Response Counts (Altair not available)")
                st.dataframe(trend_data, use_container_width=True)
        else:
            st.info("No valid date data available for trend analysis")

if __name__ == "__main__":
    main()
