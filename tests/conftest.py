"""Configuração dos testes.

Os testes de integração usam um PostgreSQL de verdade (DATABASE_URL_TESTE). O banco é
recriado no início da sessão a partir de database/schema.sql e volta aos dados de
database/seed.sql antes de cada teste, então um teste nunca interfere no outro.
"""
from pathlib import Path

import pytest
from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parent.parent
load_dotenv(RAIZ / ".env")

from app import create_app  # noqa: E402
from app.config import ConfigTeste  # noqa: E402
from app.extensions import db  # noqa: E402

TABELAS = ("historico_status, pagamentos, itens_pedido, pedidos, cupons, areas_entrega, cupcake_restricoes, "
           "cupcake_ocasioes, cupcakes, opcoes_personalizacao, restricoes_alimentares, ocasioes, sabores, "
           "enderecos, usuarios")


def _executar(sql):
    conexao = db.engine.raw_connection()
    try:
        with conexao.cursor() as cursor:
            cursor.execute(sql)
        conexao.commit()
    finally:
        conexao.close()


@pytest.fixture(scope="session")
def app():
    if not ConfigTeste.SQLALCHEMY_DATABASE_URI:
        pytest.exit("Defina DATABASE_URL_TESTE no arquivo .env para rodar os testes.")
    aplicacao = create_app(ConfigTeste)
    with aplicacao.app_context():
        _executar("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
        _executar((RAIZ / "database" / "schema.sql").read_text(encoding="utf8"))
    return aplicacao


@pytest.fixture(autouse=True)
def banco(request, app):
    """Antes de cada teste de integração, devolve o banco ao estado do seed."""
    if "integration" not in str(request.fspath):
        yield
        return
    with app.app_context():
        db.session.remove()
        _executar(f"TRUNCATE {TABELAS} RESTART IDENTITY CASCADE;")
        _executar((RAIZ / "database" / "seed.sql").read_text(encoding="utf8"))
        yield
        db.session.remove()


@pytest.fixture
def client(app):
    return app.test_client()


def html(resposta):
    return resposta.get_data(as_text=True)
