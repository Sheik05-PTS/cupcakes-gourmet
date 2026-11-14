"""Testes de integração do checkout: frete, cupom e criação do pedido (UC10, US07, US11, RN10)."""
from decimal import Decimal

from app.extensions import db
from app.models import Cupcake, StatusPedido
from tests.conftest import html
from tests.integration.ajuda import (LIMAO, cadastrar_endereco, carrinho_do_prototipo, criar_conta, fazer_pedido,
                                     ultimo_endereco, ultimo_pedido)


def preparar(client, cep="01310-100"):
    criar_conta(client)
    cadastrar_endereco(client, cep=cep)
    carrinho_do_prototipo(client)


def test_ca10_3_checkout_lista_enderecos_e_calcula_frete(client):
    preparar(client)
    texto = html(client.get("/checkout"))
    assert "Av. Paulista, 1000" in texto
    assert "Frete R$ 8,00 · entrega até 90 minutos" in texto
    assert "R$ 69,50" in texto  # 61,50 + 8,00


def test_ca11_2_endereco_fora_da_area_bloqueia_o_pagamento(client):
    preparar(client, cep="20040-020")
    texto = html(client.get("/checkout"))
    assert "Ainda não entregamos neste CEP." in texto
    assert '<button class="btn" type="button" disabled>Ir para o pagamento</button>' in texto
    client.post("/checkout/confirmar", data={"endereco_id": ultimo_endereco().id})
    assert ultimo_pedido() is None


def test_ca07_1_cupom_valido_aplica_desconto(client):
    preparar(client)
    texto = html(client.post("/checkout/cupom", data={"codigo": "doce10"}, follow_redirects=True))
    assert "Cupom aplicado: 10% de desconto nos produtos." in texto
    assert "− R$ 6,15" in texto and "R$ 63,35" in texto  # valores do protótipo (T07)


def test_ca07_2_cupom_vencido(client):
    preparar(client)
    texto = html(client.post("/checkout/cupom", data={"codigo": "VERAO2025"}, follow_redirects=True))
    assert "Cupom inválido ou expirado." in texto


def test_ca07_3_cupom_abaixo_do_minimo(client):
    criar_conta(client)
    cadastrar_endereco(client)
    client.post("/carrinho/itens", data={"cupcake_id": LIMAO, "quantidade": 1})
    texto = html(client.post("/checkout/cupom", data={"codigo": "DOCE10"}, follow_redirects=True))
    assert "Este cupom vale para pedidos a partir de R$ 30,00." in texto


def test_ca07_4_novo_cupom_substitui_o_anterior(client):
    preparar(client)
    client.post("/checkout/cupom", data={"codigo": "DOCE10"})
    texto = html(client.post("/checkout/cupom", data={"codigo": "BEMVINDO5"}, follow_redirects=True))
    assert "Desconto BEMVINDO5" in texto and "Desconto DOCE10" not in texto


def test_remover_cupom(client):
    preparar(client)
    client.post("/checkout/cupom", data={"codigo": "DOCE10"})
    texto = html(client.post("/checkout/cupom/remover", follow_redirects=True))
    assert "Desconto DOCE10" not in texto and "R$ 69,50" in texto


def test_uc10_confirmar_cria_pedido_com_valores_e_endereco_copiados(client):
    pedido = fazer_pedido(client, cupom="DOCE10")
    assert pedido.status == StatusPedido.AGUARDANDO_PAGAMENTO
    assert (pedido.subtotal, pedido.desconto, pedido.frete, pedido.total) == (
        Decimal("61.50"), Decimal("6.15"), Decimal("8.00"), Decimal("63.35"))
    assert pedido.entrega_cep == "01310100" and pedido.entrega_complemento == "ap. 52"
    assert [h.status for h in pedido.historico] == [StatusPedido.AGUARDANDO_PAGAMENTO]
    item = pedido.itens[0]
    assert item.preco_unitario == Decimal("14.40") and item.recheio.nome == "Ganache"
    assert item.mensagem == "Feliz aniversário, Ana!"


def test_rn10_preco_fica_congelado_no_pedido(client):
    pedido = fazer_pedido(client)
    db.session.get(Cupcake, LIMAO).preco = Decimal("99.00")
    db.session.commit()
    pedido = ultimo_pedido()
    assert next(i for i in pedido.itens if i.cupcake_id == LIMAO).preco_unitario == Decimal("10.90")


def test_m2_excluir_endereco_nao_altera_pedido(client):
    pedido = fazer_pedido(client)
    client.post(f"/conta/enderecos/{ultimo_endereco().id}/excluir")
    assert ultimo_pedido().entrega_logradouro == "Av. Paulista" and pedido.id == ultimo_pedido().id


def test_uc10_fe2_item_que_esgotou_impede_criar_o_pedido(client):
    preparar(client)
    db.session.get(Cupcake, LIMAO).estoque = 1
    db.session.commit()
    client.post("/checkout/confirmar", data={"endereco_id": ultimo_endereco().id})
    assert ultimo_pedido() is None


def test_checkout_com_carrinho_vazio_volta_para_o_carrinho(client):
    criar_conta(client)
    resposta = client.get("/checkout")
    assert resposta.status_code == 302 and resposta.headers["Location"].endswith("/carrinho")


def test_nao_aceita_endereco_de_outro_cliente(client):
    criar_conta(client, email="dona@example.com")
    cadastrar_endereco(client)
    endereco_alheio = ultimo_endereco().id
    client.post("/sair")
    criar_conta(client, email="outra@example.com")
    carrinho_do_prototipo(client)
    client.post("/checkout/confirmar", data={"endereco_id": endereco_alheio})
    assert ultimo_pedido() is None
