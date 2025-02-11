from flask import Blueprint, current_app
from app.services.pokemon_service import PokemonService
from app.utils.decorators import handle_api_errors, requires_auth
from app.utils.responses import (
    create_response,
    get_welcome_message,
    get_pokedex_instructions
)

pokemon_bp = Blueprint('pokemon', __name__, url_prefix='/')
pokemon_service = PokemonService()

@pokemon_bp.route('/', methods=['GET'], strict_slashes=False)
@handle_api_errors
def welcome():
    return create_response(get_welcome_message())

@pokemon_bp.route('/pokedex', methods=['GET'], strict_slashes=False)
@handle_api_errors
def instructions():
    return create_response(get_pokedex_instructions())

@pokemon_bp.route('/pokedex/<name>', methods=['GET'], strict_slashes=False)
@requires_auth
@handle_api_errors
def get_pokemon(name):
    try:
        pokemon_data = pokemon_service.get_pokemon_by_name(name)
        return create_response(pokemon_data)
    except Exception as e:
        current_app.logger.error(f"Error getting pokemon: {str(e)}")
        return create_response({
            "error": "¡Ups! No conozco ese Pokémon... ¿es uno de los nuevos?",
            "sugerencia": "Revisá que el nombre esté bien escrito."
        }, 404)

@pokemon_bp.route('/pokedex/types', methods=['GET'], strict_slashes=False)
@requires_auth
@handle_api_errors
def get_available_types():
    try:
        types_data = pokemon_service.get_pokemon_types()
        if types_data:
            return create_response(types_data)
        raise Exception("No types data returned")
    except Exception as e:
        current_app.logger.error(f"Error getting types: {str(e)}")
        return create_response({
            "error": "¡Ups! Parece que hay problemas técnicos.",
            "sugerencia": "Intentalo de nuevo en unos momentos."
        }, 500)

@pokemon_bp.route('pokedex/whos-that-pokemon', methods=['GET'], strict_slashes=False)
@requires_auth
@handle_api_errors
def random_pokemon():
    try:
        pokemon_data = pokemon_service.get_random_pokemon()
        if pokemon_data:
            return create_response(pokemon_data)
        raise Exception("No random pokemon data returned")
    except Exception as e:
        current_app.logger.error(f"Error getting random pokemon: {str(e)}")
        return create_response({
            "error": "¡Ups! El Pokémon se escapó...",
            "sugerencia": "¡Intentalo de nuevo!"
        }, 500)

@pokemon_bp.route('pokedex/whos-that-pokemon/<type>', methods=['GET'], strict_slashes=False)
@requires_auth
@handle_api_errors
def random_pokemon_by_type(type):
    try:
        pokemon_data = pokemon_service.get_random_pokemon_by_type(type)
        return create_response(pokemon_data)
    except Exception as e:
        current_app.logger.error(f"Error getting random pokemon by type: {str(e)}")
        return create_response({
            "error": f"¡Ups! No conozco el tipo '{type}'",
            "sugerencia": "Probá con tipos como 'fire', 'water', 'electric', etc."
        }, 404)

@pokemon_bp.route('pokedex/longest/<type>', methods=['GET'], strict_slashes=False)
@requires_auth
@handle_api_errors
def longest_name_pokemon(type):
    try:
        pokemon_data = pokemon_service.get_longest_name_pokemon_by_type(type)
        return create_response(pokemon_data)
    except Exception as e:
        current_app.logger.error(f"Error getting longest name pokemon: {str(e)}")
        return create_response({
            "error": f"¡Ups! No conozco el tipo '{type}'",
            "sugerencia": "Probá con tipos como 'fire', 'water', 'electric', etc."
        }, 404)