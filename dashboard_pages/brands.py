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

def main():
    st.title("🏷️ Brands Analysis Dashboard")
    st.markdown("---")
    apply_card_styles()
    
    # Debug section
    with st.expander("🔧 Debug Information", expanded=False):
        st.markdown("**Backend Connection Test:**")
        try:
            from backend_client import get_backend_client
            client = get_backend_client()
            if client:
                st.success("✅ Backend client created successfully")
                st.info(f"Base URL: {client.base_url}")
                
                # Test a simple endpoint
                try:
                    test_response = client.session.get(f"{client.base_url}/api/survey-summary")
                    st.info(f"Test endpoint status: {test_response.status_code}")
                except Exception as e:
                    st.warning(f"Test endpoint failed: {str(e)}")
            else:
                st.error("❌ Backend client creation failed")
        except Exception as e:
            st.error(f"❌ Backend connection error: {str(e)}")
    
    # Date range filter at the top
    st.markdown("### Date Range Filter")
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input("Start Date", value=None, key="brands_start_date")
    with col2:
        end_date = st.date_input("End Date", value=None, key="brands_end_date")
    
    # Fetch brands data from Profile Survey (contains brand-related questions)
    brands_data = None
    try:
        from backend_client import get_backend_client
        client = get_backend_client()
        if client:
            st.info("Loading brand-related data from Profile Survey...")
            # Use the Profile Survey data which contains brand-related questions
            brands_data = client.get_individual_survey("SB055_Profile_Survey1", full=True)
            
            if not brands_data.empty:
                
                # Filter for brand-related questions
                if 'q' in brands_data.columns:
                    brand_questions = brands_data[
                        brands_data['q'].str.contains('brand|product|service|company|prefer', case=False, na=False)
                    ]
                    
                    if not brand_questions.empty:
                        st.success(f"✅ Successfully loaded {len(brand_questions):,} brand-related responses!")
                        st.info(f"Columns: {list(brand_questions.columns)}")
                        brands_data = brand_questions
                    else:
                        st.warning("No brand-related questions found in Profile Survey data")
                        st.info("Available questions:", brands_data['q'].unique()[:10])
                else:
                    st.warning("No 'q' column found in Profile Survey data")
                    st.info("Using all Profile Survey data for analysis")
                    st.success(f"✅ Loaded {len(brands_data):,} total responses from Profile Survey")
            else:
                st.warning("No data available from Profile Survey")
                brands_data = None
        else:
            raise Exception("No backend connection")
    except Exception as e:
        st.warning(f"Backend connection failed: {str(e)}")
        st.info("Using sample brands data for demonstration")
        brands_data = None
    
    # Create sample data if no backend data available
    if brands_data is None or brands_data.empty:
        st.info("Creating sample brands data for demonstration")
        # Create sample brands data
        n_records = 1000
        
        # Create arrays with exactly n_records elements
        profile_ids = list(range(1, n_records + 1))
        survey_titles = ['Brand Survey 2024'] * n_records
        
        # Brand-related questions
        questions = (['Which brand do you prefer for groceries?'] * 200 + 
                   ['How often do you shop at this brand?'] * 200 + 
                   ['What influences your brand choice?'] * 200 + 
                   ['How satisfied are you with this brand?'] * 200 + 
                   ['Would you recommend this brand?'] * 200)
        
        # Create responses that match the questions (1000 total)
        all_responses = []
        for i in range(n_records):
            if i < 200:  # Brand preference question
                all_responses.append(['Shoprite', 'Pick n Pay', 'Woolworths', 'Spar', 'Checkers'][i % 5])
            elif i < 400:  # Frequency question
                all_responses.append(['Daily', 'Weekly', 'Monthly', 'Rarely', 'Never'][i % 5])
            elif i < 600:  # Influence question
                all_responses.append(['Price', 'Quality', 'Location', 'Service', 'Variety'][i % 5])
            elif i < 800:  # Satisfaction question
                all_responses.append(['Very Satisfied', 'Satisfied', 'Neutral', 'Dissatisfied', 'Very Dissatisfied'][i % 5])
            else:  # Recommendation question
                all_responses.append(['Definitely', 'Probably', 'Maybe', 'Probably Not', 'Definitely Not'][i % 5])
        
        # Demographics
        genders = ['Male', 'Female'] * 500
        age_groups = ['18-25', '26-35', '36-45', '46-55', '56+'] * 200
        income_groups = ['Low', 'Medium', 'High'] * 333 + ['Low']  # 1000 total
        locations = ['Cape Town', 'Johannesburg', 'Durban', 'Pretoria', 'Port Elizabeth'] * 200
        timestamps = pd.date_range('2024-01-01', periods=n_records, freq='h')
        
        brands_data = pd.DataFrame({
            'profile_id': profile_ids,
            'survey_title': survey_titles,
            'question': questions,
            'response': all_responses,
            'gender': genders,
            'age_group': age_groups,
            'income_group': income_groups,
            'location': locations,
            'timestamp': timestamps
        })
    
    if brands_data is None or brands_data.empty:
        st.error("No brands data available")
        return
    
    # Apply date filter if provided
    if 'ts' in brands_data.columns and (start_date or end_date):
        brands_data['date'] = pd.to_datetime(brands_data['ts']).dt.date
        if start_date:
            brands_data = brands_data[brands_data['date'] >= start_date]
        if end_date:
            brands_data = brands_data[brands_data['date'] <= end_date]
    
    # Key metrics
    st.markdown("### Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_responses = len(brands_data)
        st.metric("Total Responses", f"{total_responses:,}")
    
    with col2:
        unique_profiles = brands_data['pid'].nunique() if 'pid' in brands_data.columns else 0
        st.metric("Unique Profiles", f"{unique_profiles:,}")
    
    with col3:
        unique_questions = brands_data['q'].nunique() if 'q' in brands_data.columns else 0
        st.metric("Questions", f"{unique_questions:,}")
    
    with col4:
        # Show date range
        if 'ts' in brands_data.columns:
            dates = pd.to_datetime(brands_data['ts'], errors='coerce').dropna()
            if not dates.empty:
                date_range = f"{dates.min().strftime('%Y-%m-%d')} to {dates.max().strftime('%Y-%m-%d')}"
                st.metric("Date Range", date_range)
            else:
                st.metric("Date Range", "No Data")
        else:
            st.metric("Date Range", "No Data")
    
    st.markdown("---")
    
    # Sidebar filters
    with st.sidebar:
        st.header("Brands Filters")
        
        # Survey title filter
        if 'title' in brands_data.columns:
            titles = brands_data['title'].unique()
            selected_titles = st.multiselect("Choose surveys", options=titles, default=titles)
        else:
            selected_titles = []
        
        # Demographics filters
        if 'gender' in brands_data.columns:
            genders = brands_data['gender'].unique()
            selected_genders = st.multiselect("Gender", genders, default=genders)
        else:
            selected_genders = []
        
        if 'age_group' in brands_data.columns:
            ages = brands_data['age_group'].unique()
            selected_ages = st.multiselect("Age group", ages, default=ages)
        else:
            selected_ages = []
        
        if 'salary' in brands_data.columns:
            salaries = brands_data['salary'].unique()
            selected_salaries = st.multiselect("Salary range", salaries, default=salaries)
        else:
            selected_salaries = []
        
        if 'location' in brands_data.columns:
            locations = brands_data['location'].unique()
            selected_locations = st.multiselect("Location", locations, default=locations)
        else:
            selected_locations = []
    
    # Apply filters
    filtered_data = brands_data.copy()
    
    if selected_titles and 'title' in brands_data.columns:
        filtered_data = filtered_data[filtered_data['title'].isin(selected_titles)]
    
    if selected_genders and 'gender' in brands_data.columns:
        filtered_data = filtered_data[filtered_data['gender'].isin(selected_genders)]
    
    if selected_ages and 'age_group' in brands_data.columns:
        filtered_data = filtered_data[filtered_data['age_group'].isin(selected_ages)]
    
    if selected_salaries and 'salary' in brands_data.columns:
        filtered_data = filtered_data[filtered_data['salary'].isin(selected_salaries)]
    
    if selected_locations and 'location' in brands_data.columns:
        filtered_data = filtered_data[filtered_data['location'].isin(selected_locations)]
    
    # Show filter info
    if len(filtered_data) < len(brands_data):
        st.info(f"Showing {len(filtered_data):,} of {len(brands_data):,} responses")
    
    # Question selection
    if 'q' in filtered_data.columns:
        questions = filtered_data['q'].unique()
        if len(questions) > 0:
            selected_question = st.selectbox("Select a question to analyze:", questions)
            
            if selected_question:
                # Filter data for selected question
                question_data = filtered_data[filtered_data['q'] == selected_question]
                
                if not question_data.empty:
                    # Response distribution
                    response_counts = question_data['resp'].value_counts()
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.subheader("Response Distribution")
                        
                        # Create response distribution table
                        dist_data = []
                        total_responses = len(question_data)
                        for response, count in response_counts.items():
                            percentage = (count / total_responses) * 100
                            dist_data.append({
                                'Response': response,
                                'Count': f"{count:,}",
                                'Percentage': f"{percentage:.1f}%"
                            })
                        
                        dist_df = pd.DataFrame(dist_data)
                        st.table(dist_df)
                        
                        # Download button
                        csv_data = dist_df.to_csv(index=False)
                        st.download_button(
                            "Download Response Distribution (CSV)",
                            csv_data,
                            f"brands_response_distribution_{selected_question.replace(' ', '_')}.csv",
                            "text/csv"
                        )
                    
                    with col2:
                        st.subheader("Visualization")
                        
                        # Create pie chart
                        fig = px.pie(
                            values=response_counts.values,
                            names=response_counts.index,
                            title=f"Response Distribution",
                            color_discrete_sequence=px.colors.qualitative.Set3
                        )
                        fig.update_traces(textposition='inside', textinfo='percent+label')
                        st.plotly_chart(fig, width='stretch')
                    
                    # Crosstab analysis
                    st.subheader("Crosstab Analysis")
                    
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        # Available columns for crosstab
                        available_cols = ['response', 'gender', 'age_group', 'income_group', 'location']
                        available_cols = [col for col in available_cols if col in question_data.columns]
                        row_col = st.selectbox("Rows", available_cols, index=0, key="brands_row_col")
                    
                    with col2:
                        col_col = st.selectbox("Columns", available_cols, index=1, key="brands_col_col")
                    
                    with col3:
                        show_mode = st.radio("Show", ["Counts", "% by column"], index=0, key="brands_show_mode")
                    
                    # Create crosstab
                    if row_col != col_col:
                        try:
                            crosstab_data = pd.crosstab(
                                question_data[row_col], 
                                question_data[col_col], 
                                margins=True
                            )
                            
                            if show_mode == "% by column":
                                # Convert to percentages by column
                                crosstab_data = crosstab_data.div(crosstab_data.iloc[-1], axis=1) * 100
                                crosstab_data = crosstab_data.round(1)
                                st.dataframe(crosstab_data.style.format("{:.1f}%"), width='stretch')
                            else:
                                st.dataframe(crosstab_data.style.format("{:,}"), width='stretch')
                            
                            # Download crosstab
                            csv_data = crosstab_data.to_csv()
                            st.download_button(
                                "Download Crosstab (CSV)",
                                csv_data,
                                f"brands_crosstab_{row_col}_vs_{col_col}.csv",
                                "text/csv"
                            )
                            
                        except Exception as e:
                            st.error(f"Error creating crosstab: {str(e)}")
                    else:
                        st.warning("Please select different columns for rows and columns")
                else:
                    st.info("No responses found for the selected question with current filters")
        else:
            st.info("No questions available with current filters")
    else:
        st.info("No survey question data available")
    
    # Brand preference analysis
    if 'question' in filtered_data.columns and 'response' in filtered_data.columns:
        st.markdown("### Brand Preference Analysis")
        
        # Find brand preference question
        brand_questions = filtered_data[filtered_data['question'].str.contains('brand|prefer', case=False, na=False)]
        
        if not brand_questions.empty:
            # Get the most common brand preference question
            brand_question = brand_questions['question'].value_counts().index[0]
            brand_data = filtered_data[filtered_data['question'] == brand_question]
            
            if not brand_data.empty:
                # Brand preference by demographics
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Brand Preferences by Gender")
                    if 'gender' in brand_data.columns:
                        brand_gender = pd.crosstab(brand_data['response'], brand_data['gender'])
                        st.dataframe(brand_gender, width='stretch')
                
                with col2:
                    st.subheader("Brand Preferences by Age Group")
                    if 'age_group' in brand_data.columns:
                        brand_age = pd.crosstab(brand_data['response'], brand_data['age_group'])
                        st.dataframe(brand_age, width='stretch')
                
                # Brand preference chart
                st.subheader("Brand Preference Distribution")
                brand_counts = brand_data['response'].value_counts()
                
                fig = px.bar(
                    x=brand_counts.values,
                    y=brand_counts.index,
                    orientation='h',
                    title="Brand Preferences",
                    labels={'x': 'Number of Responses', 'y': 'Brand'}
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, width='stretch')
    
    # Response trends over time
    if 'timestamp' in filtered_data.columns:
        st.markdown("### Response Trends Over Time")
        
        # Group by date and count responses
        filtered_data['date'] = pd.to_datetime(filtered_data['timestamp']).dt.date
        daily_counts = filtered_data.groupby('date').size().reset_index(name='responses')
        
        if not daily_counts.empty:
            # Create trend chart
            trend_data = pd.DataFrame({
                'date': daily_counts['date'].astype(str),
                'responses': daily_counts['responses']
            })
            
            altair_chart = create_altair_chart(
                trend_data,
                'line',
                'date',
                'responses',
                'Daily Brands Survey Responses',
                width=800,
                height=300
            )
            
            if altair_chart is not None:
                st.altair_chart(altair_chart, use_container_width=True)
            else:
                st.info("Daily Response Counts (Altair not available)")
                st.dataframe(trend_data, width='stretch')
        else:
            st.info("No valid date data available for trend analysis")

if __name__ == "__main__":
    main()
