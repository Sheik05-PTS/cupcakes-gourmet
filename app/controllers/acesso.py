"""Controle de acesso: usuário logado, login obrigatório e área exclusiva da loja (RN06, RN20)."""
from functools import wraps
from urllib.parse import urlparse

from flask import abort, g, redirect, request, session, url_for

from ..extensions import db
from ..models import Usuario

CHAVES_PRESERVADAS = ("carrinho", "cep_estimado")


def usuario_atual():
    if "usuario" not in g:
        usuario_id = session.get("usuario_id")
        g.usuario = db.session.get(Usuario, usuario_id) if usuario_id else None
    return g.usuario


def iniciar_sessao(usuario):
    """Renova a sessão no login (evita fixação de sessão) sem perder o carrinho (RN06)."""
    preservado = {k: session[k] for k in CHAVES_PRESERVADAS if k in session}
    session.clear()
    session.update(preservado)
    session["usuario_id"] = usuario.id
    session.permanent = True
    g.usuario = usuario


def encerrar_sessao():
    session.clear()
    g.usuario = None


def destino_seguro(destino, padrao):
    """Só aceita redirecionar para páginas deste site."""
    if destino and destino.startswith("/") and not destino.startswith("//") and not urlparse(destino).netloc:
        return destino
    return padrao


def login_obrigatorio(view):
    @wraps(view)
    def envolvida(*args, **kwargs):
        if usuario_atual() is None:
            return redirect(url_for("autenticacao.entrar", proximo=request.full_path.rstrip("?")))
        return view(*args, **kwargs)
    return envolvida


def admin_obrigatorio(view):
    @wraps(view)
    def envolvida(*args, **kwargs):
        usuario = usuario_atual()
        if usuario is None:
            return redirect(url_for("autenticacao.entrar", proximo=request.full_path.rstrip("?")))
        if not usuario.eh_admin():
            abort(403)  # CA17.5
        return view(*args, **kwargs)
    return envolvida
