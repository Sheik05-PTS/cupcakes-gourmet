"""Controller de autenticação: entrar, criar conta e sair (US13, UC07, UC08)."""
from flask import Blueprint, flash, redirect, render_template, request, url_for

from ..models import ErrosDeValidacao, Usuario
from .acesso import destino_seguro, encerrar_sessao, iniciar_sessao, usuario_atual

bp = Blueprint("autenticacao", __name__)


def _destino_apos_login(usuario):
    padrao = "/admin" if usuario.eh_admin() else url_for("vitrine.index")
    return destino_seguro(request.values.get("proximo"), padrao)


@bp.route("/entrar", methods=["GET", "POST"])
def entrar():
    if usuario_atual():
        return redirect(_destino_apos_login(usuario_atual()))
    erro = None
    if request.method == "POST":
        usuario = Usuario.autenticar(request.form.get("email"), request.form.get("senha"))
        if usuario:
            iniciar_sessao(usuario)
            return redirect(_destino_apos_login(usuario))  # CA13.4
        erro = "E-mail ou senha inválidos."  # CA13.5
    veio_do_checkout = "checkout" in (request.values.get("proximo") or "")
    return render_template("autenticacao/entrar.html", erro=erro, email=request.form.get("email", ""),
                           proximo=request.values.get("proximo", ""), veio_do_checkout=veio_do_checkout)


@bp.route("/criar-conta", methods=["GET", "POST"])
def criar_conta():
    erros, dados = {}, {}
    if request.method == "POST":
        dados = request.form
        try:
            usuario = Usuario.cadastrar_cliente(dados.get("nome"), dados.get("email"), dados.get("telefone"),
                                                dados.get("senha"))
        except ErrosDeValidacao as e:
            erros = e.erros
        else:
            iniciar_sessao(usuario)  # CA13.1: já entra logado
            flash(f"Conta criada. Bem-vindo(a), {usuario.primeiro_nome}!", "ok")
            return redirect(_destino_apos_login(usuario))
    return render_template("autenticacao/criar_conta.html", erros=erros, dados=dados,
                           proximo=request.values.get("proximo", ""))


@bp.post("/sair")
def sair():
    encerrar_sessao()  # CA13.6
    return redirect(url_for("vitrine.index"))
