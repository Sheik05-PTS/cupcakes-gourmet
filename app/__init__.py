"""Fábrica da aplicação Cupcakes Gourmet (Flask, padrão MVC).

- Models:      app/models       (entidades e regras de negócio)
- Views:       app/views        (templates HTML) e app/static (CSS, JS, imagens)
- Controllers: app/controllers  (rotas)
"""
from flask import Flask, render_template
from werkzeug.exceptions import HTTPException

from . import cli, formatacao
from .config import Config
from .controllers import BLUEPRINTS
from .extensions import csrf, db


def create_app(config=Config):
    app = Flask(__name__, template_folder="views", static_folder="static")
    app.config.from_object(config)
    if not app.config.get("SECRET_KEY") or not app.config.get("SQLALCHEMY_DATABASE_URI"):
        raise RuntimeError("Defina SECRET_KEY e DATABASE_URL (veja o arquivo .env.example).")

    db.init_app(app)
    csrf.init_app(app)
    for blueprint in BLUEPRINTS:
        app.register_blueprint(blueprint)

    formatacao.registrar(app)
    cli.registrar(app)
    _registrar_paginas_de_erro(app)

    @app.context_processor
    def contexto_global():
        from .controllers.acesso import usuario_atual
        from .controllers.carrinho import carrinho_atual
        from .models import STATUS_INFO
        return {"qtd_carrinho": carrinho_atual().total_itens(), "aba": None, "usuario_logado": usuario_atual(),
                "STATUS_INFO": STATUS_INFO}

    return app


def _registrar_paginas_de_erro(app):
    """RNF06: erros mostram página amigável, sem detalhes técnicos."""

    @app.errorhandler(HTTPException)
    def erro_http(erro):
        return render_template("erros/http.html", erro=erro), erro.code

    @app.errorhandler(Exception)
    def erro_inesperado(erro):
        app.logger.exception("Erro inesperado: %s", erro)
        db.session.rollback()
        return render_template("erros/http.html", erro=None), 500
