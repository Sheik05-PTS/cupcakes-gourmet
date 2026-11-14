"""Comandos de terminal: preparar o banco e criar o usuário administrador.

    flask --app wsgi banco criar        cria as tabelas e carrega os dados iniciais (banco vazio)
    flask --app wsgi criar-admin        cria ou atualiza um administrador da loja
"""
from pathlib import Path

import click
from sqlalchemy import text

from .extensions import db
from .models import Perfil, RegraDeNegocio, Usuario

PASTA_BANCO = Path(__file__).resolve().parent.parent / "database"


def executar_script(nome_arquivo):
    sql = (PASTA_BANCO / nome_arquivo).read_text(encoding="utf8")
    conexao = db.engine.raw_connection()
    try:
        with conexao.cursor() as cursor:
            cursor.execute(sql)
        conexao.commit()
    finally:
        conexao.close()


def banco_vazio():
    return db.session.scalar(text("SELECT to_regclass('public.cupcakes') IS NULL"))


def criar_ou_atualizar_admin(email, senha, nome, telefone):
    usuario = Usuario.buscar_por_email(email)
    if usuario is None:
        usuario = Usuario(email=email.strip().lower(), nome=nome, telefone=telefone)
        db.session.add(usuario)
    usuario.perfil = Perfil.ADMINISTRADOR
    usuario.definir_senha(senha)
    db.session.commit()
    return usuario


def registrar(app):
    @app.cli.group("banco")
    def banco():
        """Preparação do banco de dados."""

    @banco.command("criar")
    def criar():
        """Executa schema.sql e seed.sql, se o banco ainda estiver vazio."""
        if not banco_vazio():
            click.echo("O banco já tem as tabelas. Nada foi alterado.")
            return
        executar_script("schema.sql")
        executar_script("seed.sql")
        click.echo("Tabelas criadas e dados iniciais carregados.")

    @app.cli.command("criar-admin")
    @click.option("--email", required=True)
    @click.option("--senha", required=True)
    @click.option("--nome", default="Equipe da Loja")
    @click.option("--telefone", default="11999990000")
    def criar_admin(email, senha, nome, telefone):
        """Cria (ou atualiza a senha de) um administrador da loja."""
        try:
            usuario = criar_ou_atualizar_admin(email, senha, nome, telefone)
        except RegraDeNegocio as erro:
            raise click.ClickException(erro.mensagem)
        click.echo(f"Administrador pronto: {usuario.email}")
