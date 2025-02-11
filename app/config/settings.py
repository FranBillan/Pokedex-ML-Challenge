import os
from dotenv import load_dotenv
from flask import Flask

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Configuración de Okta
OKTA_DOMAIN = os.getenv('OKTA_DOMAIN')
OKTA_CLIENT_ID = os.getenv('OKTA_CLIENT_ID')
OKTA_CLIENT_SECRET = os.getenv('OKTA_CLIENT_SECRET')

def load_config(app: Flask) -> None:
    """
    Carga la configuración básica en la aplicación Flask
    
    Args:
        app (Flask): Instancia de la aplicación Flask
    """
    # Configuración básica
    app.config['JSON_AS_ASCII'] = False  # Para manejar caracteres especiales en JSON
    app.config['DEBUG'] = True  # Útil para desarrollo
    
    # Validar configuración de Okta
    if not all([OKTA_DOMAIN, OKTA_CLIENT_ID, OKTA_CLIENT_SECRET]):
        raise ValueError(
            "Faltan variables de entorno necesarias para la autenticación con Okta. "
            "Revisar la configuración de OKTA_DOMAIN, OKTA_CLIENT_ID y OKTA_CLIENT_SECRET"
        )