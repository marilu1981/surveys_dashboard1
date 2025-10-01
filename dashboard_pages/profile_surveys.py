"""
Profile Surveys Dashboard Page
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend_client import get_backend_client
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode, GridUpdateMode
from chart_utils import create_altair_chart

# Add the styles directory to the path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'styles'))
from card_style import apply_card_styles

# No need for CSS to hide pages since they're moved out of the pages/ directory

@st.cache_data(ttl=600, show_spinner=True)  # Cache for 10 minutes
def get_real_data():
    """Get real data from Parquet file or API fallback - optimized for performance"""
    client = get_backend_client()
    if not client:
        st.warning("Backend connection not available - using sample data")
        return None, None, None, None

    try:
        # Start with efficient data loading strategy
        with st.spinner("Loading profile survey data..."):
            responses = pd.DataFrame()
            
            # Strategy 1: Try Parquet first for optimal performance
            # Use the survey that we know works with Parquet
            # Since we've seen SB055_Profile_Survey1 working with Parquet, use it directly
            primary_survey = "SB055_Profile_Survey1"
            
            try:
                # Try main API first with higher limit for Parquet efficiency
                responses = client.get_responses_parquet(
                    survey=primary_survey, 
                    limit=10000  # Parquet can handle larger datasets efficiently
                )
                
                # If main API fails, try individual survey endpoint
                if responses.empty:
                    responses = client.get_responses_parquet_direct(
                        survey=primary_survey, 
                        limit=10000  # Parquet allows for larger samples
                    )
            except Exception as e:
                pass  # Silently try fallback
            
            # Strategy 2: Fallback to JSON API if Parquet fails
            if responses.empty:
                try:
                    responses = client.get_responses(
                        survey=primary_survey, 
                        limit=10000,  # Higher limit since Parquet should handle this better
                        format="json"
                    )
                except Exception as e:
                    pass  # Silently try next fallback
                
                # Strategy 3: Last fallback to individual survey endpoint
                if responses.empty:
                    try:
                        responses = client.get_individual_survey(
                            primary_survey, 
                            limit=10000, 
                            format="json"
                        )
                    except Exception as e:
                        pass  # Final fallback failed
        
        if responses.empty:
            st.warning("Unable to retrieve profile survey responses from the backend")
            return None, None, None, None

        # Efficient column mapping without duplicate checks
        column_mapping = {
            "q": "SURVEY_QUESTION",
            "resp": "RESPONSE", 
            "pid": "PROFILE_ID"
        }
        
        for old_col, new_col in column_mapping.items():
            if old_col in responses.columns and new_col not in responses.columns:
                responses[new_col] = responses[old_col]

        # Optimize datetime conversion
        if "ts" in responses.columns:
            responses["ts"] = pd.to_datetime(responses["ts"], errors="coerce")
            if "SURVEY_DATE" not in responses.columns:
                responses["SURVEY_DATE"] = responses["ts"].dt.date

        # Create questions DataFrame efficiently
        if "SURVEY_QUESTION" in responses.columns:
            unique_questions = responses["SURVEY_QUESTION"].dropna().unique()
        elif "q" in responses.columns:
            unique_questions = responses["q"].dropna().unique() 
        else:
            unique_questions = []
            
        questions_df = pd.DataFrame({"question": unique_questions})
        
        # Get available profile surveys dynamically
        survey_ids = []
        try:
            # Get all available surveys and filter for profile surveys
            survey_summary = client.get_survey_summary()
            if isinstance(survey_summary, dict) and 'surveys' in survey_summary:
                for survey_info in survey_summary['surveys']:
                    if isinstance(survey_info, dict):
                        title = survey_info.get('survey_title', '')
                        if 'profile' in title.lower() or 'SB055' in title:
                            survey_ids.append(title)
            
            # Fallback to hardcoded if no surveys found
            if not survey_ids:
                survey_ids = ["SB055_Profile_Survey1"]
                
        except Exception as e:
            st.warning(f"Could not fetch survey list, using default: {str(e)[:50]}...")
            survey_ids = ["SB055_Profile_Survey1"]

        return survey_ids, questions_df, questions_df, responses

    except Exception as exc:
        st.error(f"Error getting data from backend: {exc}")
        return None, None, None, None

def main():
    st.set_page_config(page_title="", page_icon=":bar_chart:", layout="wide")

    st.title("Profile Surveys Dashboard")
    st.markdown("--------------------------------")
    
    # Apply card styles
    apply_card_styles()
    
    # Only show sidebar navigation if not called from main app
    if 'current_page' not in st.session_state:
        # Sidebar navigation
        st.sidebar.title("Navigation")
        st.sidebar.markdown("---")
        
        # Add navigation buttons
        if st.sidebar.button("🏠 Home", key="home_survey"):
            st.switch_page("app.py")
        
        if st.sidebar.button("Demographics", key="demographics_survey"):
            st.switch_page("dashboard_pages/demographics.py")
        
        if st.sidebar.button("Survey Questions", key="survey_questions_survey"):
            st.rerun()
    
    # Initialize session state for data persistence
    if 'profile_survey_data' not in st.session_state:
        st.session_state.profile_survey_data = None
        st.session_state.profile_survey_loaded = False
    
    # Get data (cached and persistent)
    if not st.session_state.profile_survey_loaded:
        with st.spinner("Loading profile survey data..."):
            survey_ids, shop_questions, range_questions, responses = get_real_data()
            st.session_state.profile_survey_data = {
                'survey_ids': survey_ids,
                'shop_questions': shop_questions, 
                'range_questions': range_questions,
                'responses': responses
            }
            st.session_state.profile_survey_loaded = True
    else:
        # Use cached data
        data = st.session_state.profile_survey_data
        survey_ids = data['survey_ids']
        shop_questions = data['shop_questions']
        range_questions = data['range_questions'] 
        responses = data['responses']
    
    if survey_ids and responses is not None and not responses.empty:
        # Show data summary and controls
        col1, col2 = st.columns([3, 1])
        with col1:
            # Show data summary without status messages
            st.write(f"**Dataset:** {len(responses):,} responses loaded")
        
        with col2:
            if st.button("🔄 Refresh", help="Clear all caches and reload with new Parquet method"):
                # Clear all cached data and methods
                st.session_state.profile_survey_loaded = False
                st.session_state.profile_survey_data = None
                get_real_data.clear()  # Clear Streamlit cache
                
                # Clear backend client method caches
                client = get_backend_client()
                if client and hasattr(client, 'get_responses_parquet'):
                    try:
                        client.get_responses_parquet.clear()
                    except:
                        pass
                
                st.success("All caches cleared! Using updated Parquet method...")
                st.rerun()
        
        # Date Range Filter
        st.markdown("### 📅 Date Range Filter (NOTE: for shops visited, Usave was only added on 02 Sept 2025)")
        
        # Convert ts column to datetime if it exists
        if 'ts' in responses.columns:
            responses['ts'] = pd.to_datetime(responses['ts'], errors='coerce')
            valid_dates = responses['ts'].dropna()
            
            if not valid_dates.empty:
                min_date = valid_dates.min().date()
                max_date = valid_dates.max().date()
                
                # Create date slider
                date_range = st.date_input(
                    "Select date range",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date,
                    key="date_range_filter_survey"
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
                    
                    # st.info(f"📊 Showing data from {start_date} to {end_date} ({len(responses):,} responses)")
                else:
                    st.info("📊 Please select both start and end dates")
            else:
                st.warning("⚠️ No valid date data found in responses")
        else:
            st.warning("⚠️ No timestamp column found in responses")
        # st.success(f"✅ Connected to Snowflake - Analyzing All Data from {len(survey_ids)} Surveys: {survey_ids}")
        
        # # Debug: Show data summary
        # st.markdown("###  Data Debug Information")
        # with st.container(horizontal=True):
        #     cols = st.columns(3, gap="small", width=300)

        # with cols[0]:
        #     st.metric("Total Responses", f"{len(responses):,}")
        
        # with cols[1]:
        #     if 'ts' in responses.columns:
        #         valid_dates = pd.to_datetime(responses['ts'], errors='coerce').dropna()
        #         st.metric("Valid Timestamps", f"{len(valid_dates):,}")
        #     else:
        #         st.metric("Valid Timestamps", "0")
        
        # with cols[2]:
        #     if 'q' in responses.columns:
        #         unique_questions = responses['q'].dropna().nunique()
        #         st.metric("Unique Questions", f"{unique_questions:,}")
        #     else:
        #         st.metric("Unique Questions", "0")
        
        # # Show column information
        # st.markdown("#### 📊 Data Columns")
        # st.write(f"**Available columns:** {list(responses.columns)}")
        
        # # Show sample data
        # st.markdown("#### 📋 Sample Data (First 5 rows)")
        # st.dataframe(responses.head(), use_container_width=True)
        
        # Debug: Show available survey questions (commented out for cleaner display)
        # st.write(f"**Available columns:** {list(responses.columns)}")
        
        if 'SURVEY_QUESTION' in responses.columns:
            available_questions = responses['SURVEY_QUESTION'].unique()
            # st.info(f"📋 Available Survey Questions ({len(available_questions)}): {', '.join(available_questions[:5])}{'...' if len(available_questions) > 5 else ''}")
        elif 'q' in responses.columns:
            available_questions = responses['q'].unique()
            # st.info(f"📋 Available Questions via 'q' column ({len(available_questions)}): {', '.join(available_questions[:5])}{'...' if len(available_questions) > 5 else ''}")
        
        # Helper function to create filters for a specific section
        def create_section_filters(section_name, data, include_gender=True, include_age=True):
            st.markdown(f"#### {section_name} Filters")
            
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
                st.info(f"Showing {total_filtered:,} of {total_original:,} responses")
            
            return filtered_data
        
        # Shop Visitation Analysis
        shop_question = "Which of these shops do you visit most often (Select all that apply)"
        shop_responses = responses[responses['q'] == shop_question]
        
        # Debug: Show shop analysis data
        # st.markdown("#### Shop Visitation Analysis Debug")
        st.write(f"**Question:** '{shop_question}'")
        # st.write(f"**Found responses:** {len(shop_responses)}")
        
        if 'q' in responses.columns:
            all_questions = responses['q'].unique()
            # st.write(f"**All available questions:** {list(all_questions)}")
        
        # Debug: Check for similar questions
        if shop_responses.empty and 'q' in responses.columns:
            similar_questions = [q for q in responses['q'].unique() if 'shop' in q.lower() or 'visit' in q.lower()]
            if similar_questions:
                st.info(f"No exact match for shop question. Similar questions found: {similar_questions}")
        
        if not shop_responses.empty:
            with st.container():
                # st.markdown("#### Shop Visitation Analysis")
                
                # Add filters for this section
                filtered_shop = create_section_filters("Shop Visits", shop_responses)
                
                # Process the responses - they might be comma-separated or individual responses
                all_shops = []
                for response in filtered_shop['resp']:
                    if pd.notna(response):
                        # Split by comma and clean up
                        shops = [shop.strip() for shop in str(response).split(',')]
                        all_shops.extend(shops)
                
                if all_shops:
                    # Count shop visits (unique respondents per shop)
                    if 'pid' in shop_responses.columns:
                        # Create a mapping of shop to PIDs for unique counting
                        shop_pid_data = []
                        for idx, row in shop_responses.iterrows():
                            shops = [s.strip() for s in str(row.get('resp', '')).split(',') if s.strip()]
                            for shop in shops:
                                shop_pid_data.append({'shop': shop, 'pid': row.get('pid')})
                        
                        if shop_pid_data:
                            shop_df = pd.DataFrame(shop_pid_data)
                            shop_counts = shop_df.groupby('shop')['pid'].nunique().sort_values(ascending=False)
                            total_shop_responses = shop_responses['pid'].nunique()
                            st.caption("📊 Counting unique respondents per shop to avoid double-counting")
                        else:
                            shop_counts = pd.Series(all_shops).value_counts()
                            total_shop_responses = len(shop_responses)
                    else:
                        shop_counts = pd.Series(all_shops).value_counts()
                        total_shop_responses = len(shop_responses)
                        st.caption("⚠️ Using response count (PID not available for unique counting)")
                    
                    # Create two-column layout for chart and table
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Create a bar chart for shop visits
                        fig_shops = px.bar(
                            x=shop_counts.values,
                            y=shop_counts.index,
                            orientation='h',
                            title=f"Shop Visitation by Unique Visitors - Sample Size: {total_shop_responses:,}",
                            labels={'x': 'Unique Visitors (PIDs)', 'y': 'Shop'}
                        )
                        fig_shops.update_layout(
                            height=400,
                            showlegend=False,
                            yaxis={'categoryorder': 'total ascending'}  # Rank high to low
                        )
                        st.plotly_chart(fig_shops, use_container_width=True, config={'displayModeBar': False})
                    
                    with col2:
                        # Show shop data table with percentages based on unique PIDs
                        shop_data = pd.DataFrame({
                            "Shop": shop_counts.index,
                            "Unique Visitors": [f"{count:,}" for count in shop_counts.values],
                            "% of Total PIDs": [f"{pct:.1f}%" for pct in (shop_counts.values / total_shop_responses * 100)]
                        })
                        
                        st.table(shop_data)
                else:
                    st.info("No shop data found in responses.")
        else:
            st.info(f"No responses found for the question: '{shop_question}'")

        st.markdown("--------------------------------")
        # Travel Cost Analysis
        travel_question = "How much did you pay for this trip?"
        travel_responses = responses[responses['q'] == travel_question]
        
        # Debug: Show travel cost analysis data
        # st.markdown("#### 💰 Travel Cost Analysis Debug")
        st.write(f"**Question:** '{travel_question}'")
        # st.write(f"**Found responses:** {len(travel_responses)}")
        
        # Debug: Check for similar questions
        if travel_responses.empty and 'q' in responses.columns:
            similar_questions = [q for q in responses['q'].unique() if 'trip' in q.lower() or 'pay' in q.lower() or 'cost' in q.lower()]
            if similar_questions:
                st.info(f" No exact match for trip cost question. Similar questions found: {similar_questions}")
        
        if not travel_responses.empty:
            with st.container():
                
                # Add filters for this section
                filtered_travel = create_section_filters("Trip Costs", travel_responses)
                
                # Process trip cost data using improved extraction logic
                trip_costs = []
                for response in filtered_travel['resp']:
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
                    # Use unique PIDs for sample size to be consistent with other sections
                    if 'pid' in filtered_travel.columns:
                        total_trip_responses = filtered_travel['pid'].nunique()
                        st.caption("📊 Sample size based on unique respondents (PIDs)")
                    else:
                        total_trip_responses = len(filtered_travel)
                        st.caption("⚠️ Sample size based on response count (PID not available)")
                    
                    # Calculate statistics
                    avg_cost = trip_df['cost'].mean()
                    median_cost = trip_df['cost'].median()
                    min_cost = trip_df['cost'].min()
                    max_cost = trip_df['cost'].max()
                    

                    
                    # Cost statistics cards
                    st.markdown("##### Trip Cost Statistics")
                    col3, col4, col5, col6 = st.columns(4)
                    
                    with col3:
                        st.metric("Average Cost", f"R {avg_cost:,.2f}")
                    
                    with col4:
                        st.metric("Median Cost", f"R {median_cost:,.2f}")
                    
                    with col5:
                        st.metric("Minimum Cost", f"R {min_cost:,.2f}")
                    
                    with col6:
                        st.metric("Maximum Cost", f"R {max_cost:,.2f}")
                    
                    # Cost range analysis
                    
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
                        title=f"Trip Cost Distribution - Unique Respondents: {total_trip_responses:,}",
                        color='Count',
                        color_continuous_scale='viridis',
                        labels={'Count': 'Number of Cost Entries', 'Range': 'Cost Range'}
                    )
                    fig_range.update_layout(
                        height=500,
                        showlegend=False,
                        xaxis_tickangle=-45,
                        coloraxis_colorbar=dict(
                            title="Count",
                            titleside="right"
                        )
                    )
                    st.plotly_chart(fig_range, use_container_width=True, config={'displayModeBar': False})
                    
                    # Show detailed cost data table
                    st.markdown("##### Cost Range Breakdown")
                    range_data = pd.DataFrame({
                        "Range": range_df['Range'],
                        "Count": [f"{count:,}" for count in range_df['Count']],
                        "Percentage": [f"{pct:.1f}%" for pct in range_df['Percentage']]
                    })
                    
                    st.table(range_data)
                    
                else:
                    st.info("No valid cost data found in responses.")
        else:
            st.info(f"No responses found for the question: '{travel_question}'")
        st.markdown("--------------------------------")
        # Main Source of Money/Employment Analysis
        st.markdown("### 💼 Employment & Income Analysis")
        
        # Strategy 1: Use direct employment column if available
        if 'employment' in responses.columns:
            st.write("**Data Source:** Employment column")
            money_responses = responses[responses['employment'].notna()].copy()
            money_responses['resp'] = money_responses['employment']
            money_question = "Employment Status (from column data)"
            st.write(f"**Found responses:** {len(money_responses)}")
            
        else:
            # Strategy 2: Look for employment/money questions
            possible_money_questions = [
                "What is your main source of money?",
                "Which of these describes you?",
                "Please select your current employment status.",
                "What is your employment status?",
                "How do you make money?",
                "What is your source of income?"
            ]
            
            money_question = None
            money_responses = pd.DataFrame()
            
            # Find the best matching question
            for question in possible_money_questions:
                temp_responses = responses[responses['q'] == question]
                if not temp_responses.empty:
                    money_question = question
                    money_responses = temp_responses
                    break
            
            # If no exact match, look for questions with employment/money keywords
            if money_responses.empty and 'q' in responses.columns:
                all_questions = responses['q'].unique()
                money_related = [q for q in all_questions if any(keyword in q.lower() for keyword in ['money', 'source', 'income', 'employment', 'describes you', 'work'])]
                
                if money_related:
                    money_question = money_related[0]  # Use the first match
                    money_responses = responses[responses['q'] == money_question]
                    st.info(f"📊 Using closest match: '{money_question}' ({len(money_responses)} responses)")
            
            st.write(f"**Question:** '{money_question}'")
            st.write(f"**Found responses:** {len(money_responses)}")
        
        if not money_responses.empty:
            with st.container():
                
                # Add filters for this section
                filtered_money = create_section_filters("Money Source", money_responses)
                
                # Get money source distribution (count unique PIDs per response)
                if 'pid' in filtered_money.columns:
                    money_dist = filtered_money.groupby('resp')['pid'].nunique().sort_values(ascending=False)
                    total_money_responses = filtered_money['pid'].nunique()
                    st.caption("📊 Counting unique respondents to avoid double-counting")
                else:
                    money_dist = filtered_money['resp'].value_counts()
                    total_money_responses = len(filtered_money)
                    st.caption("⚠️ Using response count (PID not available for unique counting)")
                
                # Show only horizontal bar chart for money sources
                fig_money_bar = px.bar(
                    x=money_dist.values,
                    y=money_dist.index,
                    orientation='h',
                    title=f"Main Source of Money - Unique Respondents: {total_money_responses:,}",
                    labels={'x': 'Unique Respondents (PIDs)', 'y': 'Money Source'},
                    color=money_dist.values,
                    color_continuous_scale='Viridis'
                )
                fig_money_bar.update_layout(
                    height=500,
                    showlegend=False,
                    yaxis={'categoryorder': 'total ascending'},
                    coloraxis_colorbar=dict(
                        title="Count",
                        titleside="right"
                    )
                )
                st.plotly_chart(fig_money_bar, use_container_width=True, config={'displayModeBar': False})
                
                # Money source data table and Side Hustles chart
                col_side_hustles, col_table = st.columns([2, 1])

                with col_side_hustles:
                    side_hustles_filtered = filtered_money[filtered_money['side_hustles'].notna()]
                    
                    if not side_hustles_filtered.empty:
                        # Count unique PIDs per side hustle to avoid double-counting
                        if 'pid' in side_hustles_filtered.columns:
                            side_hustles_dist = side_hustles_filtered.groupby('side_hustles')['pid'].nunique().sort_values(ascending=False)
                            side_hustles_count = side_hustles_filtered['pid'].nunique()
                        else:
                            side_hustles_dist = side_hustles_filtered['side_hustles'].value_counts()
                            side_hustles_count = len(side_hustles_filtered)
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
                        st.plotly_chart(fig_side_hustles, use_container_width=True, config={'displayModeBar': False})
                    else:
                        st.info("No side hustles data available (all values are NaN)")

                with col_table:
                    money_data = pd.DataFrame({
                        "Money Source": money_dist.index,
                        "Unique Respondents": [f"{count:,}" for count in money_dist.values],
                        "% of Total PIDs": [f"{pct:.1f}%" for pct in (money_dist.values / total_money_responses * 100)]
                    })
                    st.table(money_data)
        else:
            st.info(f"No responses found for the question: '{money_question}'")
        
        # SEM Segment Analysis (if available)
        if 'sem_segment' in responses.columns:
            st.markdown("--------------------------------")
            st.markdown("### 📊 SEM (Socioeconomic Market) Segments")
            
            sem_filtered = responses[responses['sem_segment'].notna()]
            if not sem_filtered.empty:
                # Count unique PIDs per SEM segment
                if 'pid' in sem_filtered.columns:
                    sem_dist = sem_filtered.groupby('sem_segment')['pid'].nunique().sort_values(ascending=False)
                    total_sem_respondents = sem_filtered['pid'].nunique()
                else:
                    sem_dist = sem_filtered['sem_segment'].value_counts()
                    total_sem_respondents = len(sem_filtered)
                
                col_sem_chart, col_sem_table = st.columns([2, 1])
                
                with col_sem_chart:
                    fig_sem = px.bar(
                        x=sem_dist.values,
                        y=sem_dist.index,
                        orientation='h',
                        title=f"SEM Segment Distribution - Unique Respondents: {total_sem_respondents:,}",
                        labels={'x': 'Unique Respondents (PIDs)', 'y': 'SEM Segment'},
                        color=sem_dist.values,
                        color_continuous_scale='viridis'
                    )
                    fig_sem.update_layout(
                        height=400,
                        showlegend=False,
                        yaxis={'categoryorder': 'total ascending'}
                    )
                    st.plotly_chart(fig_sem, use_container_width=True, config={'displayModeBar': False})
                
                with col_sem_table:
                    sem_table_data = pd.DataFrame({
                        "SEM Segment": sem_dist.index,
                        "Unique Respondents": [f"{count:,}" for count in sem_dist.values],
                        "% of Total PIDs": [f"{(count/total_sem_respondents*100):.1f}%" for count in sem_dist.values]
                    })
                    st.table(sem_table_data)
        
                
    else:
        st.warning("⚠️ No data found or connection failed")
        st.info("The dashboard is working but couldn't retrieve data from your backend API.")

if __name__ == "__main__":
    main()
