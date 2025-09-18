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
def load_cellphone_survey_data():
    """Load and cache cellphone survey data from group endpoint"""
    try:
        from backend_client import get_backend_client
        client = get_backend_client()
        if client:
            # Load data from SB056 group (4,426 total responses)
            cellphone_data = client.get_survey_group("SB056", full=True)
            if not cellphone_data.empty:
                # Add group identifier
                cellphone_data['SURVEY_GROUP'] = 'SB056'
                return cellphone_data
            else:
                return None
        else:
            raise Exception("No backend connection")
    except Exception as e:
        return None

@st.cache_data(ttl=300)
def create_sample_cellphone_data():
    """Create and cache sample cellphone survey data"""
    n_records = 1000
    
    # Create arrays with exactly n_records elements
    profile_ids = list(range(1, n_records + 1))
    survey_group = 'SB056'
    
    # Cellphone questions
    base_questions = [
        'What type of cellphone do you use?',
        'Which network provider do you use?',
        'How much do you spend on airtime monthly?',
        'Do you use data bundles?',
        'What is your primary use for your cellphone?',
        'Are you satisfied with your current network provider?'
    ]
    questions = base_questions * (n_records // 6) + base_questions[:n_records % 6]
    
    # Responses for each question
    responses = []
    for i, question in enumerate(questions):
        if 'type of cellphone' in question.lower():
            responses.append(['Smartphone', 'Feature phone', 'Basic phone'][i % 3])
        elif 'network provider' in question.lower():
            responses.append(['MTN', 'Vodacom', 'Cell C', 'Telkom'][i % 4])
        elif 'spend on airtime' in question.lower():
            responses.append(['R0-R50', 'R51-R150', 'R151-R300', 'R300+'][i % 4])
        elif 'data bundles' in question.lower():
            responses.append(['Yes', 'No', 'Sometimes'][i % 3])
        elif 'primary use' in question.lower():
            responses.append(['Calls', 'SMS', 'Internet', 'Social media'][i % 4])
        elif 'satisfied' in question.lower():
            responses.append(['Very satisfied', 'Satisfied', 'Neutral', 'Dissatisfied'][i % 4])
        else:
            responses.append(['Yes', 'No', 'Maybe'][i % 3])
    
    # Create timestamps
    import datetime
    base_date = datetime.datetime.now() - datetime.timedelta(days=30)
    timestamps = [(base_date + datetime.timedelta(days=i % 30, hours=i % 24)).isoformat() for i in range(n_records)]
    
    # Create DataFrame
    data = {
        'PROFILE_ID': profile_ids,
        'SURVEY_GROUP': [survey_group] * n_records,
        'SURVEY_QUESTION': questions,
        'RESPONSE': responses,
        'SURVEY_DATE': timestamps
    }
    
    return pd.DataFrame(data)

@st.cache_data(ttl=300)
def calculate_cellphone_metrics(data):
    """Calculate cellphone survey metrics"""
    if data is None or data.empty:
        return {
            'total_responses': 0,
            'unique_profiles': 0,
            'unique_questions': 0,
            'surveys_count': 0,
            'date_range': 'No Data'
        }
    
    # Flexible column detection
    profile_col = None
    question_col = None
    response_col = None
    date_col = None
    survey_col = None
    
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
        elif 'survey' in col_lower and ('group' in col_lower or 'id' in col_lower):
            survey_col = col
    
    total_responses = len(data)
    unique_profiles = data[profile_col].nunique() if profile_col else 0
    unique_questions = data[question_col].nunique() if question_col else 0
    surveys_count = data[survey_col].nunique() if survey_col else 0
    
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
        'surveys_count': surveys_count,
        'date_range': date_range
    }

def main():
    st.title("📱 Cellphone Survey Dashboard")
    st.markdown("---")
    apply_card_styles()
    
    # Fetch cellphone survey data with caching
    with st.spinner("Loading Cellphone Survey data..."):
        cellphone_data = load_cellphone_survey_data()
    
    if cellphone_data is None:
        st.info("Creating sample cellphone survey data for demonstration")
        cellphone_data = create_sample_cellphone_data()
    else:
        st.success(f"✅ Loaded Cellphone Survey data: {len(cellphone_data):,} responses")
    
    # Calculate metrics
    metrics = calculate_cellphone_metrics(cellphone_data)
    
    # Display key metrics
    st.markdown("### 📊 Key Metrics")
    col1, col2, col3, col4, col5 = st.columns(5)
    
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
            <div class="metric-value">{metrics['surveys_count']:,}</div>
            <div class="metric-label">Surveys</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['date_range']}</div>
            <div class="metric-label">Date Range</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Sidebar filters
    with st.sidebar:
        st.header("Cellphone Survey Filters")
        
        if 'show_filters' not in st.session_state:
            st.session_state.show_filters = False
        
        if st.button("🔧 Toggle Filters", key="toggle_filters"):
            st.session_state.show_filters = not st.session_state.show_filters
        
        # Get filter options
        survey_groups = cellphone_data['SURVEY_GROUP'].unique().tolist() if 'SURVEY_GROUP' in cellphone_data.columns else []
        questions = cellphone_data['SURVEY_QUESTION'].unique().tolist() if 'SURVEY_QUESTION' in cellphone_data.columns else []
        responses = cellphone_data['RESPONSE'].unique().tolist() if 'RESPONSE' in cellphone_data.columns else []
        
        if st.session_state.show_filters:
            selected_surveys = st.multiselect(
                "Survey Group",
                options=survey_groups,
                default=survey_groups,
                key="cellphone_surveys"
            )
            
            selected_questions = st.multiselect(
                "Survey Questions",
                options=questions,
                default=questions,
                key="cellphone_questions"
            )
            
            selected_responses = st.multiselect(
                "Responses",
                options=responses,
                default=responses,
                key="cellphone_responses"
            )
        else:
            # Use default values when filters are hidden
            selected_surveys = survey_groups
            selected_questions = questions
            selected_responses = responses
        
        # Apply filters
        filtered_data = cellphone_data.copy()
        
        if 'SURVEY_GROUP' in cellphone_data.columns:
            filtered_data = filtered_data[filtered_data['SURVEY_GROUP'].isin(selected_surveys)]
        if 'SURVEY_QUESTION' in cellphone_data.columns:
            filtered_data = filtered_data[filtered_data['SURVEY_QUESTION'].isin(selected_questions)]
        if 'RESPONSE' in cellphone_data.columns:
            filtered_data = filtered_data[filtered_data['RESPONSE'].isin(selected_responses)]
        
        # Check if filters are applied
        filters_applied = (
            len(selected_surveys) < len(survey_groups) or
            len(selected_questions) < len(questions) or
            len(selected_responses) < len(responses)
        )
        
        if filters_applied:
            st.info("🔍 Filters applied - showing filtered data")
        else:
            st.success("📊 Showing all data - no filters applied")
            st.markdown("---")
            st.markdown("**Available Filters:**")
            st.markdown("• Survey Group")
            st.markdown("• Survey Questions")
            st.markdown("• Responses")
            st.markdown("*Click 'Toggle Filters' above to show/hide filter controls*")
    
    # Survey Distribution Chart
    st.markdown("### 📊 Survey Distribution")
    
    if not filtered_data.empty and 'SURVEY_GROUP' in filtered_data.columns:
        # Create survey distribution chart
        survey_counts = filtered_data['SURVEY_GROUP'].value_counts().reset_index()
        survey_counts.columns = ['Survey Group', 'Count']
        
        # Create a pie chart
        fig = px.pie(
            survey_counts,
            values='Count',
            names='Survey Group',
            title="Responses by Survey Group",
            color_discrete_sequence=px.colors.qualitative.Vivid
        )
        
        fig.update_layout(
            height=500,
            margin=dict(l=50, r=50, t=80, b=50)
        )
        
        st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
    
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
        
        st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
        
        # Summary table
        st.markdown("#### Summary Table")
        summary_table = response_counts.pivot(index='SURVEY_QUESTION', columns='RESPONSE', values='count').fillna(0)
        st.dataframe(summary_table, width='stretch')
    else:
        st.info("No response data available for visualization")
    
    # Download button
    if not filtered_data.empty:
        st.markdown("---")
        csv = filtered_data.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv,
            file_name="cellphone_survey_data.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
