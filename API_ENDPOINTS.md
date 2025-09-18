# 🚀 Survey Backend API Documentation

## 🌐 Deployment Status
✅ **LIVE & DEPLOYED** - All endpoints are available at the production URL below.

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
      "response_count": 1500,
      "date_range": {
        "earliest": "2025-01-01",
        "latest": "2025-12-31"
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
      "response_count": 1500
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

### 3. Survey Responses (Main Data)
**GET** `/api/responses`

Get filtered and paginated survey responses with advanced filtering options.

**Query Parameters:**
- `survey` (string) - Filter by survey title
- `limit` (number) - Number of responses (default: 1000, max: 10000)
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
      "ts": "2025-01-15T10:30:00Z",
      "title": "SB055_Profile_Survey1",
      "q": "What is your age group?",
      "resp": "25-34",
      "pid": "profile_123",
      "gender": "Male",
      "age_group": "25-34",
      "salary": "R15,000 - R25,000",
      "employment": "Employed",
      "location": "Gauteng",
      "sem_segment": "High Value"
    }
  ],
  "pagination": {
    "total": 1500,
    "limit": 1000,
    "offset": 0,
    "has_more": true
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
  start_date: '2025-01-01',
  end_date: '2025-12-31'
};
const data = await getFilteredResponses(filters);
```

---

## 📋 Survey-Specific Endpoints

### 4. Individual Survey Data
**GET** `/api/survey/:surveyTitle`

Get data for a specific survey with optional full dataset.

**Parameters:**
- `surveyTitle` (path) - The exact survey title (e.g., `SB055_Profile_Survey1`)
- `full` (query) - Set to `true` for complete dataset (default: `false`)

**Response:**
```json
{
  "survey_title": "SB055_Profile_Survey1",
  "total_responses": 1500,
  "data": [...],
  "pagination": {
    "total": 1500,
    "limit": 1000,
    "offset": 0
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

### 5. Survey Group Data
**GET** `/api/survey-group/:groupPrefix`

Get data for surveys with matching prefix.

**Parameters:**
- `groupPrefix` (path) - Survey title prefix (e.g., `SB055` for all SB055 surveys)
- `full` (query) - Set to `true` for complete dataset (default: `false`)

**Frontend Usage:**
```javascript
const getSurveyGroupData = async (groupPrefix, full = false) => {
  const url = `https://ansebmrsurveysv1.oa.r.appspot.com/api/survey-group/${groupPrefix}${full ? '?full=true' : ''}`;
  const response = await fetch(url);
  return await response.json();
};

// Get all SB055 surveys
const sb055Data = await getSurveyGroupData('SB055');
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
      "filename": "SB055_Profile_Survey1.json",
      "response_count": 1500,
      "file_size_mb": 67.8
    }
  ]
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
    "total_responses": 1500,
    "total_surveys": 5,
    "date_range": {
      "earliest": "2025-01-01",
      "latest": "2025-12-31"
    }
  },
  "overall_demographics": {
    "gender": {
      "Male": 750,
      "Female": 650,
      "Other": 100
    },
    "age_groups": {
      "18-24": 200,
      "25-34": 500,
      "35-44": 400,
      "45-54": 300,
      "55+": 100
    },
    "employment": {
      "Employed": 1200,
      "Unemployed": 200,
      "Student": 100
    }
  },
  "cross_tabulations": {
    "gender_by_age": {
      "Male": {
        "18-24": 100,
        "25-34": 250,
        "35-44": 200
      }
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
  "total_responses": 1500,
  "data": [...],
  "exported_at": "2025-01-20T10:30:00Z"
}
```

**Response (CSV):**
```csv
ts,title,q,resp,pid,gender,age_group,salary,employment,location,sem_segment
2025-01-15T10:30:00Z,SB055_Profile_Survey1,What is your age group?,25-34,profile_123,Male,25-34,R15,000 - R25,000,Employed,Gauteng,High Value
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
    "title": "survey_title",
    "q": "question_text",
    "resp": "response_text",
    "pid": "profile_id",
    "gender": "Gender",
    "age_group": "Age-Group",
    "salary": "Monthly Personal Income",
    "employment": "Employment",
    "location": "Location",
    "sem_segment": "SEM Segment",
    "sem_score": "SEM Score"
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
  "status": "healthy",
  "uptime": "2h 30m 15s",
  "cache_size": 5,
  "cache_hits": 150,
  "cache_misses": 10,
  "memory_usage": "45.2 MB",
  "timestamp": "2025-01-20T10:30:00Z"
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
  "timestamp": "2025-01-20T10:30:00Z"
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
- Pagination is recommended for large datasets
- Use specific survey endpoints for better performance
- Demographics endpoint provides pre-computed data for faster dashboard loading

## 📱 CORS Support

All endpoints support CORS for frontend integration. No additional configuration needed.

---

**Last Updated:** January 2025  
**API Version:** 1.0  
**Base URL:** https://ansebmrsurveysv1.oa.r.appspot.com
