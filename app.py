from flask import Flask, render_template, request, redirect, session, flash, url_for, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from sqlalchemy import Enum
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os 
from dotenv import load_dotenv
from flask_mail import Mail, Message
#import sqlite3
import threading
from functools import wraps
#from werkzeug.utils import secure_filename
#import uuid


load_dotenv()

app = Flask(__name__, static_folder='static/Assents')

# Configuração do Flask-Mail com base no .env
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

mail = Mail(app)

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
    nascimento = db.Column(db.Date, nullable=True) 



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
    sexo = db.Column(Enum('Fêmea', 'Macho', 'female', 'male', name='sexo_enum'), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    tamanho = db.Column(db.String(20), nullable=False)
    disponivel = db.Column(db.Boolean, nullable=False, default=True)
    data_cadastro = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    foto_url = db.Column(db.String(255), nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    idade = db.Column(db.String(10), nullable=False)


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
    status = db.Column(db.Enum('pendente', 'adotado', 'cancelado', name='status_enum'), default='pendente')
    data_doacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<DoacaoPet {self.id} - Pet ID: {self.pet_id}, Usuario ID: {self.usuario_id}, Status: {self.status}>'

# -------- FUNÇÕES DE LOGIN --------

@lm.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))




def enviar_email_assincrono(app, msg):
    with app.app_context():
        mail.send(msg)

# -------- ROTAS --------

@app.route('/')
def home():
    return render_template('index.html', titulo="DotaPet")

#@app.route('/adoacao')
#def home():
#    return render_template('adoacao.html', titulo="DotaPet")

@app.route("/home")
def pagina_principal():
    return render_template('home.html') 


@app.route("/busca")
def busca():
    return render_template('busca.html')


@app.route("/conheca")
def pagina_conheca():
    return render_template("conheca.html")

@app.route("/listar_animais")
def pagina_adocao():
    return render_template("animais.html")


@app.route("/ajude")
def ajude():
    return render_template("ajuda.html")





#@app.route("/adotar")
#def adotar():
#    return render_template("adotar.html")






@app.route('/esqueceu_senha', methods=['GET', 'POST'])
def esqueceu_senha():
    if request.method == 'POST':
        email = request.form.get('email')

        # Buscar o usuário no banco de dados
        usuario = Usuario.query.filter_by(email=email).first()
        print(f"Usuário encontrado: {usuario.nome}, email: {usuario.email}, senha: {usuario.senha}")


        if usuario:
            try:
                # Enviar a senha por e-mail
                msg = Message(
                    subject='Recuperação de Senha - Dotapet',
                    sender=app.config['MAIL_USERNAME'],
                    recipients=[email],
                    body=f'Olá {usuario.nome},\n\nSua senha atual é: {usuario.senha}\n\nRecomendamos que você a altere após acessar sua conta.'
                )
                threading.Thread(target=enviar_email_assincrono, args=(app, msg)).start()
                flash('E-mail enviado com sucesso! Verifique sua caixa de entrada.', 'success')


            except Exception as e:
                flash(f'Erro ao enviar e-mail: {e}', 'danger')
        else:
            flash('E-mail não encontrado.', 'danger')

    return render_template('esqueceu_senha.html')


@app.route('/anunciar', methods=['GET', 'POST'])
def anunciar():
    # Se o método for POST (após um envio de formulário, por exemplo), redireciona para /animais
    if request.method == 'POST':
        return redirect('/animais')
    
    # Se o método for GET (quando o usuário acessa a página para visualizar o formulário), renderiza a página de anúncio
    return render_template('anunciar.html')

    






@app.route("/login", methods=["GET", "POST"])
def login():
    erro = None

    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["password"]
        

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and usuario.senha == senha:
            login_user(usuario)  # <-- aqui é a correção!

            try:
                msg = Message(
                    subject='Bem-vindo de volta!!',
                    sender=app.config['MAIL_USERNAME'],
                    recipients=[email],
                    body=f'Olá {usuario.nome},\n\nBem-vindo de volta, seu animalzinho está feliz em te ver! \n\nÉ sempre uma honra vê-lo por aqui.😁'
                )
                threading.Thread(target=enviar_email_assincrono, args=(app, msg)).start()

            except Exception as e:
                print(f"Erro ao enviar e-mail: {e}")
                erro = "Erro ao enviar o e-mail. Tente novamente mais tarde."

            next_page = request.args.get('next')
            return redirect(next_page or url_for('pagina_principal'))

        else:
            erro = "E-mail ou senha inválidos. Tente novamente."




    return render_template("login.html", erro=erro)


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
        nascimento_str = request.form.get('nascimento')
        nascimento = datetime.strptime(nascimento_str, "%Y-%m-%d").date() if nascimento_str else None

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
            pet_preferido_id=pet_preferido_id,
            nascimento=nascimento,
            data_cadastro=datetime.utcnow()
        )
        db.session.add(novo_usuario)
        db.session.commit()

        # === ENVIO DO E-MAIL ===
        try:
            msg = Message(
                subject='Cadastro realizado com sucesso!',
                sender=app.config['MAIL_USERNAME'],
                recipients=[email],
                body=f'Olá {nome},\n\nSeu cadastro foi concluído com sucesso!\n\nObrigado por se registrar.\n Seja Bem-Vindo a DotaPet'
            )
            threading.Thread(target=enviar_email_assincrono, args=(app, msg)).start()

        except Exception as e:
            print(f"Erro ao enviar email: {e}")

        flash('Usuário cadastrado com sucesso!')
        return redirect(url_for('login'))

    return render_template('cadastro.html')


@app.route("/verifica-login")
def verifica_login():
    prox = request.args.get("prox")

    if "usuario_id" in session:
        return redirect(url_for(prox))  # redireciona para a rota desejada se estiver logado
    else:
        return redirect(url_for("login", prox=prox))  # envia para o login com parâmetro de retorno
    

@app.route('/animais')
def listar_animais():
    pets = Pet.query.all()  # Consulta todos os pets cadastrados
    return render_template('animais.html', pets=pets)  # Passa os pets para o template





if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Cria as tabelas no banco caso não existam
    app.run(debug=True)
