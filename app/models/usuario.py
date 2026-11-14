"""Usuários do sistema (clientes e administradores) e endereços de entrega."""
import enum
import re
from datetime import datetime

from sqlalchemy import Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import db
from .erros import RegraDeNegocio, Validador

UFS = ("AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA",
       "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO")
REGEX_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class Perfil(enum.Enum):
    CLIENTE = "CLIENTE"
    ADMINISTRADOR = "ADMINISTRADOR"


def senha_valida(senha):
    return bool(senha) and len(senha) >= 8 and re.search(r"[A-Za-z]", senha) and re.search(r"\d", senha)


def validar_senha(senha):
    """RN17: no mínimo 8 caracteres, com pelo menos uma letra e um número."""
    if not senha_valida(senha):
        raise RegraDeNegocio("Use no mínimo 8 caracteres, com letras e números.", campo="senha")


def so_digitos(texto):
    return re.sub(r"\D", "", texto or "")


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

    enderecos: Mapped[list["Endereco"]] = relationship(back_populates="usuario", cascade="all, delete-orphan",
                                                       order_by="Endereco.id.desc()")

    def definir_senha(self, senha):
        validar_senha(senha)
        self.senha_hash = generate_password_hash(senha)

    def verificar_senha(self, senha):
        return bool(senha) and check_password_hash(self.senha_hash, senha)

    def eh_admin(self):
        return self.perfil == Perfil.ADMINISTRADOR

    @property
    def primeiro_nome(self):
        return (self.nome or "").split(" ")[0]

    @staticmethod
    def buscar_por_email(email):
        if not email:
            return None
        return db.session.scalar(db.select(Usuario).where(func.lower(Usuario.email) == email.strip().lower()))

    @staticmethod
    def cadastrar_cliente(nome, email, telefone, senha):
        """US13 / CA13.1–CA13.3. Levanta ErrosDeValidacao com a mensagem de cada campo."""
        nome = (nome or "").strip()
        email = (email or "").strip().lower()
        telefone = so_digitos(telefone)
        v = Validador()
        v.exigir(len(nome) >= 3, "nome", "Informe seu nome completo.")
        if v.exigir(REGEX_EMAIL.match(email), "email", "Informe um e-mail válido."):
            v.exigir(Usuario.buscar_por_email(email) is None, "email", "Este e-mail já está cadastrado.")
        v.exigir(10 <= len(telefone) <= 11, "telefone", "Informe o celular com DDD.")
        v.exigir(senha_valida(senha), "senha", "Use no mínimo 8 caracteres, com letras e números.")
        v.conferir()
        usuario = Usuario(nome=nome, email=email, telefone=telefone, perfil=Perfil.CLIENTE)
        usuario.definir_senha(senha)
        db.session.add(usuario)
        db.session.commit()
        return usuario

    @staticmethod
    def autenticar(email, senha):
        """CA13.5: devolve o usuário ou None, sem dizer se o erro foi no e-mail ou na senha."""
        usuario = Usuario.buscar_por_email(email)
        if usuario and usuario.verificar_senha(senha):
            return usuario
        return None


class Endereco(db.Model):
    __tablename__ = "enderecos"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    apelido: Mapped[str | None]
    cep: Mapped[str]
    logradouro: Mapped[str]
    numero: Mapped[str]
    complemento: Mapped[str | None]
    bairro: Mapped[str]
    cidade: Mapped[str]
    uf: Mapped[str]
    criado_em: Mapped[datetime] = mapped_column(server_default=func.now())

    usuario: Mapped[Usuario] = relationship(back_populates="enderecos")

    def formatado(self):
        linha = f"{self.logradouro}, {self.numero}"
        if self.complemento:
            linha += f", {self.complemento}"
        return f"{linha} · {self.bairro} · {self.cep[:5]}-{self.cep[5:]}"

    @staticmethod
    def de_formulario(usuario, dados):
        """RN18 / CA10.1–CA10.2: valida e cria o endereço do usuário."""
        cep = so_digitos(dados.get("cep"))
        campos = {k: (dados.get(k) or "").strip() for k in
                  ("apelido", "logradouro", "numero", "complemento", "bairro", "cidade")}
        uf = (dados.get("uf") or "").strip().upper()
        v = Validador()
        v.exigir(len(cep) == 8, "cep", "Informe um CEP com 8 dígitos.")
        v.exigir(campos["logradouro"], "logradouro", "Obrigatório.")
        v.exigir(campos["numero"], "numero", "Obrigatório.")
        v.exigir(len(campos["numero"]) <= 10, "numero", "Use no máximo 10 caracteres.")
        v.exigir(campos["bairro"], "bairro", "Obrigatório.")
        v.exigir(campos["cidade"], "cidade", "Obrigatório.")
        v.exigir(uf in UFS, "uf", "Escolha o estado.")
        v.exigir(len(campos["apelido"]) <= 30, "apelido", "Use no máximo 30 caracteres.")
        v.exigir(len(campos["complemento"]) <= 60, "complemento", "Use no máximo 60 caracteres.")
        v.exigir(len(campos["logradouro"]) <= 120, "logradouro", "Use no máximo 120 caracteres.")
        v.conferir()
        endereco = Endereco(usuario=usuario, cep=cep, uf=uf, apelido=campos["apelido"] or None,
                            complemento=campos["complemento"] or None, logradouro=campos["logradouro"],
                            numero=campos["numero"], bairro=campos["bairro"], cidade=campos["cidade"])
        db.session.add(endereco)
        db.session.commit()
        return endereco
