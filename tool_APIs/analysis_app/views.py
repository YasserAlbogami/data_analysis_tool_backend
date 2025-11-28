# analysis_app/views.py
from rest_framework.decorators import api_view
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
import pandas as pd
import io
import json
from datetime import datetime
import google.generativeai as genai
import os
from dotenv import load_dotenv
from django.shortcuts import render

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))




def get_dataset_info(df):
    """
    Extract dataset information using pandas methods
    """
    # Get df.head() as string
    head_str = df.head().to_string()
    
    # Get df.describe() as string
    describe_str = df.describe().to_string()
    
    # Get df.info() as string
    buffer = io.StringIO()
    df.info(buf=buffer)
    info_str = buffer.getvalue()
    
    return {
        'head': head_str,
        'describe': describe_str,
        'info': info_str
    }

def analyze_with_gemini(dataset_info, df):
    """
    Send dataset information to Gemini for analysis
    """
    try:
        # Use gemini-1.5-flash instead of experimental model (more stable and higher limits)
        model = genai.GenerativeModel('gemini-2.0-flash-lite')
        
        prompt = f"""
You are a data analyst. Analyze the following dataset information and provide a comprehensive description.

Dataset Head (first 5 rows):
{dataset_info['head']}

Dataset Description (statistical summary):
{dataset_info['describe']}

Dataset Info (column types and non-null counts):
{dataset_info['info']}

Please provide a detailed analysis in the following JSON format:
{{
    "dataset_description": "A comprehensive 2-3 paragraph description of the dataset, including what type of data it contains, the main features, and any notable patterns or characteristics you observe.", what does it represent you must include that
    "key_insights": [
        "List 3-5 key insights about the data"
    ],
    "data_quality": {{
        "completeness": "Assessment of missing values",
        "potential_issues": ["List any potential data quality issues"]
    }},
    "recommendations": [
        "List 2-3 recommendations for analysis or data cleaning"
    ]
}}

Return ONLY the JSON object, no additional text or markdown.
"""
        
        response = model.generate_content(prompt)
        
        # Parse the response
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith('```json'):
            response_text = response_text.replace('```json', '').replace('```', '').strip()
        elif response_text.startswith('```'):
            response_text = response_text.replace('```', '').strip()
        
        analysis = json.loads(response_text)
        return analysis
        
    except Exception as e:
        error_msg = str(e)
        print(f"Gemini API Error: {error_msg}")
        
        # Enhanced fallback response with more detailed analysis
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        missing_summary = df.isnull().sum()
        missing_cols = missing_summary[missing_summary > 0].to_dict()
        
        # Check if it's a rate limit error
        if "429" in error_msg or "quota" in error_msg.lower():
            api_status = "Rate limit exceeded. Using fallback analysis."
        else:
            api_status = f"API unavailable: {error_msg[:100]}. Using fallback analysis."
        
        return {
            "dataset_description": f"This dataset contains {len(df)} records across {len(df.columns)} features. "
                                 f"It includes {len(numeric_cols)} numerical columns ({', '.join(numeric_cols[:3])}{', ...' if len(numeric_cols) > 3 else ''}) "
                                 f"and {len(categorical_cols)} categorical columns ({', '.join(categorical_cols[:3])}{', ...' if len(categorical_cols) > 3 else ''}). "
                                 f"The dataset shows {'minimal' if df.isnull().sum().sum() < len(df) * 0.05 else 'significant'} missing data patterns. "
                                 f"Note: {api_status}",
            "key_insights": [
                f"Total records: {len(df):,}",
                f"Total features: {len(df.columns)}",
                f"Numerical features: {len(numeric_cols)}",
                f"Categorical features: {len(categorical_cols)}",
                f"Missing values: {df.isnull().sum().sum():,} ({(df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100):.2f}%)"
            ],
            "data_quality": {
                "completeness": f"Missing values found in {len(missing_cols)} columns" if missing_cols else "No missing values detected",
                "potential_issues": [f"{col}: {count} missing" for col, count in list(missing_cols.items())[:5]] if missing_cols else ["Data appears complete"]
            },
            "recommendations": [
                "Examine distribution of numerical features for outliers",
                "Check categorical variables for consistency",
                "Consider feature engineering based on domain knowledge"
            ]
        }

@api_view(['GET', 'POST'])
def dataset_description(request):
    """
    Upload CSV file and get AI-powered dataset description
    POST /api/analysis/dataset-description/
    
    Form Data:
    - file: CSV file
    """
    # Handle GET request - show instructions
    if request.method == 'GET':
        return Response({
            'message': 'Upload a CSV file to get dataset description',
            'instructions': 'Use POST method with form-data and attach a CSV file with key "file"',
            'endpoint': '/api/analysis/dataset-description/',
            'method': 'POST',
            'content_type': 'multipart/form-data',
            'example_curl': 'curl -X POST http://localhost:8000/api/analysis/dataset-description/ -F "file=@your_file.csv"'
        })
    
    # Handle POST request - process uploaded file
    try:
        # Check if file is in request
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file uploaded. Please upload a CSV file.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        csv_file = request.FILES['file']
        
        # Validate file extension
        if not csv_file.name.endswith('.csv'):
            return Response(
                {'error': 'Invalid file type. Please upload a CSV file.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Read CSV file
        try:
            df = pd.read_csv(csv_file)
        except Exception as e:
            return Response(
                {'error': f'Error reading CSV file: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if dataframe is empty
        if df.empty:
            return Response(
                {'error': 'The uploaded CSV file is empty.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get dataset information
        dataset_info = get_dataset_info(df)
        
        # Get AI analysis from Gemini
        gemini_analysis = analyze_with_gemini(dataset_info, df)
        
        # Calculate basic metrics
        metrics = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'column_names': df.columns.tolist(),
            'column_types': df.dtypes.astype(str).to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'total_missing': int(df.isnull().sum().sum()),
            'memory_usage_mb': round(df.memory_usage(deep=True).sum() / 1024**2, 2),
            'numeric_columns': df.select_dtypes(include=['number']).columns.tolist(),
            'categorical_columns': df.select_dtypes(include=['object']).columns.tolist(),
        }
        
        # Combine everything into final response
        response_data = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'filename': csv_file.name,
            'dataset_description': gemini_analysis.get('dataset_description', ''),
            'key_insights': gemini_analysis.get('key_insights', []),
            'data_quality': gemini_analysis.get('data_quality', {}),
            'recommendations': gemini_analysis.get('recommendations', []),
            'metrics': metrics,
        }
        print(f"Check Point the response data is:\n{response_data}")
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'An error occurred: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
def home_page(request):
    
    return render(request, template_name="analysis_app/index.html")