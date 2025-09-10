"""
Script to set up the required database schema in Snowflake
"""
import streamlit as st
from database import SnowflakeConnection

def setup_database():
    """Set up the database schema"""
    st.title("🗄️ Snowflake Database Setup")
    
    st.markdown("""
    This script will help you set up the required tables in your Snowflake database.
    Make sure you have the necessary permissions to create tables.
    """)
    
    if st.button("🚀 Set Up Database Schema"):
        db = SnowflakeConnection()
        
        if not db.connect():
            st.error("❌ Cannot connect to Snowflake. Please check your credentials.")
            return
        
        st.info("🔄 Creating database schema...")
        
        # Create surveys table
        surveys_table_sql = """
        CREATE TABLE IF NOT EXISTS surveys (
            survey_id INTEGER PRIMARY KEY,
            survey_name VARCHAR(255) NOT NULL,
            survey_type VARCHAR(100),
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
            status VARCHAR(50) DEFAULT 'Active',
            created_by VARCHAR(255)
        )
        """
        
        try:
            db.execute_query(surveys_table_sql)
            st.success("✅ Created SURVEYS table")
        except Exception as e:
            st.error(f"❌ Failed to create SURVEYS table: {str(e)}")
        
        # Create survey_responses table
        responses_table_sql = """
        CREATE TABLE IF NOT EXISTS survey_responses (
            response_id INTEGER PRIMARY KEY AUTOINCREMENT,
            survey_id INTEGER NOT NULL,
            user_id INTEGER,
            rating INTEGER CHECK (rating >= 1 AND rating <= 5),
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
            comments TEXT,
            metadata VARIANT,
            FOREIGN KEY (survey_id) REFERENCES surveys(survey_id)
        )
        """
        
        try:
            db.execute_query(responses_table_sql)
            st.success("✅ Created SURVEY_RESPONSES table")
        except Exception as e:
            st.error(f"❌ Failed to create SURVEY_RESPONSES table: {str(e)}")
        
        # Insert sample data
        st.info("🔄 Inserting sample data...")
        
        # Insert surveys
        insert_surveys_sql = """
        INSERT INTO surveys (survey_id, survey_name, survey_type, description) VALUES
        (1, 'Customer Satisfaction Survey', 'CSAT', 'Quarterly customer satisfaction survey'),
        (2, 'Employee Engagement Survey', 'NPS', 'Annual employee engagement and satisfaction survey'),
        (3, 'Product Feedback Survey', 'Product', 'Continuous product feedback and feature requests')
        """
        
        try:
            db.execute_query(insert_surveys_sql)
            st.success("✅ Inserted sample surveys")
        except Exception as e:
            st.warning(f"⚠️ Failed to insert surveys (may already exist): {str(e)}")
        
        # Insert sample responses
        insert_responses_sql = """
        INSERT INTO survey_responses (survey_id, user_id, rating, comments) VALUES
        (1, 1001, 5, 'Excellent service and support!'),
        (1, 1002, 4, 'Very good overall experience'),
        (1, 1003, 3, 'Average service, room for improvement'),
        (1, 1004, 5, 'Outstanding customer service'),
        (1, 1005, 4, 'Good experience, minor issues resolved quickly'),
        (2, 2001, 4, 'Great team environment and management'),
        (2, 2002, 3, 'Some challenges with work-life balance'),
        (2, 2003, 5, 'Love working here, excellent culture'),
        (2, 2004, 4, 'Good company with growth opportunities'),
        (2, 2005, 3, 'Decent place to work, some improvements needed'),
        (3, 3001, 4, 'Product is good, needs some feature improvements'),
        (3, 3002, 5, 'Amazing product, love the new features'),
        (3, 3003, 3, 'Product works but could be more intuitive'),
        (3, 3004, 4, 'Solid product with good performance'),
        (3, 3005, 2, 'Product has several issues that need fixing')
        """
        
        try:
            db.execute_query(insert_responses_sql)
            st.success("✅ Inserted sample responses")
        except Exception as e:
            st.warning(f"⚠️ Failed to insert responses (may already exist): {str(e)}")
        
        st.success("🎉 Database setup completed!")
        st.info("You can now run the main dashboard: `streamlit run app.py`")

if __name__ == "__main__":
    setup_database()
