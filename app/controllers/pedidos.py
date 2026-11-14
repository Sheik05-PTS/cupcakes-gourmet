"""Controller dos pedidos do cliente: lista, detalhe e status para atualização automática (US12, CA13.7)."""
from flask import Blueprint, abort, jsonify, render_template

from ..extensions import db
from ..models import Pedido
from ..formatacao import data_hora
from .acesso import login_obrigatorio, usuario_atual

bp = Blueprint("pedidos", __name__, url_prefix="/pedidos")


def _pedido_do_cliente(pedido_id):
    pedido = Pedido.do_cliente(pedido_id, usuario_atual())
    if pedido is None:
        abort(404, description="pedido")  # CA12.4
    return pedido


@bp.get("")
@login_obrigatorio
def lista():
    pedidos = db.session.scalars(db.select(Pedido).where(Pedido.usuario_id == usuario_atual().id)
                                 .order_by(Pedido.criado_em.desc(), Pedido.id.desc())).all()
    return render_template("pedidos/lista.html", pedidos=pedidos, aba="pedidos")


@bp.get("/<int:pedido_id>")
@login_obrigatorio
def detalhe(pedido_id):
    return render_template("pedidos/detalhe.html", pedido=_pedido_do_cliente(pedido_id), aba="pedidos")


@bp.get("/<int:pedido_id>/status")
@login_obrigatorio
def status(pedido_id):
    """Consultado a cada 30 segundos pela tela do pedido (CA12.2)."""
    pedido = _pedido_do_cliente(pedido_id)
    return jsonify(status=pedido.status.value, texto=pedido.status_texto,
                   etapas=[{"status": e["status"].value, "situacao": e["situacao"],
                            "quando": data_hora(e["quando"]) if e["quando"] else None}
                           for e in pedido.linha_do_tempo()])
