"""
Módulo de inicialización de utilidades.
Exporta funciones y decoradores incluyendo:
- Decoradores para manejo de errores y procesos de autenticación
- Funciones para crear respuestas HTTP
- Mensajes de la API
"""

from .decorators import handle_api_errors, requires_auth
from .responses import (
    create_response,
    create_auth_error_response,
    create_invalid_token_response,
    get_welcome_message,
    get_pokedex_instructions
)

__all__ = [
    'handle_api_errors',
    'requires_auth',
    'create_response',
    'create_auth_error_response',
    'create_invalid_token_response',
    'get_welcome_message',
    'get_pokedex_instructions'
]