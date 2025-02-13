"""
Módulo de rutas de la Pokedex.
Define los endpoints para las diferentes funcionalidades de la API.
"""

from flask import Blueprint, current_app
from app.services.pokemon_service import PokemonService
from app.utils.decorators import handle_api_errors, requires_auth
from app.utils.responses import (
    create_response,
    get_welcome_message,
    get_pokedex_instructions
)
from app.utils.logger import get_logger

pokemon_bp = Blueprint('pokemon', __name__, url_prefix='/') #Organiza el grupo de paths en un blueprint
pokemon_service = PokemonService() #Inicia el servicio /../services/pokemon_service.py
logger = get_logger()

@pokemon_bp.route('/', methods=['GET'], strict_slashes=False)
@handle_api_errors
def welcome():
    """
    Endpoint de bienvenida.
    Muestra un mensaje inicial con instrucciones básicas.
    
    Returns:
        Response: Mensaje de bienvenida
    """
    logger.info('Acceso a la página de bienvenida')
    return create_response(get_welcome_message())

@pokemon_bp.route('/pokedex', methods=['GET'], strict_slashes=False)
@handle_api_errors
def instructions():
    """
    Endpoint de instrucciones.
    Proporciona una lista de todas las funcionalidades desarrolladas para la API.
    
    Returns:
        Response: Lista de endpoints y sus descripciones
    """
    logger.info('Acceso a las instrucciones de la Pokedex')
    return create_response(get_pokedex_instructions())

@pokemon_bp.route('/pokedex/<name>', methods=['GET'], strict_slashes=False)
@requires_auth
@handle_api_errors
def get_pokemon(name):
    """
    Endpoint para obtener información de un Pokemon específico por nombre.
    
    Args:
        name (str): Nombre del Pokemon a buscar
    
    Returns:
        Response: Información detallada del Pokemon o mensaje de error
        
    Status codes:
        200: Pokemon encontrado
        404: Pokemon no encontrado
    """
    logger.info(f'Buscando información del Pokemon: {name}')
    try:
        pokemon_data = pokemon_service.get_pokemon_by_name(name)
        logger.info(f'Información obtenida exitosamente para: {name}')
        return create_response(pokemon_data)
    except Exception as e:
        logger.error(f'Error al buscar Pokemon {name}: {str(e)}')
        return create_response({
            "error": "¡Ups! No conozco ese Pokemon... ¿es uno de los nuevos?",
            "sugerencia": "Revisá que el nombre esté bien escrito."
        }, 404)

@pokemon_bp.route('/pokedex/types', methods=['GET'], strict_slashes=False)
@requires_auth
@handle_api_errors
def get_available_types():
    """
    Endpoint para obtener todos los tipos de Pokemon disponibles.
    
    Returns:
        Response: Lista de tipos de Pokemon o mensaje de error
        
    Status codes:
        200: Tipos obtenidos correctamente
        500: Error interno
    """
    logger.info('Consultando tipos de Pokemon disponibles')
    try:
        types_data = pokemon_service.get_pokemon_types()
        if types_data:
            logger.info('Tipos de Pokemon obtenidos exitosamente')
            return create_response(types_data)
        raise Exception("No se obtuvieron datos de tipos")
    except Exception as e:
        logger.error(f'Error al obtener tipos de Pokemon: {str(e)}')
        return create_response({
            "error": "¡Ups! Parece que hay problemas técnicos.",
            "sugerencia": "Intentalo de nuevo en unos momentos."
        }, 500)

@pokemon_bp.route('pokedex/whos-that-pokemon', methods=['GET'], strict_slashes=False)
@requires_auth
@handle_api_errors
def random_pokemon():
    """
    Endpoint para obtener un Pokemon aleatorio.
    
    Returns:
        Response: Información del Pokemon aleatorio o mensaje de error
        
    Status codes:
        200: Pokemon obtenido correctamente
        500: Error interno
    """
    logger.info('Solicitando Pokemon aleatorio')
    try:
        pokemon_data = pokemon_service.get_random_pokemon()
        if pokemon_data:
            logger.info(f'Pokemon aleatorio obtenido: {pokemon_data["pokemon"]["nombre"]}')
            return create_response(pokemon_data)
        raise Exception("No se obtuvieron datos del Pokemon aleatorio")
    except Exception as e:
        logger.error(f'Error al obtener Pokemon aleatorio: {str(e)}')
        return create_response({
            "error": "¡Ups! El Pokemon se escapó...",
            "sugerencia": "¡Intentalo de nuevo!"
        }, 500)

@pokemon_bp.route('pokedex/whos-that-pokemon/<type>', methods=['GET'], strict_slashes=False)
@requires_auth
@handle_api_errors
def random_pokemon_by_type(type):
    """
    Endpoint para obtener un Pokemon aleatorio de un tipo específico.
    
    Args:
        type (str): Tipo de Pokemon (ej: fire, water, electric)
    
    Returns:
        Response: Información del Pokemon aleatorio del tipo especificado o mensaje de error
        
    Status codes:
        200: Pokemon encontrado
        404: Tipo de Pokemon no válido
    """
    logger.info(f'Solicitando Pokemon aleatorio de tipo: {type}')
    try:
        pokemon_data = pokemon_service.get_random_pokemon_by_type(type)
        logger.info(f'Pokemon aleatorio de tipo {type} obtenido: {pokemon_data["pokemon"]["nombre"]}')
        return create_response(pokemon_data)
    except Exception as e:
        logger.error(f'Error al obtener Pokemon aleatorio de tipo {type}: {str(e)}')
        return create_response({
            "error": f"¡Ups! No conozco el tipo '{type}'",
            "sugerencia": "Probá con tipos como 'fire', 'water', 'electric', etc."
        }, 404)

@pokemon_bp.route('pokedex/longest/<type>', methods=['GET'], strict_slashes=False)
@requires_auth
@handle_api_errors
def longest_name_pokemon(type):
    """
    Endpoint para obtener el Pokemon con el nombre más largo de un tipo específico.
    
    Args:
        type (str): Tipo de Pokemon (ej: fire, water, electric)
    
    Returns:
        Response: Información del Pokemon con el nombre más largo del tipo especificado
        
    Status codes:
        200: Pokemon encontrado
        404: Tipo de Pokemon no válido
    """
    logger.info(f'Buscando Pokemon con nombre más largo de tipo: {type}')
    try:
        pokemon_data = pokemon_service.get_longest_name_pokemon_by_type(type)
        logger.info(f'Encontrado Pokemon con nombre más largo de tipo {type}: {pokemon_data["pokemon"]["nombre"]}')
        return create_response(pokemon_data)
    except Exception as e:
        logger.error(f'Error al buscar Pokemon con nombre más largo de tipo {type}: {str(e)}')
        return create_response({
            "error": f"¡Ups! No conozco el tipo '{type}'",
            "sugerencia": "Probá con tipos como 'fire', 'water', 'electric', etc."
        }, 404)