-- Snowflake Database Schema for Surveys Dashboard
-- Run these commands in your Snowflake environment to set up the required tables

-- Create database and schema (adjust names as needed)
CREATE DATABASE IF NOT EXISTS SURVEYS_DB;
USE DATABASE SURVEYS_DB;
CREATE SCHEMA IF NOT EXISTS SURVEYS_SCHEMA;
USE SCHEMA SURVEYS_SCHEMA;

-- Surveys table
CREATE TABLE IF NOT EXISTS surveys (
    survey_id INTEGER PRIMARY KEY,
    survey_name VARCHAR(255) NOT NULL,
    survey_type VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    status VARCHAR(50) DEFAULT 'Active',
    created_by VARCHAR(255)
);

-- Survey responses table
CREATE TABLE IF NOT EXISTS survey_responses (
    response_id INTEGER PRIMARY KEY AUTOINCREMENT,
    survey_id INTEGER NOT NULL,
    user_id INTEGER,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    comments TEXT,
    metadata VARIANT, -- For storing additional response data as JSON
    FOREIGN KEY (survey_id) REFERENCES surveys(survey_id)
);

-- Survey questions table (optional - for more detailed surveys)
CREATE TABLE IF NOT EXISTS survey_questions (
    question_id INTEGER PRIMARY KEY AUTOINCREMENT,
    survey_id INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50), -- 'rating', 'text', 'multiple_choice', etc.
    question_order INTEGER,
    is_required BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (survey_id) REFERENCES surveys(survey_id)
);

-- Survey question responses table (optional - for detailed responses)
CREATE TABLE IF NOT EXISTS survey_question_responses (
    response_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    answer_text TEXT,
    answer_numeric DECIMAL(10,2),
    answer_boolean BOOLEAN,
    FOREIGN KEY (response_id) REFERENCES survey_responses(response_id),
    FOREIGN KEY (question_id) REFERENCES survey_questions(question_id)
);

-- Insert sample data
INSERT INTO surveys (survey_id, survey_name, survey_type, description) VALUES
(1, 'Customer Satisfaction Survey', 'CSAT', 'Quarterly customer satisfaction survey'),
(2, 'Employee Engagement Survey', 'NPS', 'Annual employee engagement and satisfaction survey'),
(3, 'Product Feedback Survey', 'Product', 'Continuous product feedback and feature requests');

-- Insert sample responses
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
(3, 3005, 2, 'Product has several issues that need fixing');

-- Create views for common queries
CREATE OR REPLACE VIEW survey_summary AS
SELECT 
    s.survey_id,
    s.survey_name,
    s.survey_type,
    COUNT(r.response_id) as total_responses,
    AVG(r.rating) as avg_rating,
    MIN(r.rating) as min_rating,
    MAX(r.rating) as max_rating,
    COUNT(DISTINCT r.user_id) as unique_respondents,
    ROUND(COUNT(CASE WHEN r.rating >= 4 THEN 1 END) * 100.0 / COUNT(r.response_id), 2) as satisfaction_rate
FROM surveys s
LEFT JOIN survey_responses r ON s.survey_id = r.survey_id
GROUP BY s.survey_id, s.survey_name, s.survey_type;

-- Create view for rating distribution
CREATE OR REPLACE VIEW rating_distribution AS
SELECT 
    survey_id,
    rating,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY survey_id), 2) as percentage
FROM survey_responses
GROUP BY survey_id, rating
ORDER BY survey_id, rating;

-- Grant permissions (adjust as needed for your environment)
-- GRANT USAGE ON DATABASE SURVEYS_DB TO ROLE YOUR_ROLE;
-- GRANT USAGE ON SCHEMA SURVEYS_SCHEMA TO ROLE YOUR_ROLE;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA SURVEYS_SCHEMA TO ROLE YOUR_ROLE;
