"""Controller do painel da loja: pedidos e cupcakes (US15, US16, US17). Só para administradores (RN20)."""
from pathlib import Path

from flask import Blueprint, abort, current_app, flash, jsonify, redirect, render_template, request, url_for

from ..extensions import db
from ..models import (STATUS_INFO, Cupcake, ErrosDeValidacao, Ocasiao, Pedido, RegraDeNegocio, RestricaoAlimentar,
                      Sabor, StatusPedido)
from .acesso import admin_obrigatorio, usuario_atual

bp = Blueprint("admin", __name__, url_prefix="/admin")

FILTROS = [None, StatusPedido.PAGO, StatusPedido.EM_PREPARO, StatusPedido.SAIU_PARA_ENTREGA,
           StatusPedido.AGUARDANDO_PAGAMENTO, StatusPedido.ENTREGUE, StatusPedido.CANCELADO]


@bp.before_request
@admin_obrigatorio
def exigir_admin():
    """Toda rota deste blueprint exige perfil Administrador (CA17.5)."""


@bp.get("")
def index():
    return redirect(url_for("admin.pedidos"))


# ------------------------------------------------------------------ pedidos
@bp.get("/pedidos")
def pedidos():
    status = request.args.get("status")
    filtro = StatusPedido[status] if status in StatusPedido.__members__ else None
    return render_template("admin/pedidos.html", pedidos=Pedido.para_painel(filtro), filtro=filtro, filtros=FILTROS,
                           contagem=Pedido.contagem_por_status(), resumo=Pedido.resumo_novos(), secao="pedidos")


@bp.get("/pedidos/novos")
def pedidos_novos():
    """Consultado a cada 30 segundos pelo painel aberto (CA17.6)."""
    return jsonify(Pedido.resumo_novos())


def _pedido(pedido_id):
    pedido = db.session.get(Pedido, pedido_id)
    if pedido is None:
        abort(404, description="pedido")
    return pedido


@bp.get("/pedidos/<int:pedido_id>")
def pedido(pedido_id):
    pedido = _pedido(pedido_id)
    if not pedido.visto_pelo_admin and pedido.status != StatusPedido.AGUARDANDO_PAGAMENTO:
        pedido.visto_pelo_admin = True  # deixa de aparecer como "Novo"
        db.session.commit()
    proximo = pedido.proximo_status()
    return render_template("admin/pedido.html", pedido=pedido, proximo=proximo,
                           proximo_info=STATUS_INFO.get(proximo), secao="pedidos")


@bp.post("/pedidos/<int:pedido_id>/avancar")
def avancar(pedido_id):
    pedido = _pedido(pedido_id)
    try:
        pedido.avancar_status(usuario_atual())
        db.session.commit()
        flash(f"Pedido {pedido.numero} agora está “{pedido.status_texto}”.", "ok")  # CA17.3
    except RegraDeNegocio as erro:
        db.session.rollback()
        flash(erro.mensagem, "erro")
    return redirect(url_for("admin.pedido", pedido_id=pedido_id))


@bp.post("/pedidos/<int:pedido_id>/cancelar")
def cancelar(pedido_id):
    pedido = _pedido(pedido_id)
    try:
        devolveu = pedido.cancelar(usuario_atual())
        db.session.commit()
        sufixo = " O estoque foi devolvido." if devolveu else ""
        flash(f"Pedido {pedido.numero} cancelado.{sufixo}", "ok")  # CA17.4
    except RegraDeNegocio as erro:
        db.session.rollback()
        flash(erro.mensagem, "erro")
    return redirect(url_for("admin.pedido", pedido_id=pedido_id))


# ------------------------------------------------------------------ cupcakes
@bp.get("/cupcakes")
def cupcakes():
    lista = Cupcake.todos_para_painel()
    return render_template("admin/cupcakes.html", cupcakes=lista, secao="cupcakes",
                           esgotados=sum(1 for c in lista if c.ativo and c.estoque == 0),
                           inativos=sum(1 for c in lista if not c.ativo))


def _imagens_disponiveis():
    pasta = Path(current_app.static_folder) / "img" / "cupcakes"
    return sorted(f"/static/img/cupcakes/{p.name}" for p in pasta.glob("*.svg"))


def _formulario(cupcake, titulo):
    erros = {}
    if request.method == "POST":
        try:
            cupcake.preencher(request.form, request.form.getlist("ocasioes", type=int),
                              request.form.getlist("restricoes", type=int))
        except ErrosDeValidacao as e:
            erros = e.erros
            db.session.rollback()
        else:
            db.session.add(cupcake)
            db.session.commit()
            flash("Cupcake salvo.", "ok")
            return redirect(url_for("admin.cupcakes"))
    dados = request.form if request.method == "POST" else None
    if dados:
        marcadas = {"ocasioes": dados.getlist("ocasioes", type=int), "restricoes": dados.getlist("restricoes", type=int),
                    "sabor": dados.get("sabor_id", type=int)}
    else:
        marcadas = {"ocasioes": [o.id for o in cupcake.ocasioes], "restricoes": [r.id for r in cupcake.restricoes],
                    "sabor": cupcake.sabor_id}
    return render_template("admin/cupcake_form.html", cupcake=cupcake, titulo=titulo, erros=erros, dados=dados,
                           marcadas=marcadas,
                           sabores=db.session.scalars(db.select(Sabor).order_by(Sabor.nome)).all(),
                           ocasioes=db.session.scalars(db.select(Ocasiao).order_by(Ocasiao.nome)).all(),
                           restricoes=db.session.scalars(db.select(RestricaoAlimentar).order_by(RestricaoAlimentar.nome)).all(),
                           imagens=_imagens_disponiveis(), secao="cupcakes")


@bp.route("/cupcakes/novo", methods=["GET", "POST"])
def novo_cupcake():
    return _formulario(Cupcake(ativo=True, estoque=0, personalizavel=False), "Novo cupcake")


def _cupcake(cupcake_id):
    cupcake = db.session.get(Cupcake, cupcake_id)
    if cupcake is None:
        abort(404, description="cupcake")
    return cupcake


@bp.route("/cupcakes/<int:cupcake_id>/editar", methods=["GET", "POST"])
def editar_cupcake(cupcake_id):
    return _formulario(_cupcake(cupcake_id), "Editar cupcake")


@bp.post("/cupcakes/<int:cupcake_id>/ativo")
def alternar_ativo(cupcake_id):
    """US16 / CA16.2: liga ou desliga o cupcake na vitrine."""
    cupcake = _cupcake(cupcake_id)
    cupcake.ativo = not cupcake.ativo
    db.session.commit()
    flash(f"{cupcake.nome} {'voltou para' if cupcake.ativo else 'saiu da'} vitrine.", "ok")
    return redirect(url_for("admin.cupcakes"))


@bp.post("/cupcakes/<int:cupcake_id>/excluir")
def excluir_cupcake(cupcake_id):
    cupcake = _cupcake(cupcake_id)
    try:
        cupcake.excluir()
        db.session.commit()
        flash(f"{cupcake.nome} foi excluído.", "ok")
        return redirect(url_for("admin.cupcakes"))
    except RegraDeNegocio as erro:  # CA15.4
        flash(erro.mensagem, "erro")
        return redirect(url_for("admin.editar_cupcake", cupcake_id=cupcake_id))
