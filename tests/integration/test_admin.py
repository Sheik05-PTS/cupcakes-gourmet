"""Testes de integração do painel da loja (US15, US16, US17, RN19, RN20)."""
from decimal import Decimal

import pytest

from app.cli import criar_ou_atualizar_admin
from app.extensions import db
from app.models import Cupcake, StatusPedido
from tests.conftest import html
from tests.integration.ajuda import CARTAO_OK, LIMAO, PISTACHE, RED_VELVET, entrar, fazer_pedido, ultimo_pedido

ADMIN = ("loja.teste@example.com", "Cupcake2026")
FORM_VALIDO = {"nome": "Baunilha de Madagascar", "descricao": "Massa leve de baunilha.",
               "ingredientes": "Farinha, baunilha, ovos, leite, manteiga.", "preco": "11,90", "estoque": "15",
               "sabor_id": "3", "ocasioes": ["4"], "restricoes": [], "foto_url": "", "personalizavel": "1", "ativo": "1"}


@pytest.fixture
def admin(client):
    criar_ou_atualizar_admin(*ADMIN, "Juliana Lima", "11999990000")
    return client


def pedido_pago(client):
    """Cliente faz e paga um pedido; depois entra a conta da loja."""
    pedido = fazer_pedido(client)
    client.post(f"/pedidos/{pedido.id}/pagamento/cartao", data=CARTAO_OK)
    client.post("/sair")
    criar_ou_atualizar_admin(*ADMIN, "Juliana Lima", "11999990000")
    entrar(client, *ADMIN)
    return ultimo_pedido()


# RN20 / CA17.5 -------------------------------------------------------------
def test_ca17_5_cliente_comum_recebe_acesso_negado(client):
    fazer_pedido(client)
    for url in ("/admin/pedidos", "/admin/cupcakes", "/admin/cupcakes/novo"):
        resposta = client.get(url)
        assert resposta.status_code == 403 and "Acesso negado" in html(resposta)
    assert client.post("/admin/cupcakes/1/ativo").status_code == 403


def test_visitante_e_levado_para_entrar(client):
    resposta = client.get("/admin/pedidos")
    assert resposta.status_code == 302 and "/entrar" in resposta.headers["Location"]


def test_login_da_loja_abre_o_painel(admin):
    resposta = admin.post("/entrar", data={"email": ADMIN[0], "senha": ADMIN[1]})
    assert resposta.headers["Location"] == "/admin"


# US17 — pedidos -----------------------------------------------------------
def test_ca17_1_lista_de_pedidos_com_filtro_por_status(client):
    pedido = pedido_pago(client)
    texto = html(client.get("/admin/pedidos"))
    assert pedido.numero in texto and "Ana Paula Souza" in texto and "R$ 69,50" in texto
    assert "Pago (1)" in texto
    assert pedido.numero not in html(client.get("/admin/pedidos?status=ENTREGUE"))


def test_ca17_6_pedido_pago_aparece_como_novo_ate_ser_aberto(client):
    pedido = pedido_pago(client)
    assert client.get("/admin/pedidos/novos").get_json() == {"novos": 1, "ultimo_id": pedido.id}
    assert '<span class="pill novo">Novo</span>' in html(client.get("/admin/pedidos"))
    client.get(f"/admin/pedidos/{pedido.id}")
    assert client.get("/admin/pedidos/novos").get_json()["novos"] == 0
    assert '<span class="pill novo">Novo</span>' not in html(client.get("/admin/pedidos"))


def test_ca17_2_detalhe_mostra_personalizacao_endereco_pagamento_e_historico(client):
    pedido = pedido_pago(client)
    texto = html(client.get(f"/admin/pedidos/{pedido.id}"))
    assert "Recheio Ganache · Cobertura Cream cheese" in texto and "Feliz aniversário, Ana!" in texto
    assert "Av. Paulista, 1000" in texto and "Cartão Visa final 1111 · aprovado" in texto
    assert "Aguardando pagamento · cliente" in texto and "Pago · sistema" in texto


def test_ca17_3_avancar_status_registra_responsavel(client):
    pedido = pedido_pago(client)
    texto = html(client.post(f"/admin/pedidos/{pedido.id}/avancar", follow_redirects=True))
    assert f"Pedido {pedido.numero} agora está “Em preparo”." in texto
    pedido = ultimo_pedido()
    assert pedido.status == StatusPedido.EM_PREPARO
    assert pedido.historico[-1].responsavel.nome == "Juliana Lima"
    assert "Em preparo · Juliana (loja)" in texto


def test_ca12_2_cliente_ve_o_novo_status(client):
    pedido = pedido_pago(client)
    client.post(f"/admin/pedidos/{pedido.id}/avancar")
    client.post(f"/admin/pedidos/{pedido.id}/avancar")
    assert ultimo_pedido().status == StatusPedido.SAIU_PARA_ENTREGA


def test_uc16_fe1_pedido_entregue_nao_tem_botao_de_avancar(client):
    pedido = pedido_pago(client)
    for _ in range(3):
        client.post(f"/admin/pedidos/{pedido.id}/avancar")
    texto = html(client.get(f"/admin/pedidos/{pedido.id}"))
    assert ultimo_pedido().status == StatusPedido.ENTREGUE
    assert "Avançar para" not in texto and "Cancelar pedido" not in texto


def test_uc16_fe2_pedido_aguardando_pagamento_nao_avanca(client):
    fazer_pedido(client)
    client.post("/sair")
    criar_ou_atualizar_admin(*ADMIN, "Juliana Lima", "11999990000")
    entrar(client, *ADMIN)
    pedido = ultimo_pedido()
    texto = html(client.post(f"/admin/pedidos/{pedido.id}/avancar", follow_redirects=True))
    assert "Este pedido ainda está aguardando pagamento do cliente." in texto
    assert ultimo_pedido().status == StatusPedido.AGUARDANDO_PAGAMENTO


def test_ca17_4_cancelar_pedido_pago_devolve_estoque(client):
    pedido = pedido_pago(client)
    estoque_antes = db.session.get(Cupcake, LIMAO).estoque
    texto = html(client.post(f"/admin/pedidos/{pedido.id}/cancelar", follow_redirects=True))
    assert f"Pedido {pedido.numero} cancelado. O estoque foi devolvido." in texto
    db.session.expire_all()
    assert ultimo_pedido().status == StatusPedido.CANCELADO
    assert db.session.get(Cupcake, LIMAO).estoque == estoque_antes + 3


def test_rn16_nao_cancela_depois_de_sair_para_entrega(client):
    pedido = pedido_pago(client)
    client.post(f"/admin/pedidos/{pedido.id}/avancar")
    client.post(f"/admin/pedidos/{pedido.id}/avancar")
    texto = html(client.post(f"/admin/pedidos/{pedido.id}/cancelar", follow_redirects=True))
    assert "Este pedido não pode mais ser cancelado." in texto
    assert ultimo_pedido().status == StatusPedido.SAIU_PARA_ENTREGA


def test_cliente_nao_paga_pedido_cancelado_pela_loja(client):
    fazer_pedido(client)
    pedido = ultimo_pedido()
    pedido.cancelar(None)
    db.session.commit()
    texto = html(client.post(f"/pedidos/{pedido.id}/pagamento/cartao", data=CARTAO_OK, follow_redirects=True))
    assert "Este pedido já foi pago ou cancelado." in texto


# US15 / US16 — cupcakes ----------------------------------------------------
def test_ca16_3_lista_destaca_esgotados_e_inativos(admin):
    entrar(admin, *ADMIN)
    texto = html(admin.get("/admin/cupcakes"))
    assert "8 cupcakes · 1 esgotado · 1 inativo" in texto
    trecho = texto[texto.index(">Pistache<"):texto.index(">Pistache<") + 600]
    assert "Esgotado" in trecho


def test_ca15_1_cadastrar_cupcake_aparece_na_vitrine(admin):
    entrar(admin, *ADMIN)
    texto = html(admin.post("/admin/cupcakes/novo", data=FORM_VALIDO, follow_redirects=True))
    assert "Cupcake salvo." in texto
    novo = db.session.scalar(db.select(Cupcake).where(Cupcake.nome == "Baunilha de Madagascar"))
    assert novo.preco == Decimal("11.90") and novo.estoque == 15 and novo.personalizavel
    assert [o.nome for o in novo.ocasioes] == ["Dia a dia"]
    assert "Baunilha de Madagascar" in html(admin.get("/"))


def test_ca15_2_dados_invalidos_mostram_mensagem_por_campo(admin):
    entrar(admin, *ADMIN)
    dados = {**FORM_VALIDO, "nome": "", "preco": "0,00", "estoque": "-1", "sabor_id": ""}
    texto = html(admin.post("/admin/cupcakes/novo", data=dados))
    for mensagem in ("Obrigatório.", "Deve ser maior que zero.", "Informe um número inteiro maior ou igual a zero.",
                     "Escolha o sabor."):
        assert mensagem in texto
    assert db.session.scalar(db.select(db.func.count()).select_from(Cupcake)) == 8


def test_nome_repetido_e_recusado(admin):
    entrar(admin, *ADMIN)
    texto = html(admin.post("/admin/cupcakes/novo", data={**FORM_VALIDO, "nome": "red velvet"}))
    assert "Já existe um cupcake com este nome." in texto


def test_ca15_3_editar_preco_nao_altera_pedidos_antigos(client):
    pedido = pedido_pago(client)
    cupcake = db.session.get(Cupcake, LIMAO)
    dados = {**FORM_VALIDO, "nome": cupcake.nome, "preco": "12,50", "sabor_id": str(cupcake.sabor_id)}
    client.post(f"/admin/cupcakes/{LIMAO}/editar", data=dados)
    db.session.expire_all()
    assert db.session.get(Cupcake, LIMAO).preco == Decimal("12.50")
    item = next(i for i in ultimo_pedido().itens if i.cupcake_id == LIMAO)
    assert item.preco_unitario == Decimal("10.90") and pedido.id == ultimo_pedido().id


def test_ca15_4_cupcake_vendido_nao_pode_ser_excluido(client):
    pedido_pago(client)
    texto = html(client.post(f"/admin/cupcakes/{RED_VELVET}/excluir", follow_redirects=True))
    assert "Este cupcake já foi vendido. Você pode inativá-lo." in texto
    assert db.session.get(Cupcake, RED_VELVET) is not None


def test_cupcake_nunca_vendido_pode_ser_excluido(admin):
    entrar(admin, *ADMIN)
    texto = html(admin.post(f"/admin/cupcakes/{PISTACHE}/excluir", follow_redirects=True))
    assert "Pistache foi excluído." in texto
    assert db.session.get(Cupcake, PISTACHE) is None


def test_ca16_1_alterar_estoque_reflete_na_vitrine(admin):
    entrar(admin, *ADMIN)
    cupcake = db.session.get(Cupcake, PISTACHE)
    dados = {**FORM_VALIDO, "nome": "Pistache", "preco": "14,90", "estoque": "12", "sabor_id": str(cupcake.sabor_id)}
    admin.post(f"/admin/cupcakes/{PISTACHE}/editar", data=dados)
    assert "Adicionar 1 Pistache" in html(admin.get("/")) or "Escolher e adicionar Pistache" in html(admin.get("/"))


def test_ca16_2_inativar_e_reativar(admin):
    entrar(admin, *ADMIN)
    texto = html(admin.post(f"/admin/cupcakes/{LIMAO}/ativo", follow_redirects=True))
    assert "Limão Siciliano saiu da vitrine." in texto
    assert ">Limão Siciliano</a>" not in html(admin.get("/"))
    admin.post(f"/admin/cupcakes/{LIMAO}/ativo")
    assert ">Limão Siciliano</a>" in html(admin.get("/"))
