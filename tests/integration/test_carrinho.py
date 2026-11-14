"""Testes de integração do carrinho (US04, US05, US06) e da estimativa de frete (CA11.3)."""
from app.extensions import db
from app.models import Cupcake
from tests.conftest import html

RED_VELVET, LIMAO, PISTACHE = 1, 3, 4
GANACHE, CREAM_CHEESE, CHANTILLY = 2, 5, 6


def adicionar(client, cupcake_id, quantidade=1, **extra):
    return client.post("/carrinho/itens", data={"cupcake_id": cupcake_id, "quantidade": quantidade, **extra},
                       follow_redirects=True)


def itens_da_sessao(client):
    with client.session_transaction() as sessao:
        return sessao.get("carrinho", [])


def test_ca04_1_adicionar_mostra_confirmacao(client):
    resposta = adicionar(client, LIMAO, 2)
    assert "Adicionado ao carrinho." in html(resposta)
    assert itens_da_sessao(client)[0]["quantidade"] == 2


def test_ca04_2_icone_do_carrinho_mostra_total_de_itens(client):
    adicionar(client, LIMAO, 2)
    adicionar(client, RED_VELVET, 1, recheio_id=GANACHE, cobertura_id=CREAM_CHEESE)
    assert '<span class="badge">3</span>' in html(client.get("/"))


def test_ca04_3_mesmo_cupcake_e_mesma_personalizacao_soma_na_mesma_linha(client):
    adicionar(client, LIMAO, 2)
    adicionar(client, LIMAO, 3)
    itens = itens_da_sessao(client)
    assert len(itens) == 1 and itens[0]["quantidade"] == 5


def test_ca04_4_quantidade_fora_de_1_a_20_e_recusada(client):
    assert "A quantidade deve ser de 1 a 20." in html(adicionar(client, LIMAO, 21))
    assert "A quantidade deve ser de 1 a 20." in html(adicionar(client, LIMAO, 0))
    assert itens_da_sessao(client) == []


def test_ca04_4_quantidade_acima_do_estoque_e_recusada(client):
    db.session.get(Cupcake, LIMAO).estoque = 4
    db.session.commit()
    assert "Só temos 4 unidades disponíveis." in html(adicionar(client, LIMAO, 5))


def test_ca04_4_soma_de_linhas_nao_passa_do_estoque(client):
    db.session.get(Cupcake, RED_VELVET).estoque = 3
    db.session.commit()
    adicionar(client, RED_VELVET, 2, recheio_id=GANACHE, cobertura_id=CREAM_CHEESE)
    resposta = adicionar(client, RED_VELVET, 2, recheio_id=GANACHE, cobertura_id=CHANTILLY)
    assert "Só temos 3 unidades disponíveis." in html(resposta)


def test_rn02_cupcake_esgotado_nao_entra_no_carrinho(client):
    assert "Este cupcake está esgotado no momento." in html(adicionar(client, PISTACHE, 1))


def test_ca05_2_personalizacao_soma_acrescimo_no_preco(client):
    adicionar(client, RED_VELVET, 2, recheio_id=GANACHE, cobertura_id=CREAM_CHEESE, mensagem="Feliz aniversário, Ana!")
    texto = html(client.get("/carrinho"))
    assert "R$ 14,40 cada" in texto and "R$ 28,80" in texto
    assert "Ganache · Cream cheese" in texto and "Feliz aniversário, Ana!" in texto


def test_ca05_3_mensagem_acima_de_60_caracteres_e_recusada(client):
    resposta = adicionar(client, RED_VELVET, 1, recheio_id=GANACHE, cobertura_id=CREAM_CHEESE, mensagem="x" * 61)
    assert "A mensagem pode ter até 60 caracteres." in html(resposta)


def test_rn04_cobertura_enviada_como_recheio_e_recusada(client):
    resposta = adicionar(client, RED_VELVET, 1, recheio_id=CREAM_CHEESE, cobertura_id=CREAM_CHEESE)
    assert "Escolha um recheio da lista." in html(resposta)


def test_ca05_4_cupcake_nao_personalizavel_ignora_personalizacao(client):
    adicionar(client, LIMAO, 1, recheio_id=GANACHE, mensagem="Oi")
    item = itens_da_sessao(client)[0]
    assert item["recheio_id"] is None and item["mensagem"] == ""


def test_ca05_5_personalizacoes_diferentes_ficam_em_linhas_separadas(client):
    adicionar(client, RED_VELVET, 1, recheio_id=GANACHE, cobertura_id=CREAM_CHEESE)
    adicionar(client, RED_VELVET, 1, recheio_id=GANACHE, cobertura_id=CHANTILLY)
    assert len(itens_da_sessao(client)) == 2


def test_ca06_1_carrinho_mostra_linhas_e_subtotal(client):
    adicionar(client, RED_VELVET, 2, recheio_id=GANACHE, cobertura_id=CREAM_CHEESE)
    adicionar(client, LIMAO, 3)
    texto = html(client.get("/carrinho"))
    assert "Subtotal (5 itens)" in texto and "R$ 61,50" in texto


def test_ca06_2_alterar_quantidade_recalcula(client):
    adicionar(client, LIMAO, 1)
    chave = itens_da_sessao(client)[0]["chave"]
    client.post(f"/carrinho/itens/{chave}/quantidade", data={"quantidade": 1, "acao": "mais"})
    client.post(f"/carrinho/itens/{chave}/quantidade", data={"quantidade": 2, "acao": "mais"})
    assert itens_da_sessao(client)[0]["quantidade"] == 3
    assert "R$ 32,70" in html(client.get("/carrinho"))


def test_ca06_3_remover_e_desfazer(client):
    adicionar(client, LIMAO, 2)
    chave = itens_da_sessao(client)[0]["chave"]
    resposta = client.post(f"/carrinho/itens/{chave}/remover", follow_redirects=True)
    assert "Item removido do carrinho." in html(resposta) and "DESFAZER" in html(resposta)
    assert itens_da_sessao(client) == []
    client.post("/carrinho/desfazer")
    assert itens_da_sessao(client)[0]["quantidade"] == 2


def test_ca06_4_carrinho_vazio(client):
    texto = html(client.get("/carrinho"))
    assert "Seu carrinho está vazio" in texto and "Ver cupcakes" in texto


def test_ca11_3_estimativa_de_frete_por_cep_sem_login(client):
    adicionar(client, LIMAO, 1)
    texto = html(client.post("/carrinho/frete", data={"cep": "01310-100"}, follow_redirects=True))
    assert "Frete R$ 8,00 · entrega até 90 minutos" in texto


def test_ca11_3_cep_fora_da_area(client):
    adicionar(client, LIMAO, 1)
    texto = html(client.post("/carrinho/frete", data={"cep": "20040-020"}, follow_redirects=True))
    assert "Ainda não entregamos neste CEP." in texto


def test_cep_com_formato_invalido(client):
    adicionar(client, LIMAO, 1)
    texto = html(client.post("/carrinho/frete", data={"cep": "0131"}, follow_redirects=True))
    assert "Informe um CEP com 8 dígitos." in texto


def test_item_que_esgotou_depois_de_adicionado_bloqueia_finalizar(client):
    adicionar(client, LIMAO, 2)
    db.session.get(Cupcake, LIMAO).estoque = 0
    db.session.commit()
    texto = html(client.get("/carrinho"))
    assert "Este cupcake esgotou." in texto and "Ajuste os itens indisponíveis" in texto
