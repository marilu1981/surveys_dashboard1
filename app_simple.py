import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Surveys Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .survey-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        border-left: 5px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

def get_sample_data():
    """Return sample data for demonstration"""
    return {
        'surveys': pd.DataFrame({
            'survey_id': [1, 2, 3],
            'survey_name': ['Customer Satisfaction', 'Employee Engagement', 'Product Feedback'],
            'survey_type': ['CSAT', 'NPS', 'Product'],
            'created_at': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'status': ['Active', 'Active', 'Active']
        }),
        'responses': pd.DataFrame({
            'response_id': range(1, 101),
            'survey_id': [1] * 40 + [2] * 35 + [3] * 25,
            'user_id': range(1, 101),
            'rating': [4, 5, 3, 4, 5, 2, 4, 5, 3, 4] * 10,
            'submitted_at': pd.date_range('2024-01-01', periods=100, freq='H'),
            'comments': ['Great service!'] * 50 + ['Needs improvement'] * 30 + ['Excellent!'] * 20
        })
    }

def show_dashboard_home():
    """Display the main dashboard home page"""
    
    # Welcome section
    st.markdown("""
    ## Welcome to the Surveys Dashboard
    
    This dashboard provides comprehensive insights from your survey data. 
    Navigate through different surveys using the sidebar or explore the overview below.
    """)
    
    # Key metrics section
    st.markdown("### 📈 Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>Total Surveys</h3>
            <h2>1,247</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>Response Rate</h3>
            <h2>78.5%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>Avg. Rating</h3>
            <h2>4.2/5</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>Active Surveys</h3>
            <h2>3</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Survey overview section
    st.markdown("### 📋 Survey Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Sample survey data for demonstration
        survey_data = {
            'Survey': ['Customer Satisfaction', 'Employee Engagement', 'Product Feedback'],
            'Responses': [456, 321, 470],
            'Completion Rate': [85.2, 72.1, 91.3],
            'Avg Rating': [4.3, 3.8, 4.5]
        }
        
        df = pd.DataFrame(survey_data)
        
        # Display survey summary table
        st.markdown("#### Survey Summary")
        st.dataframe(df, use_container_width=True)
    
    with col2:
        # Response rate chart
        st.markdown("#### Response Rate by Survey")
        fig = px.bar(
            df, 
            x='Survey', 
            y='Completion Rate',
            color='Completion Rate',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(
            height=300,
            showlegend=False,
            xaxis_title="Survey",
            yaxis_title="Completion Rate (%)"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent activity section
    st.markdown("### 🔄 Recent Activity")
    
    # Sample recent responses
    recent_data = {
        'Timestamp': ['2024-01-15 14:30', '2024-01-15 14:25', '2024-01-15 14:20', '2024-01-15 14:15'],
        'Survey': ['Customer Satisfaction', 'Product Feedback', 'Employee Engagement', 'Customer Satisfaction'],
        'Rating': [5, 4, 3, 5],
        'Comments': ['Excellent service!', 'Good product, needs improvement', 'Great team environment', 'Very satisfied']
    }
    
    recent_df = pd.DataFrame(recent_data)
    st.dataframe(recent_df, use_container_width=True)

def show_survey_page(survey_id, survey_name):
    """Display a survey page"""
    st.title(f"📋 {survey_name}")
    st.markdown("---")
    
    # Get sample data
    sample_data = get_sample_data()
    responses = sample_data['responses'][sample_data['responses']['survey_id'] == survey_id]
    
    if responses.empty:
        st.warning("No data available for this survey")
        return
    
    # Key metrics
    st.markdown("### 📊 Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Responses",
            value=f"{len(responses):,}",
            delta="12% from last week"
        )
    
    with col2:
        st.metric(
            label="Average Rating",
            value=f"{responses['rating'].mean():.1f}/5",
            delta="0.3 from last week"
        )
    
    with col3:
        st.metric(
            label="Unique Respondents",
            value=f"{responses['user_id'].nunique():,}",
            delta="8% from last week"
        )
    
    with col4:
        satisfaction_rate = (responses['rating'] >= 4).sum() / len(responses) * 100
        st.metric(
            label="Satisfaction Rate",
            value=f"{satisfaction_rate:.1f}%",
            delta="2.1% from last week"
        )
    
    # Charts section
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Rating Distribution")
        rating_dist = responses['rating'].value_counts().reset_index()
        rating_dist.columns = ['rating', 'count']
        
        fig = px.pie(
            rating_dist, 
            values='count', 
            names='rating',
            title="Distribution of Ratings",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Rating Trends")
        time_series = responses.groupby(responses['submitted_at'].dt.date).agg({
            'response_id': 'count',
            'rating': 'mean'
        }).reset_index()
        time_series.columns = ['date', 'daily_responses', 'daily_avg_rating']
        
        fig = px.line(
            time_series, 
            x='date', 
            y='daily_avg_rating',
            title="Daily Average Rating Trend",
            markers=True
        )
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Average Rating",
            yaxis=dict(range=[1, 5])
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent responses
    st.markdown("#### Recent Responses")
    recent_responses = responses[['submitted_at', 'rating', 'comments']].head(10)
    recent_responses['submitted_at'] = pd.to_datetime(recent_responses['submitted_at']).dt.strftime('%Y-%m-%d %H:%M')
    st.dataframe(recent_responses, use_container_width=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">📊 Surveys Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["🏠 Dashboard Home", "📋 Customer Satisfaction", "📋 Employee Engagement", "📋 Product Feedback"]
    )
    
    # Main content based on page selection
    if page == "🏠 Dashboard Home":
        show_dashboard_home()
    elif page == "📋 Customer Satisfaction":
        show_survey_page(1, "Customer Satisfaction Survey")
    elif page == "📋 Employee Engagement":
        show_survey_page(2, "Employee Engagement Survey")
    elif page == "📋 Product Feedback":
        show_survey_page(3, "Product Feedback Survey")

if __name__ == "__main__":
    main()
