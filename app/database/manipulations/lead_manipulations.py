from ..models import *
from ..connection import init_db

def new_lead(ia_id:int, name:str, phone:str, message:list) -> Lead:
    print('cheguei')
    db = init_db()

    if not db:
        raise(Exception('Database is not available'))
    
    try:
        
        lead = Lead(
            ia_id = ia_id,
            phone = phone,
            name = name,
            message = message
            )

        db.add(lead)
        db.commit()
        db.refresh(lead)

        print(f'New Lead was created : {lead.name} - {lead.phone}')

        return lead

    except Exception as ex:
        print(f'Error -> {ex}')
    finally:
        db.close()

def filter_lead(phone: str, message: dict) -> Lead:
    db = init_db()

    if not db:
        raise(Exception('Database is not available'))
    
    try:
        
        lead = db.query(Lead).filter(Lead.phone == phone).first()
        if not lead:
            print(f'Lead is not available with this phone number: {phone}')
            return None
        
        historico = lead.message
        if not historico:
            historico = []
        
        historico.append(message)
        lead.message = historico

        db.commit()
        db.refresh(lead)

        print(f'Lead was update and conversation too: {lead.name} - {lead.phone}')

        return lead

    except Exception as ex:
        print(f'Error -> {ex}')
    finally:
        db.close()


def update_lead(lead_id: int, message: list, resume: str) -> Lead:
    db = init_db()

    if not db:
        raise(Exception('Database is not available'))
    
    try:
        
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            print(f'Lead is not available with this ID: {lead_id}')
            return None
        
        if resume:
            lead.resume = resume
        
        historico = lead.message
        if not historico:
            historico = []
        
        historico.append(message)
        lead.message = historico

        db.commit()
        db.refresh(lead)

        print(f'Lead was update and conversation too: {lead.name} - {lead.phone}')

        return True

    except Exception as ex:
        print(f'Error -> {ex}')
    finally:
        db.close()