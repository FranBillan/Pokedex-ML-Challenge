from flask import Blueprint, request
from app.services.auth_service import AuthService
from app.utils.decorators import handle_api_errors
from app.utils.responses import create_response

auth_bp = Blueprint('auth', __name__)
#auth_bp.url_map.strict_slashes = False
auth_service = AuthService()

@auth_bp.route('/obtener-ficha', methods=['POST'])
@handle_api_errors
def get_token():
    try:
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

        # Delegar la lógica de autenticación al servicio
        token_response = auth_service.get_auth_token(username, password)
        
        if isinstance(token_response, dict) and 'error' in token_response:
            return create_response(token_response, 401)
            
        return create_response({
            "access_token": token_response
        })
            
    except Exception as e:
        return create_response({
            "error": "Error en la autenticación",
            "sugerencia": "Revisá que el cuerpo de la solicitud se ajuste al siguiente ejemplo.",
            "ejemplo": [{
                'username': '<usuario>',
                'password': '<contraseña>'
            }]
        }, 500)