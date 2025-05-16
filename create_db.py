from flask import Flask
from models import db
from dotenv import load_dotenv
import os

# Carrega variáveis do .env
load_dotenv()

app = Flask(__name__)

# Configura o app
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv('SECRET_KEY')

# Inicializa o banco
db.init_app(app)

# Cria as tabelas no arquivo SQLite
with app.app_context():
    db.create_all()
    print("Tabelas criadas com sucesso!")
