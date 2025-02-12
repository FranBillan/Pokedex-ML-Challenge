"""
Establece configuración principal de la aplicación.
Gestiona la carga de variables de entorno y la configuración inicial de Flask.
"""

import os
from dotenv import load_dotenv
from flask import Flask
from app.utils.logger import setup_logging, get_logger

# Carga variables de entorno desde el archivo .env
load_dotenv()

# Obtiene logger
logger = get_logger()

# Trae variables de Okta desde .env
OKTA_DOMAIN = os.getenv('OKTA_DOMAIN')
OKTA_CLIENT_ID = os.getenv('OKTA_CLIENT_ID')
OKTA_CLIENT_SECRET = os.getenv('OKTA_CLIENT_SECRET')

def load_config(app: Flask) -> None:
    """
    Carga y valida la configuración inicial en la aplicación Flask.
    
    Esta función:
    - Configura el sistema de logging
    - Valida la presencia de las credenciales necesarias de Okta
    
    Args:
        app (Flask): Instancia de la aplicación Flask a configurar
        
    Raises:
        ValueError: Si falta alguna de las variables de entorno requeridas para Okta
    """
    # Configuración básica
    app.config['JSON_AS_ASCII'] = False #Permite caracteres especiales en las respuestas JSON.
    app.config['DEBUG'] = True #Setea el nivel de la app en debug, mostrando mensajes logger en este nivel.
    
    # Configurar logging
    setup_logging(app)
    logger.info('---Iniciando configuracion de la aplicacion.')
    
    # Validar configuración de Okta
    if not all([OKTA_DOMAIN, OKTA_CLIENT_ID, OKTA_CLIENT_SECRET]):
        logger.error('Faltan variables de entorno requeridas para la autenticación con Okta.')
        raise ValueError(
            "Faltan variables de entorno necesarias para la autenticación con Okta. "
            "Revisar la configuración de OKTA_DOMAIN, OKTA_CLIENT_ID y OKTA_CLIENT_SECRET"
        )
    
    logger.info('---Aplicacion iniciada correctamente.')