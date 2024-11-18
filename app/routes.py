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

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@routes.route('/', methods=['GET', 'POST'])
def upload_file():
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
                df = pd.read_csv(filepath)
                preview = df.head().to_html(classes='table table-bordered')

                return render_template('upload.html', preview=preview, columns=df.columns.tolist())
        
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
                df = pd.DataFrame(data)
                preview = df.head().to_html(classes='table table-bordered')
                return render_template('upload.html', preview=preview, columns=df.columns.tolist())
            
            except Exception as e:
                flash(f"Error connecting to Google Sheets: {e}")
                return redirect(request.url)
        
        else:
            flash("Please either upload a CSV file or provide a Google Sheet ID.")
            return redirect(request.url)
    
    return render_template('upload.html')
