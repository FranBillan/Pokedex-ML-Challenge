import requests
import random
from typing import Dict, List, Union, Optional
from app.api.errors.handlers import PokemonNotFoundError, TypeNotFoundError, ConnectionError

class PokemonService:
    def __init__(self):
        self.base_url = 'https://pokeapi.co/api/v2'
     
    def _make_request(self, url: str) -> requests.Response:
        """Método auxiliar para hacer requests con manejo de errores consistente"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Levanta una excepción para códigos de error HTTP
            return response
        except requests.exceptions.RequestException as e:
            raise ConnectionError()    
    
    def get_pokemon_by_name(self, name: str) -> Dict:
        """
        Obtiene información detallada de un Pokémon por su nombre
        """
        try:
            url = f'{self.base_url}/pokemon/{name.lower()}'
            response = requests.get(url)
            
            if response.status_code == 404:
                raise PokemonNotFoundError(name)
                
            if response.status_code == 200:
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
            
            raise ConnectionError()
            
        except requests.exceptions.RequestException:
            raise ConnectionError()

    def get_pokemon_types(self) -> Dict:
        """
        Obtiene todos los tipos de Pokémon disponibles
        
        Returns:
            dict: Lista de tipos de Pokémon
        """
        response = self._make_request(f'{self.base_url}/type')
        data = response.json()
        
        valid_types = [
            type_data['name'] 
            for type_data in data['results'] 
            if type_data['name'] not in ['unknown', 'shadow']
        ]
        
        return {
            "mensaje": "¡Estos son todos los tipos de Pokémon disponibles!",
            "tipos": valid_types,
            "consejo": "Podés usar estos tipos en endpoints como /whos-that-pokemon/<tipo> o /longest/<tipo>"
        }
    
    def get_pokemon_by_type(self, type_name: str) -> List[str]:
        """
        Obtiene todos los Pokémon de un tipo específico
        """
        try:
            url = f'{self.base_url}/type/{type_name.lower()}'
            response = requests.get(url)
            
            if response.status_code == 404:
                raise TypeNotFoundError(type_name)
                
            if response.status_code == 200:
                data = response.json()
                return [pokemon['pokemon']['name'] for pokemon in data['pokemon']]
            
            raise ConnectionError()
            
        except requests.exceptions.RequestException:
            raise ConnectionError()
    
    def get_random_pokemon(self) -> Dict:
        """
        Obtiene un Pokémon aleatorio
        
        Returns:
            dict: Información del Pokémon aleatorio
        """
        random_id = random.randint(1, 898)  # Límite de la PokeAPI
        response = self._make_request(f'{self.base_url}/pokemon/{random_id}')
        data = response.json()
        
        return {
            "mensaje": "¡Un Pokémon salvaje apareció!",
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
        Obtiene un Pokémon aleatorio de un tipo específico
        """
        # Primero verificamos si el tipo existe
        pokemons_of_type = self.get_pokemon_by_type(type_name)  # Esto ya lanzará TypeNotFoundError si es necesario
        
        try:
            random_name = random.choice(pokemons_of_type)
            url = f'{self.base_url}/pokemon/{random_name}'
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "mensaje": f"¡Un Pokémon salvaje de tipo {type_name} apareció!",
                    "pokemon": {
                        "nombre": data["name"],
                        "tipos": [t["type"]["name"] for t in data["types"]],
                        "altura": f"{data['height']/10} mt",
                        "peso": f"{data['weight']/10} kg",
                        "número_pokedex": data["id"]
                    }
                }
            
            raise ConnectionError()
            
        except requests.exceptions.RequestException:
            raise ConnectionError()
    
    def get_longest_name_pokemon_by_type(self, type_name: str) -> Dict:
        """
        Obtiene el Pokémon con el nombre más largo de un tipo específico
        """
        # Primero verificamos si el tipo existe
        pokemons = self.get_pokemon_by_type(type_name)  # Esto ya lanzará TypeNotFoundError si es necesario
        
        try:
            longest_name = max(pokemons, key=len)
            url = f'{self.base_url}/pokemon/{longest_name}'
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "mensaje": f"¡El Pokémon de tipo {type_name} con el nombre más largo es...",
                    "pokemon": {
                        "nombre": data["name"],
                        "tipos": [t["type"]["name"] for t in data["types"]],
                        "longitud_nombre": f"{len(data['name'])} caracteres",
                        "número_pokedex": data["id"]
                    }
                }
            
            raise ConnectionError()
            
        except requests.exceptions.RequestException:
            raise ConnectionError()