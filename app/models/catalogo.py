"""Catálogo: cupcakes, sabores, ocasiões, restrições e opções de personalização."""
import enum
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation

from sqlalchemy import Column, Enum, ForeignKey, Table, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db
from .erros import EstoqueInsuficiente, RegraDeNegocio, Validador

cupcake_ocasioes = Table(
    "cupcake_ocasioes", db.metadata,
    Column("cupcake_id", ForeignKey("cupcakes.id"), primary_key=True),
    Column("ocasiao_id", ForeignKey("ocasioes.id"), primary_key=True),
)

cupcake_restricoes = Table(
    "cupcake_restricoes", db.metadata,
    Column("cupcake_id", ForeignKey("cupcakes.id"), primary_key=True),
    Column("restricao_id", ForeignKey("restricoes_alimentares.id"), primary_key=True),
)


class Sabor(db.Model):
    __tablename__ = "sabores"
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str]


class Ocasiao(db.Model):
    __tablename__ = "ocasioes"
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str]


class RestricaoAlimentar(db.Model):
    __tablename__ = "restricoes_alimentares"
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str]


class TipoOpcao(enum.Enum):
    RECHEIO = "RECHEIO"
    COBERTURA = "COBERTURA"


class OpcaoPersonalizacao(db.Model):
    __tablename__ = "opcoes_personalizacao"
    id: Mapped[int] = mapped_column(primary_key=True)
    tipo: Mapped[TipoOpcao] = mapped_column(Enum(TipoOpcao, name="tipo_opcao", create_type=False))
    nome: Mapped[str]
    acrescimo: Mapped[Decimal]
    ativo: Mapped[bool] = mapped_column(default=True)

    @staticmethod
    def ativas(tipo):
        consulta = (db.select(OpcaoPersonalizacao)
                    .where(OpcaoPersonalizacao.tipo == tipo, OpcaoPersonalizacao.ativo.is_(True))
                    .order_by(OpcaoPersonalizacao.id))
        return db.session.scalars(consulta).all()


class Cupcake(db.Model):
    __tablename__ = "cupcakes"

    id: Mapped[int] = mapped_column(primary_key=True)
    sabor_id: Mapped[int] = mapped_column(ForeignKey("sabores.id"))
    nome: Mapped[str]
    descricao: Mapped[str]
    ingredientes: Mapped[str]
    preco: Mapped[Decimal]
    foto_url: Mapped[str | None]
    estoque: Mapped[int] = mapped_column(default=0)
    ativo: Mapped[bool] = mapped_column(default=True)
    personalizavel: Mapped[bool] = mapped_column(default=False)
    criado_em: Mapped[datetime] = mapped_column(server_default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    sabor: Mapped[Sabor] = relationship(lazy="joined")
    ocasioes: Mapped[list[Ocasiao]] = relationship(secondary=cupcake_ocasioes, order_by=Ocasiao.nome)
    restricoes: Mapped[list[RestricaoAlimentar]] = relationship(secondary=cupcake_restricoes,
                                                               order_by=RestricaoAlimentar.nome)

    def disponivel(self):
        """RN02: aparece para compra se estiver ativo e tiver estoque."""
        return self.ativo and self.estoque > 0

    def baixar_estoque(self, quantidade):
        if quantidade > self.estoque:
            raise EstoqueInsuficiente(f"{self.nome} ficou indisponível. Ajuste seu carrinho para continuar.")
        self.estoque -= quantidade

    def devolver_estoque(self, quantidade):
        self.estoque += quantidade

    @staticmethod
    def da_vitrine(cupcake_id):
        """Cupcake visível na vitrine (ativo), ou None. Inativos não aparecem (RN02)."""
        cupcake = db.session.get(Cupcake, cupcake_id)
        return cupcake if cupcake and cupcake.ativo else None

    # ------------------------------------------------------------ painel da loja
    def preencher(self, dados, ocasioes_ids, restricoes_ids):
        """US15 / RN01: valida os campos do formulário e atualiza o cupcake. Levanta ErrosDeValidacao."""
        v = Validador()
        nome = (dados.get("nome") or "").strip()
        descricao = (dados.get("descricao") or "").strip()
        ingredientes = (dados.get("ingredientes") or "").strip()
        foto_url = (dados.get("foto_url") or "").strip()
        preco = FiltrosVitrine._dinheiro(dados.get("preco"))
        estoque_txt = (dados.get("estoque") or "").strip()
        sabor = db.session.get(Sabor, int(dados.get("sabor_id"))) if (dados.get("sabor_id") or "").isdigit() else None

        if v.exigir(nome, "nome", "Obrigatório.") and v.exigir(len(nome) <= 80, "nome", "Use no máximo 80 caracteres."):
            repetido = db.session.scalar(db.select(Cupcake).where(func.lower(Cupcake.nome) == nome.lower(),
                                                                  Cupcake.id != (self.id or 0)))
            v.exigir(repetido is None, "nome", "Já existe um cupcake com este nome.")
        v.exigir(descricao, "descricao", "Obrigatório.")
        v.exigir(len(descricao) <= 500, "descricao", "Use no máximo 500 caracteres.")
        v.exigir(ingredientes, "ingredientes", "Obrigatório.")
        v.exigir(len(ingredientes) <= 500, "ingredientes", "Use no máximo 500 caracteres.")
        v.exigir(preco is not None and preco > 0, "preco", "Deve ser maior que zero.")
        v.exigir(preco is None or preco < Decimal("1000000"), "preco", "Valor muito alto.")
        v.exigir(estoque_txt.isdigit(), "estoque", "Informe um número inteiro maior ou igual a zero.")
        v.exigir(sabor is not None, "sabor_id", "Escolha o sabor.")
        v.exigir(not foto_url or (foto_url.startswith(("/", "https://")) and len(foto_url) <= 500),
                 "foto_url", "Use um endereço que comece com / ou https://.")
        v.conferir()

        self.nome, self.descricao, self.ingredientes = nome, descricao, ingredientes
        self.preco = preco.quantize(Decimal("0.01"))
        self.estoque = int(estoque_txt)
        self.sabor = sabor
        self.foto_url = foto_url or None
        self.personalizavel = dados.get("personalizavel") in ("1", "on", "true")
        self.ativo = dados.get("ativo") in ("1", "on", "true")
        self.ocasioes = db.session.scalars(db.select(Ocasiao).where(Ocasiao.id.in_(ocasioes_ids or [0]))).all()
        self.restricoes = db.session.scalars(
            db.select(RestricaoAlimentar).where(RestricaoAlimentar.id.in_(restricoes_ids or [0]))).all()
        return self

    def ja_vendido(self):
        from .pedido import ItemPedido  # import local: pedido.py depende deste módulo
        return db.session.scalar(db.select(ItemPedido.id).where(ItemPedido.cupcake_id == self.id).limit(1)) is not None

    def excluir(self):
        """RN19: cupcake que já foi vendido não pode ser excluído, só inativado."""
        if self.ja_vendido():
            raise RegraDeNegocio("Este cupcake já foi vendido. Você pode inativá-lo.")
        db.session.delete(self)

    @staticmethod
    def todos_para_painel():
        return db.session.scalars(db.select(Cupcake).order_by(Cupcake.ativo.desc(), Cupcake.nome)).all()


@dataclass
class FiltrosVitrine:
    """Filtros da vitrine (US02). Todos os filtros informados valem ao mesmo tempo (CA02.5)."""
    busca: str = ""
    sabor_id: int | None = None
    ocasiao_id: int | None = None
    restricao_id: int | None = None
    preco_min: Decimal | None = None
    preco_max: Decimal | None = None
    erros: list = field(default_factory=list)

    @staticmethod
    def _inteiro(valor):
        try:
            return int(valor) if valor not in (None, "") else None
        except ValueError:
            return None

    @staticmethod
    def _dinheiro(valor):
        if valor in (None, ""):
            return None
        texto = str(valor).replace("R$", "").strip()
        if "," in texto:  # formato brasileiro: 1.234,56
            texto = texto.replace(".", "").replace(",", ".")
        try:
            numero = Decimal(texto)
        except InvalidOperation:
            return None
        return numero if numero >= 0 else None

    @classmethod
    def de_parametros(cls, args):
        filtros = cls(
            busca=(args.get("busca") or "").strip()[:60],
            sabor_id=cls._inteiro(args.get("sabor")),
            ocasiao_id=cls._inteiro(args.get("ocasiao")),
            restricao_id=cls._inteiro(args.get("restricao")),
            preco_min=cls._dinheiro(args.get("preco_min")),
            preco_max=cls._dinheiro(args.get("preco_max")),
        )
        filtros.validar()
        return filtros

    def validar(self):
        if self.preco_min is not None and self.preco_max is not None and self.preco_min > self.preco_max:
            self.erros.append("O preço mínimo não pode ser maior que o máximo.")  # CA02.7
            self.preco_min = self.preco_max = None

    def ativos(self):
        return any([self.busca, self.sabor_id, self.ocasiao_id, self.restricao_id,
                    self.preco_min is not None, self.preco_max is not None])

    def buscar(self):
        consulta = db.select(Cupcake).where(Cupcake.ativo.is_(True))
        if self.busca:
            consulta = consulta.where(Cupcake.nome.ilike(f"%{self.busca}%"))
        if self.sabor_id:
            consulta = consulta.where(Cupcake.sabor_id == self.sabor_id)
        if self.ocasiao_id:
            consulta = consulta.where(Cupcake.ocasioes.any(Ocasiao.id == self.ocasiao_id))
        if self.restricao_id:
            consulta = consulta.where(Cupcake.restricoes.any(RestricaoAlimentar.id == self.restricao_id))
        if self.preco_min is not None:
            consulta = consulta.where(Cupcake.preco >= self.preco_min)
        if self.preco_max is not None:
            consulta = consulta.where(Cupcake.preco <= self.preco_max)
        # disponíveis primeiro, depois por nome
        consulta = consulta.order_by((Cupcake.estoque > 0).desc(), Cupcake.nome)
        return db.session.scalars(consulta).unique().all()


def validar_quantidade(quantidade, maximo):
    """RN03: quantidade inteira de 1 até o máximo permitido."""
    try:
        quantidade = int(quantidade)
    except (TypeError, ValueError):
        raise RegraDeNegocio(f"A quantidade deve ser de 1 a {maximo}.", campo="quantidade")
    if quantidade < 1 or quantidade > maximo:
        raise RegraDeNegocio(f"A quantidade deve ser de 1 a {maximo}.", campo="quantidade")
    return quantidade
