# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
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


class Doacao(db.Model):
    __tablename__ = 'doacoes'

    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Float, nullable=False)
    metodo_pagamento = db.Column(db.Enum('Pix', 'Credito', 'Debito', 'Boleto'), nullable=False)
    data_doacao = db.Column(db.DateTime, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
