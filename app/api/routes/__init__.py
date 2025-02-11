from flask import Flask
from .auth import auth_bp
from .pokemon import pokemon_bp

def register_routes(app: Flask):
    """
    Registra todos los blueprints de la aplicación
    """
    app.register_blueprint(auth_bp)
    app.register_blueprint(pokemon_bp)