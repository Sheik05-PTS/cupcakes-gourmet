"""Configurações da aplicação, lidas de variáveis de ambiente."""
import os


def normalizar_url_banco(url):
    """Converte a URL do PostgreSQL para o driver psycopg 3 usado pelo SQLAlchemy.

    Serviços como Render e Neon entregam URLs no formato postgres:// ou postgresql://.
    """
    if not url:
        return url
    for prefixo in ("postgres://", "postgresql://"):
        if url.startswith(prefixo):
            return "postgresql+psycopg://" + url[len(prefixo):]
    return url


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = normalizar_url_banco(os.environ.get("DATABASE_URL"))
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("FLASK_ENV_PRODUCAO") == "1"
    WTF_CSRF_TIME_LIMIT = None

    # Regras de negócio configuráveis
    QTD_MAX_POR_ITEM = 20          # RN03
    PIX_VALIDADE_MINUTOS = 15      # RN11
    INTERVALO_ATUALIZACAO_S = 30   # CA12.2 e CA17.6


class ConfigTeste(Config):
    TESTING = True
    SECRET_KEY = "chave-de-teste"
    SQLALCHEMY_DATABASE_URI = normalizar_url_banco(os.environ.get("DATABASE_URL_TESTE"))
    WTF_CSRF_ENABLED = False
