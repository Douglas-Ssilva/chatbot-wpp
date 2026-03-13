from ..models import *
from ..connection import init_db

def filter_ia(phone: str) -> IA:
    db = init_db()

    if not db:
        raise(Exception('Database is not available'))
        
    try:
        
        ia = db.query(IA).filter(IA.phone_number == phone).first()
        if not ia:
            print(f'IA is not available with phone number: {phone}')   
            return None

        # Acessa os relacionamentos (Foreign Keys)
        # Isso força o carregamento dessas relações se estiver lazy loading
        # Exemplo:
        # ia_config → pode ser uma tabela relacionada com configurações
        
        ia.ia_config
        ia.active_prompt

        print(f'IA is available with phone number: {phone}')   
        return ia

    except Exception as ex:
        print(f'Error: {ex}')
    
    finally:
        if db:
            db.close()

    return None