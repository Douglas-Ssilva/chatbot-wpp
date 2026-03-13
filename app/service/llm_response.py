# Importa a memória que mantém uma janela das últimas interações da conversa
from langchain.memory import ConversationBufferWindowMemory

# Importa o modelo de chat da OpenAI integrado ao LangChain
from langchain_openai.chat_models import ChatOpenAI

# Importa a cadeia de conversação pronta do LangChain
from langchain.chains.conversation.base import ConversationChain

# Importa a classe para criação de templates de prompt
from langchain.prompts import PromptTemplate


# Classe responsável por gerar respostas da IA
class IAresponse:

    # Método construtor da classe
    def __init__ (self, api_key: str, ia_model: str, system_prompt: str, resume_lead: str = ''):
        
        # Armazena a chave da API
        self.api_key = api_key
        
        # Armazena o modelo da IA que será utilizado
        self.ia_model = ia_model
        
        # Armazena o prompt base do sistema (instruções fixas para a IA)
        self.system_prompt = system_prompt

        # Ideia principal é economia de tokens, passando apenas o resumo para a IA,
        # enviando apenas os pontos-chave da conversa anterior
        if resume_lead:
            
            # Caso exista um resumo do lead, informa no console
            print('Resumo encontrado')

            # Template base da resposta incluindo histórico e input do usuário
            response_prompt = """
            historico da conversa: 
            {history}

            usuario: {input}
            """

            # Acrescenta ao resumo a descrição de que se trata do resumo geral das interações
            resume_lead += f'\nresumo de todas interações que houve com o lead: {resume_lead}'

        else:
            # Caso não exista resumo, utiliza o mesmo template padrão
            response_prompt = """
            historico da conversa: 
            {history}

            usuario: {input}
            """

        # Concatena o prompt do sistema com o template de resposta
        self.system_prompt += response_prompt

        # Caso nenhum modelo seja informado, define um modelo padrão
        if not self.ia_model:
            self.ia_model = 'gpt-4o-mini'


    # Método responsável por gerar a resposta da IA
    def generate_response(self, message_lead: str, history_message: list = []) -> str:
        try:
            
            # Instancia o modelo de chat com modelo e chave da API
            chat = ChatOpenAI(model = self.ia_model, api_key = self.api_key)

            # Cria uma memória que guarda apenas as 20 últimas interações
            # Isso ajuda a reduzir custo de tokens
            memory = ConversationBufferWindowMemory(k = 20)

            # Cria o template de prompt a partir do system_prompt definido no construtor
            review_template = PromptTemplate.from_template(self.system_prompt)

            # Cria a cadeia de conversação passando:
            # - o modelo LLM
            # - a memória configurada
            # - o template do prompt
            conversation = ConversationChain(
                llm = chat,
                memory = memory,
                prompt = review_template
            )

            # ===============================
            # Alimentar a memória da IA com histórico anterior
            # ===============================

            # Caso não exista histórico anterior
            if not history_message:
                
                # Adiciona apenas a mensagem atual do usuário na memória
                conversation.memory.chat.memory.add_user_message(message_lead)

            else:
                # Caso exista histórico, percorre cada mensagem
                for msg in history_message:
                    
                    # Se a mensagem for do usuário
                    if msg['role'] == 'user' :
                        # Adiciona mensagem do usuário na memória
                        conversation.memory.chat_memory.add_user_message(msg.get('content') or '')
                    
                    # Se a mensagem for da IA (assistente)
                    elif msg['role'] == 'assistent':
                        # Adiciona resposta da IA na memória
                        conversation.memory.chat_memory.add_ai_message(msg.get('content') or '')

            # Exibe no console o total de interações carregadas
            print(f'TOtal de interações: {len(history_message)}')

            # Executa a previsão da IA passando a nova mensagem do usuário
            response_ia = conversation.predict(input = message_lead)

            # Exibe no console a resposta gerada pela IA
            print(f'IA response: {response_ia}')

            # Retorna a resposta gerada
            return response_ia


        # Caso ocorra algum erro durante o processo
        except Exception as ex:
            
            # Exibe o erro no console
            print(f'Erro ao processar response: {ex}')
            
            # Retorna string vazia em caso de erro
            return ''
        
    def generate_resume(self, history_message:list=[]) -> str:
        try:
            message = "Gere um resumo detalhado dessa conversa"
            system_prompt = """
            Você é um assistente especializado em resumir conversas com leads. Seu objetivo é identificar, extrair e armazenar de forma clara todos os pontos-chave e informações importantes discutidas durante a conversa. Ao elaborar o resumo, siga estas diretrizes:

            1. **Identificação dos Pontos-Chave:** Extraia os tópicos principais da conversa, incluindo necessidades, interesses, objeções e próximos passos do lead.
            2. **Organização das Informações:** Estruture o resumo de maneira clara e organizada, facilitando a visualização dos dados mais relevantes.
            3. **Foco nas Informações Relevantes:** Certifique-se de que nenhuma informação importante seja omitida. Dados como informações de contato, dúvidas específicas e requisitos do lead devem ser destacados.
            4. **Clareza e Concisão:** O resumo deve ser conciso, mas detalhado o suficiente para fornecer um panorama completo da conversa.
            5. **Privacidade e Segurança:** Garanta que todas as informações sensíveis sejam tratadas com a devida confidencialidade.

            Utilize este prompt para transformar a conversa em um resumo que possibilite um acompanhamento eficaz e estratégico do lead.

            Histórico da conversa:
            {history}
            Usuário: {input}
            """

            chat = ChatOpenAI(model=self.ia_model, api_key=self.api_key)
            memory = ConversationBufferWindowMemory(k=60)
            review_template = PromptTemplate.from_template(system_prompt)
            conversation = ConversationChain(
                llm=chat,
                memory=memory,
                prompt=review_template
            )

            # Alimenta a memória com cada mensagem do histórico
            if not history_message:
                conversation.memory.chat_memory.add_user_message(message)
            else:
                for msg in history_message:

                    #Adicionando memoria do User
                    if msg["role"] == "user":
                        conversation.memory.chat_memory.add_user_message(msg.get("content") or "")
                    
                    #Adicionando memoria da IA
                    elif msg["role"] == "assistant":
                        conversation.memory.chat_memory.add_ai_message(msg.get("content") or "")

            print(f"Total de {len(history_message)} interações")   
            resposta = conversation.predict(input=message)
            print(f"Resposta da IA   : {resposta}")
            
            return resposta
        except Exception as ex:
            print(f"❌ Erro ao processar resposta: {ex}")
            return None