from flask import Flask, request, Response, redirect, session
from functools import wraps
import requests
import random
import json
import os
from jose import jwt
from urllib.request import urlopen
from dotenv import load_dotenv
from utils import (
    handle_api_errors,
    create_response,
    pokemon_not_found_error,
    type_not_found_error,
    get_pokemon_by_type,
    auth_error_response,
    route_not_found_error,
    get_welcome_message,
    get_pokedex_instructions,
    get_random_pokemon,
    requires_auth
)
#Carga de variables de entorno
load_dotenv()

app = Flask(__name__)
# Esto hace que Flask trate /endpoint/ igual que /endpoint
app.url_map.strict_slashes = False

# Configuración de Okta - estos valores deberían estar en variables de ambiente
OKTA_DOMAIN = os.getenv('OKTA_DOMAIN')
OKTA_CLIENT_ID = os.getenv('OKTA_CLIENT_ID')
OKTA_CLIENT_SECRET = os.getenv('OKTA_CLIENT_SECRET')


# Endpoint para obtener token
# Endpoint para obtener token
@app.route('/obtener-ficha', methods=['POST'])
def get_token():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return Response(
                json.dumps({
                    "error": "Se requiere username y password",
                    "sugerencia": "Envía tus credenciales en el body de la petición para obtener tu ficha de entrenador.",
                    "ejemplo": [{
                    'username': '<usuario>',
                    'password': '<contraseña>'
                    }],
                }, ensure_ascii=False),
                mimetype='application/json',
                status=400
            )

        token_url = f"https://{OKTA_DOMAIN}/oauth2/default/v1/token"
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'password',
            'username': username,
            'password': password,
            'scope': 'openid',
            'client_id': OKTA_CLIENT_ID,
            'client_secret': OKTA_CLIENT_SECRET
        }
        
        response = requests.post(token_url, headers=headers, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            return Response(
                json.dumps({
                    "access_token": token_data['access_token']
                }, ensure_ascii=False),
                mimetype='application/json'
            )
        else:
            return Response(
                json.dumps({
                    "error": "No hay un entrenador asociado a esas credenciales en nuestros registros. Intentá de nuevo.",
                    "sugerencia": "Verificá tu username y password."
                }, ensure_ascii=False),
                mimetype='application/json',
                status=401
            )
            
    except Exception as e:
        return Response(
            json.dumps({
                "error": "Error en la autenticación",
                "sugerencia": str(e)
            }, ensure_ascii=False),
            mimetype='application/json',
            status=500
        )


@app.route('/', methods=['GET'])
@handle_api_errors
def welcome():
    return create_response(get_welcome_message())

@app.route('/pokedex', methods=['GET'])
@handle_api_errors
def instructions():
    return create_response(get_pokedex_instructions())

# Función auxiliar para obtener un pokemon random
def get_random_pokemon():
    random_id = random.randint(1, 898)
    url = f'https://pokeapi.co/api/v2/pokemon/{random_id}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

@app.route('/pokedex/<name>', methods=['GET'])
@requires_auth
@handle_api_errors
def get_pokemon(name):
    url = f'https://pokeapi.co/api/v2/pokemon/{name.lower()}'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        pokemon_data = {
            "mensaje": f"¡Atrapaste a {name.capitalize()}! A continuación, te presento su información:",
            "pokemon": {
                "nombre": data["name"],
                "tipos": [t["type"]["name"] for t in data["types"]],
                "altura": f"{data['height']/10} mt",
                "peso": f"{data['weight']/10} kg",
                "número_pokedex": data["id"],
                "habilidades": [
                    ability["ability"]["name"].replace("-", " ")
                    for ability in data["abilities"]
                ],
                "stats": {
                    "hp": data["stats"][0]["base_stat"],
                    "ataque": data["stats"][1]["base_stat"],
                    "defensa": data["stats"][2]["base_stat"],
                    "ataque_especial": data["stats"][3]["base_stat"],
                    "defensa_especial": data["stats"][4]["base_stat"],
                    "velocidad": data["stats"][5]["base_stat"]
                }
            }
        }
        return create_response(pokemon_data)
    
    return create_response(pokemon_not_found_error(name), 404)


@app.route('/pokedex/types', methods=['GET'])
@requires_auth
@handle_api_errors
def get_available_types():
    types_url = 'https://pokeapi.co/api/v2/type'
    response = requests.get(types_url)
    
    if response.status_code == 200:
        data = response.json()
        valid_types = [
            type_data['name'] 
            for type_data in data['results'] 
            if type_data['name'] not in ['unknown', 'shadow']
        ]
        
        response_data = {
            "mensaje": "¡Estos son todos los tipos de Pokémon disponibles!",
            "tipos": valid_types,
            "consejo": "Podés usar estos tipos en endpoints como /whos-that-pokemon/<tipo> o /longest/<tipo>"
        }
        return create_response(response_data)
    
    return create_response({
        "error": "¡Ups! No pude obtener los tipos",
        "sugerencia": "Intentalo de nuevo en unos momentos."
    }, 404)

@app.route('/pokedex/whos-that-pokemon', methods=['GET'])
@requires_auth
@handle_api_errors
def random_pokemon():
    data = get_random_pokemon()
    
    if data:
        pokemon_data = {
            "mensaje": "¡Un Pokémon salvaje apareció!",
            "pokemon": {
                "nombre": data["name"],
                "tipos": [t["type"]["name"] for t in data["types"]],
                "altura": data["height"]/10,
                "peso": data["weight"]/10,
                "número_pokedex": data["id"]
            }
        }
        return create_response(pokemon_data)
    
    return create_response({
        "error": "¡Ups! El Pokémon se escapó...",
        "sugerencia": "¡Intentalo de nuevo!"
    }, 404)

@app.route('/pokedex/whos-that-pokemon/<type>', methods=['GET'])
@requires_auth
@handle_api_errors
def random_pokemon_by_type(type):
    pokemons_of_type = get_pokemon_by_type(type)
    
    if not pokemons_of_type:
        return create_response(type_not_found_error(type), 404)
    
    random_name = random.choice(pokemons_of_type)
    url = f'https://pokeapi.co/api/v2/pokemon/{random_name}'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        pokemon_data = {
            "mensaje": f"¡Un Pokémon salvaje de tipo {type} apareció!",
            "pokemon": {
                "nombre": data["name"],
                "tipos": [t["type"]["name"] for t in data["types"]],
                "altura": data["height"]/10,
                "peso": data["weight"]/10,
                "número_pokedex": data["id"]
            }
        }
        return create_response(pokemon_data)
    
    return create_response({
        "error": "¡Ups! El Pokémon se escapó...",
        "sugerencia": "¡Intentalo de nuevo!"
    }, 404)

@app.route('/pokedex/longest/<type>', methods=['GET'])
@requires_auth
@handle_api_errors
def longest_name_pokemon(type):
    # Obtener todos los pokemon del tipo especificado
    pokemons = get_pokemon_by_type(type)
    
    if not pokemons:
        return create_response(type_not_found_error(type), 404)

    # Encontrar el nombre más largo
    longest_name = max(pokemons, key=len)
    
    # Obtener detalles del pokemon
    url = f'https://pokeapi.co/api/v2/pokemon/{longest_name}'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        pokemon_data = {
            "mensaje": f"¡El Pokémon de tipo {type} con el nombre más largo es...",
            "pokemon": {
                "nombre": data["name"],
                "tipos": [t["type"]["name"] for t in data["types"]],
                "longitud_nombre": len(data["name"]),
                "número_pokedex": data["id"]
            }
        }
        return create_response(pokemon_data)
        
    return create_response({
        "error": "¡Ups! El Pokémon se escapó...",
        "sugerencia": "¡Intentalo de nuevo!"
    }, 404)

@app.errorhandler(404)
def not_found(e):
    return create_response(route_not_found_error(), 404)

if __name__ == '__main__':
    app.run(debug=True, port=5000)