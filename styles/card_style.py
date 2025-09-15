import streamlit as st

def apply_card_styles():
    """Apply custom CSS for cards and dashboard look"""
    st.markdown("""
    <style>
    .card {
        background: #232B36;
        border-radius: 16px;
        box-shadow: 0 4px 24px 0 rgba(0,0,0,0.8);
        padding: 2rem 1.5rem 1.5rem 1.5rem;
        margin-bottom: 2rem;
    }
    .dashboard-container {
        display: flex;
        flex-wrap: wrap;
        gap: 2rem 1.5rem;
    }
    .card-title {
        font-size: 1.2rem;
        color: #f8f8ff;
        margin-bottom: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 600;
        color: #2979ff;
        margin-bottom: 0.6rem;
    }
    .metric-card {
        background: #232B36;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 12px 0 rgba(0,0,0,0.6);
        border-left: 4px solid #2979ff;
    }
    .metric-card h4 {
        color: #f8f8ff;
        margin-bottom: 0.5rem;
        font-size: 1.1rem;
    }
    .metric-card p {
        color: #b0b0b0;
        margin: 0;
        font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)

def create_metric_card(title, value, description=None):
    """Create a styled metric card"""
    if description:
        return f'''
        <div class="metric-card">
            <h4>{title}</h4>
            <div class="metric-value">{value}</div>
            <p>{description}</p>
        </div>
        '''
    else:
        return f'''
        <div class="metric-card">
            <h4>{title}</h4>
            <div class="metric-value">{value}</div>
        </div>
        '''

def create_dashboard_container():
    """Start a dashboard container"""
    st.markdown('<div class="dashboard-container">', unsafe_allow_html=True)

def end_dashboard_container():
    """End a dashboard container"""
    st.markdown('</div>', unsafe_allow_html=True)