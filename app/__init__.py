"""
Módulo principal de inicialización de la aplicación.
Inicia la creación y configuración de todos los componentes:
    - Carga de configuración y variables de entorno
    - Registro de rutas y blueprints
    - Configuración de manejo de errores

Se ejecuta durante run.py
"""

from flask import Flask
from app.api.routes import register_routes
from app.api.errors.handlers import register_error_handlers
from app.config.settings import load_config
from app.utils.logger import get_logger

logger = get_logger()

def create_app():
    """
    Crea y configura la aplicación Flask.
    
    Returns:
        Flask: Aplicación configurada y lista para ejecutar
    """
    logger.info('Iniciando creacion de la aplicacion Flask.')
    
    app = Flask(__name__) #Inicializa la aplicación Flask
    
    logger.debug('Cargando variables de entorno')
    load_config(app) #Carga la configuración base y variables de entorno
    
    app.url_map.strict_slashes = False #Configura el manejo de URLs flexibles (con/sin trailing slash)
    
    logger.debug('Registrando rutas')
    register_routes(app) #Registra todas las rutas de la API
    
    logger.debug('Configurando manejo de errores')
    register_error_handlers(app) #Configura el sistema de manejo de errores
    
    logger.info('Aplicacion Flask creada exitosamente.')
    return app