"""Controller do checkout: endereço, frete, cupom e criação do pedido (UC10, UC11, US07, US11)."""
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from ..extensions import db
from ..models import AreaEntrega, Endereco, RegraDeNegocio, ServicoPedido, validar_cupom
from .acesso import login_obrigatorio, usuario_atual
from .carrinho import carrinho_atual

bp = Blueprint("checkout", __name__, url_prefix="/checkout")
FUSO = ZoneInfo("America/Sao_Paulo")


def hoje():
    return datetime.now(FUSO).date()


def _endereco_escolhido(usuario):
    enderecos = usuario.enderecos
    escolhido_id = request.args.get("endereco_id", type=int) or session.get("checkout_endereco")
    escolhido = next((e for e in enderecos if e.id == escolhido_id), None) or (enderecos[0] if enderecos else None)
    if escolhido:
        session["checkout_endereco"] = escolhido.id
    return enderecos, escolhido


@bp.get("")
@login_obrigatorio
def index():
    carrinho = carrinho_atual()
    if carrinho.vazio():
        return redirect(url_for("carrinho.ver"))
    usuario = usuario_atual()
    enderecos, escolhido = _endereco_escolhido(usuario)
    endereco_atendido, erro_entrega = escolhido, None
    if escolhido:
        try:
            AreaEntrega.para_cep(escolhido.cep)
        except RegraDeNegocio as erro:
            endereco_atendido, erro_entrega = None, erro.mensagem  # CA11.2
    codigo, erro_cupom = session.get("checkout_cupom"), None
    try:
        resumo = ServicoPedido.resumo(carrinho, endereco_atendido, codigo, hoje())
    except RegraDeNegocio as erro:  # o cupom deixou de valer (ex.: o subtotal mudou)
        session.pop("checkout_cupom", None)
        erro_cupom = erro.mensagem
        resumo = ServicoPedido.resumo(carrinho, endereco_atendido, None, hoje())
    indisponiveis = [l for l in resumo["linhas"] if l.indisponivel]
    return render_template("checkout/index.html", enderecos=enderecos, escolhido=escolhido, resumo=resumo,
                           erro_entrega=erro_entrega, erro_cupom=erro_cupom, indisponiveis=indisponiveis,
                           qtd_itens=carrinho.total_itens())


@bp.post("/cupom")
@login_obrigatorio
def aplicar_cupom():
    carrinho = carrinho_atual()
    subtotal = ServicoPedido.resumo(carrinho, None, None, hoje())["subtotal"]
    try:
        cupom = validar_cupom(request.form.get("codigo"), subtotal, hoje())
    except RegraDeNegocio as erro:
        flash(erro.mensagem, "erro")  # CA07.2, CA07.3
    else:
        session["checkout_cupom"] = cupom.codigo  # CA07.4: substitui o anterior
        flash(f"Cupom aplicado: {cupom.descricao()}.", "ok")
    return redirect(url_for("checkout.index"))


@bp.post("/cupom/remover")
@login_obrigatorio
def remover_cupom():
    session.pop("checkout_cupom", None)
    return redirect(url_for("checkout.index"))


@bp.post("/confirmar")
@login_obrigatorio
def confirmar():
    usuario = usuario_atual()
    endereco = db.session.get(Endereco, request.form.get("endereco_id", type=int) or 0)
    try:
        pedido = ServicoPedido.criar_pedido(usuario, carrinho_atual(), endereco, session.get("checkout_cupom"), hoje())
    except RegraDeNegocio as erro:
        flash(erro.mensagem, "erro")
        destino = "carrinho.ver" if "indisponível" in erro.mensagem else "checkout.index"
        return redirect(url_for(destino))
    session.pop("checkout_cupom", None)
    return redirect(url_for("pagamento.index", pedido_id=pedido.id))
