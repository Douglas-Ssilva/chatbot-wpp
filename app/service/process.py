import random
import time

from app.database.manipulations import ia_manipulations, lead_manipulations
from app.service.queue_manager import get_phone_lock
from app.service.llm_response import IAresponse
from app.service.break_messages import *

def process_webhook(data: dict):
    """
    Função para processar dados do webhook
    """

    try:
        # infos basicas
        ia_phone = data['sender'].split('@')[0]
        ia_name = data['instance']

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
        lead_phone = data['data']['key']['remoteJid'].split('@')[0]

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
            
            llm = IAresponse(api_key, ia_model, system_prompt, resume_lead)
            response_lead = llm.generate_response(message_content, history)
            if not response_lead:
                raise Exception('Nenhuma resposta gerada pela IA')

            #Tratar msg IA
            list_message_to_lead = quebrar_mensagens(response_lead)
            if not list_message_to_lead:
                list_message_to_lead = [response_lead]

            #Envio msg lead
            for msg in list_message_to_lead:
                delay = calculate_typing_delay(msg)    
                print(f'Delay: {delay}s')
                print(f'IA: {msg}')

            #Criando uma lógica para a frase: OI TUdo bem ser considerada apenas uma interação
            resumo = None
            total_interacoes = 0
            ultimo_role = None
            for mensagem in history:
                if mensagem['role'] != ultimo_role:
                    total_interacoes +=1
                    ultimo_role = mensagem['role']

            print(f'Total interações reais: {total_interacoes}')

            #Verificando necessidade de criar resumo
            for n in range(20,26):
                if total_interacoes % n == 0 :
                    print(f'Interações bateu: {total_interacoes}, criando resumo')
                    resumo = llm.generate_resume(history)

            #Update banco
            message_ia = {
                "role":"assistant",
                "content": response_lead
            }

            lead_update = lead_manipulations.update_lead(lead_db.id, message_ia, resumo)
            if not lead_update:
                raise Exception(f'Falhar ao atualizar o lead: {lead_db.id}')
            
            print(f'Sucesso ao processar LEAD: {lead_db.name}')


    except Exception as ex:
        print(f'Error in process: {ex}')


def process_message(data: dict, instance: str, message_id: str, message_type: str, ia_infos: object) -> str :
    
    if message_type == "conversation":
        return data["data"]["message"]["conversation"]

    elif message_type == "extendedTextMessage":
        return data["data"]["message"]["extendedTextMessage"]["text"]

    elif message_type == "imageMessage":
        print("Imagem detectada!")
        #return processar_imagem(instance, message_id, ia_infos)
        return "mensagem de imagem"

    elif message_type == "audioMessage":
        print("Áudio identificado!")
        #return processar_audio(instance, message_id, ia_infos)
        return "mensagem de audio"

    elif message_type == "documentWithCaptionMessage":
        print("Documento identificado!")
        type_file = data.get("data").get("message").get("documentWithCaptionMessage").get("message").get("documentMessage").get("mimetype").split("/")[1]
        #return processar_documento(instance, message_id, type_file, ia_infos), type_file
        return "mensagem de documento"

    else:
        print(f"Tipo de mensagem não identificada: {message_type} retornando...")
        return