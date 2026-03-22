import random
import time
import logging
import json

from app.database.manipulations import ia_manipulations, lead_manipulations
from app.service.queue_manager import get_phone_lock
from app.service.llm_response import IAresponse
from app.service.break_messages import *
from app.apis.evolution import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('PROCESS')

def process_webhook(data: dict):
    """
    Função para processar dados do webhook
    """

    logger.info('Processando webhook')

    try:
        # infos basicas
        ia_phone = data['sender'].split('@')[0]
        ia_name = data['instance']
        logger.debug('ia_phone: %s', ia_phone)

        # pesquisa em banco de qual ia direcionar
        ia_infos = ia_manipulations.filter_ia(ia_phone)

        if not ia_infos:
            raise Exception('IA not found with this phone number in our database')

        if ia_infos.status is not True:
            raise Exception(f'IA {ia_infos.nome} is not active')

        # Extrair conteúdo da msg
        message_id = data['data']['key']['id']
        message_type = data['data']['messageType']
        message_content = process_message(data, ia_name, message_id, message_type, ia_infos)

        if not message_content:
            raise Exception('It is not possible extract the message type.')

        # Extraindo as infos do lead
        lead_name = data['data']['pushName']
        lead_phone = data['data']['key']['remoteJidAlt'].split('@')[0]
        
        logger.info('lead_phone: %s', lead_phone)        
        logger.debug("data:\n%s", json.dumps(data, indent=2, ensure_ascii=False))

        # não deixa processar mais de uma mensagem por vez
        lock = get_phone_lock(lead_phone)

        with lock:
            current_message_lead = {
                "role": "user",
                "name": lead_name,
                "content": message_content
            }

            lead_db = lead_manipulations.filter_lead(lead_phone, current_message_lead)

            if not lead_db:
                lead_db = lead_manipulations.new_lead(ia_infos.id, lead_name, lead_phone, [current_message_lead])

            # Gerando resposta com LLM
            history = lead_db.message
            resume_lead = lead_db.resume
            api_key = ia_infos.ia_config.credentials.get('api_key')
            ia_model = ia_infos.ia_config.credentials.get('ia_model')
            system_prompt = ia_infos.active_prompt.prompt_text

            if not system_prompt:
                raise Exception('Nenhum prompt cadastrado ou ativo para a IA')
            
            logger.info('history: %s', history)

            llm = IAresponse(api_key, ia_model, system_prompt, resume_lead)
            response_lead = llm.generate_response(message_content, history)
            logger.info('response_lead: %s', response_lead)
            if not response_lead:
                raise Exception('Nenhuma resposta gerada pela IA')

            #Tratar msg IA
            list_message_to_lead = quebrar_mensagens(response_lead)
            if not list_message_to_lead:
                list_message_to_lead = [response_lead]

            #Envio msg lead
            for msg in list_message_to_lead:
                delay = calculate_typing_delay(msg)    
                logger.debug('Delay: %s', delay)
                logger.info('MSG quebrada sendo enviada: %s', msg)
                response_canal = send_message(ia_name, lead_phone, msg, delay)
                if response_canal.get("status_code") not in [200, 201]:
                    raise(Exception(f"Erro ao enviar mensagem ao lead > {msg}"))

            #Criando uma lógica para a frase: OI TUdo bem ser considerada apenas uma interação
            resumo = None
            total_interacoes = 0
            ultimo_role = None
            for mensagem in history:
                if mensagem['role'] != ultimo_role:
                    total_interacoes +=1
                    ultimo_role = mensagem['role']

            logger.debug('Total interações reais: %s', total_interacoes)

            #Verificando necessidade de criar resumo
            for n in range(20,26):
                if total_interacoes % n == 0 :
                    logger.info('Interações bateu: %s, criando resumo', total_interacoes)
                    resumo = llm.generate_resume(history)

            #Update banco
            message_ia = {
                "role":"assistant",
                "content": response_lead
            }

            lead_update = lead_manipulations.update_lead(lead_db.id, message_ia, resumo)
            if not lead_update:
                raise Exception(f'Falhar ao atualizar o lead: {lead_db.id}')
            
            logger.info('Sucesso ao processar LEAD: %s', lead_db.name)


    except Exception as ex:
        logger.error('Error in process: %s', ex)


def process_message(data: dict, instance: str, message_id: str, message_type: str, ia_infos: object) -> str :
    logger.debug('message_type: %s', message_type)

    if message_type == "conversation":
        return data["data"]["message"]["conversation"]
    
    elif message_type == "extendedTextMessage":
        return data["data"]["message"]["extendedTextMessage"]["text"]
    
    elif message_type == "imageMessage":
        logger.debug("Imagem detectada!")
        return processar_imagem(instance, message_id, ia_infos)
    
    elif message_type == "audioMessage":
        logger.debug("Áudio identificado!")
        return processar_audio(instance, message_id, ia_infos)
    
    elif message_type == "documentWithCaptionMessage":
        logger.debug("Documento identificado!")
        type_file = data.get("data").get("message").get("documentWithCaptionMessage").get("message").get("documentMessage").get("mimetype").split("/")[1]
        return processar_documento(instance, message_id, type_file, ia_infos), type_file
    else:
        logger.info("Tipo de mensagem não identificada: %s retornando...", message_type)
        return "Mensagem não odentificada"