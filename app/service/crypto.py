"""
Projeto que teremos flexibilidade de usar várias IAs,
cada uma atendendo um cliente específico
"""

import os
# Biblioteca padrão do Python usada aqui para acessar variáveis de ambiente.

# Importa a função que carrega automaticamente as variáveis definidas no arquivo .env.
from dotenv import load_dotenv

# Biblioteca padrão usada para converter dicionários Python em JSON e vice-versa.
import json

# Importa a classe Fernet responsável por realizar criptografia simétrica (encrypt/decrypt).
from cryptography.fernet import Fernet

# Lê o arquivo .env e carrega as variáveis para que possam ser acessadas com os.getenv().
load_dotenv()

# Busca a variável de ambiente chamada FERNET_KEY. Se não existir no ambiente, retornará None.
FERNET_KEY = os.getenv('FERNET_KEY')


# Cria a instância de criptografia. .encode() transforma a string da chave em bytes, pois o Fernet trabalha com bytes.
fernet = Fernet(FERNET_KEY.encode())


def encrypt_data(data: dict) -> str:

    # Converte o dicionário Python em uma string JSON.
    json_data = json.dumps(data)

    # json_data.encode() → converte string para bytes fernet.encrypt() → criptografa os bytes .decode() → converte os bytes criptografados em string
    encrypted_data = fernet.encrypt(json_data.encode()).decode()
    return encrypted_data
    


def decrypt_data(data: str) -> dict:

    # data.encode() → transforma a string criptografada em bytes fernet.decrypt() → descriptografa e retorna bytes do JSON original
    decrypted_data = fernet.decrypt(data.encode())

    # .decode() → converte bytes para string JSON json.loads() → converte JSON para dicionário Python
    data_json = json.loads(decrypted_data.decode())
    return data_json


# print(decrypt_data(encrypt_data({'teste':'teste'})))
