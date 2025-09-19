import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from backend_client import get_backend_client
from chart_utils import create_altair_chart
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'styles'))
from card_style import apply_card_styles

# Image service removed
IMAGE_SERVICE_AVAILABLE = False

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_health_data(full: bool = True):
    """Load and cache health data using efficient endpoint"""
    try:
        from backend_client import get_backend_client
        client = get_backend_client()
        if client:
            if full:
                # Use the individual survey endpoint with limit for cost efficiency
                health_data = client.get_individual_survey("SB055_Profile_Survey1", limit=1000)
            else:
                # Use the health surveys method with limit for sample data
                health_data = client.get_health_surveys(limit=100)
            
            if health_data.empty:
                return None
            return health_data
        else:
            raise Exception("No backend connection")
    except Exception as e:
        return None

@st.cache_data(ttl=300)
def create_sample_data():
    """Create and cache sample data"""
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
    timestamps = pd.date_range('2024-01-01', periods=n_records, freq='h')
    
    return pd.DataFrame({
        'pid': profile_ids,
        'title': survey_titles,
        'q': survey_questions,
        'resp': responses,
        'gender': genders,
        'age_group': age_groups,
        'salary': monthly_salaries,
        'employment': employment_statuses,
        'ts': timestamps
    })

def main():
    st.title("Health Surveys Dashboard")
    st.markdown("---")
    apply_card_styles()
    
    # Fetch health data with caching
    # Load full health data for complete analysis
    with st.spinner("Loading health survey dataset..."):
        health_data = load_health_data(full=False)  # Use limit instead of full=True for cost efficiency
    
    if health_data is None:
        st.info("Creating sample health data for demonstration")
        health_data = create_sample_data()
    else:
        st.success(f"✅ Loaded complete dataset: {len(health_data):,} responses")
    
    if health_data is None or health_data.empty:
        st.error("No health data available")
        return
    
    
    # Key metrics - cached calculation
    @st.cache_data
    def calculate_metrics(data):
        profile_col = None
        for col in ['pid', 'profile_id', 'PROFILE_ID', 'user_id', 'id']:
            if col in data.columns:
                profile_col = col
                break
        
        question_col = None
        for col in ['q', 'question', 'SURVEY_QUESTION', 'survey_question', 'survey_questions']:
            if col in data.columns:
                question_col = col
                break
        
        return {
            'total_responses': len(data),
            'unique_profiles': data[profile_col].nunique() if profile_col else 0,
            'unique_questions': data[question_col].nunique() if question_col else 0,
            'profile_col': profile_col,
            'question_col': question_col
        }
    
    metrics = calculate_metrics(health_data)
    
    st.markdown("### Key Metrics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Responses", f"{metrics['total_responses']:,}")
    
    with col2:
        st.metric("Unique Profiles", f"{metrics['unique_profiles']:,}")
        if metrics['profile_col']:
            st.caption(f"Using column: {metrics['profile_col']}")
    
    with col3:
        st.metric("Questions", f"{metrics['unique_questions']:,}")
        if metrics['question_col']:
            st.caption(f"Using column: {metrics['question_col']}")
    
    st.markdown("---")
    
    # Image Gallery Section removed
    
    st.markdown("---")
        
    # Sidebar filters
    with st.sidebar:
        st.header("Health Filters")
        
        # Initialize session state for showing filters
        if 'show_filters' not in st.session_state:
            st.session_state.show_filters = False
        
        # Button to toggle filter visibility
        if st.button("🔧 Toggle Filters", key="toggle_filters"):
            st.session_state.show_filters = not st.session_state.show_filters
        
        # Always get the filter values, but conditionally show the controls
        # Survey title filter
        if 'SURVEY_TITLE' in health_data.columns:
            titles = health_data['SURVEY_TITLE'].unique()
            if st.session_state.show_filters:
                selected_titles = st.multiselect("Choose surveys", options=titles, default=titles, key="survey_filter")
            else:
                selected_titles = titles.tolist()
        else:
            selected_titles = []
        
        # Demographics filters
        if 'GENDER' in health_data.columns:
            genders = health_data['GENDER'].unique()
            if st.session_state.show_filters:
                selected_genders = st.multiselect("Gender", genders, default=genders, key="gender_filter")
            else:
                selected_genders = genders.tolist()
        else:
            selected_genders = []
        
        if 'AGE_GROUP' in health_data.columns:
            ages = health_data['AGE_GROUP'].unique()
            if st.session_state.show_filters:
                selected_ages = st.multiselect("Age group", ages, default=ages, key="age_filter")
            else:
                selected_ages = ages.tolist()
        else:
            selected_ages = []
        
        if 'MONTHLY_SALARY' in health_data.columns:
            salaries = health_data['MONTHLY_SALARY'].unique()
            if st.session_state.show_filters:
                selected_salaries = st.multiselect("Monthly salary", salaries, default=salaries, key="salary_filter")
            else:
                selected_salaries = salaries.tolist()
        else:
            selected_salaries = []
        
        if 'EMPLOYMENT_STATUS' in health_data.columns:
            employs = health_data['EMPLOYMENT_STATUS'].unique()
            if st.session_state.show_filters:
                selected_employs = st.multiselect("Employment status", employs, default=employs, key="employment_filter")
            else:
                selected_employs = employs.tolist()
        else:
            selected_employs = []
        
        # Check if any filters are applied (not all data selected)
        all_titles_selected = len(selected_titles) == len(health_data['SURVEY_TITLE'].unique()) if 'SURVEY_TITLE' in health_data.columns else True
        all_genders_selected = len(selected_genders) == len(health_data['GENDER'].unique()) if 'GENDER' in health_data.columns else True
        all_ages_selected = len(selected_ages) == len(health_data['AGE_GROUP'].unique()) if 'AGE_GROUP' in health_data.columns else True
        all_salaries_selected = len(selected_salaries) == len(health_data['MONTHLY_SALARY'].unique()) if 'MONTHLY_SALARY' in health_data.columns else True
        all_employs_selected = len(selected_employs) == len(health_data['EMPLOYMENT_STATUS'].unique()) if 'EMPLOYMENT_STATUS' in health_data.columns else True
        
        filters_applied = not (all_titles_selected and all_genders_selected and all_ages_selected and all_salaries_selected and all_employs_selected)
        
        if filters_applied:
            st.info("🔍 Filters applied - showing filtered data")
        else:
            st.success("📊 Showing all data - no filters applied")
            st.markdown("---")
            st.markdown("**Available Filters:**")
            st.markdown("• Survey Title")
            st.markdown("• Gender") 
            st.markdown("• Age Group")
            st.markdown("• Monthly Salary")
            st.markdown("• Employment Status")
            st.markdown("")
            st.markdown("*Click 'Toggle Filters' above to show/hide filter controls*")
    
    # Apply filters with progress indicator
    with st.spinner("Applying filters..."):
        filtered_data = health_data.copy()
        
        if selected_titles and 'SURVEY_TITLE' in health_data.columns:
            filtered_data = filtered_data[filtered_data['SURVEY_TITLE'].isin(selected_titles)]
        
        if selected_genders and 'GENDER' in health_data.columns:
            filtered_data = filtered_data[filtered_data['GENDER'].isin(selected_genders)]
        
        if selected_ages and 'AGE_GROUP' in health_data.columns:
            filtered_data = filtered_data[filtered_data['AGE_GROUP'].isin(selected_ages)]
        
        if selected_salaries and 'MONTHLY_SALARY' in health_data.columns:
            filtered_data = filtered_data[filtered_data['MONTHLY_SALARY'].isin(selected_salaries)]
        
        if selected_employs and 'EMPLOYMENT_STATUS' in health_data.columns:
            filtered_data = filtered_data[filtered_data['EMPLOYMENT_STATUS'].isin(selected_employs)]
    
    # Show filter info
    if len(filtered_data) < len(health_data):
        st.info(f"Showing {len(filtered_data):,} of {len(health_data):,} responses")
    
    # Question selection
    question_col = None
    for col in ['SURVEY_QUESTION', 'survey_question', 'question', 'q', 'survey_questions']:
        if col in filtered_data.columns:
            question_col = col
            break
    
    if question_col:
        questions = filtered_data[question_col].unique()
        if len(questions) > 0:
            selected_question = st.selectbox("Select a question to analyze:", questions)
            
            if selected_question:
                # Filter data for selected question
                question_data = filtered_data[filtered_data[question_col] == selected_question]
                
                if not question_data.empty:
                    # Find response column
                    response_col = None
                    for col in ['RESPONSE', 'response', 'answer', 'a', 'responses']:
                        if col in question_data.columns:
                            response_col = col
                            break
                    
                    if response_col:
                        # Response distribution
                        response_counts = question_data[response_col].value_counts()
                        
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
                            
                            # Create pie chart with optimized rendering
                            fig = px.pie(
                                values=response_counts.values,
                                names=response_counts.index,
                                title=f"Response Distribution",
                                color_discrete_sequence=['#FFD700', '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8']
                            )
                            fig.update_traces(textposition='inside', textinfo='percent+label')
                            fig.update_layout(
                                showlegend=True,
                                height=400,
                                margin=dict(l=20, r=20, t=40, b=20)
                            )
                            st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
                    else:
                        st.warning("No response column found in the data")
                    
                    # Crosstab analysis
                    st.subheader("Crosstab Analysis")
                    
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        # Available columns for crosstab - use detected column names
                        available_cols = []
                        if response_col:
                            available_cols.append(response_col)
                        for col in ['GENDER', 'AGE_GROUP', 'MONTHLY_SALARY', 'EMPLOYMENT_STATUS', 'gender', 'age_group', 'monthly_salary', 'employment_status']:
                            if col in question_data.columns:
                                available_cols.append(col)
                        
                        if available_cols:
                            row_col = st.selectbox("Rows", available_cols, index=0, key="health_row_col")
                        else:
                            st.warning("No suitable columns for crosstab analysis")
                            row_col = None
                    
                    with col2:
                        if available_cols:
                            col_col = st.selectbox("Columns", available_cols, index=1 if len(available_cols) > 1 else 0, key="health_col_col")
                        else:
                            col_col = None
                    
                    with col3:
                        show_mode = st.radio("Show", ["Counts", "% by column"], index=0, key="health_show_mode")
                    
                    # Create crosstab
                    if row_col and col_col and row_col != col_col:
                        try:
                            crosstab_data = pd.crosstab(
                                question_data[row_col], 
                                question_data[col_col], 
                                margins=True
                            )
                            
                            # Create chart based on crosstab data
                            st.markdown("#### Crosstab Chart")
                            
                            # Remove margins row for charting
                            chart_data = crosstab_data.drop('All', errors='ignore')
                            chart_data = chart_data.drop('All', axis=1, errors='ignore')
                            
                            if show_mode == "% by column":
                                # Convert to percentages by column
                                crosstab_data = crosstab_data.div(crosstab_data.iloc[-1], axis=1) * 100
                                crosstab_data = crosstab_data.round(1)
                                
                                # Create percentage chart - transpose for better visualization
                                chart_data = crosstab_data.drop('All', errors='ignore')
                                chart_data = chart_data.drop('All', axis=1, errors='ignore')
                                
                                # Transpose the data so columns become x-axis and rows become legend
                                chart_data_transposed = chart_data.T
                                
                                # Create stacked bar chart for percentages
                                fig = px.bar(
                                    chart_data_transposed,
                                    title=f"{col_col} vs {row_col} - Percentages",
                                    labels={'value': 'Percentage (%)', 'index': col_col},
                                    color_discrete_sequence=['#FFD700', '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8']
                                )
                                fig.update_layout(
                                    xaxis_title=col_col,
                                    yaxis_title="Percentage (%)",
                                    height=500,
                                    margin=dict(l=20, r=20, t=40, b=20)
                                )
                                fig.update_xaxes(tickangle=45)
                                st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
                                
                                st.dataframe(crosstab_data.style.format("{:.1f}%"), width='stretch')
                            else:
                                # Create count chart - transpose for better visualization
                                chart_data_transposed = chart_data.T
                                
                                # Create stacked bar chart for counts
                                fig = px.bar(
                                    chart_data_transposed,
                                    title=f"{col_col} vs {row_col} - Counts",
                                    labels={'value': 'Count', 'index': col_col},
                                    color_discrete_sequence=['#FFD700', '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8']
                                )
                                fig.update_layout(
                                    xaxis_title=col_col,
                                    yaxis_title="Count",
                                    height=500,
                                    margin=dict(l=20, r=20, t=40, b=20)
                                )
                                fig.update_xaxes(tickangle=45)
                                st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
                                
                                st.dataframe(crosstab_data.style.format("{:,}"), width='stretch')
                            
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
    

if __name__ == "__main__":
    main()