"""Testes unitários de formatação, configuração, CEP e senha."""
from decimal import Decimal

import pytest

from app.config import normalizar_url_banco
from app.formatacao import cep, moeda, numero_pedido
from app.models import RegraDeNegocio, normalizar_cep, validar_senha


@pytest.mark.parametrize("valor, esperado", [
    (Decimal("12.9"), "R$ 12,90"), (Decimal("1234.5"), "R$ 1.234,50"), (Decimal("0"), "R$ 0,00"), (None, ""),
])
def test_moeda_no_padrao_brasileiro(valor, esperado):
    assert moeda(valor) == esperado


def test_numero_do_pedido_com_seis_digitos():
    assert numero_pedido(128) == "#000128"


def test_cep_formatado():
    assert cep("01310100") == "01310-100"


@pytest.mark.parametrize("url, esperado", [
    ("postgres://u:s@h/db", "postgresql+psycopg://u:s@h/db"),
    ("postgresql://u:s@h/db", "postgresql+psycopg://u:s@h/db"),
    ("postgresql+psycopg://u:s@h/db", "postgresql+psycopg://u:s@h/db"),
])
def test_url_do_banco_usa_driver_psycopg(url, esperado):
    assert normalizar_url_banco(url) == esperado


# RN18 ------------------------------------------------------------------
@pytest.mark.parametrize("entrada", ["01310-100", "01310100", " 01310.100 "])
def test_rn18_cep_valido_fica_so_com_digitos(entrada):
    assert normalizar_cep(entrada) == "01310100"


@pytest.mark.parametrize("entrada", ["0131010", "013101000", "", None, "abcde-fgh"])
def test_rn18_cep_invalido_e_recusado(entrada):
    with pytest.raises(RegraDeNegocio) as erro:
        normalizar_cep(entrada)
    assert erro.value.mensagem == "Informe um CEP com 8 dígitos."


# RN17 ------------------------------------------------------------------
@pytest.mark.parametrize("senha", ["Cupcake2026", "abc12345"])
def test_rn17_senha_forte_aceita(senha):
    validar_senha(senha)


@pytest.mark.parametrize("senha", ["curta1", "somenteletras", "12345678", "", None])
def test_rn17_senha_fraca_recusada(senha):
    with pytest.raises(RegraDeNegocio) as erro:
        validar_senha(senha)
    assert erro.value.campo == "senha"
