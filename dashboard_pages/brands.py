"""
Brands Analysis Dashboard Page
"""
import streamlit as st
import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'styles'))
from card_style import apply_card_styles

def main():
    st.title("🏷️ Brands Analysis Dashboard")
    st.markdown("---")
    apply_card_styles()
    
    st.info("🚧 This page is currently under development. Shop visitation analysis has been moved to the Profile Surveys page.")

if __name__ == "__main__":
    main()
