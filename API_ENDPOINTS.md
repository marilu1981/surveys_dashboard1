# 🚀 Survey Backend API Documentation

## Base URL
```
https://ansebmrsurveysv1.oa.r.appspot.com
```

## 📊 Core Data Endpoints

### 1. Survey Summary
**GET** `/api/survey-summary`

Get overview of all surveys with response counts and metadata.

**Response:**
```json
{
  "surveys": [
    {
      "title": "SB055_Profile_Survey1",
      "response_count": 146165,
      "date_range": {
        "earliest": "2025-08-14",
        "latest": "2025-08-20"
      }
    }
  ]
}
```

**Frontend Usage:**
```javascript
const getSurveySummary = async () => {
  const response = await fetch('https://ansebmrsurveysv1.oa.r.appspot.com/api/survey-summary');
  return await response.json();
};
```

---

### 2. Survey Questions
**GET** `/api/survey-questions`

Get all unique questions across surveys with survey mapping.

**Response:**
```json
{
  "questions": [
    {
      "question": "What is your age group?",
      "surveys": ["SB055_Profile_Survey1"],
      "response_count": 146165
    }
  ]
}
```

**Frontend Usage:**
```javascript
const getSurveyQuestions = async () => {
  const response = await fetch('https://ansebmrsurveysv1.oa.r.appspot.com/api/survey-questions');
  return await response.json();
};
```

---

### 3. Survey Responses (Main Data) - ✅ OPTIMIZED
**GET** `/api/responses`

Get filtered and paginated survey responses with advanced filtering options. Now uses individual survey files for better performance.

**Query Parameters:**
- `survey` (string) - Filter by survey title (e.g., `SB055_Profile_Survey1`)
- `limit` (number) - Number of responses (default: 1000, max: 5000)
- `offset` (number) - Pagination offset (default: 0)
- `gender` (string) - Filter by gender (Male, Female, Other)
- `age_group` (string) - Filter by age group (18-24, 25-34, 35-44, etc.)
- `employment` (string) - Filter by employment status
- `start_date` (string) - Filter by start date (YYYY-MM-DD)
- `end_date` (string) - Filter by end date (YYYY-MM-DD)

**Response:**
```json
{
  "data": [
    {
      "ts": "2025-08-14",
      "created_at": "2025-08-14T13:47:38+00:00",
      "title": "SB055_Profile_Survey1",
      "q": "How many people are in your taxi with you today?",
      "resp": "2-3 people",
      "engagement_id": 483370,
      "pid": 2,
      "gender": "Male",
      "age_group": "25-34",
      "salary": "R15,000 - R25,000",
      "employment": "Employed",
      "home_province": "Gauteng",
      "sem_segment": "High Value"
    }
  ],
  "pagination": {
    "total": 146165,
    "limit": 1000,
    "offset": 0,
    "hasMore": true
  }
}
```

**Frontend Usage:**
```javascript
const getFilteredResponses = async (filters = {}) => {
  const params = new URLSearchParams(filters);
  const response = await fetch(`https://ansebmrsurveysv1.oa.r.appspot.com/api/responses?${params}`);
  return await response.json();
};

// Example usage
const filters = {
  survey: 'SB055_Profile_Survey1',
  limit: 1000,
  gender: 'Male',
  age_group: '25-34',
  start_date: '2025-08-01',
  end_date: '2025-08-31'
};
const data = await getFilteredResponses(filters);
```

---

## 📋 Survey-Specific Endpoints

### 4. Individual Survey Data - ✅ FIXED
**GET** `/api/survey/:surveyTitle`

Get data for a specific survey with optional full dataset. Now uses individual survey files for better performance.

**Parameters:**
- `surveyTitle` (path) - The exact survey title (e.g., `SB055_Profile_Survey1`)
- `full` (query) - Set to `true` for complete dataset (default: `false`)

**Available Surveys:**
- `SB055_Profile_Survey1` (146,165 responses)
- `SB056_Cellphone_Survey` (2,426 responses)
- `SB056_Cellphone_Survey-02` (2,000 responses)
- `FI027_1Life_Funeral_Cover_Survey` (9,885 responses)
- `FI027_Funeral_Cover_Survey-02` (8,712 responses)
- `FI027_Funeral_Cover_Survey-03` (55,617 responses)
- `FI028_1Life_Funeral_Cover_Survey2` (6,316 responses)
- `FI028_1Life_Funeral_Cover_Survey2-02` (5,536 responses)
- `FI028_1Life_Funeral_Cover_Survey2-03` (22,697 responses)
- `TP005_Convinience_Store_Products_Survey_Briefing_Form` (39,187 responses)

**Response:**
```json
{
  "survey_title": "SB055_Profile_Survey1",
  "data": [...],
  "pagination": {
    "total": 146165,
    "limit": 1000,
    "offset": 0,
    "hasMore": true
  }
}
```

**Frontend Usage:**
```javascript
const getSurveyData = async (surveyTitle, full = false) => {
  const url = `https://ansebmrsurveysv1.oa.r.appspot.com/api/survey/${surveyTitle}${full ? '?full=true' : ''}`;
  const response = await fetch(url);
  return await response.json();
};

// Get paginated data
const data = await getSurveyData('SB055_Profile_Survey1');

// Get full dataset for reporting
const fullData = await getSurveyData('SB055_Profile_Survey1', true);
```

---

### 5. Survey Group Data - ✅ OPTIMIZED
**GET** `/api/survey-group/:groupPrefix`

Get data for surveys with matching prefix. Now uses individual survey files instead of the large responses.ndjson file.

**Parameters:**
- `groupPrefix` (path) - Survey title prefix (e.g., `SB055`, `FI027`, `FI028`)
- `full` (query) - Set to `true` for complete dataset (default: `false`)

**Available Groups:**
- `SB055` - Profile Survey Group (1 survey)
- `SB056` - Cellphone Survey Group (2 surveys)
- `FI027` - Funeral Cover Survey Group (3 surveys)
- `FI028` - 1Life Funeral Cover Survey Group (3 surveys)
- `TP005` - Convenience Store Survey Group (1 survey)

**Frontend Usage:**
```javascript
const getSurveyGroupData = async (groupPrefix, full = false) => {
  const url = `https://ansebmrsurveysv1.oa.r.appspot.com/api/survey-group/${groupPrefix}${full ? '?full=true' : ''}`;
  const response = await fetch(url);
  return await response.json();
};

// Get all SB055 surveys
const sb055Data = await getSurveyGroupData('SB055');

// Get all funeral cover surveys
const funeralData = await getSurveyGroupData('FI027');
```

---

### 6. Survey Index
**GET** `/api/surveys`

Get lightweight index of all available surveys.

**Response:**
```json
{
  "surveys": [
    {
      "title": "SB055_Profile_Survey1",
      "filename": "surveys/SB055_Profile_Survey1.json",
      "response_count": 146165,
      "file_size_mb": 67.8
    }
  ],
  "total_surveys": 10,
  "total_responses": 298541
}
```

**Frontend Usage:**
```javascript
const getSurveyIndex = async () => {
  const response = await fetch('https://ansebmrsurveysv1.oa.r.appspot.com/api/surveys');
  return await response.json();
};
```

---

## 📈 Demographics & Analytics

### 7. Demographics Summary
**GET** `/api/demographics`

Get pre-computed demographics breakdown for dashboard.

**Response:**
```json
{
  "overview": {
    "total_responses": 298541,
    "total_surveys": 10,
    "date_range": {
      "earliest": "2025-08-14",
      "latest": "2025-08-26"
    }
  },
  "overall_demographics": {
    "gender": {
      "Male": 150000,
      "Female": 120000,
      "Other": 28541
    },
    "age_groups": {
      "18-24": 50000,
      "25-34": 100000,
      "35-44": 80000,
      "45-54": 50000,
      "55+": 18541
    },
    "employment": {
      "Employed": 200000,
      "Unemployed": 50000,
      "Student": 48541
    }
  }
}
```

**Frontend Usage:**
```javascript
const getDemographics = async () => {
  const response = await fetch('https://ansebmrsurveysv1.oa.r.appspot.com/api/demographics');
  return await response.json();
};
```

---

## 📊 Reporting Endpoints

### 8. Profile Survey Reporting
**GET** `/api/reporting/profile-survey`

Get complete profile survey data for reporting with CSV export option.

**Query Parameters:**
- `format` (string) - Response format: `json` or `csv` (default: `json`)

**Response (JSON):**
```json
{
  "survey_title": "SB055_Profile_Survey1",
  "data": [...],
  "total": 146165,
  "note": "Complete Profile Survey dataset for reporting",
  "export_formats": ["json", "csv"],
  "usage": "Add ?format=csv for CSV export"
}
```

**Response (CSV):**
```csv
ts,created_at,title,q,resp,engagement_id,pid,gender,age_group,salary,employment,home_province,sem_segment
2025-08-14,2025-08-14T13:47:38+00:00,SB055_Profile_Survey1,How many people are in your taxi with you today?,2-3 people,483370,2,Male,25-34,R15,000 - R25,000,Employed,Gauteng,High Value
```

**Frontend Usage:**
```javascript
const exportProfileSurvey = async (format = 'json') => {
  const response = await fetch(`https://ansebmrsurveysv1.oa.r.appspot.com/api/reporting/profile-survey?format=${format}`);
  
  if (format === 'csv') {
    const csvText = await response.text();
    // Download CSV file
    const blob = new Blob([csvText], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'profile_survey_data.csv';
    a.click();
    return csvText;
  }
  
  return await response.json();
};

// Export as JSON
const jsonData = await exportProfileSurvey('json');

// Export as CSV (downloads file)
const csvData = await exportProfileSurvey('csv');
```

---

## 🔧 Utility Endpoints

### 9. Vocabulary Maps
**GET** `/api/vocab`

Get vocabulary mappings for form dropdowns and filters.

**Response:**
```json
{
  "gender_values": ["Male", "Female", "Other"],
  "employment_values": ["Employed", "Unemployed", "Student", "Retired"],
  "salary_band_values": ["R0 - R5,000", "R5,000 - R15,000", "R15,000 - R25,000"],
  "age_group_values": ["18-24", "25-34", "35-44", "45-54", "55+"],
  "location_values": ["Gauteng", "Western Cape", "KwaZulu-Natal"],
  "sem_segment_values": ["High Value", "Medium Value", "Low Value"]
}
```

**Frontend Usage:**
```javascript
const getVocabulary = async () => {
  const response = await fetch('https://ansebmrsurveysv1.oa.r.appspot.com/api/vocab');
  return await response.json();
};

// Use for dropdown options
const vocab = await getVocabulary();
// vocab.gender_values can be used for gender dropdown
// vocab.age_group_values can be used for age group dropdown
```

---

### 10. Data Schema
**GET** `/api/schema`

Get data schema documentation with field descriptions.

**Response:**
```json
{
  "responses.ndjson": {
    "ts": "ISO date (Africa/Johannesburg tz applied)",
    "created_at": "ISO timestamp when response was created",
    "title": "survey_title",
    "q": "question_text",
    "resp": "response_text",
    "engagement_id": "Unique engagement identifier",
    "pid": "profile_id",
    "gender": "Gender",
    "age_group": "Age-Group",
    "salary": "Monthly Personal Income",
    "employment": "Employment Status",
    "home_province": "Home Province",
    "sem_segment": "SEM Segment",
    "sem_score": "SEM Score",
    "side_hustles": "Side Hustles information"
  }
}
```

**Frontend Usage:**
```javascript
const getSchema = async () => {
  const response = await fetch('https://ansebmrsurveysv1.oa.r.appspot.com/api/schema');
  return await response.json();
};
```

---

### 11. Health Check
**GET** `/api/health`

Check server status and performance metrics.

**Response:**
```json
{
  "status": "ok",
  "message": "Service is healthy",
  "cache_size": 5,
  "uptime": 11.973258698,
  "timestamp": "2025-09-18T22:58:00Z"
}
```

**Frontend Usage:**
```javascript
const checkHealth = async () => {
  const response = await fetch('https://ansebmrsurveysv1.oa.r.appspot.com/api/health');
  return await response.json();
};
```

---

## 🎯 Complete Frontend Integration Examples

### React Hook Example
```javascript
import { useState, useEffect } from 'react';

const useSurveyData = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = async (endpoint, options = {}) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`https://ansebmrsurveysv1.oa.r.appspot.com${endpoint}`, options);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const result = await response.json();
      setData(result);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { data, loading, error, fetchData };
};

// Usage in component
const SurveyDashboard = () => {
  const { data, loading, error, fetchData } = useSurveyData();

  useEffect(() => {
    fetchData('/api/survey-summary');
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      {data?.surveys?.map(survey => (
        <div key={survey.title}>
          <h3>{survey.title}</h3>
          <p>Responses: {survey.response_count}</p>
        </div>
      ))}
    </div>
  );
};
```

### Filter Component Example
```javascript
const SurveyFilters = ({ onFiltersChange }) => {
  const [filters, setFilters] = useState({
    survey: '',
    gender: '',
    age_group: '',
    employment: '',
    start_date: '',
    end_date: '',
    limit: 1000
  });

  const handleFilterChange = (key, value) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    onFiltersChange(newFilters);
  };

  return (
    <div className="filters">
      <select 
        value={filters.survey} 
        onChange={(e) => handleFilterChange('survey', e.target.value)}
      >
        <option value="">All Surveys</option>
        <option value="SB055_Profile_Survey1">Profile Survey 1</option>
        <option value="SB056_Cellphone_Survey">Cellphone Survey</option>
        <option value="FI027_1Life_Funeral_Cover_Survey">Funeral Cover Survey</option>
      </select>
      
      <select 
        value={filters.gender} 
        onChange={(e) => handleFilterChange('gender', e.target.value)}
      >
        <option value="">All Genders</option>
        <option value="Male">Male</option>
        <option value="Female">Female</option>
        <option value="Other">Other</option>
      </select>
      
      <input 
        type="date" 
        value={filters.start_date}
        onChange={(e) => handleFilterChange('start_date', e.target.value)}
        placeholder="Start Date"
      />
      
      <input 
        type="date" 
        value={filters.end_date}
        onChange={(e) => handleFilterChange('end_date', e.target.value)}
        placeholder="End Date"
      />
    </div>
  );
};
```

### Chart Data Example
```javascript
const useChartData = (filters) => {
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchChartData = async () => {
      setLoading(true);
      try {
        const params = new URLSearchParams(filters);
        const response = await fetch(`https://ansebmrsurveysv1.oa.r.appspot.com/api/responses?${params}`);
        const data = await response.json();
        
        // Process data for charts
        const processedData = processDataForCharts(data.data);
        setChartData(processedData);
      } catch (error) {
        console.error('Error fetching chart data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchChartData();
  }, [filters]);

  return { chartData, loading };
};

const processDataForCharts = (responses) => {
  // Group by age group for age distribution chart
  const ageDistribution = responses.reduce((acc, response) => {
    const ageGroup = response.age_group || 'Unknown';
    acc[ageGroup] = (acc[ageGroup] || 0) + 1;
    return acc;
  }, {});

  // Group by gender for gender distribution chart
  const genderDistribution = responses.reduce((acc, response) => {
    const gender = response.gender || 'Unknown';
    acc[gender] = (acc[gender] || 0) + 1;
    return acc;
  }, {});

  return {
    ageDistribution,
    genderDistribution,
    totalResponses: responses.length
  };
};
```

## 🚨 Error Handling

All endpoints return consistent error responses:

```json
{
  "error": "Error message description",
  "code": "ERROR_CODE",
  "timestamp": "2025-09-18T22:58:00Z"
}
```

Common HTTP status codes:
- `200` - Success
- `400` - Bad Request (invalid parameters)
- `404` - Not Found (survey not found)
- `500` - Internal Server Error

## 🔧 Performance Notes

- All responses are compressed with gzip
- Data is cached for 5 minutes to reduce GCS calls
- Individual survey files are used instead of large responses.ndjson for better performance
- Pagination is recommended for large datasets (max 5000 records per request)
- Use specific survey endpoints for better performance
- Demographics endpoint provides pre-computed data for faster dashboard loading

## 📱 CORS Support

All endpoints support CORS for frontend integration. No additional configuration needed.

## 🎯 Current Status

**✅ Working Endpoints (11/11):**
- `/api/health` - Health Check
- `/api/surveys` - Survey Index
- `/api/demographics` - Demographics Summary
- `/api/survey-summary` - Survey Summary
- `/api/survey-questions` - Survey Questions
- `/api/vocab` - Vocabulary Mappings
- `/api/schema` - Schema Documentation
- `/api/responses` - Filtered Responses (Optimized)
- `/api/survey/:surveyTitle` - Individual Survey Data (Fixed)
- `/api/survey-group/:groupPrefix` - Survey Group Data (Optimized)
- `/api/reporting/profile-survey` - Profile Survey Reporting

**🔧 Recent Optimizations:**
- Updated all endpoints to use individual survey files instead of large responses.ndjson
- Added proper file path handling for surveys in GCS bucket
- Improved error handling and timeout protection
- Enhanced pagination and filtering capabilities

---

**Last Updated:** September 18, 2025  
**API Version:** 2.0  
**Base URL:** https://ansebmrsurveysv1.oa.r.appspot.com
