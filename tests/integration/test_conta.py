"""Testes de integração: criar conta, entrar, sair e endereços (US13, US10)."""
from app.extensions import db
from app.models import Usuario
from tests.conftest import html
from tests.integration.ajuda import LIMAO, adicionar, cadastrar_endereco, criar_conta, entrar


def test_ca13_1_criar_conta_entra_logado(client):
    texto = html(criar_conta(client))
    assert "Conta criada. Bem-vindo(a), Ana!" in texto
    with client.session_transaction() as sessao:
        assert sessao.get("usuario_id")
    usuario = Usuario.buscar_por_email("ana@example.com")
    assert usuario.telefone == "11987654321" and usuario.senha_hash != "Teste2026"


def test_ca13_2_email_ja_cadastrado(client):
    criar_conta(client)
    client.post("/sair")
    texto = html(criar_conta(client, email="ANA@example.com"))
    assert "Este e-mail já está cadastrado." in texto and "Entrar com este e-mail" in texto


def test_ca13_3_senha_fraca_mostra_a_regra(client):
    texto = html(criar_conta(client, senha="abc"))
    assert "Use no mínimo 8 caracteres, com letras e números." in texto
    assert 'value="Ana Paula Souza"' in texto  # FE3: não apaga o que foi digitado


def test_ca13_4_login_volta_para_a_pagina_de_origem(client):
    criar_conta(client)
    client.post("/sair")
    resposta = client.post("/entrar", data={"email": "ana@example.com", "senha": "Teste2026", "proximo": "/pedidos"})
    assert resposta.status_code == 302 and resposta.headers["Location"].endswith("/pedidos")


def test_ca13_5_credenciais_erradas_mensagem_generica(client):
    criar_conta(client)
    client.post("/sair")
    for email, senha in (("ana@example.com", "errada123"), ("ninguem@example.com", "Teste2026")):
        assert "E-mail ou senha inválidos." in html(entrar(client, email, senha))


def test_login_nao_redireciona_para_outro_site(client):
    criar_conta(client)
    client.post("/sair")
    resposta = client.post("/entrar", data={"email": "ana@example.com", "senha": "Teste2026",
                                            "proximo": "https://site-malicioso.com"})
    assert resposta.headers["Location"] == "/"


def test_ca13_6_sair_encerra_a_sessao(client):
    criar_conta(client)
    client.post("/sair")
    assert client.get("/conta").status_code == 302


def test_rn06_carrinho_continua_depois_do_login(client):
    adicionar(client, LIMAO, 2)
    criar_conta(client)
    with client.session_transaction() as sessao:
        assert sessao["carrinho"][0]["quantidade"] == 2


def test_ca10_1_cadastrar_endereco(client):
    criar_conta(client)
    assert "Endereço salvo." in html(cadastrar_endereco(client))
    texto = html(client.get("/conta"))
    assert "Av. Paulista, 1000, ap. 52 · Bela Vista · 01310-100" in texto


def test_ca10_2_endereco_com_campos_invalidos(client):
    criar_conta(client)
    texto = html(cadastrar_endereco(client, cep="0131-10", numero=""))
    assert "Informe um CEP com 8 dígitos." in texto and "Obrigatório." in texto


def test_excluir_endereco_de_outro_cliente_nao_e_permitido(client, app):
    criar_conta(client, email="dona@example.com")
    cadastrar_endereco(client)
    client.post("/sair")
    criar_conta(client, email="outra@example.com")
    assert client.post("/conta/enderecos/1/excluir").status_code == 404


def test_paginas_da_conta_exigem_login(client):
    for url in ("/conta", "/pedidos", "/checkout", "/conta/enderecos/novo"):
        resposta = client.get(url)
        assert resposta.status_code == 302 and "/entrar" in resposta.headers["Location"]
    assert db.session.scalar(db.select(db.func.count()).select_from(Usuario)) == 0
