"""Usuários do sistema: clientes e administradores da loja."""
import enum
import re
from datetime import datetime

from sqlalchemy import Enum, func
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import db
from .erros import RegraDeNegocio


class Perfil(enum.Enum):
    CLIENTE = "CLIENTE"
    ADMINISTRADOR = "ADMINISTRADOR"


def validar_senha(senha):
    """RN17: no mínimo 8 caracteres, com pelo menos uma letra e um número."""
    if not senha or len(senha) < 8 or not re.search(r"[A-Za-z]", senha) or not re.search(r"\d", senha):
        raise RegraDeNegocio("Use no mínimo 8 caracteres, com letras e números.", campo="senha")


class Usuario(db.Model):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str]
    email: Mapped[str]
    telefone: Mapped[str]
    senha_hash: Mapped[str]
    perfil: Mapped[Perfil] = mapped_column(Enum(Perfil, name="perfil_usuario", create_type=False),
                                           default=Perfil.CLIENTE)
    criado_em: Mapped[datetime] = mapped_column(server_default=func.now())

    def definir_senha(self, senha):
        validar_senha(senha)
        self.senha_hash = generate_password_hash(senha)

    def verificar_senha(self, senha):
        return bool(senha) and check_password_hash(self.senha_hash, senha)

    def eh_admin(self):
        return self.perfil == Perfil.ADMINISTRADOR

    @staticmethod
    def buscar_por_email(email):
        if not email:
            return None
        return db.session.scalar(db.select(Usuario).where(func.lower(Usuario.email) == email.strip().lower()))
