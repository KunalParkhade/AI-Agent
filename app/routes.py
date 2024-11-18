from flask import Blueprint, render_template, request, redirect, url_for, flash
import pandas as pd
import os
from app.utils.google_sheets import connect_to_google_sheets
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

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
    
    return render_template('upload.html')

@routes.route('/process_query', methods=['POST'])
def process_query():
    global data
    query = request.form.get('query')
    
    if not query:
        flash("Please enter a query.")
        return redirect(url_for('routes.upload_file'))

    try:
        # Simple example of processing queries
        if query.lower() == 'select top 10 rows':
            result = data.head(10)
        else:
            # Dynamic query processing based on the string (you can extend this logic)
            result = data.query(query)

        # Ensure the result is a DataFRame
        if isinstance(result, pd.Series):
            result = result.to_frame()  
        
        preview = result.to_html(classes='table table-bordered')
        return render_template('upload.html', preview=preview, columns=data.columns.tolist())

    except Exception as e:
        flash(f"Error processing query: {e}")
        return redirect(url_for('routes.upload_file'))