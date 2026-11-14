"""Controller do carrinho: adicionar, alterar, remover, desfazer e estimar frete (US04, US05, US06, CA11.3)."""
from urllib.parse import urlparse

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for

from ..extensions import db
from ..models import AreaEntrega, Carrinho, Cupcake, RegraDeNegocio, normalizar_cep

bp = Blueprint("carrinho", __name__, url_prefix="/carrinho")


def carrinho_atual():
    return Carrinho.da_sessao(session, current_app.config["QTD_MAX_POR_ITEM"])


def _voltar_para(padrao):
    """Volta para a página de origem, se for deste site; senão, para a página padrão."""
    destino = request.form.get("voltar") or request.referrer
    if destino and urlparse(destino).netloc in ("", request.host):
        return redirect(destino)
    return redirect(padrao)


@bp.get("")
def ver():
    carrinho = carrinho_atual()
    linhas = carrinho.linhas()
    subtotal = Carrinho.subtotal(linhas)
    estimativa = None
    cep = session.get("cep_estimado")
    erro_cep = None
    if cep:
        try:
            estimativa = AreaEntrega.para_cep(cep)
        except RegraDeNegocio as erro:
            erro_cep = erro.mensagem
    return render_template("carrinho/ver.html", linhas=linhas, subtotal=subtotal, estimativa=estimativa,
                           cep=cep, erro_cep=erro_cep, aba="vitrine")


@bp.post("/itens")
def adicionar():
    cupcake = db.session.get(Cupcake, request.form.get("cupcake_id", type=int) or 0)
    carrinho = carrinho_atual()
    try:
        carrinho.adicionar(cupcake, request.form.get("quantidade", 1), request.form.get("recheio_id", type=int),
                           request.form.get("cobertura_id", type=int), request.form.get("mensagem", ""))
    except RegraDeNegocio as erro:
        flash(erro.mensagem, "erro")
        destino = url_for("vitrine.detalhe", cupcake_id=cupcake.id) if cupcake else url_for("vitrine.index")
        return redirect(destino)
    carrinho.salvar(session)
    flash("Adicionado ao carrinho.", "ok")  # CA04.1
    return _voltar_para(url_for("vitrine.index"))


@bp.post("/itens/<chave>/quantidade")
def alterar(chave):
    carrinho = carrinho_atual()
    quantidade = request.form.get("quantidade", type=int) or 0
    acao = request.form.get("acao")
    if acao == "mais":
        quantidade += 1
    elif acao == "menos":
        quantidade -= 1
    try:
        if quantidade < 1:
            item = carrinho.remover(chave)
            session["item_removido"] = item
            flash("Item removido do carrinho.", "desfazer")
        else:
            carrinho.alterar_quantidade(chave, quantidade)
    except RegraDeNegocio as erro:
        flash(erro.mensagem, "erro")
    carrinho.salvar(session)
    return redirect(url_for("carrinho.ver"))


@bp.post("/itens/<chave>/remover")
def remover(chave):
    carrinho = carrinho_atual()
    try:
        session["item_removido"] = carrinho.remover(chave)
        flash("Item removido do carrinho.", "desfazer")  # CA06.3
    except RegraDeNegocio as erro:
        flash(erro.mensagem, "erro")
    carrinho.salvar(session)
    return redirect(url_for("carrinho.ver"))


@bp.post("/desfazer")
def desfazer():
    carrinho = carrinho_atual()
    carrinho.restaurar(session.pop("item_removido", None))
    carrinho.salvar(session)
    return redirect(url_for("carrinho.ver"))


@bp.post("/frete")
def estimar_frete():
    try:
        session["cep_estimado"] = normalizar_cep(request.form.get("cep"))
    except RegraDeNegocio as erro:
        session.pop("cep_estimado", None)
        flash(erro.mensagem, "erro")
    return redirect(url_for("carrinho.ver"))
