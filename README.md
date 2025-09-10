# 📊 Surveys Dashboard

A comprehensive Streamlit dashboard for analyzing survey data stored in Snowflake. This application provides interactive visualizations, analytics, and insights for multiple survey types including customer satisfaction, employee engagement, and product feedback.

## 🚀 Features

- **Interactive Dashboard**: Beautiful landing page with key metrics and navigation
- **Multiple Survey Types**: Dedicated pages for different survey categories
- **Real-time Analytics**: Connect to Snowflake for live data analysis
- **Sample Data**: Works with sample data when Snowflake is not configured
- **Export Functionality**: Download data in CSV and JSON formats
- **Responsive Design**: Modern UI with custom CSS styling

## 📋 Survey Pages

1. **Customer Satisfaction Survey** (`/survey1`)
   - Rating distribution analysis
   - Satisfaction rate tracking
   - Time series trends
   - Recent response review

2. **Employee Engagement Survey** (`/survey2`)
   - Department-wise analysis
   - Engagement category breakdown
   - Participation rate tracking
   - Action recommendations

3. **Product Feedback Survey** (`/survey3`)
   - Feature sentiment analysis
   - User segment insights
   - Product category ratings
   - Improvement recommendations

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd surveys_dashboard
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```

3. **Set up environment variables** (optional for Snowflake connection):
   ```bash
   cp .env.example .env
   # Edit .env with your Snowflake credentials
   ```

## ⚙️ Configuration

### Snowflake Setup

Create a `.env` file with your Snowflake credentials:

```env
SNOWFLAKE_ACCOUNT=your_account_name
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=your_schema
SNOWFLAKE_ROLE=your_role
```

### Database Schema

The application expects the following tables in your Snowflake database:

#### `surveys` table:
```sql
CREATE TABLE surveys (
    survey_id INTEGER,
    survey_name VARCHAR(255),
    survey_type VARCHAR(100),
    created_at TIMESTAMP,
    status VARCHAR(50)
);
```

#### `survey_responses` table:
```sql
CREATE TABLE survey_responses (
    response_id INTEGER,
    survey_id INTEGER,
    user_id INTEGER,
    rating INTEGER,
    submitted_at TIMESTAMP,
    comments TEXT
);
```

## 🚀 Running the Application

1. **Start the Streamlit app**:
   ```bash
   streamlit run app.py
   ```

2. **Open your browser** and navigate to `http://localhost:8501`

## 📊 Usage

### Without Snowflake Connection
- The app will automatically use sample data
- All features work with simulated data
- Perfect for testing and development

### With Snowflake Connection
- Configure your `.env` file with Snowflake credentials
- The app will connect to your database
- Real-time data analysis and insights

### Navigation
- Use the sidebar to navigate between different survey pages
- Each page provides specific analytics for that survey type
- Export data using the download buttons on each page

## 🎨 Customization

### Adding New Surveys
1. Create a new file in the `pages/` directory (e.g., `survey4.py`)
2. Follow the pattern of existing survey pages
3. Import and add the new survey to `app.py`

### Styling
- Custom CSS is defined in `app.py`
- Modify the `st.markdown()` sections with custom styles
- Use Streamlit's theming options for additional customization

### Database Queries
- Modify queries in `database.py` to match your schema
- Add new analysis functions as needed
- Update the sample data structure if required

## 📁 Project Structure

```
surveys_dashboard/
├── app.py                 # Main application file
├── config.py             # Configuration management
├── database.py           # Database utilities and connections
├── pages/                # Survey page modules
│   ├── __init__.py
│   ├── survey1.py        # Customer Satisfaction
│   ├── survey2.py        # Employee Engagement
│   └── survey3.py        # Product Feedback
├── pyproject.toml        # Project dependencies
├── README.md             # This file
└── .env.example          # Environment variables template
```

## 🔧 Dependencies

- **streamlit**: Web application framework
- **pandas**: Data manipulation and analysis
- **plotly**: Interactive visualizations
- **snowflake-connector-python**: Snowflake database connection
- **snowflake-sqlalchemy**: SQLAlchemy integration for Snowflake
- **sqlalchemy**: Database ORM
- **python-dotenv**: Environment variable management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the documentation
- Review the sample data structure
- Ensure your Snowflake credentials are correct
- Verify your database schema matches the expected structure

## 🔮 Future Enhancements

- [ ] User authentication and role-based access
- [ ] Real-time notifications for new responses
- [ ] Advanced filtering and search capabilities
- [ ] Automated report generation
- [ ] Integration with other data sources
- [ ] Mobile-responsive design improvements
- [ ] Advanced statistical analysis features
