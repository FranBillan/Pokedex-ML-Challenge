"""
Módulo de rutas de autenticación.
Maneja los endpoints relacionados con la obtención de tokens
"""

from flask import Blueprint, request, current_app
from app.services.auth_service import AuthService
from app.utils.decorators import handle_api_errors
from app.utils.responses import create_response
from app.utils.logger import get_logger

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService()
logger = get_logger()

@auth_bp.route('/obtener-ficha', methods=['POST'], strict_slashes=False)
@handle_api_errors
def get_token():
    """
    Endpoint para obtener un token de acceso.
    
    Espera un JSON en el body con username y password.
    Retorna un token JWT si las credenciales son válidas.
    
    Request body:
        {
            "username": str,
            "password": str
        }
        
    Returns:
        Response: JSON con el token de acceso o mensaje de error
        
    Status codes:
        200: Token generado exitosamente
        400: Credenciales faltantes o inválidas
        401: Credenciales incorrectas
        500: Error interno del servidor
    """
    logger.info('Recibida solicitud de ficha de entrenador')
    data = request.get_json()
    
    # Verificar si existen las credenciales
    if not data or 'username' not in data or 'password' not in data:
        logger.warning('Intento de obtener ficha fallido - faltan credenciales')
        return create_response({
            "error": "Se requiere username y password",
            "sugerencia": "Enviá tus credenciales en el body de la petición para obtener tu ficha de entrenador.",
            "ejemplo": [{
                'username': '<usuario>',
                'password': '<contraseña>'
            }]
        }, 400)

    username = data.get('username')
    password = data.get('password')
    
    # Verificar que las credenciales no estén vacías
    if not username.strip() or not password.strip():
        logger.warning('Intento de obtener ficha fallido - credenciales vacias')
        return create_response({
            "error": "Las credenciales no pueden estar vacías",
            "sugerencia": "Tanto el username como el password deben contener caracteres válidos.",
            "ejemplo": [{
                'username': '<usuario>',
                'password': '<contraseña>'
            }]
        }, 400)

    try:
        logger.info(f'Intentando autenticar usuario: {username}')
        token_response = auth_service.get_auth_token(username, password)
        
        # Si la respuesta es un string, es el token
        if isinstance(token_response, str):
            logger.info(f'Token generado exitosamente para usuario: {username}')
            return create_response({
                "access_token": token_response
            })
        
        # Si llegamos aquí, es un error de autenticación
        logger.warning(f'Credenciales invalidas para usuario: {username}')
        return create_response({
            "error": "No hay un entrenador asociado a esas credenciales en nuestros registros. Intentá de nuevo.",
            "sugerencia": "Verificá tu username y password."
        }, 401)
            
    except Exception as e:
        logger.error(f'Error en proceso de autenticación: {str(e)}')
        return create_response({
            "error": "¡Ups! Parece que hay problemas técnicos.",
            "sugerencia": "Intentalo de nuevo en unos momentos."
        }, 500)