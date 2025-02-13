"""
Importa desde settings las variables de entorno y las dispone como paquete python para ser consumidas en init de app
"""
from .settings import OKTA_DOMAIN, OKTA_CLIENT_ID, OKTA_CLIENT_SECRET, load_config

__all__ = ['OKTA_DOMAIN', 'OKTA_CLIENT_ID', 'OKTA_CLIENT_SECRET', 'load_config']