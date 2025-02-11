from functools import wraps
from flask import Response
import json
import requests

def handle_api_errors(f):
    """
    Decorador para manejar errores comunes de la API de manera consistente
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except requests.exceptions.RequestException as e:
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

def create_response(data, status_code=200):
    """
    Función auxiliar para crear respuestas JSON consistentes
    """
    return Response(
        json.dumps(data, ensure_ascii=False),
        mimetype='application/json',
        status=status_code
    )

def pokemon_not_found_error(name):
    """
    Función auxiliar para crear mensajes de error consistentes cuando no se encuentra un Pokémon
    """
    return {
        "error": "¡Ups! No conozco ese Pokémon... ¿es uno de los nuevos?",
        "sugerencia": "Revisá que el nombre esté bien escrito."
    }

def type_not_found_error(type_name):
    """
    Función auxiliar para crear mensajes de error consistentes cuando no se encuentra un tipo
    """
    return {
        "error": f"¡Ups! No conozco el tipo '{type_name}'",
        "sugerencia": "Probá con tipos como 'fire', 'water', 'electric', etc."
    }

def get_pokemon_by_type(type_name):
    """
    Función auxiliar para obtener todos los pokemon de un tipo específico
    """
    url = f'https://pokeapi.co/api/v2/type/{type_name.lower()}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return [pokemon['pokemon']['name'] for pokemon in data['pokemon']]
    return None

def auth_error_response(is_missing_credentials=False):
    """
    Función auxiliar para crear mensajes de error de autenticación consistentes
    """
    if is_missing_credentials:
        return {
            "error": "Se requiere username y password",
            "sugerencia": "Envía tus credenciales en el body de la petición para obtener tu ficha de entrenador.",
            "ejemplo": [{
                'username': '<usuario>',
                'password': '<contraseña>'
            }]
        }
    return {
        "error": "No hay un entrenador asociado a esas credenciales en nuestros registros. Intentá de nuevo.",
        "sugerencia": "Verificá tu username y password."
    }

def route_not_found_error():
    """
    Función auxiliar para crear mensaje de error 404 general
    """
    return {
        "error": "Por acá no hay ningún Pokemon... ¿funciona bien tu Pokeradar?",
        "sugerencia": "Revisá bien la URL o consultá /pokedex para ver todas las funciones disponibles."
    }

def get_welcome_message():
    """
    Función auxiliar para obtener el mensaje de bienvenida
    """
    return {
        "mensaje": "¡Pokedex en línea, bienvenido!",
        "consejo": "GET a /pokedex para ver todas las funciones disponibles."
    }

def get_pokedex_instructions():
    """
    Función auxiliar para obtener las instrucciones de la Pokedex
    """
    return {
        "mensaje": "¡Hola! A continuación, te detallo todas las funciones disponibles:",
        "funciones_disponibles": [
            {
                "endpoint": "/pokedex/<nombre>",
                "descripción": "¿Querés saber el tipo de un Pokémon? Dame su nombre.",
                "ejemplo": "/pokedex/serperior",
                "método": "GET"
            },
            {
                "endpoint": "/pokedex/types",
                "descripción": "¿No recordás todos los tipos? Te muestro una lista completa.",
                "ejemplo": "/pokedex/types",
                "método": "GET"
            },
            {
                "endpoint": "/pokedex/whos-that-pokemon",
                "descripción": "¿No conoces muchos? Te sugiero un Pokémon completamente al azar.",
                "ejemplo": "/pokedex/whos-that-pokemon",
                "método": "GET"
            },
            {
                "endpoint": "/pokedex/whos-that-pokemon/<tipo>",
                "descripción": "¿Tenés un tipo favorito? Te sugiero un Pokémon al azar de ese tipo.",
                "ejemplo": "/pokedex/whos-that-pokemon/psychic",
                "método": "GET"
            },
            {
                "endpoint": "/pokedex/longest/<tipo>",
                "descripción": "¿Curiosidad? Te digo cuál es el Pokémon con el nombre más largo de un tipo específico.",
                "ejemplo": "/pokedex/longest/water",
                "método": "GET"
            }
        ],
        "recordatorio": "Para usar todas estas funciones, es necesario que presentes tu ficha de entrenador! Podés buscarla en /obtener-ficha presentando tus credenciales.",
        "consejo": "Volvé a ver estas instrucciones cuando quieras visitando /pokedex"
    }

def get_random_pokemon():
    """
    Función auxiliar para obtener un pokemon aleatorio
    """
    random_id = random.randint(1, 898)
    url = f'https://pokeapi.co/api/v2/pokemon/{random_id}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def create_auth_error_response():
    """
    Función auxiliar para crear mensajes de error de autorización
    """
    return {
        "error": "Esta función está disponible solo para entrenadores autorizados. Presentá tu ficha de entrenador.",
        "sugerencia": "Debés incluir en el header 'Authorization: Bearer <token>' el código obtenido en /obtener-ficha."
    }

def create_invalid_token_response():
    """
    Función auxiliar para crear mensajes de error de token inválido
    """
    return {
        "error": "Ficha inactiva... ¿Te expulsaron de la liga? Tal vez solo tengas que tramitar una nueva.",
        "sugerencia": "Obtené un nuevo token en /obtener-ficha."
    }

def requires_auth(f):
    """
    Decorador para validar token de autenticación
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return create_response(create_auth_error_response(), 401)
        
        try:
            token = auth_header.split(" ")[1]
            
            # Endpoint de introspección de Okta
            introspect_url = f"https://{OKTA_DOMAIN}/oauth2/default/v1/introspect"
            
            # Headers y data para la introspección
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'token': token,
                'token_type_hint': 'access_token',
                'client_id': OKTA_CLIENT_ID,
                'client_secret': OKTA_CLIENT_SECRET
            }
            
            # Hacer la petición de introspección
            response = requests.post(introspect_url, headers=headers, data=data)
            
            if response.status_code == 200:
                introspection = response.json()
                if introspection.get('active'):
                    return f(*args, **kwargs)
                return create_response(create_invalid_token_response(), 401)
            
            return create_response({
                "error": "Error al validar la ficha de entrenador.",
                "sugerencia": "Obtén un nuevo token en /obtener-ficha"
            }, 401)
            
        except Exception as e:
            return create_response({
                "error": "Error al validar la ficha de entrenador.",
                "sugerencia": "Obtén un nuevo token en /obtener-ficha"
            }, 401)
    
    return decorated