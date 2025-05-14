import mysql.connector
from mysql.connector import errorcode
from dotenv import load_dotenv
import os


# Carregar as variáveis do .env
load_dotenv()

# Puxando as variáveis de ambiente
host = os.getenv('DB_HOST')
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
database = os.getenv('DB_NAME')

print("Conectando...")

try:
    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print('Existe algo errado no nome de usuário ou senha')
    else:
        print(err)

cursor = conn.cursor()


TABLES = {}

TABLES['Usuarios'] = ('''
      CREATE TABLE `usuarios` (
      `id` INT(11) NOT NULL AUTO_INCREMENT,
      `nome` VARCHAR(100) NOT NULL,
      `email` VARCHAR(100) NOT NULL,
      `senha` VARCHAR(255) NOT NULL,
      `telefone` CHAR(11) NOT NULL,
      `data_cadastro` DATETIME NOT NULL,
      PRIMARY KEY (`id`)
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;''')

TABLES['Pets'] = ('''
      CREATE TABLE `pets` (
      `id` INT(11) NOT NULL AUTO_INCREMENT,
      `nome` VARCHAR(100) NOT NULL,
      `especie` VARCHAR(40) NOT NULL,
      `sexo` ENUM('Fêmea', 'Macho') NOT NULL,
      `descricao` TEXT NOT NULL,
      `tamanho` ENUM('Pequeno', 'Medio','Grande') NOT NULL,
      `disponivel` BOOL NOT NULL,
      `data_cadastro` DATETIME NOT NULL,
      `foto_url` VARCHAR(255) NOT NULL,
      `usuario_id` INT(11) NOT NULL,
      PRIMARY KEY (`id`),
      FOREIGN KEY (`usuario_id`) REFERENCES `usuarios`(`id`)
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;''')

TABLES['Doacoes'] = ('''
      CREATE TABLE `doacoes` (
      `id` INT(11) NOT NULL AUTO_INCREMENT,
      `valor` FLOAT NOT NULL,
      `metodo_pagamento` ENUM('Pix', 'Credito', 'Debito', 'Boleto') NOT NULL,
      `data_doacao` DATETIME NOT NULL,
      `usuario_id` INT(11) NOT NULL,
      PRIMARY KEY (`id`),
      FOREIGN KEY (`usuario_id`) REFERENCES `usuarios`(`id`)
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;''')

TABLES['adocoes'] = ('''
                     
      CREATE TABLE `adocoes` (
    `id` INT(11) NOT NULL AUTO_INCREMENT,
    `data_adocao` DATETIME NOT NULL,
    `usuario_id` INT(11) NOT NULL,
    `pet_id` INT(11) NOT NULL,
    PRIMARY KEY (`id`),
    FOREIGN KEY (`usuario_id`) REFERENCES `usuarios`(`id`),
    FOREIGN KEY (`pet_id`) REFERENCES `pets`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
'''  )


for tabela_nome in TABLES:
      tabela_sql = TABLES[tabela_nome]
      try:
            print('Criando tabela {}:'.format(tabela_nome), end=' ')
            cursor.execute(tabela_sql)
      except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                  print('Já existe')
            else:
                  print(err.msg)
      else:
            print('OK')