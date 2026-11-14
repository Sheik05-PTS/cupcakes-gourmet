"""Testes dos comandos de terminal e do model de usuário."""
from app.cli import criar_ou_atualizar_admin
from app.models import Perfil, Usuario


def test_criar_admin_e_atualizar_senha(app):
    usuario = criar_ou_atualizar_admin("Loja.Teste@Example.com", "Cupcake2026", "Equipe", "11999990000")
    assert usuario.perfil == Perfil.ADMINISTRADOR and usuario.eh_admin()
    assert usuario.verificar_senha("Cupcake2026")
    assert usuario.senha_hash != "Cupcake2026"  # RN17: só o hash é gravado

    criar_ou_atualizar_admin("loja.teste@example.com", "OutraSenha1", "Equipe", "11999990000")
    assert Usuario.buscar_por_email("LOJA.TESTE@example.com").verificar_senha("OutraSenha1")


def test_comando_banco_criar_nao_mexe_em_banco_existente(app):
    resultado = app.test_cli_runner().invoke(args=["banco", "criar"])
    assert "Nada foi alterado" in resultado.output
