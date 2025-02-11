from flask import Flask
from werkzeug.exceptions import HTTPException
from app.utils.responses import create_response

class APIError(Exception):
    """Excepción base para errores de la API"""
    def __init__(self, message: str, suggestion: str = None, status_code: int = 400):
        super().__init__()
        self.message = message
        self.suggestion = suggestion
        self.status_code = status_code

class PokemonNotFoundError(APIError):
    """Se lanza cuando no se encuentra un Pokémon"""
    def __init__(self, name: str):
        super().__init__(
            message=f"¡Ups! No conozco ese Pokémon... ¿es uno de los nuevos?",
            suggestion="Revisá que el nombre esté bien escrito.",
            status_code=404
        )

class TypeNotFoundError(APIError):
    """Se lanza cuando no se encuentra un tipo de Pokémon"""
    def __init__(self, type_name: str):
        super().__init__(
            message=f"¡Ups! No conozco el tipo '{type_name}'",
            suggestion="Probá con tipos como 'fire', 'water', 'electric', etc.",
            status_code=404
        )

class AuthenticationError(APIError):
    """Se lanza cuando hay un error en la autenticación"""
    def __init__(self, is_missing_credentials: bool = False):
        if is_missing_credentials:
            message = "Se requiere username y password"
            suggestion = "Enviá tus credenciales en el body de la petición para obtener tu ficha de entrenador."
        else:
            message = "No hay un entrenador asociado a esas credenciales en nuestros registros. Intentá de nuevo."
            suggestion = "Verificá tu username y password."
        
        super().__init__(message=message, suggestion=suggestion, status_code=401)

class ConnectionError(APIError):
    """Se lanza cuando hay problemas de conexión"""
    def __init__(self):
        super().__init__(
            message="¡Ups! Parece que hay problemas técnicos.",
            suggestion="Intentalo de nuevo en unos momentos.",
            status_code=503
        )

def register_error_handlers(app: Flask):
    """
    Registra los manejadores de errores en la aplicación Flask
    
    Args:
        app (Flask): Instancia de la aplicación Flask
    """
    
    @app.errorhandler(APIError)
    def handle_api_error(error):
        response = {
            "error": error.message
        }
        if error.suggestion:
            response["sugerencia"] = error.suggestion
            
        return create_response(response, error.status_code)

    @app.errorhandler(404)
    def handle_404_error(error):
        return create_response({
            "error": "Por acá no hay ningún Pokemon... ¿funciona bien tu Pokeradar?",
            "sugerencia": "Revisá bien la URL o consultá /pokedex para ver todas las funciones disponibles."
        }, 404)

    @app.errorhandler(500)
    def handle_500_error(error):
        return create_response({
            "error": "¡Ups! El Pokémon se escapó...",
            "sugerencia": "¡Intentalo de nuevo!"
        }, 500)

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.error(f"Unexpected error: {str(error)}")
        return create_response({
            "error": "¡Ups! El Pokémon se escapó...",
            "sugerencia": "¡Intentalo de nuevo!"
        }, 500)