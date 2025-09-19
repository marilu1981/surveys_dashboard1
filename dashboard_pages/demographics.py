"""
Demographics Dashboard Page
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from backend_client import get_backend_client
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode, GridUpdateMode
import sys
import os

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from chart_utils import create_altair_chart

# Add the styles directory to the path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'styles'))
from card_style import apply_card_styles

# No need for CSS to hide pages since they're moved out of the pages/ directory

def get_real_data():
    """Get real data from your backend API"""
    client = get_backend_client()
    if not client:
        st.warning("⚠️ Backend connection not available - using sample data")
        return None, None, None, None, None
    
    try:
        # Try to get pre-computed demographics data first
        demographics_data = client.get_demographics()
        
        if demographics_data and "error" not in demographics_data:
            # Use pre-computed demographics data - this is the rich data structure
            st.success("✅ Using pre-computed demographics data from backend")
            return None, None, demographics_data, None, None
        
        # Fallback to responses data if demographics endpoint not available
        responses = client.get_responses(survey="SB055_Profile_Survey1", limit=500)  # Reduced for cost efficiency
        
        if responses.empty:
            return None, None, None, None, None
        
        # Get survey summary for analytics
        summary = client.get_surveys_index()
        
        # Create proper analytics from the responses data
        survey_ids = ['Backend Data']  # Placeholder
        
        # DEDUPLICATE DEMOGRAPHIC VARIABLES BY PID
        # For demographic analysis, we need one record per person (pid)
        # Keep the most recent record for each person (by ts)
        if 'pid' in responses.columns and 'ts' in responses.columns:
            # Sort by pid and ts (most recent first)
            responses_sorted = responses.sort_values(['pid', 'ts'], ascending=[True, False])
            # Keep first occurrence (most recent) for each pid
            demographics_data = responses_sorted.drop_duplicates(subset=['pid'], keep='first')
        else:
            demographics_data = responses
        
        # Create analytics DataFrame with proper structure
        analytics_data = {
            'total_responses': [len(responses)],  # Total survey responses
            'unique_respondents': [len(demographics_data)],  # Unique people (deduplicated)
            'avg_sem_score': [demographics_data['sem_score'].mean() if 'sem_score' in demographics_data.columns else 0]
        }
        analytics = pd.DataFrame(analytics_data)
        
        # Create score distribution from deduplicated data (only non-null values)
        if 'sem_score' in demographics_data.columns:
            # Filter out null values for sem_score from deduplicated data
            sem_scores = demographics_data['sem_score'].dropna()
            if not sem_scores.empty:
                score_dist = sem_scores.value_counts().reset_index()
                score_dist.columns = ['SEM_SCORE', 'count']
                score_dist = score_dist.sort_values('SEM_SCORE')
            else:
                score_dist = pd.DataFrame({'SEM_SCORE': [], 'count': []})
        else:
            score_dist = pd.DataFrame({'SEM_SCORE': [1, 2, 3, 4, 5], 'count': [10, 20, 30, 25, 15]})
        
        return survey_ids, responses, demographics_data, analytics, score_dist
        
    except Exception as e:
        st.error(f"Error getting data from backend: {str(e)}")
        return None, None, None, None, None
    

def render_precomputed_demographics(demographics_data):
    """Render demographics dashboard using pre-computed data"""
    
    # Side Hustles Analysis
    overall_demographics = demographics_data.get("overall_demographics", {})
    side_hustles = overall_demographics.get("side_hustles", {})
    
    if side_hustles:
        st.markdown("### 💼 Side Hustles Analysis")
        
        side_hustles_df = pd.DataFrame(list(side_hustles.items()), columns=['Side Hustle Type', 'Count'])
        fig = px.bar(side_hustles_df, x='Side Hustle Type', y='Count', title="Side Hustles Distribution")
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, width='stretch')
    
    # Cross-tabulations
    cross_tabulations = demographics_data.get("cross_tabulations", {})
    
    if cross_tabulations:
        st.markdown("### 📊 Cross-Tabulations")
        
        # Gender by Age
        gender_by_age = cross_tabulations.get("gender_by_age", {})
        if gender_by_age:
            st.markdown("#### Gender by Age Group")
            gender_age_data = []
            for age_group, genders in gender_by_age.items():
                for gender, count in genders.items():
                    gender_age_data.append({
                        'Age Group': age_group,
                        'Gender': gender,
                        'Count': count
                    })
            
            if gender_age_data:
                gender_age_df = pd.DataFrame(gender_age_data)
                fig = px.bar(gender_age_df, x='Age Group', y='Count', color='Gender', 
                           title="Gender Distribution by Age Group", barmode='group')
                st.plotly_chart(fig, width='stretch')
        
        # Employment by Gender
        employment_by_gender = cross_tabulations.get("employment_by_gender", {})
        if employment_by_gender:
            st.markdown("#### Employment Status by Gender")
            emp_gender_data = []
            for gender, employments in employment_by_gender.items():
                for employment, count in employments.items():
                    emp_gender_data.append({
                        'Gender': gender,
                        'Employment': employment,
                        'Count': count
                    })
            
            if emp_gender_data:
                emp_gender_df = pd.DataFrame(emp_gender_data)
                fig = px.bar(emp_gender_df, x='Employment', y='Count', color='Gender',
                           title="Employment Status by Gender", barmode='group')
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, width='stretch')
        
        # Salary by Age
        salary_by_age = cross_tabulations.get("salary_by_age", {})
        if salary_by_age:
            st.markdown("#### Salary Distribution by Age Group")
            salary_age_data = []
            for age_group, salaries in salary_by_age.items():
                for salary, count in salaries.items():
                    salary_age_data.append({
                        'Age Group': age_group,
                        'Salary Band': salary,
                        'Count': count
                    })
            
            if salary_age_data:
                salary_age_df = pd.DataFrame(salary_age_data)
                fig = px.bar(salary_age_df, x='Age Group', y='Count', color='Salary Band',
                           title="Salary Distribution by Age Group", barmode='group')
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, width='stretch')
    
    # Question Analysis - Response Distributions
    question_analysis = demographics_data.get("question_analysis", {})
    response_distributions = question_analysis.get("response_distributions", {})
    
    if response_distributions:
        st.markdown("### ❓ Question Analysis - Response Distributions")
        
        # "Which of these describes you?" question
        describes_question = response_distributions.get("Which of these describes you?", {})
        if describes_question:
            st.markdown("#### Which of these describes you?")
            describes_data = pd.DataFrame(list(describes_question.items()), columns=['Response', 'Count'])
            fig = px.pie(describes_data, values='Count', names='Response', 
                        title="Which of these describes you?")
            st.plotly_chart(fig, width='stretch')
        
        # "What is your main source of money?" question
        money_source_question = response_distributions.get("What is your main source of money?", {})
        if money_source_question:
            st.markdown("#### What is your main source of money?")
            money_source_data = pd.DataFrame(list(money_source_question.items()), columns=['Response', 'Count'])
            fig = px.pie(money_source_data, values='Count', names='Response',
                        title="What is your main source of money?")
            st.plotly_chart(fig, width='stretch')
    
    # SEM Score Analysis
    sem_analysis = demographics_data.get("sem_analysis", {})
    if sem_analysis and "by_segment" in sem_analysis:
        st.markdown("### 📊 SEM Score Analysis")
        
        by_segment = sem_analysis["by_segment"]
        if "mean" in by_segment:
            st.markdown("#### Mean SEM Score per SEM Group")
            sem_mean_data = []
            for segment, mean_score in by_segment["mean"].items():
                sem_mean_data.append({
                    'SEM Segment': segment,
                    'Mean Score': mean_score
                })
            
            sem_mean_df = pd.DataFrame(sem_mean_data)
            # Sort by segment number for better visualization
            sem_mean_df['Segment_Num'] = sem_mean_df['SEM Segment'].str.extract(r'(\d+)').astype(int)
            sem_mean_df = sem_mean_df.sort_values('Segment_Num')
            
            fig = px.bar(sem_mean_df, x='SEM Segment', y='Mean Score', 
                        title="Mean SEM Score per SEM Group")
            fig.update_layout(
                xaxis_title="SEM Segment",
                yaxis_title="Mean SEM Score"
            )
            st.plotly_chart(fig, width='stretch')
    
    

def main():
    st.title("📊 Demographics Dashboard")
    st.markdown("---")
    
    # Apply card styles
    apply_card_styles()
    
    # Custom CSS for smaller date range text
    st.markdown("""
    <style>
    .stMetric > div > div > div {
        font-size: 0.8rem !important;
    }
    .stMetric > div > div > div[data-testid="metric-value"] {
        font-size: 0.9rem !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Get data
    survey_ids, responses, demographics_data, analytics, score_dist = get_real_data()
    
    # Check if we have pre-computed demographics data
    if demographics_data and isinstance(demographics_data, dict) and "overview" in demographics_data:
        # Use pre-computed demographics data
        render_precomputed_demographics(demographics_data)
        return
    
    if survey_ids and (responses is not None and not responses.empty):
        # Date Range Filter
        st.markdown("### 📅 Date Range Filter")
        
        # Convert ts column to datetime if it exists
        if 'ts' in responses.columns:
            responses['ts'] = pd.to_datetime(responses['ts'], errors='coerce')
            valid_dates = responses['ts'].dropna()
            
            if not valid_dates.empty:
                min_date = valid_dates.min().date()
                max_date = valid_dates.max().date()
                
                # Create date slider
                date_range = st.date_input(
                    "Select date range:",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date,
                    key="date_range_filter"
                )
                
                # Apply date filter to responses
                if len(date_range) == 2:
                    start_date, end_date = date_range
                    # Convert to datetime for comparison
                    start_datetime = pd.to_datetime(start_date)
                    end_datetime = pd.to_datetime(end_date) + pd.Timedelta(days=1)  # Include end date
                    
                    # Filter responses by date range
                    responses = responses[
                        (responses['ts'] >= start_datetime) & 
                        (responses['ts'] < end_datetime)
                    ]
                    
                    # Update demographics data to match filtered responses
                    if 'pid' in responses.columns:
                        filtered_pids = responses['pid'].unique()
                        demographics_data = demographics_data[demographics_data['pid'].isin(filtered_pids)]
                    
                    st.info(f"📊 Showing data from {start_date} to {end_date} ({len(responses):,} responses)")
                else:
                    st.info("📊 Please select both start and end dates")
            else:
                st.warning("⚠️ No valid date data found in responses")
        else:
            st.warning("⚠️ No timestamp column found in responses")
        # st.success(f"✅ Connected to Snowflake - Analyzing All Data from {len(survey_ids)} Surveys: {survey_ids}")
        
        # Helper function to create filters for a specific section
        def create_section_filters(section_name, data, include_gender=True, include_age=True):
            st.markdown(f"#### 🔍 {section_name} Filters")
            
            # Determine number of columns based on which filters to include
            num_filters = sum([include_age, include_gender, True])  # Always include SEM
            if num_filters == 3:
                col1, col2, col3 = st.columns(3)
            elif num_filters == 2:
                col1, col2 = st.columns(2)
            else:
                col1 = st.container()
            
            col_index = 0
            
            # Create a list of available columns
            available_cols = []
            if num_filters >= 1:
                available_cols.append(col1)
            if num_filters >= 2:
                available_cols.append(col2)
            if num_filters >= 3:
                available_cols.append(col3)
            
            # Age filter
            if include_age:
                with available_cols[col_index]:
                    if 'age_group' in data.columns:
                        age_options = sorted([age for age in data['age_group'].unique() if pd.notna(age)])
                        selected_ages = st.multiselect("Age Groups", age_options, default=[], key=f"age_{section_name}")
                    else:
                        selected_ages = []
                col_index += 1
            else:
                selected_ages = []
            
            # Gender filter
            if include_gender:
                with available_cols[col_index]:
                    if 'gender' in data.columns:
                        gender_options = ['All'] + sorted([gender for gender in data['gender'].unique() if pd.notna(gender)])
                        selected_gender = st.selectbox("Gender", gender_options, key=f"gender_{section_name}")
                    else:
                        selected_gender = 'All'
                col_index += 1
            else:
                selected_gender = 'All'
            
            # SEM filter as checkboxes
            with available_cols[col_index]:
                if 'sem_segment' in data.columns:
                    sem_options = sorted([sem for sem in data['sem_segment'].unique() if pd.notna(sem)])
                    selected_sems = st.multiselect("SEM Segments", sem_options, default=[], key=f"sem_{section_name}")
                else:
                    selected_sems = []
            
            # Apply filters
            filtered_data = data.copy()
            
            if include_age and selected_ages:  # Only filter if at least one age group is selected
                filtered_data = filtered_data[filtered_data['age_group'].isin(selected_ages)]
            
            if include_gender and selected_gender != 'All':
                filtered_data = filtered_data[filtered_data['gender'] == selected_gender]
            
            if selected_sems:  # Only filter if at least one SEM segment is selected
                filtered_data = filtered_data[filtered_data['sem_segment'].isin(selected_sems)]
            
            # Show filter summary
            total_original = len(data)
            total_filtered = len(filtered_data)
            
            if total_filtered < total_original:
                st.info(f"📊 Showing {total_filtered:,} of {total_original:,} responses")
            
            return filtered_data
        
        # Key metrics
        st.markdown("### 📊 Key Metrics")
        col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
        
        with col1:
            total_responses = analytics.iloc[0, 0]  # total_responses from analytics
            st.metric("Total Responses", f"{total_responses:,}")
        
        with col2:
            unique_respondents = analytics.iloc[0, 1]  # unique_respondents from analytics
            st.metric("Unique Profiles", f"{unique_respondents:,}")
        
        with col3:
            avg_score = analytics.iloc[0, 2]  # avg_sem_score from analytics
            if not pd.isna(avg_score) and avg_score > 0:
                st.metric("Average SEM Score", f"{avg_score:.1f}")
            else:
                st.metric("Average SEM Score", "No Data")
        
        with col4:
            # Show date range
            if 'ts' in responses.columns:
                dates = pd.to_datetime(responses['ts'], errors='coerce').dropna()
                if not dates.empty:
                    date_range = f"{dates.min().strftime('%Y-%m-%d')} to {dates.max().strftime('%Y-%m-%d')}"
                    st.metric("Date Range", date_range)
                else:
                    st.metric("Date Range", "No Data")
            else:
                st.metric("Date Range", "No Data")
        
        # Add Altair chart example
        st.markdown("### 📈 Response Trends")
        
        # Create sample trend data based on actual timestamps if available
        if 'ts' in responses.columns:
            dates = pd.to_datetime(responses['ts'], errors='coerce').dropna()
            if not dates.empty:
                # Create daily response counts
                daily_counts = dates.dt.date.value_counts().sort_index()
                trend_data = pd.DataFrame({
                    'date': daily_counts.index.astype(str),  # Convert to string for Altair
                    'responses': daily_counts.values
                })
                
                
                # Create Altair chart
                altair_chart = create_altair_chart(
                    trend_data, 
                    'line', 
                    'date', 
                    'responses', 
                    'Daily Response Trends',
                    width=800,
                    height=300
                )
                
                if altair_chart is not None:
                    st.altair_chart(altair_chart, use_container_width=True)
                else:
                    # Fallback to a simple table if Altair is not available
                    st.info("📊 Daily Response Counts (Altair not available)")
                    st.dataframe(trend_data, width='stretch')
            else:
                st.info("No valid date data available for trend analysis")
        else:
            st.info("No timestamp data available for trend analysis")
        
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            if 'gender' in demographics_data.columns:
                with st.container():
                    st.markdown("#### Gender Distribution")
                    
                    # Add filters for this section (exclude gender filter since this IS the gender chart)
                    filtered_gender = create_section_filters("Gender", demographics_data, include_gender=False, include_age=True)
                    
                    # Filter out null values for gender
                    gender_data = filtered_gender['gender'].dropna()
                    if not gender_data.empty:
                        gender_dist = gender_data.value_counts()
                        total_gender_responses = gender_dist.sum()
                        fig = px.pie(
                            values=gender_dist.values, 
                            names=gender_dist.index, 
                            title=f"Sample Size: {total_gender_responses:,}"
                        )
                        st.plotly_chart(fig, width='stretch')
                    else:
                        st.info("No gender data available (all values are null)")
        
        with col2:
            if 'age_group' in demographics_data.columns:
                with st.container():
                    st.markdown("#### Age Group Distribution")
                    
                    # Add filters for this section (exclude age filter since this IS the age chart)
                    filtered_age = create_section_filters("Age", demographics_data, include_gender=True, include_age=False)
                    
                    # Filter out null values for age_group
                    age_data = filtered_age['age_group'].dropna()
                    if not age_data.empty:
                        age_dist = age_data.value_counts()
                        total_age_responses = age_dist.sum()
                        fig = px.bar(
                            x=age_dist.index, 
                            y=age_dist.values, 
                            title=f"Sample Size: {total_age_responses:,}"
                        )
                        fig.update_layout(
                            xaxis_title="",
                            yaxis_title=""
                        )
                        st.plotly_chart(fig, width='stretch')
                    else:
                        st.info("No age group data available (all values are null)")
        
        # Employment Status and Location Analysis
        col3, col4 = st.columns(2)
        
        with col3:
            if 'employment' in demographics_data.columns:
                with st.container():
                    st.markdown("#### Employment Status")
                    
                    # Add filters for this section
                    filtered_employment = create_section_filters("Employment", demographics_data)
                    
                    # Filter out null values for employment
                    employment_data = filtered_employment['employment'].dropna()
                    if not employment_data.empty:
                        emp_dist = employment_data.value_counts()
                        total_emp_responses = emp_dist.sum()
                        fig = px.pie(
                            values=emp_dist.values, 
                            names=emp_dist.index, 
                            title=f"Sample Size: {total_emp_responses:,}",
                            color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9']
                        )
                        st.plotly_chart(fig, width='stretch')
                    else:
                        st.info("No employment data available (all values are null)")
        
        with col4:
            # Side Hustles Analysis
            if 'side_hustles' in demographics_data.columns:
                with st.container():
                    st.markdown("#### Side Hustles")
                    side_hustles_data = demographics_data['side_hustles'].dropna()
                    if not side_hustles_data.empty:
                        side_hustles_dist = side_hustles_data.value_counts()
                        total_side_hustles_responses = side_hustles_dist.sum()
                        fig = px.pie(
                            values=side_hustles_dist.values,
                            names=side_hustles_dist.index,
                            title=f"Sample Size: {total_side_hustles_responses:,}",
                            color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
                        )
                        st.plotly_chart(fig, width='stretch')
                    else:
                        st.info("No side hustles data available (all values are null)")
        
        # Additional row for more charts
        col5, col6 = st.columns(2)
        
        with col5:
            # Location Analysis
            if 'location' in demographics_data.columns:
                with st.container():
                    st.markdown("#### Location Distribution")
                    
                    # Add filters for this section
                    filtered_location = create_section_filters("Location", demographics_data)
                    
                    # Filter out null values for location
                    location_data = filtered_location['location'].dropna()
                    if not location_data.empty:
                        loc_dist = location_data.value_counts()
                    
                    # Create location data for mapping
                    location_data = pd.DataFrame({
                        'location': loc_dist.index,
                        'count': loc_dist.values
                    })
                    
                    # Create South Africa province mapping
                    # Map common location names to South African provinces
                    province_mapping = {
                        'Western Cape': ['Cape Town', 'Western Cape', 'Cape', 'Stellenbosch', 'Paarl', 'George', 'Mossel Bay'],
                        'Gauteng': ['Johannesburg', 'Pretoria', 'Gauteng', 'Sandton', 'Centurion', 'Midrand', 'Roodepoort'],
                        'KwaZulu-Natal': ['Durban', 'KwaZulu-Natal', 'KZN', 'Pietermaritzburg', 'Newcastle', 'Richards Bay'],
                        'Eastern Cape': ['Port Elizabeth', 'Eastern Cape', 'PE', 'East London', 'Grahamstown', 'Uitenhage'],
                        'Free State': ['Bloemfontein', 'Free State', 'Welkom', 'Bethlehem', 'Kroonstad'],
                        'Limpopo': ['Polokwane', 'Limpopo', 'Tzaneen', 'Lephalale', 'Mokopane'],
                        'Mpumalanga': ['Nelspruit', 'Mpumalanga', 'Witbank', 'Secunda', 'Middelburg'],
                        'North West': ['Mahikeng', 'North West', 'Rustenburg', 'Potchefstroom', 'Klerksdorp'],
                        'Northern Cape': ['Kimberley', 'Northern Cape', 'Upington', 'Springbok', 'Kuruman']
                    }
                    
                    # Create province data
                    province_counts = {}
                    for location, count in loc_dist.items():
                        location_lower = str(location).lower()
                        matched_province = None
                        
                        for province, keywords in province_mapping.items():
                            for keyword in keywords:
                                if keyword.lower() in location_lower:
                                    matched_province = province
                                    break
                            if matched_province:
                                break
                        
                        if matched_province:
                            province_counts[matched_province] = province_counts.get(matched_province, 0) + count
                        else:
                            # If no match found, try to match partial province names
                            for province in province_mapping.keys():
                                if province.lower() in location_lower:
                                    province_counts[province] = province_counts.get(province, 0) + count
                                    break
                    
                    # Create province data DataFrame
                    if province_counts:
                        province_data = pd.DataFrame({
                            'Province': list(province_counts.keys()),
                            'Count': list(province_counts.values())
                        })
                        
                        # Create a clean bar chart for provinces ranked high to low
                        total_responses = province_data['Count'].sum()
                        fig_bar = px.bar(
                            x=province_data['Count'],
                            y=province_data['Province'],
                            orientation='h',
                            title=f"South Africa - Response Counts by Province (Ranked High to Low) - Sample Size: {total_responses:,}",
                            labels={'x': 'Response Count', 'y': 'Province'}
                        )
                        fig_bar.update_layout(
                            height=400,
                            showlegend=False,
                            yaxis={'categoryorder': 'total ascending'}  # This ensures high to low ranking
                        )
                        st.plotly_chart(fig_bar, width='stretch')
                    else:
                        st.info("No province data could be mapped from location names.")
                        # Show original location data
                        loc_dist_top = loc_dist.head(10)
                        fig = px.bar(
                            x=loc_dist_top.index, 
                            y=loc_dist_top.values, 
                            title="Top 10 Locations",
                            color=loc_dist_top.values,
                            color_continuous_scale='Viridis'
                        )
                        fig.update_layout(
                            xaxis_title="Location",
                            yaxis_title="Response Count",
                            showlegend=False,
                            xaxis_tickangle=-45
                        )
                        st.plotly_chart(fig, width='stretch')
        
        # SEM Groups Analysis
        if 'sem_segment' in demographics_data.columns:
            with st.container():
                st.markdown("#### SEM Groups Distribution")
                
                # Add filters for this section
                filtered_sem = create_section_filters("SEM Groups", demographics_data)
                
                # Filter out null values for sem_segment
                sem_data = filtered_sem['sem_segment'].dropna()
                if not sem_data.empty:
                    sem_groups = sem_data.value_counts()
                    
                    # Sort SEM groups by label (SEM 1, SEM 2, etc.)
                    def extract_sem_number(x):
                        try:
                            # Extract number from SEM label (e.g., "SEM 5" -> 5)
                            import re
                            match = re.search(r'SEM\s*(\d+)', str(x), re.IGNORECASE)
                            if match:
                                return int(match.group(1))
                            else:
                                return 999  # Put non-matching items at the end
                        except:
                            return 999
                    
                    # Create a DataFrame to sort properly
                    sem_df = pd.DataFrame({
                        'group': sem_groups.index,
                        'count': sem_groups.values
                    })
                    
                    # Add sort key column
                    sem_df['sort_key'] = sem_df['group'].apply(extract_sem_number)
                    
                    # Sort by the sort key
                    sem_df_sorted = sem_df.sort_values('sort_key')
                    
                    # Create sorted series
                    sem_groups_sorted = pd.Series(
                        sem_df_sorted['count'].values, 
                        index=sem_df_sorted['group'].values
                    )
                    
                    # Get total sample size
                    total_sample = sem_groups.sum()
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Pie chart showing percentage share with sample size - brighter colors
                        fig_pie = px.pie(
                            values=sem_groups.values, 
                            names=sem_groups.index, 
                            title=f"SEM Groups - Percentage Share<br><sub>Sample Size: {total_sample:,} responses</sub>",
                            color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9']
                        )
                        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                        fig_pie.update_layout(font_size=12)
                        st.plotly_chart(fig_pie, width='stretch')
                    
                    with col2:
                        # Bar chart showing counts with sample size, ordered by SEM labels - no color coding
                        fig_bar = px.bar(
                            x=sem_groups_sorted.index, 
                            y=sem_groups_sorted.values, 
                            title=f"SEM Groups - Count Distribution<br><sub>Sample Size: {total_sample:,} responses</sub>",
                            color_discrete_sequence=['#1f77b4']  # Single bright blue color
                        )
                        fig_bar.update_layout(
                            xaxis_title="SEM Segment", 
                            yaxis_title="Count",
                            font_size=12,
                            showlegend=False
                        )
                        st.plotly_chart(fig_bar, width='stretch')
                    
                    # Show detailed breakdown with better styling
                    st.markdown("##### SEM Groups Breakdown")
                    sem_breakdown = pd.DataFrame({
                        'SEM Group': sem_groups.index,
                        'Count': sem_groups.values,
                        'Percentage': (sem_groups.values / sem_groups.sum() * 100).round(2)
                    })
                    
                    # Configure AgGrid
                    gb = GridOptionsBuilder.from_dataframe(sem_breakdown)
                    gb.configure_pagination(paginationAutoPageSize=True)
                    gb.configure_side_bar()
                    gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc='sum', editable=True)
                    gb.configure_column('Count', type=['numericColumn', 'numberColumnFilter', 'customNumericFormat'], precision=0)
                    gb.configure_column('Percentage', type=['numericColumn', 'numberColumnFilter', 'customNumericFormat'], precision=2)
                    gridOptions = gb.build()
                    
                    # Display AgGrid
                    AgGrid(sem_breakdown, gridOptions=gridOptions, enable_enterprise_modules=True, height=400)
                else:
                    st.info("No SEM segment data available (all values are null)")
    
    elif demographics_data is not None and not demographics_data.empty:
        # Handle case where we have demographics data but no responses data
        st.info("📊 Using pre-computed demographics data from backend")
        
        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Responses", f"{len(demographics_data):,}")
        
        with col2:
            unique_respondents = demographics_data['pid'].nunique() if 'pid' in demographics_data.columns else len(demographics_data)
            st.metric("Unique Respondents", f"{unique_respondents:,}")
        
        with col3:
            if 'sem_score' in demographics_data.columns:
                avg_score = demographics_data['sem_score'].mean()
                if not pd.isna(avg_score) and avg_score > 0:
                    st.metric("Average SEM Score", f"{avg_score:.1f}")
                else:
                    st.metric("Average SEM Score", "No Data")
            else:
                st.metric("Average SEM Score", "No Data")
        
        with col4:
            st.metric("Date Range", "Pre-computed")
        
        # Display demographics charts using the pre-computed data
        st.markdown("### 📊 Demographics Overview")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'gender' in demographics_data.columns:
                gender_dist = demographics_data['gender'].value_counts()
                if not gender_dist.empty:
                    fig = px.pie(
                        values=gender_dist.values, 
                        names=gender_dist.index, 
                        title=f"Gender Distribution (n={len(demographics_data):,})"
                    )
                    st.plotly_chart(fig, width='stretch')
                else:
                    st.info("No gender data available")
        
        with col2:
            if 'age_group' in demographics_data.columns:
                age_dist = demographics_data['age_group'].value_counts()
                if not age_dist.empty:
                    fig = px.bar(
                        x=age_dist.index, 
                        y=age_dist.values,
                        title=f"Age Group Distribution (n={len(demographics_data):,})"
                    )
                    fig.update_layout(
                        xaxis_title="Age Group",
                        yaxis_title="Count"
                    )
                    st.plotly_chart(fig, width='stretch')
                else:
                    st.info("No age group data available")
        
    else:
        st.warning("⚠️ No data found or connection failed")
        st.info("The dashboard is working but couldn't retrieve data from your backend API.")

if __name__ == "__main__":
    main()
