"""
Módulo de servicio de Pokemon.
Proporciona una interfaz para interactuar con la PokeAPI y obtener información 
sobre diferentes Pokemon y sus características.
"""

import requests
import random
from typing import Dict, List, Optional
from app.utils.logger import get_logger

logger = get_logger()

class PokemonService:
    """
    Servicio para interactuar con la PokeAPI.
    
    Attributes:
        base_url (str): URL base de la PokeAPI
    """
    
    def __init__(self):
        """Inicializa el servicio con la URL base de la PokeAPI."""
        self.base_url = 'https://pokeapi.co/api/v2'
        logger.debug('Servicio Pokemon inicializado')
     
    def _make_request(self, url: str) -> requests.Response:
        """
        Método auxiliar para hacer requests con manejo de errores consistente.
        
        Args:
            url (str): URL a consultar
            
        Returns:
            requests.Response: Respuesta de la API
            
        Raises:
            requests.exceptions.HTTPError: Si el recurso no existe (404)
            requests.exceptions.RequestException: Si hay problemas de conexión
            
        Ejemplo:
            >>> response = self._make_request('https://pokeapi.co/api/v2/pokemon/pikachu')
            >>> data = response.json()
        """
        logger.debug(f'Realizando petición a: {url}')
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            logger.debug(f'Petición exitosa. Status code: {response.status_code}')
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f'---Error en petición a PokeAPI: {str(e)}')
            raise
    
    def get_pokemon_by_name(self, name: str) -> Dict:
        """
        Obtiene información detallada de un Pokemon por su nombre.
        
        Args:
            name (str): Nombre del Pokemon
            
        Returns:
            Dict: Información detallada del Pokemon incluyendo tipos, stats y habilidades
            
        Ejemplo:
            >>> pokemon_info = get_pokemon_by_name('pikachu')
            >>> print(pokemon_info['pokemon']['tipos'])
        """
        logger.info(f'---Buscando información del Pokemon: {name}')
        response = self._make_request(f'{self.base_url}/pokemon/{name.lower()}')
        data = response.json()
        
        return {
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
        logger.info(f'---Información obtenida exitosamente para: {name}')

    def get_pokemon_types(self) -> Dict:
        """
        Obtiene todos los tipos de Pokemon disponibles
        
        Returns:
            Dict: Lista de tipos de Pokemon
        """
        response = self._make_request(f'{self.base_url}/type')
        data = response.json()
        
        valid_types = [
            type_data['name'] 
            for type_data in data['results'] 
            if type_data['name'] not in ['unknown', 'shadow']
        ]
        
        return {
            "mensaje": "¡Estos son todos los tipos de Pokemon disponibles!",
            "tipos": valid_types,
            "consejo": "Podés usar estos tipos en endpoints como /whos-that-pokemon/<tipo> o /longest/<tipo>"
        }
    
    def get_pokemon_by_type(self, type_name: str) -> List[str]:
        """
        Obtiene todos los Pokemon de un tipo específico
        
        Args:
            type_name (str): Nombre del tipo
            
        Returns:
            List[str]: Lista de nombres de Pokemon
        """
        response = self._make_request(f'{self.base_url}/type/{type_name.lower()}')
        data = response.json()
        return [pokemon['pokemon']['name'] for pokemon in data['pokemon']]
    
    def get_random_pokemon(self) -> Dict:
        """
        Obtiene un Pokemon aleatorio
        
        Returns:
            Dict: Información del Pokemon aleatorio
        """
        random_id = random.randint(1, 898)  # Límite de la PokeAPI
        response = self._make_request(f'{self.base_url}/pokemon/{random_id}')
        data = response.json()
        
        return {
            "mensaje": "¡Un Pokemon salvaje apareció!",
            "pokemon": {
                "nombre": data["name"],
                "tipos": [t["type"]["name"] for t in data["types"]],
                "altura": f"{data['height']/10} mt",
                "peso": f"{data['weight']/10} kg",
                "número_pokedex": data["id"]
            }
        }
    
    def get_random_pokemon_by_type(self, type_name: str) -> Dict:
        """
        Obtiene un Pokemon aleatorio de un tipo específico (solo formas default)
        
        Args:
            type_name (str): Nombre del tipo
                
        Returns:
            Dict: Información del Pokemon aleatorio
        """
        pokemons_of_type = self.get_pokemon_by_type(type_name)
        
        while True:
            random_name = random.choice(pokemons_of_type)
            response = self._make_request(f'{self.base_url}/pokemon/{random_name}')
            data = response.json()
            
            if data.get("is_default", False): #Verifica que sea un Pokemon base (no variaciones)
                return {
                    "mensaje": f"¡Un Pokemon salvaje de tipo {type_name} apareció!",
                    "pokemon": {
                        "nombre": data["name"],
                        "tipos": [t["type"]["name"] for t in data["types"]],
                        "altura": f"{data['height']/10} mt",
                        "peso": f"{data['weight']/10} kg",
                        "número_pokedex": data["id"]
                    }
                }
    
    def get_longest_name_pokemon_by_type(self, type_name: str) -> Dict:
        """
        Obtiene el Pokemon con el nombre más largo de un tipo específico (solo formas default)
        
        Args:
            type_name (str): Nombre del tipo
                
        Returns:
            Dict: Información del Pokemon
        """
        pokemons = self.get_pokemon_by_type(type_name) #Obtiene todos los Pokemon de un tipo.
        
        # Ordena lista por longitud de mayor a menor
        sorted_names = sorted(pokemons, key=len, reverse=True)
        
        # Itera en la lista hasta encontrar un Pokemon base (no variaciones)
        for pokemon_name in sorted_names:
            response = self._make_request(f'{self.base_url}/pokemon/{pokemon_name}')
            data = response.json()
            
            if data.get("is_default", False):
                return {
                    "mensaje": f"¡El Pokemon de tipo {type_name} con el nombre más largo es...",
                    "pokemon": {
                        "nombre": data["name"],
                        "tipos": [t["type"]["name"] for t in data["types"]],
                        "longitud_nombre": f"{len(data['name'])} caracteres",
                        "número_pokedex": data["id"]
                    }
                }