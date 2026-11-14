"""Controller do pagamento simulado: cartão, Pix e confirmação (UC12, US08, US09)."""
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, session, url_for

from ..extensions import db
from ..models import (DadosCartao, ErrosDeValidacao, GatewaySimulado, MetodoPagamento, Pagamento, Pedido,
                      RegraDeNegocio, ServicoPagamento, StatusPagamento, StatusPedido, pix_restante_segundos)
from .acesso import login_obrigatorio, usuario_atual
from .carrinho import carrinho_atual

bp = Blueprint("pagamento", __name__)


def servico():
    return ServicoPagamento(GatewaySimulado(current_app.config["PIX_VALIDADE_MINUTOS"]))


def _pedido_do_cliente(pedido_id):
    pedido = Pedido.do_cliente(pedido_id, usuario_atual())
    if pedido is None:
        abort(404, description="pedido")
    return pedido


def _pix_pendente(pedido):
    pendentes = [p for p in pedido.pagamentos if p.metodo == MetodoPagamento.PIX and p.status == StatusPagamento.PENDENTE]
    return pendentes[-1] if pendentes else None


def _concluir(pedido):
    carrinho = carrinho_atual()  # CA09.3: carrinho vazio após a confirmação
    carrinho.limpar()
    carrinho.salvar(session)
    return redirect(url_for("pagamento.confirmado", pedido_id=pedido.id))


@bp.get("/pedidos/<int:pedido_id>/pagamento")
@login_obrigatorio
def index(pedido_id):
    pedido = _pedido_do_cliente(pedido_id)
    if pedido.status != StatusPedido.AGUARDANDO_PAGAMENTO:
        return redirect(url_for("pedidos.detalhe", pedido_id=pedido.id))
    metodo = request.args.get("metodo", "cartao")
    pix = _pix_pendente(pedido) if metodo == "pix" else None
    return render_template("pagamento/index.html", pedido=pedido, metodo=metodo, pix=pix,
                           restante=pix_restante_segundos(pix), erros={}, dados={})


@bp.post("/pedidos/<int:pedido_id>/pagamento/cartao")
@login_obrigatorio
def pagar_cartao(pedido_id):
    pedido = _pedido_do_cliente(pedido_id)
    dados = DadosCartao(request.form.get("numero", ""), request.form.get("nome", ""),
                        request.form.get("validade", ""), request.form.get("cvv", ""))
    hoje = datetime.now(ZoneInfo("America/Sao_Paulo")).date()
    erros, erro_geral = {}, None
    try:
        servico().pagar_com_cartao(pedido, dados, hoje)
    except ErrosDeValidacao as e:
        erros = e.erros  # CA08.6
    except RegraDeNegocio as e:
        erro_geral = e.mensagem  # CA08.5 e CA08.8
    else:
        return _concluir(pedido)
    db.session.refresh(pedido)
    # devolve o que foi digitado, menos o CVV (nunca reexibido)
    preenchido = {"numero": request.form.get("numero", ""), "nome": request.form.get("nome", ""),
                  "validade": request.form.get("validade", "")}
    return render_template("pagamento/index.html", pedido=pedido, metodo="cartao", pix=None, restante=0,
                           erros=erros, erro_geral=erro_geral, dados=preenchido), 422


@bp.post("/pedidos/<int:pedido_id>/pagamento/pix")
@login_obrigatorio
def gerar_pix(pedido_id):
    pedido = _pedido_do_cliente(pedido_id)
    try:
        servico().gerar_pix(pedido)
    except RegraDeNegocio as erro:
        flash(erro.mensagem, "erro")
        return redirect(url_for("pedidos.detalhe", pedido_id=pedido.id))
    return redirect(url_for("pagamento.index", pedido_id=pedido.id, metodo="pix"))


@bp.post("/pagamentos/<int:pagamento_id>/confirmar")
@login_obrigatorio
def confirmar_pix(pagamento_id):
    pagamento = db.session.get(Pagamento, pagamento_id)
    if pagamento is None or pagamento.pedido.usuario_id != usuario_atual().id:
        abort(404, description="pedido")
    try:
        servico().confirmar_pix(pagamento)
    except RegraDeNegocio as erro:
        flash(erro.mensagem, "erro")  # CA08.3
        return redirect(url_for("pagamento.index", pedido_id=pagamento.pedido_id, metodo="pix"))
    return _concluir(pagamento.pedido)


@bp.get("/pedidos/<int:pedido_id>/confirmado")
@login_obrigatorio
def confirmado(pedido_id):
    pedido = _pedido_do_cliente(pedido_id)
    if pedido.pagamento_aprovado() is None:
        return redirect(url_for("pedidos.detalhe", pedido_id=pedido.id))
    return render_template("pagamento/confirmado.html", pedido=pedido)
