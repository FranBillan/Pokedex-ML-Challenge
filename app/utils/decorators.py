from functools import wraps
from flask import request
import requests
from typing import Callable, Any
from app.utils.responses import (
    create_response,
    create_auth_error_response,
    create_invalid_token_response
)

def handle_api_errors(f: Callable) -> Callable:
    """
    Decorador para manejar errores comunes de la API de manera consistente
    
    Args:
        f (Callable): Función a decorar
        
    Returns:
        Callable: Función decorada con manejo de errores
    """
    @wraps(f)
    def decorated(*args: Any, **kwargs: Any) -> Any:
        try:
            return f(*args, **kwargs)
        except requests.exceptions.RequestException:
            error_data = {
                "error": "¡Ups! Parece que hay problemas técnicos.",
                "sugerencia": "Intentalo de nuevo en unos momentos."
            }
            return create_response(error_data, 500)
        except Exception as e:
            error_data = {
                "error": "¡Ups! El Pokémon se escapó...",
                "sugerencia": "¡Intentalo de nuevo!"
            }
            return create_response(error_data, 500)
    return decorated

def requires_auth(f: Callable) -> Callable:
    """
    Decorador para validar token de autenticación
    
    Args:
        f (Callable): Función a decorar
        
    Returns:
        Callable: Función decorada con validación de token
    """
    @wraps(f)
    def decorated(*args: Any, **kwargs: Any) -> Any:
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return create_response(create_auth_error_response(), 401)
        
        try:
            #Lazy import para evitar problemas por importación circular
            from app.services.auth_service import AuthService
            auth_service = AuthService()
            
            token = auth_header.split(" ")[1]
            is_valid = auth_service.validate_token(token)
            
            if is_valid:
                return f(*args, **kwargs)
            
            return create_response(create_invalid_token_response(), 401)
            
        except Exception:
            return create_response({
                "error": "Error al validar la ficha de entrenador.",
                "sugerencia": "Obtén un nuevo token en /obtener-ficha"
            }, 401)
    
    return decorated