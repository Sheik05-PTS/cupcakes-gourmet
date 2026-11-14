"""Testes de integração do acompanhamento de pedidos (US12, CA13.7)."""
from app.extensions import db
from app.models import StatusPedido
from tests.conftest import html
from tests.integration.ajuda import CARTAO_OK, fazer_pedido, ultimo_pedido


def test_ca13_7_meus_pedidos_do_mais_recente_para_o_mais_antigo(client):
    primeiro = fazer_pedido(client)
    client.post("/carrinho/itens", data={"cupcake_id": 3, "quantidade": 1})
    client.post("/checkout/confirmar", data={"endereco_id": 1})
    segundo = ultimo_pedido()
    texto = html(client.get("/pedidos"))
    assert texto.index(segundo.numero) < texto.index(primeiro.numero)
    assert "Aguardando pagamento" in texto


def test_ca12_1_linha_do_tempo_com_etapas_e_horarios(client):
    pedido = fazer_pedido(client)
    client.post(f"/pedidos/{pedido.id}/pagamento/cartao", data=CARTAO_OK)
    texto = html(client.get(f"/pedidos/{pedido.id}"))
    for etapa in ("Aguardando pagamento", "Pago", "Em preparo", "Saiu para entrega", "Entregue"):
        assert etapa in texto
    assert "etapa atual" in texto and "Esta tela se atualiza sozinha." in texto


def test_ca12_2_status_em_json_para_atualizacao_automatica(client):
    pedido = fazer_pedido(client)
    dados = client.get(f"/pedidos/{pedido.id}/status").get_json()
    assert dados["status"] == "AGUARDANDO_PAGAMENTO" and len(dados["etapas"]) == 5
    pedido = ultimo_pedido()
    pedido.registrar(StatusPedido.PAGO)
    db.session.commit()
    assert client.get(f"/pedidos/{pedido.id}/status").get_json()["texto"] == "Pago"


def test_ca12_3_pedido_cancelado_em_destaque(client):
    pedido = fazer_pedido(client)
    pedido = ultimo_pedido()
    pedido.cancelar(None)
    db.session.commit()
    texto = html(client.get(f"/pedidos/{pedido.id}"))
    assert "Pedido cancelado." in texto and "Esta tela se atualiza sozinha." not in texto


def test_ca12_4_pedido_de_outro_cliente_nao_aparece(client):
    pedido = fazer_pedido(client)
    client.post("/sair")
    client.post("/criar-conta", data={"nome": "Outra Pessoa", "email": "outra@example.com",
                                      "telefone": "11911112222", "senha": "Teste2026"})
    for url in (f"/pedidos/{pedido.id}", f"/pedidos/{pedido.id}/status"):
        resposta = client.get(url)
        assert resposta.status_code == 404
    assert "Pedido não encontrado" in html(client.get(f"/pedidos/{pedido.id}"))


def test_uc13_fa1_pedido_aguardando_oferece_pagar_agora(client):
    pedido = fazer_pedido(client)
    assert "Pagar agora" in html(client.get(f"/pedidos/{pedido.id}"))
