# 📊 Data Analysis Tool - Backend

Django REST Framework backend for AI-powered data analysis using Google Gemini.

## 🎯 What We're Building

An intelligent data analysis system that uses Google Gemini AI to automatically analyze CSV datasets and provide insights, recommendations, and automated analysis workflows.

## 🏗️ Current Project Structure

```
backend/
├── tool_APIs/
│   ├── tool_APIs/           # Django settings & main URLs
│   ├── analysis_app/        # Our main app
│   │   ├── views.py         # API logic
│   │   ├── urls.py          # API routes
│   │   └── templates/       # Test UI
│   |                 # API keys (DO NOT COMMIT)
│   └── manage.py
├── .env
├── requirements.txt
└── pyproject.toml
```

## ⚡ Quick Start

1. **Install dependencies**
```bash
cd backend
pip install -r requirements.txt # or: uv pip install -r requirements.txt
```

2. **Set up your API key**

Create `backend/.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```
Get your key: https://aistudio.google.com/app/apikey

3. **Run the server**
```bash
cd tool_APIs
python manage.py migrate
python manage.py runserver
```

Visit: http://localhost:8000/api/analysis/analyzer/

## 📡 Current API Endpoints

### 1. Dataset Description (✅ Complete)
`POST /api/analysis/dataset-description/`

Upload CSV → Get AI analysis with insights, data quality assessment, and recommendations.

**Test it:**
- Web UI: http://localhost:8000/api/analysis/analyzer/
- cURL: `curl -X POST http://localhost:8000/api/analysis/dataset-description/ -F "file=@data.csv"`

## 🚧 TODO - Next Features to Implement

### High Priority
- [ ] **Visualization Suggestions Endpoint**
  - Analyze dataset and suggest appropriate chart types
  - Return chart configurations based on data types
  - Endpoint: `/api/analysis/suggest-visualizations/`

- [ ] **AI Chat Assistant Endpoint**
  - Real-time Q&A about uploaded datasets
  - Natural language queries like "What's the average age?" or "Show me correlations"
  - Endpoint: `/api/analysis/chat/`

### Medium Priority
- [ ] **Data Cleaning Endpoint**
  - Automatic missing value detection and handling
  - Outlier identification
  - Data type corrections

- [ ] **Report Generation**
  - PDF/Word export of analysis results
  - Include visualizations and insights

### Future Enhancements
- [ ] User authentication (JWT)
- [ ] Task queue for large datasets (Celery + Redis)
- [ ] PostgreSQL database
- [ ] Web scraping agent
- [ ] Email automation

## 🛠️ Tech Stack

- **Framework**: Django 5.1 + Django REST Framework
- **AI**: Google Gemini 2.0 Flash Lite
- **Data**: Pandas, NumPy
- **LLM Tools**: LangChain (for future multi-agent workflows)

## 🧪 Testing Your Changes

1. Test the current endpoint with sample CSV
2. Check the web interface at `/api/analysis/analyzer/`
3. Verify JSON response format matches expected structure

## 📝 For Teammates

### Adding New Endpoints
1. Add your function in `analysis_app/views.py`
2. Register route in `analysis_app/urls.py`
3. Test with cURL or web interface
4. Update this README with new endpoint info

### Important Files
- `views.py` - All API logic goes here
- `urls.py` - Route definitions
- `.env` - Your API keys (never commit this!)
- `settings.py` - Django configuration

### Common Issues
- **Rate limit error**: Gemini free tier = 15 requests/minute. Wait 30 seconds.
- **CORS error**: Add your frontend URL to `CORS_ALLOWED_ORIGINS` in settings.py
- **Import errors**: Run `uv sync` or reinstall requirements

## 🤝 Git Workflow

```bash
git checkout -b feature/your-feature-name
# Make your changes
git add .
git commit -m "Add: your feature description"
git push origin feature/your-feature-name
# Create pull request
```

## 📞 Questions?

Text me immediately

---
**Status**: Active Development 🚧  
**Last Updated**: November 28, 2025