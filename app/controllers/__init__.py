"""Camada Controller: blueprints que recebem as requisições e escolhem a View."""
from . import admin, autenticacao, carrinho, checkout, conta, pagamento, pedidos, vitrine

BLUEPRINTS = [vitrine.bp, carrinho.bp, autenticacao.bp, conta.bp, checkout.bp, pagamento.bp, pedidos.bp, admin.bp]
