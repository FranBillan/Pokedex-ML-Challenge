from flask import Flask
from app.api.routes import register_routes
from app.api.errors.handlers import register_error_handlers
from app.config.settings import load_config

def create_app():
    """
    Crea y configura la aplicación Flask
    """
    app = Flask(__name__)
    
    # Cargar configuración
    load_config(app)
    
    # Configuración para permitir trailing slashes
    app.url_map.strict_slashes = False
    
    # Registrar rutas
    register_routes(app)
    
    # Registrar manejadores de errores
    register_error_handlers(app)
    
    
    return app