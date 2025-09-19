# Centralized global styles for the dashboard.
# Import and call inject_global_styles() from app.py once (at app startup)
import streamlit as st

def inject_global_styles(base_font="14px", scale=1.0):
    """
    Inject a consistent global CSS to normalize fonts and key component sizes.
    - base_font: the root body font size
    - scale: multiplier for titles etc (e.g. 1.1 for slightly larger)
    """
    title_size = f"{int(float(base_font.replace('px','')) * 1.4 * scale)}px"
    h3_size = f"{int(float(base_font.replace('px','')) * 1.2 * scale)}px"
    h4_size = f"{int(float(base_font.replace('px','')) * 1.05 * scale)}px"
    metric_label = f"{int(float(base_font.replace('px','')) * 0.95 * scale)}px"
    metric_value = f"{int(float(base_font.replace('px','')) * 1.6 * scale)}px"
    # Add any other variables you want to expose

    css = f"""
    <style>
      :root {{
        --base-font: {base_font};
        --title-font-size: {title_size};
        --h3-font-size: {h3_size};
        --h4-font-size: {h4_size};
        --metric-label-size: {metric_label};
        --metric-value-size: {metric_value};
      }}

      /* Base text */
      .stApp, .stApp .block-container, body, .streamlit-expanderHeader {{
        font-size: var(--base-font) !important;
      }}

      /* Page titles & headings */
      .stTitle, .stApp h1 {{
        font-size: var(--title-font-size) !important;
        font-weight: 700 !important;
      }}
      .stMarkdown h3, .stApp h3 {{
        font-size: var(--h3-font-size) !important;
        font-weight: 600 !important;
        margin-bottom: 0.6rem !important;
      }}
      .stMarkdown h4, .stApp h4 {{
        font-size: var(--h4-font-size) !important;
        font-weight: 550 !important;
        margin-bottom: 0.45rem !important;
      }}

      /* Metrics (Streamlit st.metric uses nested divs) */
      .stMetric > div > div > div {{
        font-size: var(--metric-label-size) !important;
      }}
      .stMetric > div > div > div[data-testid="metric-value"] {{
        font-size: var(--metric-value-size) !important;
        font-weight: 700 !important;
      }}

      /* Buttons/select boxes and controls */
      .stButton > button, .stSelectbox > div, .stMultiSelect > div {{
        font-size: var(--base-font) !important;
      }}
      
      /* Sidebar button styling */
      div[data-testid="stSidebar"] .stButton > button {{
        font-size: var(--base-font) !important;
        font-weight: 500 !important;
        text-align: left !important;
      }}

      /* Plotly chart text fallback: increase default chart font consistency */
      .js-plotly-plot .gtitle, .js-plotly-plot .gtitle * {{
        font-size: var(--h4-font-size) !important;
      }}
      .js-plotly-plot .xtitle, .js-plotly-plot .ytitle, .js-plotly-plot .xtick, .js-plotly-plot .ytick {{
        font-size: var(--base-font) !important;
      }}

      /* Small helpers to avoid per-page overrides taking effect */
      /* Pages that still inject page-specific CSS will now be less likely to cause wildly different sizes */
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)