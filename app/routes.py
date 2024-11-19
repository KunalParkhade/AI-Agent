from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import pandas as pd
import os
from app.utils.google_sheets import connect_to_google_sheets
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import requests

from app.utils.search_api import search_bing

load_dotenv(dotenv_path=os.path.join(os.getcwd(), 'app', 'config', '.env'))

routes = Blueprint('routes', __name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
data = None  # To store the data globally for processing

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@routes.route('/', methods=['GET', 'POST'])
def upload_file():
    global data
    if request.method == 'POST':
        # Check if file is selected for upload
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            
            if file and allowed_file(file.filename):
                filepath = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(filepath)

                # Stores the file path in session
                session['uploaded_file_path'] = filepath

                # Load and preview CSV
                data = pd.read_csv(filepath)
                preview = data.head().to_html(classes='table table-bordered')

                return render_template('upload.html', preview=preview, columns=data.columns.tolist())
        
        # Check if Google Sheets Sheet ID is provided
        elif 'sheet_id' in request.form:
            sheet_id = request.form['sheet_id']

            if not sheet_id:
                flash("Google Sheet ID is required.")
                return redirect(request.url)

            try:
                # Fetch credentials from .env file
                credentials_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS')

                # Load credentials from the path
                credentials = Credentials.from_service_account_file(credentials_path)

                # Connect to Google Sheets
                data = connect_to_google_sheets(credentials_path, sheet_id)
                data = pd.DataFrame(data)
                preview = data.head().to_html(classes='table table-bordered')
                return render_template('upload.html', preview=preview, columns=data.columns.tolist())
            
            except Exception as e:
                flash(f"Error connecting to Google Sheets: {e}")
                return redirect(request.url)
        
        else:
            flash("Please either upload a CSV file or provide a Google Sheet ID.")
            return redirect(request.url)
        
    #If no POST request, check if a file is already uploaded
    uploaded_file_path = session.get('uploaded_file_path', None)
    if uploaded_file_path:
        try:
            # Load and preview the existing CSV
            df = pd.read_csv(uploaded_file_path)
            preview = df.head().to_html(classes='table table-bordered')
            return render_template('upload.html', preview=preview, columns=df.columns.tolist())
        except Exception as e:
            flash(f"Error loading existing file: {e}")
            session.pop('uploaded_file_path', None)
    
    return render_template('upload.html')

@routes.route('/process_query', methods=['POST'])
def process_query():
    global data
    query = request.form.get('query')
    
    # Ensure data is loaded
    if data is None:
        flash("No data available. Please upload a file or connect to Google Sheets first.")
        return redirect(url_for('routes.upload_file'))

    if not query:
        flash("Please enter a query.")
        return redirect(url_for('routes.upload_file'))

    try:
        # Simple example of processing queries
        if query.lower() == 'select top 10 rows':
            result = data.head(10)
        elif query.lower().startswith('filter'):
            # Example: "filter age > 30"
            condition = query[7:].strip()
            result = data.query(condition)
        elif query.lower().startswith('select columns'):
            # Example: "select columns name, age"
            columns = query[15:].strip().split(",")
            result = data[columns]
        else:
            # Dynamic query processing based on the string (you can extend this logic)
            result = data.query(query)

        # IF result is in pandas Series -->
        if isinstance(result, pd.Series):
            result = result.to_frame() 

        # Ensure result in pandas DataFrame
        if isinstance(result, pd.DataFrame):
            preview = result.to_html(classes='table table-bordered')
        else:
            raise ValueError("The result of the query is not a valid DataFrame or Series.")
        
        return render_template('upload.html', preview=preview, columns=data.columns.tolist())

    except Exception as e:
        flash(f"Error processing query: {e}")
        return redirect(url_for('routes.upload_file'))


@routes.route('/web_search', methods=['GET', 'POST'])
def web_search():
    if request.method == 'POST':
        query = request.form.get('query')
        if not query:
            flash("Please enter a search query.")
            return redirect(request.url)
        
        try:
            # Call the Bing API with the search query
            search_results = search_bing(query)

            # Extract relevant search result information
            web_pages = search_results.get('webPages', {}).get('value', [])
            return render_template('web_search.html', query=query, web_pages=web_pages)
        except Exception as e:
            flash(f"Error performing search: {e}")
            return redirect(request.url)
        
    return render_template('web_search.html')
    
    # query = request.form.get('search_query')

    # if not query:
    #     flash("Please enter a search query.")
    #     return render_template('upload.html', search_results=None, preview=None)
    
    # try:
    #     # Using Bing Search API
    #     api_key = os.getenv('BING_API_KEY')
    #     endpoint = "https://api.bing.microsoft.com/v7.0/search"
    #     headers = {"Ocp-Apim-Subscription-Key": api_key}
    #     params = {"q": query, "count": 10}

    #     response = requests.get(endpoint, headers=headers, params=params)
    #     response.raise_for_status()
    #     search_results = response.json()

    #     # Extract relevant data
    #     results = []
    #     for result in search_results.get('webPages', {}).get('value', []):
    #         results.append({"name": result["name"], "url": result["url"], "snippet": result["snippet"]})

    #     return render_template('upload.html', search_results=results, preview=None)
    
    # except Exception as e:
    #     flash(f"Error during web search: {e}")
    #     return render_template('upload.html', search_results=None, preview=None)