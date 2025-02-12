import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask

"""
Módulo de gestión de logs de la aplicación.
Inicia una configuración de logger y sus funciones.
"""

# Crear una instancia de logger específica para la aplicación
logger = logging.getLogger('pokedex')

def get_logger():
    """
    Obtiene la instancia del logger de la aplicación.
    
    returns:
        logging.logger: Logger configurado para la aplicación
    """
    return logger

def setup_logging(app: Flask) -> None:
    """
    Configura el sistema de logging para la aplicación.
    
    Establece dos handlers:
    - FileHandler: Guarda logs en archivos rotativos.
    - StreamHandler: Muestra logs en la consola.
    
    Args:
        app (Flask): Instancia de la aplicación Flask
    
    returns: none
    """
    global logger
    
    # Si no existe, crea el directorio de logs
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Establece el formato de los logs para ambos handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(module)s - %(message)s'
    )
    
    # Configura FileHandler con rotación
    file_handler = RotatingFileHandler(
        'logs/pokedex.log',
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Configura StreamHandler para mostrar logs en consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG if app.debug else logging.INFO)
    
    # Añade ambos handlers a la instancia de logger. En run.py se ejecuta como debug.
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.setLevel(logging.DEBUG if app.debug else logging.INFO)
    
    # Vincula también con el logger de Flask
    app.logger.handlers = logger.handlers
    app.logger.setLevel(logger.level)
    
    logger.debug('Sistema de logs iniciado.')