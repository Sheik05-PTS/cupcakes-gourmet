"""Atalhos usados pelos testes de integração."""
from app.extensions import db
from app.models import Endereco, Pedido

RED_VELVET, LIMAO, PISTACHE, CACAU = 1, 3, 4, 7
GANACHE, CREAM_CHEESE = 2, 5
CARTAO_OK = {"numero": "4111 1111 1111 1111", "nome": "ANA P SOUZA", "validade": "12/30", "cvv": "123"}
CARTAO_RECUSADO = {**CARTAO_OK, "numero": "4000 0000 0000 0002"}


def criar_conta(client, email="ana@example.com", senha="Teste2026", proximo=""):
    return client.post("/criar-conta", data={"nome": "Ana Paula Souza", "email": email, "telefone": "(11) 98765-4321",
                                             "senha": senha, "proximo": proximo}, follow_redirects=True)


def entrar(client, email, senha):
    return client.post("/entrar", data={"email": email, "senha": senha}, follow_redirects=True)


def cadastrar_endereco(client, cep="01310-100", **extra):
    dados = {"apelido": "Casa", "cep": cep, "logradouro": "Av. Paulista", "numero": "1000", "complemento": "ap. 52",
             "bairro": "Bela Vista", "cidade": "São Paulo", "uf": "SP", **extra}
    return client.post("/conta/enderecos/novo", data=dados, follow_redirects=True)


def adicionar(client, cupcake_id, quantidade=1, **extra):
    return client.post("/carrinho/itens", data={"cupcake_id": cupcake_id, "quantidade": quantidade, **extra},
                       follow_redirects=True)


def carrinho_do_prototipo(client):
    """2 Red Velvet (Ganache, Cream cheese, mensagem) + 3 Limão Siciliano = R$ 61,50."""
    adicionar(client, RED_VELVET, 2, recheio_id=GANACHE, cobertura_id=CREAM_CHEESE, mensagem="Feliz aniversário, Ana!")
    adicionar(client, LIMAO, 3)


def ultimo_endereco():
    return db.session.scalars(db.select(Endereco).order_by(Endereco.id.desc())).first()


def ultimo_pedido():
    db.session.expire_all()
    return db.session.scalars(db.select(Pedido).order_by(Pedido.id.desc())).first()


def fazer_pedido(client, cupom=None):
    """Cria conta, endereço e carrinho do protótipo e confirma o checkout. Devolve o pedido."""
    criar_conta(client)
    cadastrar_endereco(client)
    carrinho_do_prototipo(client)
    if cupom:
        client.post("/checkout/cupom", data={"codigo": cupom})
    client.post("/checkout/confirmar", data={"endereco_id": ultimo_endereco().id})
    return ultimo_pedido()
