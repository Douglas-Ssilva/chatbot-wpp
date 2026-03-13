# Importa do FastAPI:
# APIRouter → para criar grupos de rotas
# BackgroundTasks → para executar tarefas em segundo plano
# status → contém códigos HTTP prontos (200, 404, etc)
from fastapi import APIRouter, BackgroundTasks, status

from app.service.process import process_webhook

# Cria uma instância de roteador
# Ele será usado para registrar rotas separadas da aplicação principal
router = APIRouter()


# Decorator que define:
# - Método HTTP: POST
# - Caminho da rota: /webhook
# - Código de retorno padrão: 200 OK
@router.post('/webhook', status_code=status.HTTP_200_OK)

# Função assíncrona que será executada quando a rota for chamada
# async → permite execução assíncrona (melhor performance)
# data: dict → espera receber um JSON no corpo da requisição
# background_tasks → permite executar tarefas depois de responder
async def receive_webhook(data: dict, background_tasks: BackgroundTasks):
    """
    Endpoint que recebe os dados do webhook e processa em background.
    Essa string é chamada de docstring e serve como documentação.
    """

    try:
        
        background_tasks.add_task(process_webhook, data)
        return {"message": "Webhook recebido com sucesso. Process in background"}

    except Exception as ex:
        print(f'Error: {ex}')
        return {'message': 'Error'}
