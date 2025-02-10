from flask import Flask, request, Response, redirect, session
from functools import wraps
import requests
import random
import json
import os
from jose import jwt
from urllib.request import urlopen
from dotenv import load_dotenv

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
                "detalle": str(e)
            }, ensure_ascii=False),
            mimetype='application/json',
            status=500
        )

# Decorator para validar token
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return Response(
                json.dumps({
                    "error": "Esta función está disponible solo para entrenadores autorizados. Presentá tu ficha de entrenador.",
                    "sugerencia": "Debés incluir en el header 'Authorization: Bearer <token>' el código obtenido en /obtener-ficha."
                }, ensure_ascii=False),
                mimetype='application/json',
                status=401
            )
        
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
                else:
                    return Response(
                        json.dumps({
                            "error": "Ficha inactiva... ¿Te expulsaron de la liga? Tal vez solo tengas que tramitar una nueva.",
                            "sugerencia": "Obtené un nuevo token en /obtener-ficha."
                        }, ensure_ascii=False),
                        mimetype='application/json',
                        status=401
                    )
            else:
                return Response(
                    json.dumps({
                        "error": "Error al validar la ficha de entrenador.",
                        "sugerencia": "Obtén un nuevo token en /obtener-ficha"
                    }, ensure_ascii=False),
                    mimetype='application/json',
                    status=401
                )
            
        except Exception as e:
            return Response(
                json.dumps({
                    "error": "Error al validar la ficha de entrenador.",
                    "sugerencia": "Obtén un nuevo token en /obtener-ficha"
                }, ensure_ascii=False),
                mimetype='application/json',
                status=401
            )
    
    return decorated

@app.route('/', methods=['GET'])
def welcome():
    data = {
        "mensaje": "¡Pokedex en línea, bienvenido!",
        "consejo": "GET a /pokedex para ver todas las funciones disponibles."
    }
    return Response(
        json.dumps(data, ensure_ascii=False),
        mimetype='application/json'
    )

@app.route('/pokedex', methods=['GET'])
def instructions():
    data = {
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
    return Response(
        json.dumps(data, ensure_ascii=False),
        mimetype='application/json'
    )

# Función auxiliar para obtener todos los pokemon de un tipo específico
def get_pokemon_by_type(type_name):
    url = f'https://pokeapi.co/api/v2/type/{type_name.lower()}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return [pokemon['pokemon']['name'] for pokemon in data['pokemon']]
    return None

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
def get_pokemon(name):
    url = f'https://pokeapi.co/api/v2/pokemon/{name.lower()}'
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            pokemon_data = {
                "mensaje": f"¡Atrapaste a {name.capitalize()}! A continuación, te presento su información:",
                "pokemon": {
                    "nombre": data["name"],
                    "tipos": [t["type"]["name"] for t in data["types"]],
                    "altura": f"{data['height']/10} mt",  # convertir a mt
                    "peso": f"{data['weight']/10} kg",  # convertir a kg
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
            return Response(
                json.dumps(pokemon_data, ensure_ascii=False),
                mimetype='application/json'
            )
        else:
            error_data = {
                "error": "¡Ups! No conozco ese Pokémon... ¿es uno de los nuevos?",
                "sugerencia": "Revisá que el nombre esté bien escrito."
            }
            return Response(
                json.dumps(error_data, ensure_ascii=False),
                mimetype='application/json'
            ), 404
            
    except requests.exceptions.RequestException as e:
        error_data = {
            "error": "¡Ups! Parece que hay problemas técnicos.",
            "sugerencia": "Intentalo de nuevo en unos momentos."
        }
        return Response(
            json.dumps(error_data, ensure_ascii=False),
            mimetype='application/json'
        ), 500

@app.route('/pokedex/whos-that-pokemon', methods=['GET'])
@requires_auth
def random_pokemon():
    try:
        response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{random.randint(1, 898)}')

        if response.status_code == 200:
            data = response.json()
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
            return Response(
                json.dumps(pokemon_data, ensure_ascii=False),
                mimetype='application/json'
            )
        else:
            error_data = {
                "error": "¡Ups! El Pokémon se escapó...",
                "sugerencia": "¡Intentalo de nuevo!"
            }
            return Response(
                json.dumps(error_data, ensure_ascii=False),
                mimetype='application/json'
            ), 404

    except requests.exceptions.RequestException as e:
        error_data = {
            "error": "¡Ups! Parece que hay problemas técnicos.",
            "sugerencia": "Intentalo de nuevo en unos momentos."
        }
        return Response(
            json.dumps(error_data, ensure_ascii=False),
            mimetype='application/json'
        ), 500

@app.route('/pokedex/whos-that-pokemon/<type>', methods=['GET'])
@requires_auth
def random_pokemon_by_type(type):
    try:
        pokemons_of_type = get_pokemon_by_type(type)
        if not pokemons_of_type:
            error_data = {
                "error": f"¡Ups! No conozco el tipo '{type}'",
                "sugerencia": "Probá con tipos como 'fire', 'water', 'electric', etc."
            }
            return Response(
                json.dumps(error_data, ensure_ascii=False),
                mimetype='application/json'
            ), 404
        
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
            return Response(
                json.dumps(pokemon_data, ensure_ascii=False),
                mimetype='application/json'
            )
        
    except requests.exceptions.RequestException as e:
        error_data = {
            "error": "¡Ups! Parece que hay problemas técnicos.",
            "sugerencia": "Intentalo de nuevo en unos momentos."
        }
        return Response(
            json.dumps(error_data, ensure_ascii=False),
            mimetype='application/json'
        ), 500

@app.route('/pokedex/longest/<type>', methods=['GET'])
@requires_auth
def longest_name_pokemon(type):
    try:
        # Obtener todos los pokemon del tipo especificado
        pokemons = get_pokemon_by_type(type)
        
        if not pokemons:
            error_data = {
                "error": f"¡Ups! No conozco el tipo '{type}'",
                "sugerencia": "Probá con tipos como 'fire', 'water', 'electric', etc."
            }
            return Response(
                json.dumps(error_data, ensure_ascii=False),
                mimetype='application/json'
            ), 404

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
            return Response(
                json.dumps(pokemon_data, ensure_ascii=False),
                mimetype='application/json'
            )
            
    except requests.exceptions.RequestException as e:
        error_data = {
            "error": "¡Ups! Parece que hay problemas técnicos.",
            "sugerencia": "Intentalo de nuevo en unos momentos."
        }
        return Response(
            json.dumps(error_data, ensure_ascii=False),
            mimetype='application/json'
        ), 500

@app.route('/pokedex/types', methods=['GET'])
@requires_auth
def get_available_types():
    try:
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
            return Response(
                json.dumps(response_data, ensure_ascii=False),
                mimetype='application/json'
            )
        else:
            error_data = {
                "error": "¡Ups! No pude obtener los tipos",
                "sugerencia": "Intentalo de nuevo en unos momentos."
            }
            return Response(
                json.dumps(error_data, ensure_ascii=False),
                mimetype='application/json'
            ), 404
            
    except requests.exceptions.RequestException as e:
        error_data = {
            "error": "¡Ups! Parece que hay problemas técnicos.",
            "sugerencia": "Intentalo de nuevo en unos momentos."
        }
        return Response(
            json.dumps(error_data, ensure_ascii=False),
            mimetype='application/json'
        ), 500

@app.errorhandler(404)
def not_found(e):
    error_data = {
        "error": "Por acá no hay ningún Pokemon... ¿funciona bien tu Pokeradar?",
        "sugerencia": "Revisá bien la URL o consultá /pokedex para ver todas las funciones disponibles."
    }
    return Response(
        json.dumps(error_data, ensure_ascii=False),
        mimetype='application/json'
    ), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)