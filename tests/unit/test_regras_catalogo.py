"""Testes unitários das regras do catálogo e do carrinho (sem banco de dados)."""
from decimal import Decimal

import pytest
from werkzeug.datastructures import MultiDict

from app.models import Cupcake, EstoqueInsuficiente, FiltrosVitrine, LinhaCarrinho, OpcaoPersonalizacao, RegraDeNegocio
from app.models import Carrinho, TipoOpcao, validar_quantidade


def cupcake(**campos):
    padrao = dict(id=1, nome="Red Velvet", preco=Decimal("12.90"), estoque=10, ativo=True, personalizavel=True)
    padrao.update(campos)
    return Cupcake(**padrao)


# RN02 ------------------------------------------------------------------
def test_rn02_cupcake_ativo_com_estoque_esta_disponivel():
    assert cupcake().disponivel()


def test_rn02_cupcake_sem_estoque_nao_esta_disponivel():
    assert not cupcake(estoque=0).disponivel()


def test_rn02_cupcake_inativo_nao_esta_disponivel():
    assert not cupcake(ativo=False).disponivel()


# RN13 ------------------------------------------------------------------
def test_rn13_baixar_estoque_reduz_a_quantidade():
    c = cupcake(estoque=5)
    c.baixar_estoque(3)
    assert c.estoque == 2


def test_rn13_baixar_mais_que_o_estoque_e_recusado():
    c = cupcake(estoque=2)
    with pytest.raises(EstoqueInsuficiente) as erro:
        c.baixar_estoque(3)
    assert "ficou indisponível" in erro.value.mensagem
    assert c.estoque == 2


def test_rn16_devolver_estoque_soma_a_quantidade():
    c = cupcake(estoque=2)
    c.devolver_estoque(3)
    assert c.estoque == 5


# RN03 ------------------------------------------------------------------
@pytest.mark.parametrize("valor", [1, "7", 20])
def test_rn03_quantidade_valida(valor):
    assert validar_quantidade(valor, 20) == int(valor)


@pytest.mark.parametrize("valor", [0, -1, 21, "abc", None])
def test_rn03_quantidade_fora_do_limite_e_recusada(valor):
    with pytest.raises(RegraDeNegocio) as erro:
        validar_quantidade(valor, 20)
    assert erro.value.mensagem == "A quantidade deve ser de 1 a 20."


# US02 — filtros ----------------------------------------------------------
def test_ca02_filtros_lidos_da_url():
    f = FiltrosVitrine.de_parametros(MultiDict({"sabor": "2", "ocasiao": "3", "restricao": "1",
                                                "preco_min": "5", "preco_max": "15,50"}))
    assert (f.sabor_id, f.ocasiao_id, f.restricao_id) == (2, 3, 1)
    assert f.preco_min == Decimal("5") and f.preco_max == Decimal("15.50")
    assert f.ativos() and not f.erros


def test_ca02_preco_com_ponto_decimal_do_campo_numerico():
    f = FiltrosVitrine.de_parametros(MultiDict({"preco_max": "15.00"}))
    assert f.preco_max == Decimal("15.00")


def test_ca02_7_preco_minimo_maior_que_maximo_gera_mensagem_e_ignora_faixa():
    f = FiltrosVitrine.de_parametros(MultiDict({"preco_min": "20", "preco_max": "10"}))
    assert f.erros == ["O preço mínimo não pode ser maior que o máximo."]
    assert f.preco_min is None and f.preco_max is None


def test_ca02_valores_invalidos_sao_ignorados():
    f = FiltrosVitrine.de_parametros(MultiDict({"sabor": "x", "preco_min": "abc", "preco_max": "-3"}))
    assert not f.ativos()


# RN04 / RN05 — linha do carrinho -------------------------------------------
def test_rn04_preco_unitario_soma_acrescimos_da_personalizacao():
    recheio = OpcaoPersonalizacao(id=2, tipo=TipoOpcao.RECHEIO, nome="Ganache", acrescimo=Decimal("1.50"), ativo=True)
    cobertura = OpcaoPersonalizacao(id=5, tipo=TipoOpcao.COBERTURA, nome="Cream cheese", acrescimo=Decimal("0"), ativo=True)
    linha = LinhaCarrinho("k", cupcake(), 2, recheio, cobertura, "Feliz aniversário, Ana!")
    assert linha.preco_unitario == Decimal("14.40")
    assert linha.subtotal == Decimal("28.80")
    assert linha.personalizacao == "Ganache · Cream cheese · “Feliz aniversário, Ana!”"


def test_rn05_mesma_personalizacao_gera_a_mesma_chave_e_diferente_gera_outra():
    a = Carrinho.chave_de(1, 2, 5, "Parabéns")
    assert a == Carrinho.chave_de(1, 2, 5, "Parabéns")
    assert a != Carrinho.chave_de(1, 2, 5, "Felicidades")
    assert a != Carrinho.chave_de(1, 3, 5, "Parabéns")


def test_carrinho_conta_itens_e_detecta_vazio():
    carrinho = Carrinho([{"chave": "a", "cupcake_id": 1, "quantidade": 2},
                         {"chave": "b", "cupcake_id": 3, "quantidade": 3}])
    assert carrinho.total_itens() == 5 and not carrinho.vazio()
    assert Carrinho().vazio()
