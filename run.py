"""
Punto de entrada principal de la aplicación.
Este módulo inicializa y ejecuta la aplicación Flask (Pokedex).

El servidor se ejecutará en modo debug en el puerto 5000 cuando se ejecute 
directamente como script.
"""

from app import create_app
from app.utils.logger import get_logger

logger = get_logger() #Obtiene logger
app = create_app() #
"""
Función flask para crear app
Desde init de /app obtiene las funciones que:
    1. Crea una nueva instancia de Flask
    2. Carga la configuración base y variables de entorno
    3. Configura el manejo de URLs (trailing slashes)
    4. Registra todas las rutas de la API
    5. Configura los manejadores de errores
    
    Returns:
        Aplicación Flask configurada y lista para ejecutar
"""
if __name__ == '__main__':
    logger.info('---Iniciando Pokedex API')
    app.run(debug=True, port=5000)