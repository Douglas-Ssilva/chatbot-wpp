import os
import time 
import openai
import base64 
import requests 

from pydub import AudioSegment

from dotenv import load_dotenv

load_dotenv()

#config credenciais
host = os.getenv('HOST_API')
api_key = os.getenv('API_KEY')

def processar_imagem(instance: str, message_id: str, ia_infos) -> str:
    print('Processando imagem...')
    img_transcript = 'Imagem enviada: Não consegui transcrever essa imagem, fale ao usuário que sua internet está ruim e que não pode baixar a imagem.'

    try:
        
        url = host + 'chat/getBase64FromMediaMessage/' + instance #endpoint padrão dentro da evolution
        body = {
            'message' : {
                'key' : { 'id' : message_id }
            },
            'convertToMp4' : False
        }

        data = post_request(url, body)
        if data.get('status_code') in [ 200, 2001 ]:
            image_base64 = data.get('response')['base64']
            api_key_gpt = ia_infos.ia_config_credentials.get('api_key')

            header = {
                'Authorization' : f'Baerer {api_key}',
                'Content-Type' : 'application/json'
            }

            #modelo que passamos para o GPT
            payload = {
                'model' : os.getenv('MODEL_ANALIZE_IMAGE_OPENAI', 'gpt-4o'),
                'messages' : [
                    {
                        'role' : 'user',
                        'content' : [
                            { 'type' : 'text', 'text' : 'Faça uma interpretação da imagem enviada' },
                            { 'type' : 'image_url', 'image_url' : { 'url' : f'data:image/jpeg;base64, {image_base64}' }}
                        ]
                    }
                ],
                'max_tokens' : 500
            }

            url = 'https://api.openai.com/v1/chat/completions'
            response = requests.post(url, headers=header, json = payload, timeout= 30)
            if not response:
                raise(Exception)
        
            response_json = response.json()
            img_transcript = response_json['choices'][0]['message']['content']
            print(f'Imagem transcrita: {img_transcript}')

    except Exception as ex:
        print(f'Erro ao processar img: {ex}')

def processar_audio(instance: str, message_id: str, ia_infos) -> str:
    print('Processando áudio')
    audio_transcript = 'Audio enviado: Não consegui transcrever esse áudio fale para o usuário que a internet está ruim e que é para enviar um texto.'
    timestamp = str(time.time())
    audio_path = f'audio_{timestamp}.ogg'#audios from wpp vem assim
    mp3_path = f'audio_{timestamp}.mp4'

    try:

        url = host + 'chat/getbase64FromMediaMessage/' + instance
        body = {
            'message' : {
                'key' : { 'id' : message_id }
            },
            'convertToMp4' : False
        }
        data = post_request(url, body)

        if data.get('status_code') in [200, 201]:
            audio_base64 = data.get('response')['base64']
            audio_bytes = base64.b64decode(audio_base64)
            with open(audio_path, 'wb') as audio_file:
                audio_file.write(audio_bytes)

            def convert_ogg_to_mp3(input_path, output_path):
                audio = AudioSegment.from_ogg(input_path)
                audio.export(output_path, format='mp3')

            convert_ogg_to_mp3(audio_path, mp3_path)    

            with open(mp3_path, 'rb') as audio_file:
                api_key = ia_infos.ia_config_credentials.get('api_key')
                openai.api_key = api_key

                response = openai.audio.transcriptions.create(
                    model = 'whisper-1',
                    file = audio_file
                )

                audio_transcript = f'Áudio enviado: {response.text}'

    except Exception as ex:
         print(f'Erro ao processar audio: {ex}')

    #deletar arquivo
    try:
        os.remove(audio_path)
        if os.path.exists(mp3_path):
            os.remove(mp3_path)

    except:
        pass
    
    return audio_transcript

def processar_documento(instance, message_id, ia_infos) -> str:
    print("Processando Docs")
    print(instance)
    print(message_id)
    print(ia_infos)
    return "Documento enviada"

def send_message(instance: str, lead_phone: str, message: str, delay: int) -> dict:
    #body padrão da evolutuion
    url = host + 'message/sendText/' + instance
    body = {
        'number' : lead_phone, 
        'options' : {
            'delay' : int(delay) * 1000,
            'presence': 'composing',
            'linkPreview' : False
        },
        'textMessage' : {
            'text' : str(message)
        }
    }

    data = post_request(url, body)
    return data


def post_request(url: str, body: dict, max_retries: int = 5, wait_seconds: int = 5) -> str:
    attemp = 0
    lead = body.get('number', 'undefined')
    response_post = { 'status_code' : None, 'response' : None }

    headers = {
        'apikey' : api_key,
        'Content-Type' : 'application/json'
    }

    while attemp < max_retries:
        attemp += 1
        response = requests.post(url, json = body, headers = headers, timeout= 120)

        try:
            response_return = response.json()
        except Exception as ex:
            response_return = response.text

        if response.status_code in [200, 201]:
            response_post = { 'status_code' : response.status_code, 'response' : response_return }
            return response_post
        
        if attemp < max_retries:
            time.sleep(wait_seconds)

    return response_post
