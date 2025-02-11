import requests
from typing import Union, Dict
from app.config.settings import OKTA_DOMAIN, OKTA_CLIENT_ID, OKTA_CLIENT_SECRET
from app.api.errors.handlers import AuthenticationError, ConnectionError

class AuthService:
    def __init__(self):
        """Inicializa el servicio de autenticación con las URLs de Okta"""
        self.token_url = f"https://{OKTA_DOMAIN}/oauth2/default/v1/token"
        self.introspect_url = f"https://{OKTA_DOMAIN}/oauth2/default/v1/introspect"
        
    def get_auth_token(self, username: str, password: str) -> str:
        """
        Obtiene un token de autenticación de Okta
        
        Args:
            username (str): Nombre de usuario
            password (str): Contraseña
            
        Returns:
            str: Token de acceso
            
        Raises:
            AuthenticationError: Si las credenciales son inválidas o están incompletas
            ConnectionError: Si hay problemas de conexión con Okta
        """
        # Validar que las credenciales no estén vacías
        if not username.strip() or not password.strip():
            raise AuthenticationError(is_missing_credentials=True)

        try:
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
            
            response = requests.post(self.token_url, headers=headers, data=data)
            
            if response.status_code == 200:
                return response.json()['access_token']
            
            # Si las credenciales son inválidas
            raise AuthenticationError(is_missing_credentials=False)
            
        except requests.exceptions.RequestException:
            raise ConnectionError()
    
    def validate_token(self, token: str) -> bool:
        """
        Valida un token de acceso usando el endpoint de introspección de Okta
        
        Args:
            token (str): Token de acceso a validar
            
        Returns:
            bool: True si el token es válido, False en caso contrario
            
        Raises:
            ConnectionError: Si hay problemas de conexión con Okta
        """
        try:
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
            
            response = requests.post(self.introspect_url, headers=headers, data=data)
            
            if response.status_code == 200:
                return response.json().get('active', False)
                
            return False
            
        except requests.exceptions.RequestException:
            raise ConnectionError()
            
    def validate_credentials(self, username: str, password: str) -> bool:
        """
        Valida si las credenciales proporcionadas están completas
        
        Args:
            username (str): Nombre de usuario
            password (str): Contraseña
            
        Returns:
            bool: True si las credenciales están completas, False en caso contrario
        """
        return bool(username and password and username.strip() and password.strip())