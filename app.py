from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='static/Assents')

# Configurações
app.secret_key = os.getenv('SECRET_KEY') or 'minha_chave_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dotapet.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar banco e login manager
db = SQLAlchemy(app)
lm = LoginManager(app)
lm.login_view = 'login'  # rota para redirecionar quando precisar logar

# -------- MODELOS --------

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    sobrenome = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    senha = db.Column(db.String(255), nullable=False)
    telefone = db.Column(db.String(20), nullable=True)
    data_cadastro = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    pet_preferido_id = db.Column(db.String(10))

    # Relações com outros modelos
    pets = db.relationship('Pet', backref='usuario', lazy=True)
    adocoes = db.relationship('Adocao', backref='usuario', lazy=True)
    doacoes_financeiras = db.relationship('DoacaoFinanceira', backref='usuario', lazy=True)
    doacoes_pet = db.relationship('DoacaoPet', backref='usuario', lazy=True)

    def __repr__(self):
        return f'<Usuario {self.nome}>'


class Pet(db.Model):
    __tablename__ = 'pets'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    especie = db.Column(db.String(40), nullable=False)
    sexo = db.Column(db.Enum('Fêmea', 'Macho'), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    tamanho = db.Column(db.Enum('Pequeno', 'Medio', 'Grande'), nullable=False)
    disponivel = db.Column(db.Boolean, nullable=False, default=True)
    data_cadastro = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    foto_url = db.Column(db.String(255), nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

    adocoes = db.relationship('Adocao', backref='pet', lazy=True)
    doacoes_pet = db.relationship('DoacaoPet', backref='pet', lazy=True)

    def __repr__(self):
        return f'<Pet {self.nome}>'


class Adocao(db.Model):
    __tablename__ = 'adocoes'
    id = db.Column(db.Integer, primary_key=True)
    data_adocao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.id'), nullable=False)


class DoacaoFinanceira(db.Model):
    __tablename__ = 'doacoes_financeiras'
    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Float, nullable=False)
    metodo_pagamento = db.Column(db.String(20), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    data_doacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class DoacaoPet(db.Model):
    __tablename__ = 'doacoes_pet'
    id = db.Column(db.Integer, primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    status = db.Column(db.Enum('pendente', 'adotado', 'cancelado'), default='pendente')
    data_doacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<DoacaoPet {self.id} - Pet ID: {self.pet_id}, Usuario ID: {self.usuario_id}, Status: {self.status}>'

# -------- FUNÇÕES DE LOGIN --------

@lm.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# -------- ROTAS --------

@app.route('/')
def home():
    return render_template('index.html', titulo="DotaPet")

@app.route('/anunciar', methods=['GET', 'POST'])
@login_required
def anunciar():
    if request.method == 'POST':
        nome = request.form['nome']
        especie = request.form['especie']
        sexo = request.form['sexo']
        tamanho = request.form['tamanho']
        descricao = request.form['descricao']
        foto_url = request.form['foto_url']
        usuario_id = current_user.id  # usuário logado

        novo_pet = Pet(
            nome=nome,
            especie=especie,
            sexo=sexo,
            tamanho=tamanho,
            descricao=descricao,
            disponivel=True,
            foto_url=foto_url,
            usuario_id=usuario_id
        )
        db.session.add(novo_pet)
        db.session.commit()
        flash('Pet anunciado com sucesso!')
        return redirect(url_for('listar_animais'))

    return render_template('anunciar.html')

@app.route('/animais')
def listar_animais():
    animais = Pet.query.filter_by(disponivel=True).all()
    return render_template('animais.html', animais=animais)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and usuario.senha == senha:  # Aqui ideal usar hash/senha segura
            login_user(usuario)
            flash(f'Bem vindo {usuario.nome}!')
            return redirect(url_for('home'))
        else:
            flash('Email ou senha incorretos.')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Usuário deslogado.')
    return redirect(url_for('home'))

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        nome = request.form['nome']
        sobrenome = request.form.get('sobrenome', '')
        email = request.form['email']
        senha = request.form['senha']  # Ideal: hash
        telefone = request.form.get('telefone', '')
        pet_preferido_id = request.form.get('pet_preferido_id')

        # Verificar se usuário já existe
        if Usuario.query.filter_by(email=email).first():
            flash('E-mail já cadastrado.')
            return redirect(url_for('cadastrar'))

        novo_usuario = Usuario(
            nome=nome,
            sobrenome=sobrenome,
            email=email,
            senha=senha,
            telefone=telefone,
            data_cadastro=datetime.utcnow()
            
        )
        db.session.add(novo_usuario)
        db.session.commit()
        flash('Usuário cadastrado com sucesso!')
        return redirect(url_for('login'))

    return render_template('cadastro.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Cria as tabelas no banco caso não existam
    app.run(debug=True)
