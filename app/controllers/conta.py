"""Controller da conta do cliente: dados e endereços (US10, UC09)."""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from ..extensions import db
from ..models import UFS, Endereco, ErrosDeValidacao
from .acesso import destino_seguro, login_obrigatorio, usuario_atual

bp = Blueprint("conta", __name__, url_prefix="/conta")


@bp.get("")
@login_obrigatorio
def index():
    return render_template("conta/index.html", usuario=usuario_atual(), aba="conta")


@bp.route("/enderecos/novo", methods=["GET", "POST"])
@login_obrigatorio
def novo_endereco():
    voltar = destino_seguro(request.values.get("voltar"), url_for("conta.index"))
    erros, dados = {}, {"cidade": "São Paulo", "uf": "SP"}
    if request.method == "POST":
        dados = request.form
        try:
            endereco = Endereco.de_formulario(usuario_atual(), dados)
        except ErrosDeValidacao as e:
            erros = e.erros
        else:
            flash("Endereço salvo.", "ok")
            separador = "&" if "?" in voltar else "?"
            return redirect(f"{voltar}{separador}endereco_id={endereco.id}" if "checkout" in voltar else voltar)
    return render_template("conta/endereco_form.html", erros=erros, dados=dados, ufs=UFS, voltar=voltar)


@bp.post("/enderecos/<int:endereco_id>/excluir")
@login_obrigatorio
def excluir_endereco(endereco_id):
    endereco = db.session.get(Endereco, endereco_id)
    if endereco is None or endereco.usuario_id != usuario_atual().id:
        abort(404)
    db.session.delete(endereco)  # pedidos antigos guardam cópia do endereço (M2)
    db.session.commit()
    flash("Endereço excluído.", "ok")
    return redirect(url_for("conta.index"))
