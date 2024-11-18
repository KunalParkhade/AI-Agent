from flask import Blueprint, render_template, request, redirect, url_for, flash
import pandas as pd
import os

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
        # Check if a file is uploaded
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
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
        
    
    return render_template('upload.html')