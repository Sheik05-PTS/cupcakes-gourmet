"""Testes de integração do pagamento simulado (US08, US09, RN11–RN14, RNF07)."""
import threading
from datetime import timedelta
from decimal import Decimal

from app.extensions import db
from app.models import (Cupcake, GatewaySimulado, ItemPedido, MetodoPagamento, Pagamento, Pedido, RegraDeNegocio,
                        ServicoPagamento, StatusPagamento, StatusPedido, Usuario)
from app.models.pedido import agora
from tests.conftest import html
from tests.integration.ajuda import CARTAO_OK, CARTAO_RECUSADO, LIMAO, RED_VELVET, fazer_pedido, ultimo_pedido


def pagar_cartao(client, pedido, dados):
    return client.post(f"/pedidos/{pedido.id}/pagamento/cartao", data=dados, follow_redirects=True)


def test_rn21_tela_de_pagamento_avisa_que_e_demonstracao(client):
    pedido = fazer_pedido(client)
    assert "Ambiente de demonstração: nenhuma cobrança real é feita." in html(client.get(f"/pedidos/{pedido.id}/pagamento"))


def test_ca08_4_e_ca09_1_cartao_aprovado_confirma_o_pedido(client):
    pedido = fazer_pedido(client, cupom="DOCE10")
    texto = html(pagar_cartao(client, pedido, CARTAO_OK))
    assert "Pedido confirmado!" in texto and "cartão Visa final 1111" in texto
    assert "R$ 63,35" in texto and "Previsão de entrega: até 90 minutos" in texto
    pedido = ultimo_pedido()
    assert pedido.status == StatusPedido.PAGO
    assert [h.status for h in pedido.historico] == [StatusPedido.AGUARDANDO_PAGAMENTO, StatusPedido.PAGO]


def test_ca09_3_carrinho_fica_vazio_apos_confirmacao(client):
    pedido = fazer_pedido(client)
    pagar_cartao(client, pedido, CARTAO_OK)
    with client.session_transaction() as sessao:
        assert sessao.get("carrinho") == []


def test_rn13_estoque_baixa_na_aprovacao(client):
    pedido = fazer_pedido(client)
    antes = {c: db.session.get(Cupcake, c).estoque for c in (RED_VELVET, LIMAO)}
    pagar_cartao(client, pedido, CARTAO_OK)
    db.session.expire_all()
    assert db.session.get(Cupcake, RED_VELVET).estoque == antes[RED_VELVET] - 2
    assert db.session.get(Cupcake, LIMAO).estoque == antes[LIMAO] - 3


def test_ca08_5_cartao_0002_recusado_e_pedido_continua_aguardando(client):
    pedido = fazer_pedido(client)
    texto = html(pagar_cartao(client, pedido, CARTAO_RECUSADO))
    assert "Pagamento recusado." in texto and "Tente outro cartão ou pague com Pix." in texto
    pedido = ultimo_pedido()
    assert pedido.status == StatusPedido.AGUARDANDO_PAGAMENTO
    assert pedido.pagamentos[-1].status == StatusPagamento.RECUSADO


def test_ca08_6_dados_invalidos_nao_apagam_o_que_foi_digitado(client):
    pedido = fazer_pedido(client)
    resposta = pagar_cartao(client, pedido, {**CARTAO_OK, "validade": "01/20", "cvv": "1"})
    texto = html(resposta)
    assert resposta.status_code == 422
    assert "Cartão vencido." in texto and "O CVV tem 3 ou 4 dígitos." in texto
    assert 'value="4111 1111 1111 1111"' in texto and 'value="1"' not in texto


def test_ca08_7_e_rn12_so_bandeira_e_final_do_cartao_sao_gravados(client):
    pedido = fazer_pedido(client)
    pagar_cartao(client, pedido, CARTAO_OK)
    pagamento = ultimo_pedido().pagamento_aprovado()
    assert (pagamento.cartao_bandeira, pagamento.cartao_final) == ("Visa", "1111")
    colunas = {c.name for c in Pagamento.__table__.columns}
    assert not {"numero", "cvv", "cartao_numero"} & colunas


def test_ca08_1_e_ca08_2_pix_gera_codigo_e_simular_confirma(client):
    pedido = fazer_pedido(client)
    texto = html(client.post(f"/pedidos/{pedido.id}/pagamento/pix", follow_redirects=True))
    assert "Código \"copia e cola\" fictício" in texto and "Simular pagamento" in texto
    pix = ultimo_pedido().pagamentos[-1]
    assert pix.metodo == MetodoPagamento.PIX and pix.status == StatusPagamento.PENDENTE
    texto = html(client.post(f"/pagamentos/{pix.id}/confirmar", follow_redirects=True))
    assert "Pedido confirmado!" in texto and "pago com Pix" in texto


def test_ca08_3_pix_expirado(client):
    pedido = fazer_pedido(client)
    client.post(f"/pedidos/{pedido.id}/pagamento/pix")
    pix = ultimo_pedido().pagamentos[-1]
    pix.pix_expira_em = agora() - timedelta(seconds=1)
    db.session.commit()
    texto = html(client.post(f"/pagamentos/{pix.id}/confirmar", follow_redirects=True))
    assert "Código Pix expirado. Gere um novo código para pagar." in texto
    assert ultimo_pedido().pagamentos[-1].status == StatusPagamento.EXPIRADO
    assert ultimo_pedido().status == StatusPedido.AGUARDANDO_PAGAMENTO  # RN14


def test_rn14_nova_tentativa_depois_de_recusa(client):
    pedido = fazer_pedido(client)
    pagar_cartao(client, pedido, CARTAO_RECUSADO)
    assert "Pedido confirmado!" in html(pagar_cartao(client, pedido, CARTAO_OK))
    assert [p.status for p in ultimo_pedido().pagamentos] == [StatusPagamento.RECUSADO, StatusPagamento.APROVADO]


def test_ca08_8_estoque_insuficiente_na_aprovacao(client):
    pedido = fazer_pedido(client)
    db.session.get(Cupcake, LIMAO).estoque = 2  # alguém comprou depois do checkout
    db.session.commit()
    texto = html(pagar_cartao(client, pedido, CARTAO_OK))
    assert "Limão Siciliano ficou indisponível." in texto
    pedido = ultimo_pedido()
    assert pedido.status == StatusPedido.AGUARDANDO_PAGAMENTO
    assert pedido.pagamentos[-1].motivo_recusa == "Estoque insuficiente no momento da aprovação."
    assert db.session.get(Cupcake, LIMAO).estoque == 2 and db.session.get(Cupcake, RED_VELVET).estoque == 18


def test_pedido_pago_nao_aceita_novo_pagamento(client):
    pedido = fazer_pedido(client)
    pagar_cartao(client, pedido, CARTAO_OK)
    resposta = client.get(f"/pedidos/{pedido.id}/pagamento")
    assert resposta.status_code == 302 and resposta.headers["Location"].endswith(f"/pedidos/{pedido.id}")


def test_cliente_nao_paga_pedido_de_outro(client):
    pedido = fazer_pedido(client)
    client.post("/sair")
    client.post("/criar-conta", data={"nome": "Outra Pessoa", "email": "outra@example.com",
                                      "telefone": "11911112222", "senha": "Teste2026"})
    assert client.get(f"/pedidos/{pedido.id}/pagamento").status_code == 404
    assert client.post(f"/pedidos/{pedido.id}/pagamento/cartao", data=CARTAO_OK).status_code == 404


def test_rnf07_dois_pagamentos_simultaneos_nao_deixam_estoque_negativo(app):
    """Dois clientes pagam ao mesmo tempo a última unidade: só um é aprovado."""
    cliente = Usuario(nome="Cliente", email="c@example.com", telefone="11999999999", senha_hash="x")
    db.session.get(Cupcake, LIMAO).estoque = 1
    pix_ids = []
    for _ in range(2):
        pedido = Pedido(cliente=cliente, subtotal=Decimal("10.90"), frete=Decimal("8"), total=Decimal("18.90"),
                        prazo_minutos=90, entrega_cep="01310100", entrega_logradouro="Av. Paulista",
                        entrega_numero="1000", entrega_bairro="Bela Vista", entrega_cidade="São Paulo", entrega_uf="SP")
        pedido.itens.append(ItemPedido(cupcake_id=LIMAO, quantidade=1, preco_unitario=Decimal("10.90")))
        pedido.registrar(StatusPedido.AGUARDANDO_PAGAMENTO)
        db.session.add(pedido)
        db.session.flush()
        pix = ServicoPagamento(GatewaySimulado()).gerar_pix(pedido)
        pix_ids.append(pix.id)
    db.session.commit()

    barreira, resultados = threading.Barrier(2), []

    def pagar(pagamento_id):
        with app.app_context():
            pagamento = db.session.get(Pagamento, pagamento_id)
            barreira.wait()
            try:
                ServicoPagamento(GatewaySimulado()).confirmar_pix(pagamento)
                resultados.append("aprovado")
            except RegraDeNegocio:
                resultados.append("recusado")
            finally:
                db.session.remove()

    threads = [threading.Thread(target=pagar, args=(i,)) for i in pix_ids]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    db.session.expire_all()
    assert sorted(resultados) == ["aprovado", "recusado"]
    assert db.session.get(Cupcake, LIMAO).estoque == 0
