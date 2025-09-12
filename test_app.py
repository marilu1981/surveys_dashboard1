"""
Simple test to check if the app can start
"""
import streamlit as st

st.title("🧪 App Test")
st.write("If you can see this, the basic app is working!")

# Test imports
try:
    import pandas as pd
    st.success("✅ Pandas imported successfully")
except Exception as e:
    st.error(f"❌ Pandas import failed: {e}")

try:
    import plotly.express as px
    st.success("✅ Plotly imported successfully")
except Exception as e:
    st.error(f"❌ Plotly import failed: {e}")

try:
    from google.cloud import bigquery
    st.success("✅ BigQuery imported successfully")
except Exception as e:
    st.error(f"❌ BigQuery import failed: {e}")

try:
    from st_aggrid import AgGrid
    st.success("✅ st-aggrid imported successfully")
except Exception as e:
    st.error(f"❌ st-aggrid import failed: {e}")

try:
    import streamlit_authenticator as stauth
    st.success("✅ streamlit-authenticator imported successfully")
except Exception as e:
    st.error(f"❌ streamlit-authenticator import failed: {e}")

st.write("Test completed!")
