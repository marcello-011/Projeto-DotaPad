# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    sobrenome = db.Column(db.String(100), nullable=False)  # Adicionando sobrenome
    data_nascimento = db.Column(db.Date, nullable=False)  # Adicionando data de nascimento
    pet_preferido = db.Column(db.String(50), nullable=True)  # Adicionando pet preferido
    email = db.Column(db.String(100), nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    telefone = db.Column(db.String(11), nullable=False)
    data_cadastro = db.Column(db.DateTime, nullable=False)



class Pets(db.Model):
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


class Adocao(db.Model):
    __tablename__ = 'adocoes'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)  # Chave estrangeira
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.id'), nullable=False)  # Chave estrangeira para a tabela `pets`
    
    # Relacionamento com Usuario
    usuario = db.relationship(
        'Usuario',
        backref='adocoes',
        lazy=True,
        primaryjoin='Adocao.usuario_id == Usuario.id'  # Especificando explicitamente a condição de junção
    )
    pet = db.relationship('Pet', backref='adocoes', lazy=True)  # Relacionamento com `Pet`





#class Doacao(db.Model):
 ##
   # id = db.Column(db.Integer, primary_key=True)
    #valor = db.Column(db.Float, nullable=False)
    #metodo_pagamento = db.Column(db.Enum('Pix', 'Credito', 'Debito', 'Boleto'), nullable=False)
    #data_doacao = db.Column(db.DateTime, nullable=False)
    #usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
