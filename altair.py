import streamlit as st
import altair as alt
import pandas as pd

def create_altair_chart(data, chart_type='line', x_col='x', y_col='y', title='Chart', width=300, height=180):
    """
    Create an Altair chart with dark theme styling
    
    Parameters:
    - data: DataFrame with the data
    - chart_type: 'line', 'bar', 'scatter', 'area'
    - x_col: column name for x-axis
    - y_col: column name for y-axis
    - title: chart title
    - width: chart width
    - height: chart height
    """
    
    # Base chart configuration
    base_chart = alt.Chart(data).properties(
        width=width,
        height=height,
        background='#181C24'
    ).configure_axis(
        labelColor='#F8F8FF',
        titleColor='#F8F8FF'
    ).configure_view(
        strokeOpacity=0
    )
    
    # Create chart based on type
    if chart_type == 'line':
        chart = base_chart.mark_line(color='#2979ff', strokeWidth=2).encode(
            x=alt.X(x_col, title=''),
            y=alt.Y(y_col, title='')
        )
    elif chart_type == 'bar':
        chart = base_chart.mark_bar(color='#2979ff').encode(
            x=alt.X(x_col, title=''),
            y=alt.Y(y_col, title='')
        )
    elif chart_type == 'scatter':
        chart = base_chart.mark_circle(color='#2979ff', size=60).encode(
            x=alt.X(x_col, title=''),
            y=alt.Y(y_col, title='')
        )
    elif chart_type == 'area':
        chart = base_chart.mark_area(color='#2979ff', opacity=0.7).encode(
            x=alt.X(x_col, title=''),
            y=alt.Y(y_col, title='')
        )
    else:
        # Default to line chart
        chart = base_chart.mark_line(color='#2979ff', strokeWidth=2).encode(
            x=alt.X(x_col, title=''),
            y=alt.Y(y_col, title='')
        )
    
    return chart

def create_sample_chart():
    """Create a sample chart for demonstration"""
    df = pd.DataFrame({
        'x': range(10),
        'y': [10, 22, 30, 15, 44, 55, 40, 33, 22, 15]
    })
    
    chart = create_altair_chart(df, 'line', 'x', 'y', 'Sample Chart')
    return chart

# For direct execution
if __name__ == "__main__":
    st.title("Altair Chart Demo")
    chart = create_sample_chart()
    st.altair_chart(chart, use_container_width=True)