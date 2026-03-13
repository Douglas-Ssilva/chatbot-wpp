# Importa a classe principal do FastAPI
# Ela é responsável por criar a aplicação da API
from fastapi import FastAPI

# Importa o arquivo webhook que está dentro da pasta app/routers
# Esse arquivo contém as rotas relacionadas ao webhook
from app.routers import webhook


# Cria a aplicação principal da API
# O parâmetro title define o nome que aparecerá na documentação automática (Swagger)
app = FastAPI(title='Chatbot Academy')


# Inclui (registra) as rotas do arquivo webhook dentro da aplicação principal
# Isso faz com que as rotas definidas em webhook.router passem a funcionar na API
app.include_router(webhook.router)
 