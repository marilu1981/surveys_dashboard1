import streamlit as st
import pandas as pd
import numpy as np

# Try to import altair, but make it optional
try:
    import altair as alt
    ALTAIR_AVAILABLE = True
except ImportError:
    ALTAIR_AVAILABLE = False
    alt = None

# Try to import plotly, but make it optional
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    px = None
    go = None

def create_altair_chart(data, chart_type='line', x_col='x', y_col='y', title='Chart', width=300, height=180, 
                       font_size=14, title_font_size=16, axis_font_size=12):
    """
    Create an Altair chart with dark theme styling and Vega-Lite v6 compatibility

    Parameters:
    - data: DataFrame with the data
    - chart_type: 'line', 'bar', 'scatter', 'area'
    - x_col: column name for x-axis
    - y_col: column name for y-axis
    - title: chart title
    - width: chart width
    - height: chart height
    - font_size: base font size for chart elements (default: 14)
    - title_font_size: font size for chart title (default: 16)
    - axis_font_size: font size for axis labels and ticks (default: 12)
    """

    if not ALTAIR_AVAILABLE or alt is None:
        st.warning("⚠️ Altair is not available. Please install it with: pip install altair")
        return None

    # Validate data
    if data is None or data.empty:
        st.warning("⚠️ No data available for chart")
        return None

    if x_col not in data.columns or y_col not in data.columns:
        st.warning(f"⚠️ Required columns '{x_col}' or '{y_col}' not found in data")
        return None

    # Additional data validation to prevent infinite extent errors
    data = data.copy()

    if data[y_col].isna().all():
        st.warning("All values in y-axis column are null/NaN")
        return None

    if 'date' in x_col.lower() or 'time' in x_col.lower():
        data[x_col] = pd.to_datetime(data[x_col], errors='coerce')
    elif not pd.api.types.is_numeric_dtype(data[x_col]):
        data[x_col] = pd.to_numeric(data[x_col], errors='coerce')

    data[y_col] = pd.to_numeric(data[y_col], errors='coerce')

    if pd.api.types.is_numeric_dtype(data[y_col]):
        data.loc[np.isinf(data[y_col]), y_col] = pd.NA
    if pd.api.types.is_numeric_dtype(data[x_col]):
        data.loc[np.isinf(data[x_col]), x_col] = pd.NA

    data = data.dropna(subset=[x_col, y_col])

    if data.empty:
        st.warning("No valid data remaining after cleaning")
        return None

    if len(data) < 2:
        st.info("Not enough data points to render the chart; showing table instead.")
        return None

    try:
        # Set Vega-Lite version to v6 for compatibility
        alt.data_transformers.enable('json')

        # Base chart configuration with Vega-Lite v6 compatibility and standardized fonts
        base_chart = alt.Chart(data).properties(
            width=width,
            height=height,
            background='#F8F8FF',
            title=alt.TitleParams(
                text=title,
                fontSize=title_font_size,
                color='#2E3440',
                fontWeight='bold'
            )
        ).configure_axis(
            labelColor='#000000',
            titleColor='#000000',
            labelFontSize=axis_font_size,
            titleFontSize=axis_font_size,
            tickColor='#F8F8FF',
            gridColor='#2E3440'
        ).configure_view(
            strokeOpacity=0
        ).configure_text(
            fontSize=font_size,
            color='#ffffff'
        )
    except Exception as e:
        st.warning(f"⚠️ Error creating Altair chart: {str(e)}")
        return None

    try:
        # Create chart based on type with proper data types
        if chart_type == 'line':
            chart = base_chart.mark_line(color='#2979ff', strokeWidth=2).encode(
                x=alt.X(x_col, title='', type='temporal' if 'date' in x_col.lower() else 'ordinal'),
                y=alt.Y(y_col, title='', type='quantitative', scale=alt.Scale(zero=False))
            )
        elif chart_type == 'bar':
            chart = base_chart.mark_bar(color='#2979ff').encode(
                x=alt.X(x_col, title='', type='ordinal'),
                y=alt.Y(y_col, title='', type='quantitative', scale=alt.Scale(zero=False))
            )
        elif chart_type == 'scatter':
            chart = base_chart.mark_circle(color='#2979ff', size=60).encode(
                x=alt.X(x_col, title='', type='quantitative'),
                y=alt.Y(y_col, title='', type='quantitative', scale=alt.Scale(zero=False))
            )
        elif chart_type == 'area':
            chart = base_chart.mark_area(color='#2979ff', opacity=0.7).encode(
                x=alt.X(x_col, title='', type='temporal' if 'date' in x_col.lower() else 'ordinal'),
                y=alt.Y(y_col, title='', type='quantitative', scale=alt.Scale(zero=False))
            )
        else:
            # Default to line chart
            chart = base_chart.mark_line(color='#2979ff', strokeWidth=2).encode(
                x=alt.X(x_col, title='', type='temporal' if 'date' in x_col.lower() else 'ordinal'),
                y=alt.Y(y_col, title='', type='quantitative', scale=alt.Scale(zero=False))
            )

        return chart
    except Exception as e:
        st.warning(f"⚠️ Error creating {chart_type} chart: {str(e)}")
        return None

def create_plotly_chart(data, chart_type='line', x_col='x', y_col='y', title='Chart', width=800, height=400,
                       font_size=14, title_font_size=16, axis_font_size=12):
    """
    Create a Plotly chart with standardized fonts and dark theme

    Parameters:
    - data: DataFrame with the data
    - chart_type: 'line', 'bar', 'scatter', 'area'
    - x_col: column name for x-axis
    - y_col: column name for y-axis
    - title: chart title
    - width: chart width
    - height: chart height
    - font_size: base font size for chart elements (default: 14)
    - title_font_size: font size for chart title (default: 16)
    - axis_font_size: font size for axis labels and ticks (default: 12)
    """

    if not PLOTLY_AVAILABLE or px is None or go is None:
        st.warning("⚠️ Plotly is not available. Please install it with: pip install plotly")
        return None

    # Validate data
    if data is None or data.empty:
        st.warning("⚠️ No data available for chart")
        return None

    if x_col not in data.columns or y_col not in data.columns:
        st.warning(f"⚠️ Required columns '{x_col}' or '{y_col}' not found in data")
        return None

    # Standardized font configuration
    font_config = {
        'family': 'Arial, sans-serif',
        'size': font_size,
        'color': '#F8F8FF'
    }

    title_config = {
        'text': title,
        'font': {
            'family': 'Arial, sans-serif',
            'size': title_font_size,
            'color': '#F8F8FF'
        },
        'x': 0.5,
        'xanchor': 'center'
    }

    axis_config = {
        'tickfont': {
            'family': 'Arial, sans-serif',
            'size': axis_font_size,
            'color': '#F8F8FF'
        },
        'title': {
            'font': {
                'family': 'Arial, sans-serif',
                'size': axis_font_size,
                'color': '#F8F8FF'
            },
            'text': ''
        },
        'gridcolor': '#2E3440',
        'linecolor': '#F8F8FF',
        'tickcolor': '#F8F8FF'
    }

    try:
        # Create chart based on type
        if chart_type == 'line':
            fig = px.line(data, x=x_col, y=y_col, title=title)
        elif chart_type == 'bar':
            fig = px.bar(data, x=x_col, y=y_col, title=title)
        elif chart_type == 'scatter':
            fig = px.scatter(data, x=x_col, y=y_col, title=title)
        elif chart_type == 'area':
            fig = px.area(data, x=x_col, y=y_col, title=title)
        else:
            # Default to line chart
            fig = px.line(data, x=x_col, y=y_col, title=title)

        # Apply standardized styling
        fig.update_layout(
            title=title_config,
            font=font_config,
            plot_bgcolor='#F8F8FF',
            paper_bgcolor='#F8F8FF',
            width=width,
            height=height,
            xaxis=axis_config,
            yaxis=axis_config,
            legend=dict(
                font=font_config,
                bgcolor='rgba(0,0,0,0)',
                bordercolor='#2E3440'
            )
        )

        # Update line/bar colors for consistency
        if chart_type in ['line', 'area']:
            fig.update_traces(line=dict(color='#2979ff', width=2))
        elif chart_type == 'bar':
            fig.update_traces(marker=dict(color='#2979ff'))
        elif chart_type == 'scatter':
            fig.update_traces(marker=dict(color='#2979ff', size=8))

        return fig

    except Exception as e:
        st.warning(f"⚠️ Error creating {chart_type} chart: {str(e)}")
        return None

def create_chart(data, chart_type='line', x_col='x', y_col='y', title='Chart', width=800, height=400,
                font_size=14, title_font_size=16, axis_font_size=12, prefer_plotly=True):
    """
    Create a chart using the best available library (Plotly preferred, Altair fallback)

    Parameters:
    - data: DataFrame with the data
    - chart_type: 'line', 'bar', 'scatter', 'area'
    - x_col: column name for x-axis
    - y_col: column name for y-axis
    - title: chart title
    - width: chart width
    - height: chart height
    - font_size: base font size for chart elements (default: 14)
    - title_font_size: font size for chart title (default: 16)
    - axis_font_size: font size for axis labels and ticks (default: 12)
    - prefer_plotly: if True, try Plotly first, then Altair (default: True)

    Returns:
    - Plotly figure or Altair chart object
    """

    if prefer_plotly and PLOTLY_AVAILABLE:
        return create_plotly_chart(data, chart_type, x_col, y_col, title, width, height, 
                                  font_size, title_font_size, axis_font_size)
    elif ALTAIR_AVAILABLE:
        return create_altair_chart(data, chart_type, x_col, y_col, title, width, height, 
                                  font_size, title_font_size, axis_font_size)
    else:
        st.warning("⚠️ Neither Plotly nor Altair is available. Please install one of them.")
        return None

def create_sample_chart():
    """Create a sample chart for demonstration"""
    df = pd.DataFrame({
        'x': range(10),
        'y': [10, 22, 30, 15, 44, 55, 40, 33, 22, 15]
    })

    chart = create_chart(df, 'line', 'x', 'y', 'Sample Chart')
    return chart

# For direct execution
if __name__ == "__main__":
    st.title("Chart Utils Demo")
    chart = create_sample_chart()
    if chart is not None:
        # Check if it's a Plotly figure or Altair chart
        if hasattr(chart, 'update_layout'):  # Plotly figure
            st.plotly_chart(chart, width='stretch')
        else:  # Altair chart
            st.altair_chart(chart, width='stretch')
    else:
        st.info("Neither Plotly nor Altair is available. Please install one of them.")
