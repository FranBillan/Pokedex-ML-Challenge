"""
Módulo de manejo de errores de la API.
"""

from flask import Flask
from werkzeug.exceptions import HTTPException
from app.utils.responses import create_response
from app.utils.logger import get_logger

logger = get_logger()

class APIError(Exception):
    """
    Excepción base para errores de la API.
    
    Attr:
        message (str): Mensaje de error para el usuario
        suggestion (str): Sugerencia opcional de cómo resolver el error
        status_code (int): Código de estado HTTP para la respuesta
    """
    def __init__(self, message: str, suggestion: str = None, status_code: int = 400):
        super().__init__()
        self.message = message
        self.suggestion = suggestion
        self.status_code = status_code

def register_error_handlers(app: Flask):
    """
    Registra los handlers en la aplicación Flask.
    Configura respuestas para diferentes tipos de errores.
    
    Args:
        app (Flask): Instancia de la aplicación Flask
    """
    
    @app.errorhandler(APIError)
    def handle_api_error(error):
        """Maneja errores de la API"""
        logger.warning(f'Error de API: {error.message}')
        response = {
            "error": error.message
        }
        if error.suggestion:
            response["sugerencia"] = error.suggestion
            
        return create_response(response, error.status_code)

    @app.errorhandler(404)
    def handle_404_error(error):
        """Maneja errores de recurso/path no encontrado"""
        logger.warning(f'Ruta no encontrada: {error}')
        return create_response({
            "error": "Por acá no hay ningún Pokemon... ¿funciona bien tu Pokeradar?",
            "sugerencia": "Revisá bien la URL o consultá /pokedex para ver todas las funciones disponibles."
        }, 404)

    @app.errorhandler(500)
    def handle_500_error(error):
        """Maneja errores internos del servidor"""
        logger.error(f'Error interno del servidor: {error}')
        return create_response({
            "error": "¡Ups! El Pokémon se escapó...",
            "sugerencia": "¡Intentalo de nuevo!"
        }, 500)

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """Maneja cualquier error no manejado específicamente"""
        logger.error(f'Error inesperado: {str(error)}')
        return create_response({
            "error": "¡Ups! El Pokémon se escapó...",
            "sugerencia": "¡Intentalo de nuevo!"
        }, 500)