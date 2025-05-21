import os
import urllib.parse
from dotenv import load_dotenv

# Carrega o .env
load_dotenv()

class Config:
    # Chave secreta do Flask
    SECRET_KEY = os.getenv('SECRET_KEY')

    # Caminho do banco SQLite
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

    # Desabilita rastreamento de modificações (melhora desempenho)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Pasta para uploads, se estiver usando
    UPLOAD_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static' 'uploads')
    
    
