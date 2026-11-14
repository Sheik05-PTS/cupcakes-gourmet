"""Testes de integração da vitrine (US01, US02, US03) com o banco real."""
from app.extensions import db
from app.models import Cupcake
from tests.conftest import html


def nomes_na_vitrine(resposta):
    texto = html(resposta)
    return [c.nome for c in db.session.scalars(db.select(Cupcake)).all() if f">{c.nome}</a>" in texto]


def test_ca01_1_vitrine_lista_cupcakes_ativos_com_nome_e_preco(client):
    resposta = client.get("/")
    assert resposta.status_code == 200
    texto = html(resposta)
    assert "Red Velvet" in texto and "R$ 12,90" in texto
    assert "/static/img/cupcakes/red-velvet.svg" in texto


def test_ca01_2_cupcake_esgotado_aparece_sem_botao_de_adicionar(client):
    texto = html(client.get("/"))
    trecho = texto[texto.index("Pistache") - 900: texto.index("Pistache") + 600]
    assert "ESGOTADO" in trecho
    assert "Adicionar 1 Pistache" not in texto


def test_ca01_3_cupcake_inativo_nao_aparece(client):
    assert "Abóbora com Especiarias" not in html(client.get("/"))


def test_ca01_4_vitrine_vazia_mostra_mensagem(client):
    db.session.execute(db.update(Cupcake).values(ativo=False))
    db.session.commit()
    assert "Nenhum cupcake disponível no momento." in html(client.get("/"))


def test_ca02_1_filtro_por_sabor(client):
    with client:
        resposta = client.get("/?sabor=2")  # Frutas
        assert sorted(nomes_na_vitrine(resposta)) == ["Limão Siciliano", "Morango com Chantilly"]


def test_ca02_2_filtro_por_faixa_de_preco(client):
    with client:
        nomes = nomes_na_vitrine(client.get("/?preco_min=12&preco_max=13"))
        assert sorted(nomes) == ["Doce de Leite com Flor de Sal", "Red Velvet"]


def test_ca02_3_filtro_por_ocasiao(client):
    with client:
        nomes = nomes_na_vitrine(client.get("/?ocasiao=2"))  # Casamento
        assert sorted(nomes) == ["Morango com Chantilly", "Pistache", "Red Velvet"]


def test_ca02_4_filtro_por_restricao_alimentar(client):
    with client:
        assert nomes_na_vitrine(client.get("/?restricao=3")) == ["Cacau 70% Vegano"]  # Vegano


def test_ca02_5_filtros_combinados_valem_ao_mesmo_tempo(client):
    with client:
        assert nomes_na_vitrine(client.get("/?restricao=2&preco_max=15")) == ["Cacau 70% Vegano"]


def test_ca02_6_filtros_sem_resultado_mostram_mensagem_e_limpar(client):
    texto = html(client.get("/?restricao=3&ocasiao=2"))
    assert "Nenhum cupcake encontrado com esses filtros" in texto
    assert "Limpar filtros" in texto


def test_ca02_7_preco_minimo_maior_que_maximo(client):
    texto = html(client.get("/?preco_min=20&preco_max=10"))
    assert "O preço mínimo não pode ser maior que o máximo." in texto


def test_busca_por_nome(client):
    with client:
        assert nomes_na_vitrine(client.get("/?busca=lim")) == ["Limão Siciliano"]


def test_ca03_1_detalhe_mostra_ingredientes_restricoes_e_preco(client):
    texto = html(client.get("/cupcakes/7"))
    assert "Cacau 70% Vegano" in texto and "R$ 13,90" in texto
    assert "Farinha de arroz" in texto and "Vegano" in texto


def test_ca03_2_cupcake_inativo_ou_inexistente_da_pagina_nao_encontrado(client):
    for url in ("/cupcakes/8", "/cupcakes/999"):
        resposta = client.get(url)
        assert resposta.status_code == 404
        assert "Cupcake não encontrado" in html(resposta)


def test_ca05_1_personalizavel_mostra_recheio_cobertura_e_mensagem(client):
    texto = html(client.get("/cupcakes/1"))
    assert 'name="recheio_id"' in texto and 'name="cobertura_id"' in texto
    assert 'maxlength="60"' in texto and "Ganache (+ R$ 1,50)" in texto


def test_ca05_4_nao_personalizavel_nao_mostra_opcoes(client):
    texto = html(client.get("/cupcakes/3"))
    assert 'name="recheio_id"' not in texto


def test_rnf06_pagina_inexistente_tem_mensagem_amigavel(client):
    resposta = client.get("/nao-existe")
    assert resposta.status_code == 404
    assert "Página não encontrada" in html(resposta)
