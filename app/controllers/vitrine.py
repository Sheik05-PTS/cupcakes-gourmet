"""Controller da vitrine: listagem com filtros e detalhe do cupcake (US01, US02, US03, US05)."""
from flask import Blueprint, abort, current_app, redirect, render_template, request, url_for

from ..extensions import db
from ..models import Cupcake, FiltrosVitrine, Ocasiao, OpcaoPersonalizacao, RestricaoAlimentar, Sabor, TipoOpcao

bp = Blueprint("vitrine", __name__)


def _opcoes_de_filtro():
    return {
        "sabores": db.session.scalars(db.select(Sabor).order_by(Sabor.nome)).all(),
        "ocasioes": db.session.scalars(db.select(Ocasiao).order_by(Ocasiao.nome)).all(),
        "restricoes": db.session.scalars(db.select(RestricaoAlimentar).order_by(RestricaoAlimentar.nome)).all(),
    }


@bp.get("/")
def index():
    filtros = FiltrosVitrine.de_parametros(request.args)
    cupcakes = filtros.buscar()
    return render_template("vitrine/index.html", cupcakes=cupcakes, filtros=filtros, **_opcoes_de_filtro())


@bp.get("/favicon.ico")
def favicon():
    return redirect(url_for("static", filename="img/icone.svg"), code=301)


@bp.get("/cupcakes/<int:cupcake_id>")
def detalhe(cupcake_id):
    cupcake = Cupcake.da_vitrine(cupcake_id)
    if cupcake is None:
        abort(404, description="cupcake")
    recheios = coberturas = []
    if cupcake.personalizavel:
        recheios = OpcaoPersonalizacao.ativas(TipoOpcao.RECHEIO)
        coberturas = OpcaoPersonalizacao.ativas(TipoOpcao.COBERTURA)
    maximo = min(current_app.config["QTD_MAX_POR_ITEM"], cupcake.estoque)
    return render_template("vitrine/detalhe.html", cupcake=cupcake, recheios=recheios,
                           coberturas=coberturas, quantidade_maxima=maximo)
