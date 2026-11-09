import logging
import requests
from typing import (
    Optional, 
    Dict, 
    Any,
)

logger = logging.getLogger(__name__)

def renovar_token_firebase(api_key: str, refresh_token: str) -> Optional[Dict[str, Any]]:
    """Comunica com o Google Identity Toolkit para renovar a sessão utilizando o refresh token."""
    
    url = f"https://securetoken.googleapis.com/v1/token?key={api_key}"
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }

    try:
        response = requests.post(url, data=payload, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        return None
        
    except Exception as erro:
        logger.exception("Erro na comunicação com a API de autenticação: %s", erro)
        return None
