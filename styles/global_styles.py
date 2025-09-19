"""Global styling helpers for the Sebenza Surveys dashboard."""
import streamlit as st


def inject_global_styles(base_font: str = "15px", scale: float = 1.05) -> None:
    """Inject opinionated styles so every page feels consistent and polished."""
    base_px = float(base_font.replace("px", ""))
    title_size = f"{int(base_px * 1.45 * scale)}px"
    h3_size = f"{int(base_px * 1.25 * scale)}px"
    h4_size = f"{int(base_px * 1.12 * scale)}px"
    metric_value = f"{int(base_px * 1.7 * scale)}px"
    metric_label = f"{int(base_px * 0.95 * scale)}px"

    css = f"""
    <style>
      :root {{
        --base-font: {base_font};
        --title-font-size: {title_size};
        --h3-font-size: {h3_size};
        --h4-font-size: {h4_size};
        --metric-value-size: {metric_value};
        --metric-label-size: {metric_label};
        --brand-primary: #1f4b99;
        --brand-accent: #13a36e;
        --surface: #ffffff;
        --surface-alt: #f5f7fb;
        --text-color: #1c2533;
        --muted-text: #5e6a7f;
      }}

      * {{
        font-family: "Segoe UI", "Roboto", "Helvetica Neue", Arial, sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
      }}

      body, .stApp {{
        font-size: var(--base-font) !important;
        color: var(--text-color) !important;
        background-color: var(--surface-alt) !important;
      }}

      .stApp .block-container {{
        padding-top: 2.5rem;
        padding-bottom: 3rem;
      }}

      .stTitle, .stApp h1 {{
        font-size: var(--title-font-size) !important;
        color: var(--text-color);
        font-weight: 700 !important;
        margin-bottom: 0.2rem !important;
      }}

      .stMarkdown h3, .stApp h3 {{
        font-size: var(--h3-font-size) !important;
        font-weight: 600 !important;
        color: var(--text-color);
        margin-bottom: 0.75rem !important;
      }}

      .stMarkdown h4, .stApp h4 {{
        font-size: var(--h4-font-size) !important;
        font-weight: 600 !important;
        color: var(--text-color);
      }}

      .stMarkdown p, .stMarkdown ul, .stMarkdown ol {{
        color: var(--text-color) !important;
      }}

      .stSidebar, .stSidebar .block-container {{
        background-color: var(--surface) !important;
      }}

      div[data-testid="stSidebar"] {{
        border-right: 1px solid #dbe1ec;
      }}

      div[data-testid="stSidebar"] .stButton > button, div[data-testid="stSidebar"] .stRadio > div {{
        font-size: var(--base-font) !important;
      }}

      div[data-testid="stSidebar"] .stButton > button {{
        width: 100%;
        text-align: left;
        font-weight: 600;
        color: var(--text-color);
        border-radius: 10px;
        border: 1px solid transparent;
        padding: 0.6rem 0.75rem;
        background-color: transparent;
        transition: all 0.18s ease-in-out;
      }}

      div[data-testid="stSidebar"] .stButton > button:hover,
      div[data-testid="stSidebar"] .stButton > button:focus {{
        background-color: rgba(31, 75, 153, 0.08);
        border-color: rgba(31, 75, 153, 0.25);
      }}

      .stMetric label[data-testid="stMetricLabel"] {{
        font-size: var(--metric-label-size) !important;
        color: var(--muted-text) !important;
      }}

      .stMetric div[data-testid="stMetricValue"] {{
        font-size: var(--metric-value-size) !important;
        color: var(--brand-primary) !important;
        font-weight: 700 !important;
      }}

      /* Plotly adjustments */
      .js-plotly-plot .gtitle, .js-plotly-plot .gtitle * {{
        font-size: var(--h4-font-size) !important;
        fill: var(--text-color) !important;
      }}

      .js-plotly-plot .xtitle, .js-plotly-plot .ytitle,
      .js-plotly-plot .xtick, .js-plotly-plot .ytick {{
        font-size: var(--base-font) !important;
        fill: var(--muted-text) !important;
      }}

      /* Dataframe tweaks */
      .stDataFrame caption {{
        color: var(--muted-text) !important;
        font-size: 0.85rem !important;
      }}

      .stDataFrame [data-testid="StyledDataFrame"] tbody tr:hover {{
        background-color: rgba(19, 163, 110, 0.08) !important;
      }}

      /* Expander */
      .streamlit-expanderHeader {{
        font-weight: 600 !important;
        color: var(--text-color) !important;
      }}

      .streamlit-expanderContent {{
        background-color: var(--surface-alt) !important;
      }}

      /* Tabs */
      .stTabs [data-baseweb="tab-list"] button {{
        font-weight: 600;
        color: var(--muted-text);
      }}

      .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {{
        color: var(--brand-primary);
        border-color: var(--brand-primary);
      }}
    </style>
    """

    st.markdown(css, unsafe_allow_html=True)
