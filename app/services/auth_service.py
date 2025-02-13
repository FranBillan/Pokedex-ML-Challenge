"""
Módulo de servicio de autenticación y validación de tokens usando Okta como proveedor de identidad.
Proporciona métodos para obtener tokens y validar su estado.
"""

import requests
from typing import Union
from app.config.settings import OKTA_DOMAIN, OKTA_CLIENT_ID, OKTA_CLIENT_SECRET
from app.utils.logger import get_logger

logger = get_logger()

class AuthService:
    """
    Servicio de autenticación que interactúa con Okta.

    Attributes:
        token_url (str): URL del endpoint de tokens de Okta
        introspect_url (str): URL del endpoint de introspección de Okta
    """
    
    def __init__(self):
        """
        Inicia el servicio de autenticación con las URLs de Okta.
        Configura las URLs necesarias para la autenticación y validación.
        """
        self.token_url = f"https://{OKTA_DOMAIN}/oauth2/default/v1/token"
        self.introspect_url = f"https://{OKTA_DOMAIN}/oauth2/default/v1/introspect"
        logger.debug('Servicio de autenticación iniciado.')
        
    def get_auth_token(self, username: str, password: str) -> Union[str, None]:
        """
        Obtiene un token de autenticación de Okta usando credenciales de usuario.
        
        Args:
            username (str): Nombre de usuario
            password (str): Contraseña
            
        Returns:
            Union[str, None]: Token de acceso si es exitoso, None si las credenciales son inválidas (el error lo presenta la ruta)
            
        Ejemplo:
            >>> auth_service = AuthService()
            >>> token = auth_service.get_auth_token("ext_lmondinn", "contraseña")
            >>> if token:
            ...     print("Autenticación exitosa")
        """
        logger.info(f'---Iniciando proceso de autenticación para usuario: {username}')
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'password',
            'username': username,
            'password': password,
            'scope': 'openid',
            'client_id': OKTA_CLIENT_ID,
            'client_secret': OKTA_CLIENT_SECRET
        }
        
        try:
            logger.debug('Enviando solicitud de auth a Okta')
            response = requests.post(self.token_url, headers=headers, data=data)
            
            if response.status_code == 200:
                logger.info('---Token obtenido exitosamente')
                return response.json()['access_token']
            
            logger.warning(f'Fallo en autenticación. Status code: {response.status_code}')
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f'---Error en solicitud de token: {str(e)}')
            return None
    
    def validate_token(self, token: str) -> bool:
        """
        Valida un token de acceso usando el endpoint de introspección de Okta.
        
        Args:
            token (str): Token de acceso a validar
            
        Returns:
            bool: True si el token es válido, False en caso contrario
            
        Ejemplo:
            >>> auth_service = AuthService()
            >>> if auth_service.validate_token(token):
            ...     print("Token válido")
        """
        logger.debug(f'Validando token: {token[:10]}...')
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'token': token,
            'token_type_hint': 'access_token',
            'client_id': OKTA_CLIENT_ID,
            'client_secret': OKTA_CLIENT_SECRET
        }
        
        try:
            response = requests.post(self.introspect_url, headers=headers, data=data)
            
            if response.status_code == 200:
                is_active = response.json().get('active', False)
                logger.info(f'---Token validado. Estado: {"válido" if is_active else "inválido"}')
                return is_active
            
            logger.warning(f'Error en validación de token. Status code: {response.status_code}')
            return False
            
        except requests.exceptions.RequestException as e:
            logger.error(f'---Error en validación de token: {str(e)}')
            return False