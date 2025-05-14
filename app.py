from flask import Flask, render_template, request, redirect, session, flash
from database import db
from config import Config
from models import db
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from dotenv import load_dotenv
# from routes import bp  # Quando for usar Blueprints

load_dotenv()





app = Flask(__name__, static_folder='static/Assents')
app.secret_key = 'dotapet'

user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
dbname = os.getenv("DB_NAME")

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{user}:{password}@{host}/{dbname}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



# app.register_blueprint(bp)  # Descomente quando for usar Blueprints

class Pet(db.Model):
    __tablename__ = 'pets'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    especie = db.Column(db.String(40), nullable=False)
    sexo = db.Column(db.Enum('Fêmea', 'Macho'), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    tamanho = db.Column(db.Enum('Pequeno', 'Medio', 'Grande'), nullable=False)
    disponivel = db.Column(db.Boolean, nullable=False)
    data_cadastro = db.Column(db.DateTime, nullable=False)
    foto_url = db.Column(db.String(255), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)




class Cadastro(db.Model):
    __tablename__ = 'cadastros'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    sobrenome = db.Column(db.String(50), nullable=False)
    data_nascimento = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    telefone = db.Column(db.String(20), nullable=False)
    pet_preferido = db.Column(db.String(50), nullable=True)

    def __init__(self, nome, sobrenome, data_nascimento, email, telefone, pet_preferido):
        self.nome = nome
        self.sobrenome = sobrenome
        self.data_nascimento = data_nascimento
        self.email = email
        self.telefone = telefone
        self.pet_preferido = pet_preferido



class Adocao(db.Model):
    __tablename__ = 'adocoes'
    id = db.Column(db.Integer, primary_key=True)
    data_adocao = db.Column(db.DateTime, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.id'), nullable=False)

    # Relacionamento com as tabelas 'usuarios' e 'pets'
    usuario = db.relationship('Usuario', backref='adocoes', lazy=True)
    pet = db.relationship('Pet', backref='adocoes', lazy=True)


class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    data_cadastro = db.Column(db.DateTime, nullable=False)

    def __init__(self, nome, email, senha, telefone, data_cadastro):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.telefone = telefone
        self.data_cadastro = data_cadastro



class DoacaoFinanceira(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    valor = db.Column(db.Float, nullable=False)
    metodo_pagamento = db.Column(db.String(20), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    data_doacao = db.Column(db.DateTime, nullable=False)

    def __init__(self, valor, metodo_pagamento, usuario_id, data_doacao):
        self.valor = valor
        self.metodo_pagamento = metodo_pagamento
        self.usuario_id = usuario_id
        self.data_doacao = data_doacao


class DoacaoPet(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    status = db.Column(db.Enum('pendente', 'adotado', 'cancelado'), default='pendente')
    data_doacao = db.Column(db.DateTime, nullable=False)

    pet = db.relationship('Pet', backref='doacao_pets', lazy=True)
    usuario = db.relationship('Usuario', backref='doacao_pets', lazy=True)

    def __init__(self, pet_id, usuario_id, status, data_doacao):
        self.pet_id = pet_id
        self.usuario_id = usuario_id
        self.status = status
        self.data_doacao = data_doacao

    def __repr__(self):
        return f'<DoacaoPet {self.id} - Pet ID: {self.pet_id}, Usuário ID: {self.usuario_id}, Status: {self.status}>'

        







@app.route('/')
def home():
    return render_template('index.html', titulo="DotaPet")

@app.route('/anunciar', methods=['GET', 'POST'])
def anunciar():
    if request.method == 'POST':
        nome = request.form['nome']
        especie = request.form['especie']
        sexo = request.form['sexo']
        tamanho = request.form['tamanho']
        idade = request.form['idade']
        pet = Pet(nome=nome, especie=especie, sexo=sexo, tamanho=tamanho, idade=idade)
        db.session.add(pet)
        db.session.commit()  # Persistindo no banco de dados
        flash('Pet anunciado com sucesso!')
        return redirect('/animais')
    return render_template('anunciar.html')



@app.route('/animais')
def listar_animais():
    animais = Pet.query.filter_by(status='disponivel').all()
    return render_template('animais.html', animais=animais)



@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/autenticar', methods=['POST',])
def autenticar():
    if 'dotapet' == request.form['senha']:
        session['usuario_logado'] = request.form['email']
        flash(session['usuario_logado'] + 'Usuário logado com sucesso!')
        return redirect('/')
    else:
        flash('Usuario não logado')
        return redirect('/login')



@app.route('/cadastro', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        nome = request.form['nome']
        sobrenome = request.form['sobrenome']
        nascimento = request.form['nascimento']
        email = request.form['email']
        telefone = request.form['telefone']
        pet_preferido = request.form['pet']

        cadastro = Cadastro(nome, sobrenome, nascimento, email, telefone, pet_preferido)
        return redirect('/login')

    return render_template('cadastro.html')








if __name__ == '__main__':
    app.run(debug=True)










'''from flask import Flask, render_template, request, redirect, url_for, flash
from config import Config
from models import db, Pets, Usuario
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

@app.route('/')
def home():
    return render_template('index.html', titulo="DotaPet")

# --- Página de Anúncio de Pet ---
@app.route('/anunciar', methods=['GET', 'POST'])
def anunciar():
    if request.method == 'POST':
        nome = request.form['nome']
        especie = request.form['especie']
        sexo = request.form['sexo']
        tamanho = request.form['tamanho']
        descricao = request.form['descricao']
        foto_url = request.form['foto_url']
        usuario_id = 1  # Exemplo fixo, ideal pegar do login
        novo_pet = Pets(
            nome=nome,
            especie=especie,
            sexo=sexo,
            tamanho=tamanho,
            descricao=descricao,
            disponivel=True,
            data_cadastro=datetime.now(),
            foto_url=foto_url,
            usuario_id=usuario_id
        )
        db.session.add(novo_pet)
        db.session.commit()
        flash('Pet anunciado com sucesso!')
        return redirect(url_for('listar_animais'))

    return render_template('anunciar.html')

# --- Página que lista todos os animais disponíveis ---
@app.route('/animais')
def listar_animais():
    animais = Pets.query.filter_by(disponivel=True).all()
    return render_template('animais.html', animais=animais)

# --- Página de login (somente exibe o formulário por enquanto) ---
@app.route('/login')
def login():
    return render_template('login.html')

# --- Cadastro de novo usuário ---
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']  # Ideal: aplicar hash
        telefone = request.form['telefone']

        novo_usuario = Usuario(
            nome=nome,
            email=email,
            senha=senha,
            telefone=telefone,
            data_cadastro=datetime.now()
        )
        db.session.add(novo_usuario)
        db.session.commit()
        flash('Usuário cadastrado com sucesso!')
        return redirect(url_for('home'))

    return render_template('cadastro.html')

if __name__ == '__main__':
    app.run(debug=True)
'''