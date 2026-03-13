"""
Dicionário global para armazenar locks por telefone
"""

import threading

phone_locks = {}

def get_phone_lock(phone: str) -> threading.Lock : 
    if phone not in phone_locks:
        phone_locks[phone] = threading.Lock()
    
    return phone_locks[phone]

