import os
import urllib.parse
from dotenv import load_dotenv

# Carrega o .env
load_dotenv()
class Config:
# Variáveis do .env
    SECRET_KEY = os.getenv('SECRET_KEY')

    usuario = os.getenv('DB_USER')
    senha = urllib.parse.quote(os.getenv('DB_PASSWORD'))
    servidor = os.getenv('DB_HOST')
    database = os.getenv('DB_NAME')

    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{usuario}:{senha}@{servidor}/{database}'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_PATH = os.path.dirname(os.path.abspath(__file__)) + '/uploads'

    
