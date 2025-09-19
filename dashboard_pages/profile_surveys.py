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

def get_real_data():
    """Get real data from your backend API"""
    client = get_backend_client()
    if not client:
        st.warning("?s??,? Backend connection not available - using sample data")
        return None, None, None, None

    PAGE_SIZE = 1000
    MAX_RECORDS = 30000

    try:
        frames: list[pd.DataFrame] = []
        total_loaded = 0
        required_questions = {
            "Which of these shops do you visit most often (Select all that apply)",
            "How much did you pay for this trip?",
            "What is your main source of money?",
        }
        seen_questions: set[str] = set()

        for offset in range(0, MAX_RECORDS, PAGE_SIZE):
            remaining = MAX_RECORDS - offset
            limit = PAGE_SIZE if remaining >= PAGE_SIZE else remaining
            if limit <= 0:
                break
            try:
                page = client.get_responses(
                    survey="SB055_Profile_Survey1",
                    limit=limit,
                    offset=offset,
                )
            except Exception:
                continue

            if not isinstance(page, pd.DataFrame) or page.empty:
                if offset == 0:
                    break
                if frames:
                    break
                continue

            frames.append(page)
            total_loaded += len(page)

            if "q" in page.columns:
                seen_questions.update(str(q) for q in page["q"].dropna().unique())

            if required_questions.issubset(seen_questions) and len(page) < PAGE_SIZE:
                break

            if len(page) < PAGE_SIZE:
                break

        responses = pd.concat(frames, ignore_index=True).drop_duplicates() if frames else pd.DataFrame()
        if responses.empty:
            st.warning('dY"S Unable to retrieve profile survey responses from the backend')
            return None, None, None, None

        if "q" in responses.columns and "SURVEY_QUESTION" not in responses.columns:
            responses["SURVEY_QUESTION"] = responses["q"]
        if "resp" in responses.columns and "RESPONSE" not in responses.columns:
            responses["RESPONSE"] = responses["resp"]
        if "pid" in responses.columns and "PROFILE_ID" not in responses.columns:
            responses["PROFILE_ID"] = responses["pid"]
        if "ts" in responses.columns:
            responses["ts"] = pd.to_datetime(responses["ts"], errors="coerce")
            if "SURVEY_DATE" not in responses.columns:
                responses["SURVEY_DATE"] = responses["ts"].dt.date
        elif "SURVEY_DATE" in responses.columns:
            responses["ts"] = pd.to_datetime(responses["SURVEY_DATE"], errors="coerce")

        client.get_survey_summary()
        survey_ids = ["SB055_Profile_Survey1"]

        if "SURVEY_QUESTION" in responses.columns:
            unique_questions = responses["SURVEY_QUESTION"].dropna().unique()
            questions_df = pd.DataFrame({"question": unique_questions})
        elif "q" in responses.columns:
            unique_questions = responses["q"].dropna().unique()
            questions_df = pd.DataFrame({"question": unique_questions})
        else:
            questions_df = pd.DataFrame()

        return survey_ids, questions_df, questions_df, responses

    except Exception as exc:  # noqa: BLE001
        st.error(f"Error getting data from backend: {exc}")
        return None, None, None, None

    try:
        primary = client.get_responses(survey="SB055_Profile_Survey1", limit=30000)
        frames: list[pd.DataFrame] = []
        if isinstance(primary, pd.DataFrame) and not primary.empty:
            frames.append(primary)

        required_questions = {
            "Which of these shops do you visit most often (Select all that apply)",
            "How much did you pay for this trip?",
            "What is your main source of money?",
        }
        seen_questions = set()
        if isinstance(primary, pd.DataFrame) and "q" in primary.columns:
            seen_questions.update(str(q) for q in primary["q"].dropna().unique())

        if required_questions - seen_questions:
            for offset in (1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000,20000,30000):
                try:
                    chunk = client.get_responses(survey="SB055_Profile_Survey1", limit=30000, offset=offset)
                except Exception:
                    continue
                if isinstance(chunk, pd.DataFrame) and not chunk.empty:
                    frames.append(chunk)
                    if "q" in chunk.columns:
                        seen_questions.update(str(q) for q in chunk["q"].dropna().unique())
                    if required_questions.issubset(seen_questions):
                        break

        responses = pd.concat(frames, ignore_index=True).drop_duplicates() if frames else pd.DataFrame()
        if responses.empty:
            st.warning("dY\"S Unable to retrieve profile survey responses from the backend")
            return None, None, None, None

        if "q" in responses.columns and "SURVEY_QUESTION" not in responses.columns:
            responses["SURVEY_QUESTION"] = responses["q"]
        if "resp" in responses.columns and "RESPONSE" not in responses.columns:
            responses["RESPONSE"] = responses["resp"]
        if "pid" in responses.columns and "PROFILE_ID" not in responses.columns:
            responses["PROFILE_ID"] = responses["pid"]
        if "ts" in responses.columns:
            responses["ts"] = pd.to_datetime(responses["ts"], errors="coerce")
            if "SURVEY_DATE" not in responses.columns:
                responses["SURVEY_DATE"] = responses["ts"].dt.date
        elif "SURVEY_DATE" in responses.columns:
            responses["ts"] = pd.to_datetime(responses["SURVEY_DATE"], errors="coerce")

        summary = client.get_survey_summary()
        survey_ids = ["SB055_Profile_Survey1"]

        if "SURVEY_QUESTION" in responses.columns:
            unique_questions = responses["SURVEY_QUESTION"].dropna().unique()
            questions_df = pd.DataFrame({"question": unique_questions})
        elif "q" in responses.columns:
            unique_questions = responses["q"].dropna().unique()
            questions_df = pd.DataFrame({"question": unique_questions})
        else:
            questions_df = pd.DataFrame()

        return survey_ids, questions_df, questions_df, responses

    except Exception as exc:  # noqa: BLE001
        st.error(f"Error getting data from backend: {exc}")
        return None, None, None, None
    
    try:
        # Get responses data from your backend using optimized endpoint
        # Try to get Profile Survey data first (most comprehensive) - use individual survey endpoint with limit for cost efficiency
        responses = client.get_individual_survey("SB055_Profile_Survey1", limit=30000)
        
        
        if responses.empty:
            # Fallback to survey index if responses endpoint fails
            st.info("📊 Responses endpoint unavailable, trying survey index...")
            survey_index = client.get_surveys_index()
            if not survey_index.empty:
                # Create a minimal responses-like structure from survey index
                responses = survey_index
            else:
                return None, None, None, None
        
        # Get survey summary for analytics
        summary = client.get_survey_summary()
        
        # Create proper analytics from the responses data
        survey_ids = ['Backend Data']  # Placeholder
        
        # For survey questions analysis, we'll use the responses data directly
        # Extract unique questions from the responses
        if 'q' in responses.columns:
            unique_questions = responses['q'].dropna().unique()
            questions_df = pd.DataFrame({'question': unique_questions})
        else:
            questions_df = pd.DataFrame()
        
        return survey_ids, questions_df, questions_df, responses
        
    except Exception as e:
        st.error(f"Error getting data from backend: {str(e)}")
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
    
    # Get data
    survey_ids, shop_questions, range_questions, responses = get_real_data()
    
    if survey_ids and responses is not None and not responses.empty:
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
        # st.dataframe(responses.head(), width='stretch')
        
        # Debug: Show available survey questions
        if 'SURVEY_QUESTION' in responses.columns:
            available_questions = responses['SURVEY_QUESTION'].unique()
            # st.info(f"📋 Available Survey Questions ({len(available_questions)}): {', '.join(available_questions[:5])}{'...' if len(available_questions) > 5 else ''}")
        
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
                        st.plotly_chart(fig_shops, width='stretch')
                    
                    with col2:
                        # Show shop data table
                        shop_data = pd.DataFrame({
                            "Shop": shop_counts.index,
                            "Visits": [f"{count:,}" for count in shop_counts.values],
                            "Percentage": [f"{pct:.1f}%" for pct in (shop_counts.values / shop_counts.sum() * 100)]
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
                        st.plotly_chart(fig_hist, width='stretch')
                    
                    with col2:
                        # Box plot for cost distribution
                        fig_box = px.box(
                            trip_df,
                            y='cost',
                            title=f"Sample Size: {total_trip_responses:,}",
                            labels={'cost': 'Cost (R)'},
                            color_discrete_sequence=['#4ECDC4']
                        )
                        fig_box.update_layout(
                            height=400,
                            showlegend=False,
                            yaxis_title="Cost (R)",
                            yaxis=dict(range=[0, 80])  # Focus on the relevant range
                        )
                        st.plotly_chart(fig_box, width='stretch')
                    
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
                    st.plotly_chart(fig_range, width='stretch')
                    
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
        # Main Source of Money Analysis
        money_question = "What is your main source of money?"
        money_responses = responses[responses['q'] == money_question]
        
        # Debug: Show money source analysis data

        st.write(f"**Question:** '{money_question}'")
        # st.write(f"**Found responses:** {len(money_responses)}")
        
        # Debug: Check for similar questions
        if money_responses.empty and 'q' in responses.columns:
            similar_questions = [q for q in responses['q'].unique() if 'money' in q.lower() or 'source' in q.lower() or 'income' in q.lower()]
            if similar_questions:
                st.info(f" No exact match for money source question. Similar questions found: {similar_questions}")
        
        if not money_responses.empty:
            with st.container():
                
                # Add filters for this section
                filtered_money = create_section_filters("Money Source", money_responses)
                
                # Get money source distribution
                money_dist = filtered_money['resp'].value_counts()
                total_money_responses = len(filtered_money)
                
                # Create two-column layout
                col1, col2 = st.columns(2)
                
                with col1:
                    # Pie chart for money sources
                    fig_money_pie = px.pie(
                        values=money_dist.values,
                        names=money_dist.index,
                        title=f"Sample Size: {total_money_responses:,}",
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
                    st.plotly_chart(fig_money_pie, width='stretch')
                
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
                    st.plotly_chart(fig_money_bar, width='stretch')
                
                # Money source data table and Side Hustles chart
                st.markdown("##### Money Source Breakdown")
                
                # Create two-column layout for table and side hustles chart
                col_table, col_side_hustles = st.columns([2, 1])
                
                with col_table:
                    money_data = pd.DataFrame({
                        "Money Source": money_dist.index,
                        "Count": [f"{count:,}" for count in money_dist.values],
                        "Percentage": [f"{pct:.1f}%" for pct in (money_dist.values / total_money_responses * 100)]
                    })
                    
                    st.table(money_data)
                
                with col_side_hustles:
                    # Side Hustles Analysis
                    st.markdown("##### Side Hustles Distribution")
                    
                    # Get side hustles data, filtering out NaN values
                    side_hustles_data = filtered_money['side_hustles'].dropna()
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
                        st.plotly_chart(fig_side_hustles, width='stretch')
                    else:
                        st.info("No side hustles data available (all values are NaN)")
        else:
            st.info(f"No responses found for the question: '{money_question}'")
        
                
    else:
        st.warning("⚠️ No data found or connection failed")
        st.info("The dashboard is working but couldn't retrieve data from your backend API.")

if __name__ == "__main__":
    main()
