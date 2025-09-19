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

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_convenience_store_data():
    """Load and cache full convenience store survey data"""
    try:
        from backend_client import get_backend_client
        client = get_backend_client()
        if client:
            # Load data from convenience store survey with full data
            survey_data = client.get_individual_survey("TP005_Convinience_Store_Products_Survey_Briefing_Form", limit=1000)  # Use limit for cost efficiency
            if not survey_data.empty:
                # Add survey identifier
                survey_data['SURVEY_ID'] = "TP005_Convinience_Store_Products_Survey_Briefing_Form"
                return survey_data
            else:
                return None
        else:
            raise Exception("No backend connection")
    except Exception as e:
        return None

@st.cache_data(ttl=300)
def create_sample_convenience_data():
    """Create and cache sample convenience store survey data"""
    n_records = 1000
    
    # Create arrays with exactly n_records elements
    profile_ids = list(range(1, n_records + 1))
    survey_id = 'TP005_Convinience_Store_Products_Survey_Briefing_Form'
    
    # Convenience store questions
    base_questions = [
        'How often do you visit convenience stores?',
        'What products do you buy most often?',
        'What is your average spending per visit?',
        'Which convenience store do you prefer?',
        'What influences your product choices?',
        'Are you satisfied with convenience store prices?',
        'Do you use convenience store services?',
        'What would improve your convenience store experience?'
    ]
    questions = base_questions * (n_records // 8) + base_questions[:n_records % 8]
    
    # Responses for each question
    responses = []
    for i, question in enumerate(questions):
        if 'how often' in question.lower():
            responses.append(['Daily', 'Weekly', 'Monthly', 'Rarely'][i % 4])
        elif 'products do you buy' in question.lower():
            responses.append(['Food', 'Beverages', 'Snacks', 'Personal care'][i % 4])
        elif 'average spending' in question.lower():
            responses.append(['R0-R50', 'R51-R100', 'R101-R200', 'R200+'][i % 4])
        elif 'which convenience store' in question.lower():
            responses.append(['7-Eleven', 'Spar', 'Pick n Pay Express', 'Other'][i % 4])
        elif 'influences your product' in question.lower():
            responses.append(['Price', 'Quality', 'Convenience', 'Brand'][i % 4])
        elif 'satisfied with prices' in question.lower():
            responses.append(['Very satisfied', 'Satisfied', 'Neutral', 'Dissatisfied'][i % 4])
        elif 'use convenience store services' in question.lower():
            responses.append(['Yes', 'No', 'Sometimes'][i % 3])
        elif 'improve your experience' in question.lower():
            responses.append(['Lower prices', 'Better selection', 'Faster service', 'Cleaner stores'][i % 4])
        else:
            responses.append(['Yes', 'No', 'Maybe'][i % 3])
    
    # Create timestamps
    import datetime
    base_date = datetime.datetime.now() - datetime.timedelta(days=30)
    timestamps = [(base_date + datetime.timedelta(days=i % 30, hours=i % 24)).isoformat() for i in range(n_records)]
    
    # Create DataFrame
    data = {
        'PROFILE_ID': profile_ids,
        'SURVEY_ID': [survey_id] * n_records,
        'SURVEY_QUESTION': questions,
        'RESPONSE': responses,
        'SURVEY_DATE': timestamps
    }
    
    return pd.DataFrame(data)

@st.cache_data(ttl=300)
def calculate_convenience_metrics(data):
    """Calculate convenience store survey metrics"""
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
    st.title("🏪 Convenience Store Survey Dashboard")
    st.markdown("---")
    apply_card_styles()
    
    # Fetch convenience store survey data with caching
    with st.spinner("Loading Convenience Store Survey data..."):
        convenience_data = load_convenience_store_data()
    
    if convenience_data is None:
        st.info("Creating sample convenience store survey data for demonstration")
        convenience_data = create_sample_convenience_data()
    else:
        st.success(f"✅ Loaded Convenience Store Survey data: {len(convenience_data):,} responses")
    
    # Calculate metrics
    metrics = calculate_convenience_metrics(convenience_data)
    
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
        st.header("Convenience Store Filters")
        
        if 'show_filters' not in st.session_state:
            st.session_state.show_filters = False
        
        if st.button("🔧 Toggle Filters", key="toggle_filters"):
            st.session_state.show_filters = not st.session_state.show_filters
        
        # Get filter options
        questions = convenience_data['SURVEY_QUESTION'].unique().tolist() if 'SURVEY_QUESTION' in convenience_data.columns else []
        responses = convenience_data['RESPONSE'].unique().tolist() if 'RESPONSE' in convenience_data.columns else []
        
        if st.session_state.show_filters:
            selected_questions = st.multiselect(
                "Survey Questions",
                options=questions,
                default=questions,
                key="convenience_questions"
            )
            
            selected_responses = st.multiselect(
                "Responses",
                options=responses,
                default=responses,
                key="convenience_responses"
            )
        else:
            # Use default values when filters are hidden
            selected_questions = questions
            selected_responses = responses
        
        # Apply filters
        filtered_data = convenience_data.copy()
        
        if 'SURVEY_QUESTION' in convenience_data.columns:
            filtered_data = filtered_data[filtered_data['SURVEY_QUESTION'].isin(selected_questions)]
        if 'RESPONSE' in convenience_data.columns:
            filtered_data = filtered_data[filtered_data['RESPONSE'].isin(selected_responses)]
        
        # Check if filters are applied
        filters_applied = (
            len(selected_questions) < len(questions) or
            len(selected_responses) < len(responses)
        )
        
        if filters_applied:
            st.info("🔍 Filters applied - showing filtered data")
        else:
            st.success("📊 Showing all data - no filters applied")
            st.markdown("---")
            st.markdown("**Available Filters:**")
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
            file_name="convenience_store_survey_data.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
