"""
Working dashboard with your actual column names
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from database import get_database
from streamlit_extras.stylable_container import stylable_container



# Page configuration
st.set_page_config(
    page_title="Surveys Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    st.title("📊Sebenza Surveys Dashboard")
    st.markdown("---")
    
    # Sidebar navigation
    st.sidebar.title("📊 Navigation")
    st.sidebar.markdown("---")
    
    # Add navigation buttons
    if st.sidebar.button("🏠 Home", key="home"):
        st.rerun()
    
    if st.sidebar.button("👥 Demographics", key="demographics"):
        st.info("👥 Demographics page - Use the main app.py for navigation between pages")
    
    if st.sidebar.button("📋 Survey Questions", key="survey_questions"):
        st.info("📋 Survey Questions page - Use the main app.py for navigation between pages")
    
    # Get data
    survey_ids, responses, analytics, score_dist = get_real_data()
    
    # Get database connection for additional queries
    db = get_database()
    
    if survey_ids and not responses.empty:
        # st.success(f"✅ Connected to Snowflake - Analyzing All Data from {len(survey_ids)} Surveys: {survey_ids}")
        
        # Debug: Show available survey questions
        if 'SURVEY_QUESTION' in responses.columns:
            available_questions = responses['SURVEY_QUESTION'].unique()
            # st.info(f"📋 Available Survey Questions ({len(available_questions)}): {', '.join(available_questions[:5])}{'...' if len(available_questions) > 5 else ''}")
        
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
        
        # Shop Visitation Analysis
        shop_question = "Which of these shops do you visit most often (Select all that apply)"
        shop_responses = responses[responses['SURVEY_QUESTION'] == shop_question]
        
        # Debug: Check for similar questions
        if shop_responses.empty and 'SURVEY_QUESTION' in responses.columns:
            similar_questions = [q for q in responses['SURVEY_QUESTION'].unique() if 'shop' in q.lower() or 'visit' in q.lower()]
            if similar_questions:
                st.info(f"🔍 No exact match for shop question. Similar questions found: {similar_questions}")
        
        if not shop_responses.empty:
            with stylable_container(
                key="shop_container",
                css_styles="""
                {
                    border: 1px solid rgba(49, 51, 63, 0.2);
                    border-radius: 0.5rem;
                    padding: calc(1em - 1px);
                    background-color: rgba(255, 255, 255, 0.05);
                }
                """,
            ):
                st.markdown("#### Shop Visitation Analysis")
                
                # Add filters for this section
                filtered_shop = create_section_filters("Shop Visits", shop_responses)
                
                # Process the responses - they might be comma-separated or individual responses
                all_shops = []
                for response in filtered_shop['RESPONSE']:
                    if pd.notna(response):
                        # Split by comma and clean up
                        shops = [shop.strip() for shop in str(response).split(',')]
                        all_shops.extend(shops)
                
                if all_shops:
                    # Count shop visits
                    shop_counts = pd.Series(all_shops).value_counts()
                    total_shop_responses = len(shop_responses)
                    
                    # Create two-column layout for chart and table
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Create a bar chart for shop visits
                        fig_shops = px.bar(
                            x=shop_counts.values,
                            y=shop_counts.index,
                            orientation='h',
                            title=f"Shop Visitation Frequency - Sample Size: {total_shop_responses:,}",
                            labels={'x': 'Number of Visits', 'y': 'Shop'}
                        )
                        fig_shops.update_layout(
                            height=400,
                            showlegend=False,
                            yaxis={'categoryorder': 'total ascending'}  # Rank high to low
                        )
                        st.plotly_chart(fig_shops, use_container_width=True)
                    
                    with col2:
                        # Show shop data table
                        shop_data = pd.DataFrame({
                            'Shop': shop_counts.index,
                            'Visits': shop_counts.values,
                            'Percentage': (shop_counts.values / shop_counts.sum() * 100).round(1)
                        })
                        
                        # Style the shop data table
                        styled_shop_df = shop_data.style.format({
                            'Visits': '{:,}',
                            'Percentage': '{:.1f}%'
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
                        
                        st.write(styled_shop_df.to_html(), unsafe_allow_html=True)
                else:
                    st.info("No shop data found in responses.")
        else:
            st.info(f"No responses found for the question: '{shop_question}'")
        
        # Travel Cost Analysis
        travel_question = "How much did you pay for this trip?"
        travel_responses = responses[responses['SURVEY_QUESTION'] == travel_question]
        
        # Debug: Check for similar questions
        if travel_responses.empty and 'SURVEY_QUESTION' in responses.columns:
            similar_questions = [q for q in responses['SURVEY_QUESTION'].unique() if 'trip' in q.lower() or 'pay' in q.lower() or 'cost' in q.lower()]
            if similar_questions:
                st.info(f"🔍 No exact match for trip cost question. Similar questions found: {similar_questions}")
        
        if not travel_responses.empty:
            with stylable_container(
                key="travel_container",
                css_styles="""
                {
                    border: 1px solid rgba(49, 51, 63, 0.2);
                    border-radius: 0.5rem;
                    padding: calc(1em - 1px);
                    background-color: rgba(255, 255, 255, 0.05);
                }
                """,
            ):
                st.markdown("#### Trip Cost Analysis")
                
                # Add filters for this section
                filtered_travel = create_section_filters("Trip Costs", travel_responses)
                
                # Process trip cost data using improved extraction logic
                trip_costs = []
                for response in filtered_travel['RESPONSE']:
                    if pd.notna(response):
                        import re
                        response_str = str(response).lower()
                        
                        # Handle ranges like "R61 to R70" - take midpoint
                        range_match = re.search(r'r?(\d+)\s*to\s*r?(\d+)', response_str)
                        if range_match:
                            min_val = float(range_match.group(1))
                            max_val = float(range_match.group(2))
                            cost = (min_val + max_val) / 2
                            trip_costs.append(cost)
                            continue
                        
                        # Handle "Less than R10" - use 5
                        less_than_match = re.search(r'less\s+than\s+r?(\d+)', response_str)
                        if less_than_match:
                            cost = float(less_than_match.group(1)) / 2
                            trip_costs.append(cost)
                            continue
                        
                        # Handle "More than R70" - use 75
                        more_than_match = re.search(r'more\s+than\s+r?(\d+)', response_str)
                        if more_than_match:
                            cost = float(more_than_match.group(1)) + 5
                            trip_costs.append(cost)
                            continue
                        
                        # Handle single numbers like "R50" or "50"
                        single_match = re.search(r'r?(\d+)', response_str)
                        if single_match:
                            cost = float(single_match.group(1))
                            if cost > 0:  # Only include positive amounts
                                trip_costs.append(cost)
                
                if trip_costs:
                    # Create trip cost DataFrame
                    trip_df = pd.DataFrame({'cost': trip_costs})
                    total_trip_responses = len(travel_responses)
                    
                    # Calculate statistics
                    avg_cost = trip_df['cost'].mean()
                    median_cost = trip_df['cost'].median()
                    min_cost = trip_df['cost'].min()
                    max_cost = trip_df['cost'].max()
                    
                    # Create two-column layout
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Cost distribution histogram with appropriate bins for R10-R70 range
                        fig_hist = px.histogram(
                            trip_df,
                            x='cost',
                            nbins=15,  # Fewer bins for better visualization of R10-R70 range
                            title=f"Trip Cost Distribution - Sample Size: {total_trip_responses:,}",
                            labels={'cost': 'Cost (R)', 'count': 'Number of Responses'},
                            color_discrete_sequence=['#FF6B6B']
                        )
                        fig_hist.update_layout(
                            height=400,
                            showlegend=False,
                            xaxis_title="Cost (R)",
                            yaxis_title="Number of Responses",
                            xaxis=dict(range=[0, 80])  # Focus on the relevant range
                        )
                        st.plotly_chart(fig_hist, use_container_width=True)
                    
                    with col2:
                        # Box plot for cost distribution
                        fig_box = px.box(
                            trip_df,
                            y='cost',
                            title=f"Trip Cost Distribution (Box Plot) - Sample Size: {total_trip_responses:,}",
                            labels={'cost': 'Cost (R)'},
                            color_discrete_sequence=['#4ECDC4']
                        )
                        fig_box.update_layout(
                            height=400,
                            showlegend=False,
                            yaxis_title="Cost (R)",
                            yaxis=dict(range=[0, 80])  # Focus on the relevant range
                        )
                        st.plotly_chart(fig_box, use_container_width=True)
                    
                    # Cost statistics cards
                    st.markdown("##### Trip Cost Statistics")
                    col3, col4, col5, col6 = st.columns(4)
                    
                    with col3:
                        st.metric("Average Cost",
                            content=f"R {avg_cost:,.2f}"
                        )
                    
                    with col4:
                        st.metric("Median Cost",
                            content=f"R {median_cost:,.2f}"
                        )
                    
                    with col5:
                        st.metric("Minimum Cost",
                            content=f"R {min_cost:,.2f}"
                        )
                    
                    with col6:
                        st.metric("Maximum Cost",
                            content=f"R {max_cost:,.2f}"
                        )
                    
                    # Cost range analysis
                    st.markdown("##### Cost Range Analysis")
                    
                    # Create cost ranges
                    cost_ranges = [
                        (0, 10, "Less than R10"),
                        (11, 20, "R11 to R20"),
                        (21, 30, "R21 to R30"),
                        (31, 40, "R31 to R40"),
                        (41, 50, "R41 to R50"),
                        (51, 60, "R51 to R60"),
                        (61, 70, "R61 to R70"),
                        (71, float('inf'), "More than R70")
                    ]
                    
                    range_counts = []
                    range_labels = []
                    
                    for min_val, max_val, label in cost_ranges:
                        if max_val == float('inf'):
                            count = len(trip_df[(trip_df['cost'] >= min_val)])
                        elif min_val == 0:  # Special case for "Less than R10"
                            count = len(trip_df[(trip_df['cost'] < max_val)])
                        else:
                            count = len(trip_df[(trip_df['cost'] >= min_val) & (trip_df['cost'] <= max_val)])
                        range_counts.append(count)
                        range_labels.append(label)
                    
                    # Create cost range bar chart
                    range_df = pd.DataFrame({
                        'Range': range_labels,
                        'Count': range_counts,
                        'Percentage': [(count / len(trip_df) * 100) for count in range_counts]
                    })
                    
                    fig_range = px.bar(
                        range_df,
                        x='Range',
                        y='Count',
                        title="Travel Cost Range Distribution",
                        color='Count',
                        color_continuous_scale='Viridis',
                        labels={'Count': 'Number of Responses', 'Range': 'Cost Range'}
                    )
                    fig_range.update_layout(
                        height=400,
                        showlegend=False,
                        xaxis_tickangle=-45
                    )
                    st.plotly_chart(fig_range, use_container_width=True)
                    
                    # Show detailed cost data table
                    st.markdown("##### Cost Range Breakdown")
                    styled_range_df = range_df.style.format({
                        'Count': '{:,}',
                        'Percentage': '{:.1f}%'
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
                    
                    st.write(styled_range_df.to_html(), unsafe_allow_html=True)
                    
                else:
                    st.info("No valid cost data found in responses.")
        else:
            st.info(f"No responses found for the question: '{travel_question}'")
        
        # Main Source of Money Analysis
        money_question = "What is your main source of money?"
        money_responses = responses[responses['SURVEY_QUESTION'] == money_question]
        
        # Debug: Check for similar questions
        if money_responses.empty and 'SURVEY_QUESTION' in responses.columns:
            similar_questions = [q for q in responses['SURVEY_QUESTION'].unique() if 'money' in q.lower() or 'source' in q.lower() or 'income' in q.lower()]
            if similar_questions:
                st.info(f"🔍 No exact match for money source question. Similar questions found: {similar_questions}")
        
        if not money_responses.empty:
            with stylable_container(
                key="money_source_container",
                css_styles="""
                {
                    border: 1px solid rgba(49, 51, 63, 0.2);
                    border-radius: 0.5rem;
                    padding: calc(1em - 1px);
                    background-color: rgba(255, 255, 255, 0.05);
                }
                """,
            ):
                st.markdown("#### Main Source of Money Analysis")
                
                # Add filters for this section
                filtered_money = create_section_filters("Money Source", money_responses)
                
                # Get money source distribution
                money_dist = filtered_money['RESPONSE'].value_counts()
                total_money_responses = len(filtered_money)
                
                # Create two-column layout
                col1, col2 = st.columns(2)
                
                with col1:
                    # Pie chart for money sources
                    fig_money_pie = px.pie(
                        values=money_dist.values,
                        names=money_dist.index,
                        title=f"Main Source of Money Distribution - Sample Size: {total_money_responses:,}",
                        color_discrete_sequence=[
                            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
                            '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'
                        ]
                    )
                    fig_money_pie.update_layout(
                        height=500,
                        showlegend=True,
                        legend=dict(
                            orientation="v",
                            yanchor="middle",
                            y=0.5,
                            xanchor="left",
                            x=1.01
                        )
                    )
                    st.plotly_chart(fig_money_pie, use_container_width=True)
                
                with col2:
                    # Horizontal bar chart for money sources
                    fig_money_bar = px.bar(
                        x=money_dist.values,
                        y=money_dist.index,
                        orientation='h',
                        title=f"Main Source of Money - Sample Size: {total_money_responses:,}",
                        labels={'x': 'Number of Responses', 'y': 'Money Source'},
                        color=money_dist.values,
                        color_continuous_scale='Viridis'
                    )
                    fig_money_bar.update_layout(
                        height=500,
                        showlegend=False,
                        yaxis={'categoryorder': 'total ascending'}
                    )
                    st.plotly_chart(fig_money_bar, use_container_width=True)
                
                # Money source data table and Side Hustles chart
                st.markdown("##### Money Source Breakdown")
                
                # Create two-column layout for table and side hustles chart
                col_table, col_side_hustles = st.columns([2, 1])
                
                with col_table:
                    money_df = pd.DataFrame({
                        'Money Source': money_dist.index,
                        'Count': money_dist.values,
                        'Percentage': (money_dist.values / total_money_responses * 100).round(2)
                    })
                    
                    styled_money_df = money_df.style.format({
                        'Count': '{:,}',
                        'Percentage': '{:.1f}%'
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
                    
                    st.write(styled_money_df.to_html(), unsafe_allow_html=True)
                
                with col_side_hustles:
                    # Side Hustles Analysis
                    st.markdown("##### Side Hustles Distribution")
                    
                    # Get side hustles data, filtering out NaN values
                    side_hustles_data = filtered_money['Side Hustles'].dropna()
                    side_hustles_count = len(side_hustles_data)
                    
                    if side_hustles_count > 0:
                        # Get side hustles distribution
                        side_hustles_dist = side_hustles_data.value_counts()
                        
                        # Create pie chart for side hustles
                        fig_side_hustles = px.pie(
                            values=side_hustles_dist.values,
                            names=side_hustles_dist.index,
                            title=f"Side Hustles - Sample Size: {side_hustles_count:,}",
                            color_discrete_sequence=[
                                '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
                                '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'
                            ]
                        )
                        fig_side_hustles.update_layout(
                            height=400,
                            showlegend=True,
                            legend=dict(
                                orientation="v",
                                yanchor="top",
                                y=1,
                                xanchor="left",
                                x=1.01
                            )
                        )
                        st.plotly_chart(fig_side_hustles, use_container_width=True)
                    else:
                        st.info("No side hustles data available (all values are NaN)")
        else:
            st.info(f"No responses found for the question: '{money_question}'")
        
        # Monthly Travel Cost Analysis
        try:
            # Get monthly spending per commuter - simplified approach
            # First get all trip cost data and process it in Python
            trip_cost_data = db.execute_query("""
                SELECT 
                    PROFILEUUID,
                    CREATED_DATE,
                    RESPONSE_X
                FROM SURVEYS_DB.RAW.NEW_DASBOARD_DATA1 
                WHERE SURVEY_QUESTION = 'How much did you pay for this trip?'
                AND RESPONSE_X IS NOT NULL
            """)
            
            if not trip_cost_data.empty:
                # Process costs in Python (more reliable than complex SQL)
                import re
                processed_costs = []
                
                for _, row in trip_cost_data.iterrows():
                    response_str = str(row['RESPONSE_X']).lower()
                    cost = None
                    
                    # Handle ranges like "R61 to R70" - take midpoint
                    range_match = re.search(r'r?(\d+)\s*to\s*r?(\d+)', response_str)
                    if range_match:
                        min_val = float(range_match.group(1))
                        max_val = float(range_match.group(2))
                        cost = (min_val + max_val) / 2
                    
                    # Handle "Less than R10" - use 5
                    elif re.search(r'less\s+than\s+r?(\d+)', response_str):
                        less_match = re.search(r'less\s+than\s+r?(\d+)', response_str)
                        cost = float(less_match.group(1)) / 2
                    
                    # Handle "More than R70" - use 75
                    elif re.search(r'more\s+than\s+r?(\d+)', response_str):
                        more_match = re.search(r'more\s+than\s+r?(\d+)', response_str)
                        cost = float(more_match.group(1)) + 5
                    
                    # Handle single numbers like "R50" or "50"
                    else:
                        single_match = re.search(r'r?(\d+)', response_str)
                        if single_match:
                            cost = float(single_match.group(1))
                    
                    if cost is not None and cost > 0:
                        processed_costs.append({
                            'PROFILEUUID': row['PROFILEUUID'],
                            'CREATED_DATE': row['CREATED_DATE'],
                            'cost': cost
                        })
                
                if processed_costs:
                    # Convert to DataFrame and process monthly data
                    costs_df = pd.DataFrame(processed_costs)
                    costs_df['CREATED_DATE'] = pd.to_datetime(costs_df['CREATED_DATE'])
                    costs_df['month'] = costs_df['CREATED_DATE'].dt.to_period('M')
                    
                    # Calculate monthly spending per commuter
                    monthly_spending = costs_df.groupby(['month', 'PROFILEUUID'])['cost'].sum().reset_index()
                    monthly_costs = monthly_spending.groupby('month').agg({
                        'PROFILEUUID': 'nunique',
                        'cost': ['mean', 'sum', 'count']
                    }).reset_index()
                    
                    # Flatten column names
                    monthly_costs.columns = ['MONTH', 'unique_commuters', 'avg_monthly_spending_per_commuter', 'total_monthly_spending', 'total_trips']
                    monthly_costs['MONTH'] = monthly_costs['MONTH'].astype(str)
                    
                    # Add month_name for display
                    monthly_costs['month_name'] = monthly_costs['MONTH']
                else:
                    monthly_costs = pd.DataFrame()
            else:
                monthly_costs = pd.DataFrame()
            
            # Calculate weekly costs using the same processed data
            if not trip_cost_data.empty and processed_costs:
                # Calculate weekly spending per commuter using week number instead of period
                costs_df['week_start'] = costs_df['CREATED_DATE'].dt.to_period('W').dt.start_time
                
                weekly_spending = costs_df.groupby(['week_start', 'PROFILEUUID'])['cost'].sum().reset_index()
                weekly_costs = weekly_spending.groupby('week_start').agg({
                    'PROFILEUUID': 'nunique',
                    'cost': ['mean', 'sum', 'count']
                }).reset_index()
                
                # Flatten column names
                weekly_costs.columns = ['WEEK', 'unique_commuters', 'avg_weekly_spending_per_commuter', 'total_weekly_spending', 'total_trips']
                weekly_costs['WEEK'] = weekly_costs['WEEK'].astype(str)
                weekly_costs['week_name'] = weekly_costs['WEEK']
            else:
                weekly_costs = pd.DataFrame()
            if not monthly_costs.empty or not weekly_costs.empty:
                with stylable_container(
                    key="monthly_travel_container",
                    css_styles="""
                    {
                        border: 1px solid rgba(49, 51, 63, 0.2);
                        border-radius: 0.5rem;
                        padding: calc(1em - 1px);
                        background-color: rgba(255, 255, 255, 0.05);
                    }
                    """,
                ):
                    st.markdown("#### Commuter Spending Analysis")
                    
                    # Add filters for this section
                    filtered_spending = create_section_filters("Commuter Spending", responses)
                    
                    # Debug: Show column names and sample data
                    if not monthly_costs.empty:
                        st.info(f"Monthly costs columns: {list(monthly_costs.columns)}")
                        st.info(f"Monthly costs sample data:\n{monthly_costs.head()}")
                        st.info(f"Monthly spending range: R{monthly_costs['avg_monthly_spending_per_commuter'].min():.2f} - R{monthly_costs['avg_monthly_spending_per_commuter'].max():.2f}")
                    if not weekly_costs.empty:
                        st.info(f"Weekly costs columns: {list(weekly_costs.columns)}")
                        st.info(f"Weekly costs sample data:\n{weekly_costs.head()}")
                        st.info(f"Weekly spending range: R{weekly_costs['avg_weekly_spending_per_commuter'].min():.2f} - R{weekly_costs['avg_weekly_spending_per_commuter'].max():.2f}")
                    
                    # Debug: Show processed trip cost data
                    st.markdown("##### 🔍 Debug: Processed Trip Cost Data")
                    if processed_costs:
                        processed_df = pd.DataFrame(processed_costs)
                        st.dataframe(processed_df.head(20))
                        st.info(f"Processed costs range: R{processed_df['cost'].min():.2f} - R{processed_df['cost'].max():.2f}")
                        st.info(f"Average processed cost: R{processed_df['cost'].mean():.2f}")
                        st.info(f"Median processed cost: R{processed_df['cost'].median():.2f}")
                        st.info(f"Total processed costs: {len(processed_costs)}")
                    else:
                        st.info("No costs were successfully processed from the responses")
                    
                    # Data is already processed above
                    
                    # Create tabs for monthly and weekly analysis
                    tab1, tab2 = st.tabs(["📅 Monthly Analysis", "📊 Weekly Analysis"])
                    
                    with tab1:
                        if not monthly_costs.empty:
                            # Create two-column layout for monthly
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                # Monthly average spending per commuter
                                fig_monthly = px.line(
                                    monthly_costs,
                                    x='month_name',
                                    y='avg_monthly_spending_per_commuter',
                                    title="Average Monthly Spending per Commuter",
                                    labels={'avg_monthly_spending_per_commuter': 'Average Spending (R)', 'month_name': 'Month'},
                                    markers=True
                                )
                                fig_monthly.update_layout(
                                    height=400,
                                    xaxis_tickangle=-45,
                                    showlegend=False
                                )
                                st.plotly_chart(fig_monthly, use_container_width=True)
                            
                            with col2:
                                # Monthly commuter count
                                fig_commuters = px.bar(
                                    monthly_costs,
                                    x='month_name',
                                    y='unique_commuters',
                                    title="Number of Active Commuters",
                                    labels={'unique_commuters': 'Number of Commuters', 'month_name': 'Month'},
                                    color='unique_commuters',
                                    color_continuous_scale='Viridis'
                                )
                                fig_commuters.update_layout(
                                    height=400,
                                    xaxis_tickangle=-45,
                                    showlegend=False
                                )
                                st.plotly_chart(fig_commuters, use_container_width=True)
                        else:
                            st.info("No monthly data available.")
                    
                    with tab2:
                        if not weekly_costs.empty:
                            # Create two-column layout for weekly
                            col3, col4 = st.columns(2)
                            
                            with col3:
                                # Weekly average spending per commuter
                                fig_weekly = px.line(
                                    weekly_costs,
                                    x='week_name',
                                    y='avg_weekly_spending_per_commuter',
                                    title="Average Weekly Spending per Commuter",
                                    labels={'avg_weekly_spending_per_commuter': 'Average Spending (R)', 'week_name': 'Week'},
                                    markers=True
                                )
                                fig_weekly.update_layout(
                                    height=400,
                                    xaxis_tickangle=-45,
                                    showlegend=False
                                )
                                st.plotly_chart(fig_weekly, use_container_width=True)
                            
                            with col4:
                                # Weekly commuter count
                                fig_weekly_commuters = px.bar(
                                    weekly_costs,
                                    x='week_name',
                                    y='unique_commuters',
                                    title="Number of Active Commuters (Weekly)",
                                    labels={'unique_commuters': 'Number of Commuters', 'week_name': 'Week'},
                                    color='unique_commuters',
                                    color_continuous_scale='Viridis'
                                )
                                fig_weekly_commuters.update_layout(
                                    height=400,
                                    xaxis_tickangle=-45,
                                    showlegend=False
                                )
                                st.plotly_chart(fig_weekly_commuters, use_container_width=True)
                        else:
                            st.info("No weekly data available.")
                    
                    # Statistics section
                    st.markdown("##### Commuter Spending Statistics")
                    col5, col6, col7, col8 = st.columns(4)
                    
                    if not monthly_costs.empty:
                        with col5:
                            st.metric(
                                title="Highest Monthly Avg per Commuter",
                                content=f"R {monthly_costs['avg_monthly_spending_per_commuter'].max():,.2f}"
                            )
                        
                        with col6:
                            st.metric(
                                title="Lowest Monthly Avg per Commuter",
                                content=f"R {monthly_costs['avg_monthly_spending_per_commuter'].min():,.2f}"
                            )
                        
                        with col7:
                            st.metric(
                                title="Overall Monthly Avg per Commuter",
                                content=f"R {monthly_costs['avg_monthly_spending_per_commuter'].mean():,.2f}"
                            )
                        
                        with col8:
                            st.metric(
                                title="Total Months",
                                content=f"{len(monthly_costs)}"
                            )
                    
                    if not weekly_costs.empty:
                        st.markdown("##### Weekly Statistics")
                        col9, col10, col11, col12 = st.columns(4)
                        
                        with col9:
                            st.metric(
                                title="Highest Weekly Avg per Commuter",
                                content=f"R {weekly_costs['avg_weekly_spending_per_commuter'].max():,.2f}"
                            )
                        
                        with col10:
                            st.metric(
                                title="Lowest Weekly Avg per Commuter",
                                content=f"R {weekly_costs['avg_weekly_spending_per_commuter'].min():,.2f}"
                            )
                        
                        with col11:
                            st.metric(
                                title="Overall Weekly Avg per Commuter",
                                content=f"R {weekly_costs['avg_weekly_spending_per_commuter'].mean():,.2f}"
                            )
                        
                        with col12:
                            st.metric(
                                title="Total Weeks",
                                content=f"{len(weekly_costs)}"
                            )
                    
                    # Data tables
                    if not monthly_costs.empty:
                        st.markdown("##### Monthly Breakdown")
                        monthly_display = monthly_costs[['month_name', 'unique_commuters', 'avg_monthly_spending_per_commuter', 'total_monthly_spending', 'total_trips']].copy()
                        monthly_display.columns = ['Month', 'Active Commuters', 'Avg Spending per Commuter (R)', 'Total Monthly Spending (R)', 'Total Trips']
                        monthly_display['Avg Spending per Commuter (R)'] = monthly_display['Avg Spending per Commuter (R)'].round(2)
                        monthly_display['Total Monthly Spending (R)'] = monthly_display['Total Monthly Spending (R)'].round(2)
                    
                        styled_monthly_df = monthly_display.style.format({
                            'Active Commuters': '{:,}',
                            'Avg Spending per Commuter (R)': 'R {:.2f}',
                            'Total Monthly Spending (R)': 'R {:.2f}',
                            'Total Trips': '{:,}'
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
                        
                        st.write(styled_monthly_df.to_html(), unsafe_allow_html=True)
                    
                    if not weekly_costs.empty:
                        st.markdown("##### Weekly Breakdown")
                        weekly_display = weekly_costs[['week_name', 'unique_commuters', 'avg_weekly_spending_per_commuter', 'total_weekly_spending', 'total_trips']].copy()
                        weekly_display.columns = ['Week', 'Active Commuters', 'Avg Spending per Commuter (R)', 'Total Weekly Spending (R)', 'Total Trips']
                        weekly_display['Avg Spending per Commuter (R)'] = weekly_display['Avg Spending per Commuter (R)'].round(2)
                        weekly_display['Total Weekly Spending (R)'] = weekly_display['Total Weekly Spending (R)'].round(2)
                        
                        styled_weekly_df = weekly_display.style.format({
                            'Active Commuters': '{:,}',
                            'Avg Spending per Commuter (R)': 'R {:.2f}',
                            'Total Weekly Spending (R)': 'R {:.2f}',
                            'Total Trips': '{:,}'
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
                        
                        st.write(styled_weekly_df.to_html(), unsafe_allow_html=True)
            else:
                st.info("No monthly travel cost data available.")
                
                # Debug: Check if we have any trip cost data at all
                st.markdown("##### 🔍 Debug: Checking for Trip Cost Data")
                debug_query = db.execute_query("""
                    SELECT 
                        COUNT(*) as total_responses,
                        COUNT(DISTINCT PROFILEUUID) as unique_respondents,
                        COUNT(CASE WHEN RESPONSE_X IS NOT NULL THEN 1 END) as non_null_responses
                    FROM SURVEYS_DB.RAW.NEW_DASBOARD_DATA1 
                    WHERE SURVEY_QUESTION = 'How much did you pay for this trip?'
                """)
                
                if not debug_query.empty:
                    st.info(f"Total trip cost responses: {debug_query.iloc[0]['TOTAL_RESPONSES']}")
                    st.info(f"Unique respondents: {debug_query.iloc[0]['UNIQUE_RESPONDENTS']}")
                    st.info(f"Non-null responses: {debug_query.iloc[0]['NON_NULL_RESPONSES']}")
                
                # Check sample responses
                sample_responses = db.execute_query("""
                    SELECT RESPONSE_X, CREATED_DATE
                    FROM SURVEYS_DB.RAW.NEW_DASBOARD_DATA1 
                    WHERE SURVEY_QUESTION = 'How much did you pay for this trip?'
                    AND RESPONSE_X IS NOT NULL
                    LIMIT 10
                """)
                
                if not sample_responses.empty:
                    st.info("Sample responses:")
                    st.dataframe(sample_responses)
                else:
                    st.info("No trip cost responses found in database")
                    
        except Exception as e:
            st.error(f"Monthly travel cost analysis error: {str(e)}")
            import traceback
            st.error(f"Full error details: {traceback.format_exc()}")
        
        # Export data
        st.markdown("#### 📥 Export Data")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Export Responses (CSV)"):
                csv = responses.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"all_surveys_responses.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("Export Analytics (JSON)"):
                json_data = analytics.to_json(orient='records')
                st.download_button(
                    label="Download JSON",
                    data=json_data,
                    file_name=f"all_surveys_analytics.json",
                    mime="application/json"
                )
        
    else:
        st.warning("⚠️ No data found or connection failed")
        st.info("The dashboard is working but couldn't retrieve data from your Snowflake table.")

if __name__ == "__main__":
    main()
