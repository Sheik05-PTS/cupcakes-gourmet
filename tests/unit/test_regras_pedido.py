"""Testes unitários: cartão, gateway simulado, cupom e transições de status do pedido (sem banco)."""
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

import pytest

from app.models import (Cupcake, Cupom, DadosCartao, ErrosDeValidacao, GatewaySimulado, ItemPedido, Pedido,
                        RegraDeNegocio, StatusPedido, TipoCupom)
from app.models.pedido import Pagamento

HOJE = date(2026, 11, 14)


def cartao(numero="4111 1111 1111 1111", nome="ANA P SOUZA", validade="12/28", cvv="123"):
    return DadosCartao(numero, nome, validade, cvv)


# RN11 / CA08.4 / CA08.6 — dados do cartão -------------------------------
@pytest.mark.parametrize("numero", ["4111 1111 1111 1111", "5555555555554444", "4000 0000 0000 0002"])
def test_ca08_numero_valido_pelo_algoritmo_de_luhn(numero):
    assert cartao(numero).numero_valido()


@pytest.mark.parametrize("numero", ["4111 1111 1111 1112", "1234", "", "abcd efgh ijkl mnop"])
def test_ca08_6_numero_invalido(numero):
    assert not cartao(numero).numero_valido()


def test_ca08_6_cartao_vencido_e_campos_invalidos_geram_mensagem_por_campo():
    with pytest.raises(ErrosDeValidacao) as erro:
        cartao(numero="4111 1111 1111 1112", nome="", validade="03/24", cvv="12").validar(HOJE)
    assert erro.value.erros == {"numero": "Número de cartão inválido.", "nome": "Informe o nome impresso no cartão.",
                                "validade": "Cartão vencido.", "cvv": "O CVV tem 3 ou 4 dígitos."}


def test_validade_no_mes_atual_ainda_vale():
    assert cartao(validade="11/26").validade_futura(HOJE)
    assert cartao(validade="11/2026").validade_futura(HOJE)
    assert not cartao(validade="10/26").validade_futura(HOJE)


@pytest.mark.parametrize("numero, bandeira", [("4111111111111111", "Visa"), ("5555555555554444", "Mastercard"),
                                              ("378282246310005", "Amex"), ("6362970000457013", "Elo")])
def test_bandeira_do_cartao(numero, bandeira):
    assert cartao(numero).bandeira() == bandeira


def test_rn12_so_os_quatro_ultimos_digitos_sao_usados():
    assert cartao("4111 1111 1111 1111").final() == "1111"


# RN11 — gateway simulado --------------------------------------------------
def test_rn11_cartao_terminado_em_0002_e_recusado_e_os_demais_aprovados():
    gateway = GatewaySimulado()
    assert not gateway.cobrar_cartao(cartao("4000 0000 0000 0002"), Decimal("10")).aprovado
    assert gateway.cobrar_cartao(cartao("4111 1111 1111 1111"), Decimal("10")).aprovado


def test_rn11_pix_vale_15_minutos():
    resultado = GatewaySimulado(15).gerar_pix(Decimal("63.35"), "000128")
    restante = resultado.expira_em - datetime.now(timezone.utc)
    assert timedelta(minutes=14, seconds=55) < restante <= timedelta(minutes=15)
    assert "63.35" in resultado.codigo and "demo" in resultado.codigo


def test_pix_expirado_depois_do_prazo():
    pagamento = Pagamento(pix_expira_em=datetime(2026, 11, 14, 15, 0, tzinfo=timezone.utc))
    assert not pagamento.pix_expirado(datetime(2026, 11, 14, 14, 59, tzinfo=timezone.utc))
    assert pagamento.pix_expirado(datetime(2026, 11, 14, 15, 1, tzinfo=timezone.utc))


# RN07 — cupom -------------------------------------------------------------
def cupom(**campos):
    padrao = dict(codigo="DOCE10", tipo=TipoCupom.PERCENTUAL, valor=Decimal("10"), valor_minimo=Decimal("30"),
                  valido_de=date(2026, 1, 1), valido_ate=date(2026, 12, 31), ativo=True)
    padrao.update(campos)
    return Cupom(**padrao)


def test_ca07_1_desconto_percentual_arredondado_em_centavos():
    assert cupom().calcular_desconto(Decimal("61.50")) == Decimal("6.15")
    assert cupom().calcular_desconto(Decimal("75.40")) == Decimal("7.54")


def test_ca07_5_desconto_fixo_limitado_ao_subtotal():
    assert cupom(tipo=TipoCupom.VALOR_FIXO, valor=Decimal("50")).calcular_desconto(Decimal("40")) == Decimal("40")


@pytest.mark.parametrize("campos", [{"ativo": False}, {"valido_ate": date(2026, 11, 13)}, {"valido_de": date(2026, 11, 15)}])
def test_ca07_2_cupom_inativo_ou_fora_da_validade(campos):
    with pytest.raises(RegraDeNegocio) as erro:
        cupom(**campos).validar(Decimal("100"), HOJE)
    assert erro.value.mensagem == "Cupom inválido ou expirado."


def test_ca07_3_subtotal_abaixo_do_minimo():
    with pytest.raises(RegraDeNegocio) as erro:
        cupom().validar(Decimal("29.99"), HOJE)
    assert erro.value.mensagem == "Este cupom vale para pedidos a partir de R$ 30,00."


def test_descricao_do_cupom():
    assert cupom().descricao() == "10% de desconto nos produtos"
    assert cupom(tipo=TipoCupom.VALOR_FIXO, valor=Decimal("5")).descricao() == "R$ 5,00 de desconto nos produtos"


# RN15 / RN16 — status do pedido -------------------------------------------
def pedido(status):
    p = Pedido(status=status)
    p.itens.append(ItemPedido(cupcake=Cupcake(nome="Limão", estoque=10), quantidade=3, preco_unitario=Decimal("10.90")))
    return p


def test_rn15_etapas_avancam_em_ordem():
    p = pedido(StatusPedido.PAGO)
    for esperado in (StatusPedido.EM_PREPARO, StatusPedido.SAIU_PARA_ENTREGA, StatusPedido.ENTREGUE):
        p.avancar_status(None)
        assert p.status == esperado
    assert not p.pode_avancar()
    with pytest.raises(RegraDeNegocio):
        p.avancar_status(None)


def test_rn15_pedido_aguardando_pagamento_nao_avanca():
    with pytest.raises(RegraDeNegocio) as erro:
        pedido(StatusPedido.AGUARDANDO_PAGAMENTO).avancar_status(None)
    assert erro.value.mensagem == "Este pedido ainda está aguardando pagamento do cliente."


def test_rn16_cancelar_pedido_pago_devolve_estoque():
    p = pedido(StatusPedido.EM_PREPARO)
    assert p.cancelar(None) is True
    assert p.status == StatusPedido.CANCELADO and p.itens[0].cupcake.estoque == 13


def test_rn16_cancelar_pedido_nao_pago_nao_mexe_no_estoque():
    p = pedido(StatusPedido.AGUARDANDO_PAGAMENTO)
    assert p.cancelar(None) is False and p.itens[0].cupcake.estoque == 10


@pytest.mark.parametrize("status", [StatusPedido.SAIU_PARA_ENTREGA, StatusPedido.ENTREGUE, StatusPedido.CANCELADO])
def test_rn16_nao_cancela_depois_de_sair_para_entrega(status):
    assert not pedido(status).pode_cancelar()


def test_rn09_total_e_subtotal_menos_desconto_mais_frete_no_item():
    item = ItemPedido(quantidade=2, preco_unitario=Decimal("14.40"))
    assert item.subtotal == Decimal("28.80")
