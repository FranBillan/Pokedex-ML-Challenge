from flask import Blueprint, request, current_app
from app.services.auth_service import AuthService
from app.utils.decorators import handle_api_errors
from app.utils.responses import create_response

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService()

@auth_bp.route('/obtener-ficha', methods=['POST'], strict_slashes=False)
@handle_api_errors
def get_token():
    data = request.get_json()
    
    # Verificar si existen las credenciales
    if not data or 'username' not in data or 'password' not in data:
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
        return create_response({
            "error": "Las credenciales no pueden estar vacías",
            "sugerencia": "Tanto el username como el password deben contener caracteres válidos.",
            "ejemplo": [{
                'username': '<usuario>',
                'password': '<contraseña>'
            }]
        }, 400)

    try:
        token_response = auth_service.get_auth_token(username, password)
        
        # Si la respuesta es un string, es el token
        if isinstance(token_response, str):
            return create_response({
                "access_token": token_response
            })
        
        # Si llegamos aquí, es un error de autenticación
        return create_response({
            "error": "No hay un entrenador asociado a esas credenciales en nuestros registros. Intentá de nuevo.",
            "sugerencia": "Verificá tu username y password."
        }, 401)
            
    except Exception as e:
        current_app.logger.error(f"Authentication error: {str(e)}")
        return create_response({
            "error": "¡Ups! Parece que hay problemas técnicos.",
            "sugerencia": "Intentalo de nuevo en unos momentos."
        }, 500)