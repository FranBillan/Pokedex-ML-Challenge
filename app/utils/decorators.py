"""
Módulo de @decoradores para el funcionamiento de la API.
Contiene decoradores para el manejo de errores y para solicitar autenticación
en los endpoints de la API.
"""

from functools import wraps
from flask import request
import requests
from typing import Callable, Any
from app.utils.logger import get_logger
from app.utils.responses import (
    create_response,
    create_auth_error_response,
    create_invalid_token_response
)

logger = get_logger() #Recupera instancia de logger

def handle_api_errors(f: Callable) -> Callable:
    """
    Decorador para manejar errores de la API de manera genérica.
    Captura excepciones y las devuelve como respuestas HTTP.
    
    Args:
        f (Callable): Función a decorar
        
    Returns:
        Callable: Función decorada con manejo de errores
        
    Ejemplo:
        @handle_api_errors
        def get_pokemon():
            # código de la función
    """
    @wraps(f) #Permite conservar mensajes de la función a la cual se añade el decorador
    def decorated(*args: Any, **kwargs: Any) -> Any:
        try:
            return f(*args, **kwargs)
        except requests.exceptions.RequestException as e:
            logger.error(f'Error de conexión en solicitud HTTP: {str(e)}')
            error_data = {
                "error": "¡Ups! Parece que hay problemas técnicos.",
                "sugerencia": "Intentalo de nuevo en unos momentos."
            }
            return create_response(error_data, 500)
        except Exception as e:
            logger.error(f'Error no manejado en endpoint: {str(e)}')
            error_data = {
                "error": "¡Ups! El Pokemon se escapó...",
                "sugerencia": "¡Intentalo de nuevo!"
            }
            return create_response(error_data, 500)
    return decorated

def requires_auth(f: Callable) -> Callable:
    """
    Decorador para validar token de autenticación.
    Verifica la presencia y validez del access token en el header Authorization.
    
    Args:
        f (Callable): Función a decorar
        
    Returns:
        Callable: Función decorada con validación de token
        
    Ejemplo:
        @requires_auth
        def get_pokemon():
            # código de la función
    """
    @wraps(f)
    def decorated(*args: Any, **kwargs: Any) -> Any:
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            logger.warning('Intento de acceso sin token de autorización')
            return create_response(create_auth_error_response(), 401)
        
        try:
            #Lazy import para evitar problemas por importación circular
            from app.services.auth_service import AuthService
            auth_service = AuthService()
            
            token = auth_header.split(" ")[1]
            logger.debug(f'Validando token: {token[:10]}...')
            
            is_valid = auth_service.validate_token(token)
            
            if is_valid:
                logger.debug('Token validado correctamente')
                return f(*args, **kwargs)
            
            logger.warning(f'Token inválido detectado: {token[:10]}...')
            return create_response(create_invalid_token_response(), 401)
            
        except Exception as e:
            logger.error(f'Error en validación de token: {str(e)}')
            return create_response({
                "error": "Error al validar la ficha de entrenador.",
                "sugerencia": "Obtén un nuevo token en /obtener-ficha"
            }, 401)
    
    return decorated