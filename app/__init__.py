from flask import Flask
from app.routes import routes

from dotenv import load_dotenv
import os

def create_app():
    load_dotenv(dotenv_path=os.path.join(os.getcwd(), 'app', 'config', '.env'))
    
    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY')
    app.register_blueprint(routes)
    return app
