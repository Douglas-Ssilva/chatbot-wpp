# Importações do SQLAlchemy (ORM para trabalhar com banco de dados)
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.service.crypto import decrypt_data


# Cria a classe base que será herdada por todos os modelos (tabelas)
Base = declarative_base()

# ===========================
# TABELA IA
# ===========================

class IA(Base): 
    # Nome da tabela no banco
    __tablename__ = 'ias'

    # Coluna id (chave primária)
    id = Column(Integer, primary_key=True, index=True)

    # Nome da IA (obrigatório e único)
    name = Column(String, nullable=False, unique=True)

    # Número de telefone vinculado à IA
    phone_number = Column(String, nullable=False, unique=True)
    
    status = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())    
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    #relationship() cria ligações entre objetos no Python
    # Relacionamento 1:N com Prompt
    prompts = relationship('Prompt', back_populates='ia')

    # Relacionamento 1:1 com IAConfig
    #uselist=False? Por padrão, relationship entende que é 1:N (lista).
    ia_config = relationship('IAConfig', back_populates='ia', uselist=False)#ia.ia_config

    # Relacionamento 1:N com Lead
    leads = relationship('Lead', back_populates='ia')

    @property
    def active_prompt(self):
        active = [ p for p in self.prompts if p.is_active ]
        return active[0] if active else None


# ===========================
# TABELA IAConfig
# ===========================

class IAConfig(Base):
    __tablename__ = 'ia_config'

    id = Column(Integer, primary_key=True, index=True)

    # Chave estrangeira apontando para tabela ias
    ia_id = Column(Integer, ForeignKey('ias.id'), nullable=False)
    
    channel = Column(String, nullable=False)
    
    # Nome da API de IA usada (ex: openai)
    ai_api = Column(String, nullable=False)

    # Credenciais criptografadas
    encrypted_credentials = Column(String, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relacionamento de volta para IA
    ia = relationship("IA", back_populates="ia_config")

    # Property permite acessar como atributo
    @property
    def credentials(self):
        # Retorna as credenciais descriptografadas
        return decrypt_data(self.encrypted_credentials)


# ===========================
# TABELA Prompt
# ===========================

class Prompt(Base):
    __tablename__ = 'prompts'

    id = Column(Integer, primary_key=True, index=True)

    # Relaciona com IA
    ia_id = Column(Integer, ForeignKey('ias.id'), nullable=False)
    
    prompt_text = Column(String, nullable=False)
    is_active = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relacionamento reverso
    ia = relationship("IA", back_populates="prompts")


# ===========================
# TABELA Lead
# ===========================

class Lead(Base):
    __tablename__ = 'leads'

    id = Column(Integer, primary_key=True, index=True)

    # Relaciona com IA
    ia_id = Column(Integer, ForeignKey('ias.id'), nullable=False)
    
    name = Column(String, nullable=True)
    phone = Column(String, nullable=True, unique=True)
    message = Column(MutableList.as_mutable(JSON), nullable=False)
    resume = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relacionamento reverso
    ia = relationship("IA", back_populates="leads")


