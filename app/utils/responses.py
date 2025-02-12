"""
Módulo de manejo de respuestas HTTP.
Proporciona funciones para crear respuestas JSON consistentes y mensajes 
predefinidos para diferentes situaciones de la API.
"""

from flask import Response
import json
from typing import Dict, Any, Union
from app.utils.logger import get_logger

logger = get_logger() #Recupera instancia de logger

def create_response(data: Dict[str, Any], status_code: int = 200) -> Response:
    """
    Crea una respuesta HTTP JSON.
    
    Args:
        data (Dict[str, Any]): Datos a enviar en la respuesta. Ej: body de un Pokemon obtenido.
        status_code (int, optional): Código de estado HTTP. Default = 200.
        
    Returns:
        Response: Respuesta HTTP.
    """
    logger.debug(f'Generando respuesta HTTP - Status: {status_code} - Data: {data}')
    return Response(
        json.dumps(data, ensure_ascii=False),
        mimetype='application/json',
        status=status_code
    )

def create_auth_error_response() -> Dict[str, str]:
    """
    Crea un mensaje de error para cuando falta el token de autenticación en la solicitud.
    
    Returns:
        Dict[str, str]: Mensaje de error.
    """
    return {
        "error": "Esta función está disponible solo para entrenadores autorizados. Presentá tu ficha de entrenador.",
        "sugerencia": "Debés incluir en el header 'Authorization: Bearer <token>' el código obtenido en /obtener-ficha"
    }

def create_invalid_token_response() -> Dict[str, str]:
    """
    Crea un mensaje de error para cuando el token es inválido o está inactivo.
    
    Returns:
        Dict[str, str]: Mensaje de error.
    """
    return {
        "error": "Ficha inactiva... ¿Te expulsaron de la liga? Tal vez solo tengas que tramitar una nueva.",
        "sugerencia": "Obtené un nuevo token en /obtener-ficha"
    }

def get_welcome_message() -> Dict[str, str]:
    """
    Obtiene el mensaje de status y tip para redirigir al endpoint con funciones.
    
    Returns:
        Dict[str, str]: Mensaje de bienvenida.
    """
    return {
        "mensaje": "¡Pokedex en línea, bienvenido!",
        "consejo": "GET a /pokedex para ver todas las funciones disponibles."
    }

def get_pokedex_instructions() -> Dict[str, Union[str, list]]:
    """
    Obtiene las instrucciones de uso de Pokedex.
    
    Returns:
        Dict[str, Union[str, list]]: Instrucciones formateadas.
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