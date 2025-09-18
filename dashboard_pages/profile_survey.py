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

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_profile_survey_data():
    """Load and cache full profile survey data"""
    try:
        from backend_client import get_backend_client
        client = get_backend_client()
        if client:
            # Use full=true to get complete dataset
            profile_data = client.get_individual_survey("SB055_Profile_Survey1", full=True)
            if profile_data.empty:
                return None
            return profile_data
        else:
            raise Exception("No backend connection")
    except Exception as e:
        return None

@st.cache_data(ttl=300)
def create_sample_profile_data():
    """Create and cache sample profile survey data"""
    n_records = 1000
    
    # Create arrays with exactly n_records elements
    profile_ids = list(range(1, n_records + 1))
    survey_titles = ['Profile Survey 2024'] * n_records
    
    # Profile questions: 6 different questions
    base_questions = [
        'What is your age group?',
        'What is your gender?',
        'What is your employment status?',
        'What is your monthly income range?',
        'What is your education level?',
        'What is your location?'
    ]
    questions = base_questions * (n_records // 6) + base_questions[:n_records % 6]
    
    # Responses for each question
    responses = []
    for i, question in enumerate(questions):
        if 'age group' in question.lower():
            responses.append(['18-25', '26-35', '36-45', '46-55', '56+'][i % 5])
        elif 'gender' in question.lower():
            responses.append(['Male', 'Female', 'Other'][i % 3])
        elif 'employment' in question.lower():
            responses.append(['Employed', 'Unemployed', 'Student', 'Retired'][i % 4])
        elif 'income' in question.lower():
            responses.append(['R0-R5000', 'R5001-R15000', 'R15001-R30000', 'R30001+'][i % 4])
        elif 'education' in question.lower():
            responses.append(['Primary', 'Secondary', 'Tertiary', 'Post-graduate'][i % 4])
        elif 'location' in question.lower():
            responses.append(['Urban', 'Rural', 'Suburban'][i % 3])
        else:
            responses.append(['Yes', 'No', 'Maybe'][i % 3])
    
    # Create timestamps
    import datetime
    base_date = datetime.datetime.now() - datetime.timedelta(days=30)
    timestamps = [(base_date + datetime.timedelta(days=i % 30, hours=i % 24)).isoformat() for i in range(n_records)]
    
    # Create DataFrame
    data = {
        'PROFILE_ID': profile_ids,
        'SURVEY_TITLE': survey_titles,
        'SURVEY_QUESTION': questions,
        'RESPONSE': responses,
        'SURVEY_DATE': timestamps
    }
    
    return pd.DataFrame(data)

@st.cache_data(ttl=300)
def calculate_profile_metrics(data):
    """Calculate profile survey metrics"""
    if data is None or data.empty:
        return {
            'total_responses': 0,
            'unique_profiles': 0,
            'unique_questions': 0,
            'date_range': 'No Data'
        }
    
    # Flexible column detection
    profile_col = None
    question_col = None
    response_col = None
    date_col = None
    
    for col in data.columns:
        col_lower = col.lower()
        if 'profile' in col_lower and 'id' in col_lower:
            profile_col = col
        elif 'question' in col_lower:
            question_col = col
        elif 'response' in col_lower:
            response_col = col
        elif 'date' in col_lower or 'timestamp' in col_lower:
            date_col = col
    
    total_responses = len(data)
    unique_profiles = data[profile_col].nunique() if profile_col else 0
    unique_questions = data[question_col].nunique() if question_col else 0
    
    # Date range
    if date_col:
        try:
            dates = pd.to_datetime(data[date_col], errors='coerce').dropna()
            if not dates.empty:
                date_range = f"{dates.min().strftime('%Y-%m-%d')} to {dates.max().strftime('%Y-%m-%d')}"
            else:
                date_range = 'No Data'
        except:
            date_range = 'No Data'
    else:
        date_range = 'No Data'
    
    return {
        'total_responses': total_responses,
        'unique_profiles': unique_profiles,
        'unique_questions': unique_questions,
        'date_range': date_range
    }

def main():
    st.title("📋 Profile Survey Dashboard")
    st.markdown("---")
    apply_card_styles()
    
    # Fetch profile survey data with caching
    with st.spinner("Loading Profile Survey data..."):
        profile_data = load_profile_survey_data()
    
    if profile_data is None:
        st.info("Creating sample profile survey data for demonstration")
        profile_data = create_sample_profile_data()
    else:
        st.success(f"✅ Loaded Profile Survey data: {len(profile_data):,} responses")
    
    # Calculate metrics
    metrics = calculate_profile_metrics(profile_data)
    
    # Display key metrics
    st.markdown("### 📊 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['total_responses']:,}</div>
            <div class="metric-label">Total Responses</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['unique_profiles']:,}</div>
            <div class="metric-label">Unique Profiles</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['unique_questions']:,}</div>
            <div class="metric-label">Questions</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['date_range']}</div>
            <div class="metric-label">Date Range</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Sidebar filters
    with st.sidebar:
        st.header("Profile Survey Filters")
        
        if 'show_filters' not in st.session_state:
            st.session_state.show_filters = False
        
        if st.button("🔧 Toggle Filters", key="toggle_filters"):
            st.session_state.show_filters = not st.session_state.show_filters
        
        # Get filter options
        survey_titles = profile_data['SURVEY_TITLE'].unique().tolist() if 'SURVEY_TITLE' in profile_data.columns else []
        questions = profile_data['SURVEY_QUESTION'].unique().tolist() if 'SURVEY_QUESTION' in profile_data.columns else []
        responses = profile_data['RESPONSE'].unique().tolist() if 'RESPONSE' in profile_data.columns else []
        
        if st.session_state.show_filters:
            selected_titles = st.multiselect(
                "Survey Title",
                options=survey_titles,
                default=survey_titles,
                key="profile_titles"
            )
            
            selected_questions = st.multiselect(
                "Survey Questions",
                options=questions,
                default=questions,
                key="profile_questions"
            )
            
            selected_responses = st.multiselect(
                "Responses",
                options=responses,
                default=responses,
                key="profile_responses"
            )
        else:
            # Use default values when filters are hidden
            selected_titles = survey_titles
            selected_questions = questions
            selected_responses = responses
        
        # Apply filters
        filtered_data = profile_data.copy()
        
        if 'SURVEY_TITLE' in profile_data.columns:
            filtered_data = filtered_data[filtered_data['SURVEY_TITLE'].isin(selected_titles)]
        if 'SURVEY_QUESTION' in profile_data.columns:
            filtered_data = filtered_data[filtered_data['SURVEY_QUESTION'].isin(selected_questions)]
        if 'RESPONSE' in profile_data.columns:
            filtered_data = filtered_data[filtered_data['RESPONSE'].isin(selected_responses)]
        
        # Check if filters are applied
        filters_applied = (
            len(selected_titles) < len(survey_titles) or
            len(selected_questions) < len(questions) or
            len(selected_responses) < len(responses)
        )
        
        if filters_applied:
            st.info("🔍 Filters applied - showing filtered data")
        else:
            st.success("📊 Showing all data - no filters applied")
            st.markdown("---")
            st.markdown("**Available Filters:**")
            st.markdown("• Survey Title")
            st.markdown("• Survey Questions")
            st.markdown("• Responses")
            st.markdown("*Click 'Toggle Filters' above to show/hide filter controls*")
    
    # Response Distribution Chart
    st.markdown("### 📊 Response Distribution")
    
    if not filtered_data.empty and 'SURVEY_QUESTION' in filtered_data.columns and 'RESPONSE' in filtered_data.columns:
        # Create response distribution chart
        response_counts = filtered_data.groupby(['SURVEY_QUESTION', 'RESPONSE']).size().reset_index(name='count')
        
        # Create a bar chart
        fig = px.bar(
            response_counts,
            x='SURVEY_QUESTION',
            y='count',
            color='RESPONSE',
            title="Response Distribution by Question",
            color_discrete_sequence=px.colors.qualitative.Vivid
        )
        
        fig.update_layout(
            xaxis_title="Survey Question",
            yaxis_title="Number of Responses",
            showlegend=True,
            height=500,
            margin=dict(l=50, r=50, t=80, b=100)
        )
        
        # Rotate x-axis labels for better readability
        fig.update_xaxes(tickangle=45)
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        # Summary table
        st.markdown("#### Summary Table")
        summary_table = response_counts.pivot(index='SURVEY_QUESTION', columns='RESPONSE', values='count').fillna(0)
        st.dataframe(summary_table, use_container_width=True)
    else:
        st.info("No response data available for visualization")
    
    # Download button
    if not filtered_data.empty:
        st.markdown("---")
        csv = filtered_data.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv,
            file_name="profile_survey_data.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
