"""Camada Controller: blueprints que recebem as requisições e escolhem a View."""
from . import carrinho, vitrine

BLUEPRINTS = [vitrine.bp, carrinho.bp]
