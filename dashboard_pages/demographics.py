"""
Demographics Dashboard Page
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from database import get_database
from streamlit_extras.stylable_container import stylable_container

# No need for CSS to hide pages since they're moved out of the pages/ directory

def get_real_data():
    """Get real data from your Snowflake table"""
    db = get_database()
    if not db:
        return None, None, None, None
    
    try:
        # Get all survey data (no survey ID filter)
        responses = db.execute_query("""
            SELECT 
                SURVEY_ID,
                SURVEY_TITLE,
                SURVEY_QUESTION,
                RESPONSE_X as RESPONSE,
                SEM_SCORE,
                GENDER,
                AGE_GROUP as AGEGROUP,
                EMPLOYMENT as "Emloyment Status",
                LOCATION,
                "salary per month",
                SEM_SEGMENT,
                "Side Hustles",
                CREATED_DATE as CREATED_AT
            FROM SURVEYS_DB.RAW.NEW_DASBOARD_DATA1
            WHERE SURVEY_ID IS NOT NULL
        """)
        
        if responses.empty:
            return None, None, None, None
        
        # Get available survey IDs for display
        surveys = db.execute_query("SELECT DISTINCT SURVEY_ID FROM SURVEYS_DB.RAW.NEW_DASBOARD_DATA1 WHERE SURVEY_ID IS NOT NULL ORDER BY SURVEY_ID")
        survey_ids = surveys['SURVEY_ID'].tolist()
        
        # Get basic analytics for all data
        analytics = db.execute_query("""
            SELECT 
                COUNT(*) as total_responses,
                COUNT(DISTINCT PROFILEUUID) as unique_respondents,
                AVG(SEM_SCORE) as avg_sem_score,
                MIN(SEM_SCORE) as min_sem_score,
                MAX(SEM_SCORE) as max_sem_score
            FROM SURVEYS_DB.RAW.NEW_DASBOARD_DATA1
            WHERE SURVEY_ID IS NOT NULL
        """)
        
        # Get SEM score distribution for all data
        score_dist = db.execute_query("""
            SELECT 
                SEM_SCORE,
                COUNT(*) as count
            FROM SURVEYS_DB.RAW.NEW_DASBOARD_DATA1
            WHERE SURVEY_ID IS NOT NULL AND SEM_SCORE IS NOT NULL
            GROUP BY SEM_SCORE
            ORDER BY SEM_SCORE
        """)
        
        return survey_ids, responses, analytics, score_dist
        
    except Exception as e:
        st.error(f"Error getting data: {str(e)}")
        return None, None, None, None

def main():
    st.title("📊 Demographics Dashboard")
    st.markdown("---")
    
    # Only show sidebar navigation if not called from main app
    if 'current_page' not in st.session_state:
        # Sidebar navigation
        st.sidebar.title("📊 Navigation")
        st.sidebar.markdown("---")
        
        # Add navigation buttons
        if st.sidebar.button("🏠 Home", key="home_demo"):
            st.switch_page("app.py")
        
        if st.sidebar.button("👥 Demographics", key="demographics_demo"):
            st.rerun()
        
        if st.sidebar.button("📋 Survey Questions", key="survey_questions_demo"):
            st.switch_page("dashboard_pages/survey_questions.py")
    
    # Get data
    survey_ids, responses, analytics, score_dist = get_real_data()
    
    if survey_ids and not responses.empty:
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
                    if 'AGEGROUP' in data.columns:
                        age_options = ['All'] + sorted([age for age in data['AGEGROUP'].unique() if pd.notna(age)])
                        selected_age = st.selectbox("Age Group", age_options, key=f"age_{section_name}")
                    else:
                        selected_age = 'All'
                col_index += 1
            else:
                selected_age = 'All'
            
            # Gender filter
            if include_gender:
                with available_cols[col_index]:
                    if 'GENDER' in data.columns:
                        gender_options = ['All'] + sorted([gender for gender in data['GENDER'].unique() if pd.notna(gender)])
                        selected_gender = st.selectbox("Gender", gender_options, key=f"gender_{section_name}")
                    else:
                        selected_gender = 'All'
                col_index += 1
            else:
                selected_gender = 'All'
            
            # SEM filter as checkboxes
            with available_cols[col_index]:
                if 'SEM_SEGMENT' in data.columns:
                    sem_options = sorted([sem for sem in data['SEM_SEGMENT'].unique() if pd.notna(sem)])
                    selected_sems = st.multiselect("SEM Segments", sem_options, default=[], key=f"sem_{section_name}")
                else:
                    selected_sems = []
            
            # Apply filters
            filtered_data = data.copy()
            
            if include_age and selected_age != 'All':
                filtered_data = filtered_data[filtered_data['AGEGROUP'] == selected_age]
            
            if include_gender and selected_gender != 'All':
                filtered_data = filtered_data[filtered_data['GENDER'] == selected_gender]
            
            if selected_sems:  # Only filter if at least one SEM segment is selected
                filtered_data = filtered_data[filtered_data['SEM_SEGMENT'].isin(selected_sems)]
            
            # Show filter summary
            total_original = len(data)
            total_filtered = len(filtered_data)
            
            if total_filtered < total_original:
                st.info(f"📊 Showing {total_filtered:,} of {total_original:,} responses")
            
            return filtered_data
        
        # Key metrics
        st.markdown("### 📊 Key Metrics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_responses = len(responses)
            st.metric("Total Responses", f"{total_responses:,}")
        
        with col2:
            unique_respondents = responses['PROFILEUUID'].nunique() if 'PROFILEUUID' in responses.columns else total_responses
            st.metric("Unique Responses", f"{unique_respondents:,}")
        
        with col3:
            if not analytics.empty:
                avg_score = analytics.iloc[0, 2]  # avg_sem_score column
                st.metric("Average SEM Score", f"{avg_score:.1f}")
            else:
                st.metric("Average SEM Score", "NA")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            if 'GENDER' in responses.columns:
                with stylable_container(
                    key="gender_container",
                    css_styles="""
                    {
                        border: 1px solid rgba(49, 51, 63, 0.2);
                        border-radius: 0.5rem;
                        padding: calc(1em - 1px);
                        background-color: rgba(255, 255, 255, 0.05);
                    }
                    """,
                ):
                    st.markdown("#### Gender Distribution")
                    
                    # Add filters for this section (exclude gender filter since this IS the gender chart)
                    filtered_gender = create_section_filters("Gender", responses, include_gender=False, include_age=True)
                    
                    gender_dist = filtered_gender['GENDER'].value_counts()
                    total_gender_responses = gender_dist.sum()
                    fig = px.pie(
                        values=gender_dist.values, 
                        names=gender_dist.index, 
                        title=f"Gender Distribution - Sample Size: {total_gender_responses:,}"
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'AGEGROUP' in responses.columns:
                with stylable_container(
                    key="age_container",
                    css_styles="""
                    {
                        border: 1px solid rgba(49, 51, 63, 0.2);
                        border-radius: 0.5rem;
                        padding: calc(1em - 1px);
                        background-color: rgba(255, 255, 255, 0.05);
                    }
                    """,
                ):
                    st.markdown("#### Age Group Distribution")
                    
                    # Add filters for this section (exclude age filter since this IS the age chart)
                    filtered_age = create_section_filters("Age", responses, include_gender=True, include_age=False)
                    
                    age_dist = filtered_age['AGEGROUP'].value_counts()
                    total_age_responses = age_dist.sum()
                    fig = px.bar(
                        x=age_dist.index, 
                        y=age_dist.values, 
                        title=f"Age Group Distribution - Sample Size: {total_age_responses:,}"
                    )
                    fig.update_layout(
                        xaxis_title="",
                        yaxis_title=""
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        # Employment Status and Location Analysis
        col3, col4 = st.columns(2)
        
        with col3:
            if 'Emloyment Status' in responses.columns:
                with stylable_container(
                    key="employment_container",
                    css_styles="""
                    {
                        border: 1px solid rgba(49, 51, 63, 0.2);
                        border-radius: 0.5rem;
                        padding: calc(1em - 1px);
                        background-color: rgba(255, 255, 255, 0.05);
                    }
                    """,
                ):
                    st.markdown("#### Employment Status")
                    
                    # Add filters for this section
                    filtered_employment = create_section_filters("Employment", responses)
                    
                    emp_dist = filtered_employment['Emloyment Status'].value_counts()
                    total_emp_responses = emp_dist.sum()
                    fig = px.pie(
                        values=emp_dist.values, 
                        names=emp_dist.index, 
                        title=f"Employment Status Distribution - Sample Size: {total_emp_responses:,}",
                        color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9']
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        with col4:
            # Location Analysis
            if 'LOCATION' in responses.columns:
                with stylable_container(
                    key="location_container",
                    css_styles="""
                    {
                        border: 1px solid rgba(49, 51, 63, 0.2);
                        border-radius: 0.5rem;
                        padding: calc(1em - 1px);
                        background-color: rgba(255, 255, 255, 0.05);
                    }
                    """,
                ):
                    st.markdown("#### Location Distribution")
                    
                    # Add filters for this section
                    filtered_location = create_section_filters("Location", responses)
                    
                    loc_dist = filtered_location['LOCATION'].value_counts()
                    
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
                        st.plotly_chart(fig_bar, use_container_width=True)
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
                        st.plotly_chart(fig, use_container_width=True)
        
        # SEM Groups Analysis
        if 'SEM_SEGMENT' in responses.columns:
            with stylable_container(
                key="sem_container",
                css_styles="""
                {
                    border: 1px solid rgba(49, 51, 63, 0.2);
                    border-radius: 0.5rem;
                    padding: calc(1em - 1px);
                    background-color: rgba(255, 255, 255, 0.05);
                }
                """,
            ):
                st.markdown("#### SEM Groups Distribution")
                
                # Add filters for this section
                filtered_sem = create_section_filters("SEM Groups", responses)
                
                sem_groups = filtered_sem['SEM_SEGMENT'].value_counts()
                
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
                    st.plotly_chart(fig_pie, use_container_width=True)
                
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
                    st.plotly_chart(fig_bar, use_container_width=True)
                
                # Show detailed breakdown with better styling
                st.markdown("##### SEM Groups Breakdown")
                sem_breakdown = pd.DataFrame({
                    'SEM Group': sem_groups.index,
                    'Count': sem_groups.values,
                    'Percentage': (sem_groups.values / sem_groups.sum() * 100).round(2)
                })
                
                # Add percentage column with % symbol
                sem_breakdown['Percentage'] = sem_breakdown['Percentage'].astype(str) + '%'
                
                # Style the dataframe
                styled_df = sem_breakdown.style.format({
                    'Count': '{:,}',  # Add commas to numbers
                }).set_properties(**{
                    'text-align': 'center',
                    'font-size': '14px',
                    'padding': '10px'
                }).set_table_styles([
                    {
                        'selector': 'thead th',
                        'props': [
                            ('background-color', '#667eea'),
                            ('color', 'white'),
                            ('font-weight', 'bold'),
                            ('text-align', 'center'),
                            ('padding', '12px'),
                            ('border', '1px solid #ddd')
                        ]
                    },
                    {
                        'selector': 'tbody tr:nth-child(even)',
                        'props': [('background-color', '#f8f9fa')]
                    },
                    {
                        'selector': 'tbody tr:hover',
                        'props': [('background-color', '#e3f2fd')]
                    },
                    {
                        'selector': 'td',
                        'props': [
                            ('border', '1px solid #ddd'),
                            ('padding', '8px')
                        ]
                    }
                ])
                
                st.write(styled_df.to_html(), unsafe_allow_html=True)
        
    else:
        st.warning("⚠️ No data found or connection failed")
        st.info("The dashboard is working but couldn't retrieve data from your Snowflake table.")

if __name__ == "__main__":
    main()
