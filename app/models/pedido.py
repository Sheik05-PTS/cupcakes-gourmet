"""Pedidos, itens, pagamentos e histórico de status (RN09, RN10, RN12, RN14, RN15, RN16)."""
import enum
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db
from .catalogo import Cupcake, OpcaoPersonalizacao
from .erros import RegraDeNegocio
from .promocao import Cupom
from .usuario import Usuario


class StatusPedido(enum.Enum):
    AGUARDANDO_PAGAMENTO = "AGUARDANDO_PAGAMENTO"
    PAGO = "PAGO"
    EM_PREPARO = "EM_PREPARO"
    SAIU_PARA_ENTREGA = "SAIU_PARA_ENTREGA"
    ENTREGUE = "ENTREGUE"
    CANCELADO = "CANCELADO"


# Texto e ícone de cada status: sempre ícone + texto, nunca só cor (RNF10)
STATUS_INFO = {
    StatusPedido.AGUARDANDO_PAGAMENTO: ("Aguardando pagamento", "hour"),
    StatusPedido.PAGO: ("Pago", "card"),
    StatusPedido.EM_PREPARO: ("Em preparo", "chef"),
    StatusPedido.SAIU_PARA_ENTREGA: ("Saiu para entrega", "truck"),
    StatusPedido.ENTREGUE: ("Entregue", "check"),
    StatusPedido.CANCELADO: ("Cancelado", "x"),
}

# RN15: as etapas só avançam nesta ordem
SEQUENCIA = [StatusPedido.AGUARDANDO_PAGAMENTO, StatusPedido.PAGO, StatusPedido.EM_PREPARO,
             StatusPedido.SAIU_PARA_ENTREGA, StatusPedido.ENTREGUE]
AVANCA_PELA_LOJA = {StatusPedido.PAGO, StatusPedido.EM_PREPARO, StatusPedido.SAIU_PARA_ENTREGA}
CANCELAVEIS = {StatusPedido.AGUARDANDO_PAGAMENTO, StatusPedido.PAGO, StatusPedido.EM_PREPARO}  # RN16


class MetodoPagamento(enum.Enum):
    PIX = "PIX"
    CARTAO = "CARTAO"


class StatusPagamento(enum.Enum):
    PENDENTE = "PENDENTE"
    APROVADO = "APROVADO"
    RECUSADO = "RECUSADO"
    EXPIRADO = "EXPIRADO"


def agora():
    return datetime.now(timezone.utc)


class Pedido(db.Model):
    __tablename__ = "pedidos"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    cupom_id: Mapped[int | None] = mapped_column(ForeignKey("cupons.id"))
    status: Mapped[StatusPedido] = mapped_column(Enum(StatusPedido, name="status_pedido", create_type=False),
                                                 default=StatusPedido.AGUARDANDO_PAGAMENTO)
    subtotal: Mapped[Decimal]
    desconto: Mapped[Decimal] = mapped_column(default=Decimal("0"))
    frete: Mapped[Decimal]
    total: Mapped[Decimal]
    prazo_minutos: Mapped[int]
    entrega_cep: Mapped[str]
    entrega_logradouro: Mapped[str]
    entrega_numero: Mapped[str]
    entrega_complemento: Mapped[str | None]
    entrega_bairro: Mapped[str]
    entrega_cidade: Mapped[str]
    entrega_uf: Mapped[str]
    visto_pelo_admin: Mapped[bool] = mapped_column(default=False)
    criado_em: Mapped[datetime] = mapped_column(server_default=func.now())

    cliente: Mapped[Usuario] = relationship()
    cupom: Mapped[Cupom | None] = relationship()
    itens: Mapped[list["ItemPedido"]] = relationship(back_populates="pedido", cascade="all, delete-orphan",
                                                     order_by="ItemPedido.id")
    pagamentos: Mapped[list["Pagamento"]] = relationship(back_populates="pedido", cascade="all, delete-orphan",
                                                         order_by="Pagamento.id")
    historico: Mapped[list["HistoricoStatus"]] = relationship(back_populates="pedido", cascade="all, delete-orphan",
                                                              order_by="HistoricoStatus.id")

    # ------------------------------------------------------------ exibição
    @property
    def numero(self):
        return f"#{self.id:06d}"

    @property
    def status_texto(self):
        return STATUS_INFO[self.status][0]

    @property
    def total_itens(self):
        return sum(i.quantidade for i in self.itens)

    def endereco_formatado(self):
        linha = f"{self.entrega_logradouro}, {self.entrega_numero}"
        if self.entrega_complemento:
            linha += f", {self.entrega_complemento}"
        return f"{linha} · {self.entrega_bairro} · {self.entrega_cep[:5]}-{self.entrega_cep[5:]}"

    def prazo_texto(self):
        if self.prazo_minutos < 120:
            return f"até {self.prazo_minutos} minutos"
        return f"até {self.prazo_minutos / 60:g} horas".replace(".", ",")

    def pagamento_aprovado(self):
        return next((p for p in self.pagamentos if p.status == StatusPagamento.APROVADO), None)

    def linha_do_tempo(self):
        """Etapas para a tela de acompanhamento (CA12.1): feitas, atual e pendentes."""
        quando = {}
        for registro in self.historico:
            quando[registro.status] = registro.registrado_em
        if self.status == StatusPedido.CANCELADO:
            etapas = [s for s in SEQUENCIA if s in quando] + [StatusPedido.CANCELADO]
        else:
            etapas = SEQUENCIA
        atual = self.status
        resultado = []
        for etapa in etapas:
            if etapa == atual:
                situacao = "atual" if atual not in (StatusPedido.ENTREGUE, StatusPedido.CANCELADO) else "feito"
            elif etapa in quando:
                situacao = "feito"
            else:
                situacao = "pend"
            texto, icone = STATUS_INFO[etapa]
            resultado.append({"status": etapa, "texto": texto, "icone": icone, "situacao": situacao,
                              "quando": quando.get(etapa)})
        return resultado

    # ------------------------------------------------------------ regras de status
    def registrar(self, status, responsavel=None):
        self.status = status
        self.historico.append(HistoricoStatus(status=status, responsavel=responsavel, registrado_em=agora()))

    def proximo_status(self):
        if self.status not in AVANCA_PELA_LOJA:
            return None
        return SEQUENCIA[SEQUENCIA.index(self.status) + 1]

    def pode_avancar(self):
        return self.proximo_status() is not None

    def pode_cancelar(self):
        return self.status in CANCELAVEIS

    def avancar_status(self, responsavel):
        """RN15: só avança, uma etapa por vez, a partir de 'Pago'."""
        if self.status == StatusPedido.AGUARDANDO_PAGAMENTO:
            raise RegraDeNegocio("Este pedido ainda está aguardando pagamento do cliente.")
        proximo = self.proximo_status()
        if proximo is None:
            raise RegraDeNegocio("Este pedido não pode mais mudar de etapa.")
        self.registrar(proximo, responsavel)

    def cancelar(self, responsavel):
        """RN16: até 'Em preparo'; se já estava pago, o estoque volta."""
        if not self.pode_cancelar():
            raise RegraDeNegocio("Este pedido não pode mais ser cancelado.")
        estava_pago = self.status in (StatusPedido.PAGO, StatusPedido.EM_PREPARO)
        if estava_pago:
            for item in self.itens:
                item.cupcake.devolver_estoque(item.quantidade)
        self.registrar(StatusPedido.CANCELADO, responsavel)
        return estava_pago

    # ------------------------------------------------------------ painel da loja
    @property
    def novo(self):
        """CA17.6: pedido pago que a loja ainda não abriu."""
        return self.status == StatusPedido.PAGO and not self.visto_pelo_admin

    @staticmethod
    def para_painel(status=None, limite=100):
        consulta = db.select(Pedido).order_by(Pedido.criado_em.desc(), Pedido.id.desc()).limit(limite)
        if status:
            consulta = consulta.where(Pedido.status == status)
        return db.session.scalars(consulta).all()

    @staticmethod
    def contagem_por_status():
        linhas = db.session.execute(db.select(Pedido.status, func.count()).group_by(Pedido.status)).all()
        return {status: total for status, total in linhas}

    @staticmethod
    def resumo_novos():
        """Usado pela atualização automática do painel: quantos novos e o número do mais recente."""
        novos = db.session.scalar(db.select(func.count()).select_from(Pedido).where(
            Pedido.status == StatusPedido.PAGO, Pedido.visto_pelo_admin.is_(False)))
        ultimo = db.session.scalar(db.select(func.max(Pedido.id)))
        return {"novos": novos or 0, "ultimo_id": ultimo or 0}

    @staticmethod
    def do_cliente(pedido_id, usuario):
        """Pedido do próprio cliente, ou None (CA12.4: não mostra pedido de outra pessoa)."""
        pedido = db.session.get(Pedido, pedido_id)
        if pedido is None or pedido.usuario_id != usuario.id:
            return None
        return pedido


class ItemPedido(db.Model):
    __tablename__ = "itens_pedido"

    id: Mapped[int] = mapped_column(primary_key=True)
    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedidos.id"))
    cupcake_id: Mapped[int] = mapped_column(ForeignKey("cupcakes.id"))
    quantidade: Mapped[int]
    preco_unitario: Mapped[Decimal]
    recheio_id: Mapped[int | None] = mapped_column(ForeignKey("opcoes_personalizacao.id"))
    cobertura_id: Mapped[int | None] = mapped_column(ForeignKey("opcoes_personalizacao.id"))
    mensagem: Mapped[str | None]

    pedido: Mapped[Pedido] = relationship(back_populates="itens")
    cupcake: Mapped[Cupcake] = relationship()
    recheio: Mapped[OpcaoPersonalizacao | None] = relationship(foreign_keys=[recheio_id])
    cobertura: Mapped[OpcaoPersonalizacao | None] = relationship(foreign_keys=[cobertura_id])

    @property
    def subtotal(self):
        return self.preco_unitario * self.quantidade

    @property
    def personalizacao(self):
        partes = [o.nome for o in (self.recheio, self.cobertura) if o]
        if self.mensagem:
            partes.append(f"“{self.mensagem}”")
        return " · ".join(partes)


class Pagamento(db.Model):
    __tablename__ = "pagamentos"

    id: Mapped[int] = mapped_column(primary_key=True)
    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedidos.id"))
    metodo: Mapped[MetodoPagamento] = mapped_column(Enum(MetodoPagamento, name="metodo_pagamento", create_type=False))
    status: Mapped[StatusPagamento] = mapped_column(Enum(StatusPagamento, name="status_pagamento", create_type=False),
                                                    default=StatusPagamento.PENDENTE)
    valor: Mapped[Decimal]
    pix_codigo: Mapped[str | None]
    pix_expira_em: Mapped[datetime | None]
    cartao_bandeira: Mapped[str | None]
    cartao_final: Mapped[str | None]
    motivo_recusa: Mapped[str | None]
    criado_em: Mapped[datetime] = mapped_column(server_default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    pedido: Mapped[Pedido] = relationship(back_populates="pagamentos")

    def pix_expirado(self, momento=None):
        return self.pix_expira_em is not None and (momento or agora()) > self.pix_expira_em

    def descricao(self):
        if self.metodo == MetodoPagamento.CARTAO:
            return f"Cartão {self.cartao_bandeira} final {self.cartao_final}"
        return "Pix"


class HistoricoStatus(db.Model):
    __tablename__ = "historico_status"

    id: Mapped[int] = mapped_column(primary_key=True)
    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedidos.id"))
    status: Mapped[StatusPedido] = mapped_column(Enum(StatusPedido, name="status_pedido", create_type=False))
    responsavel_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    registrado_em: Mapped[datetime] = mapped_column(server_default=func.now())

    pedido: Mapped[Pedido] = relationship(back_populates="historico")
    responsavel: Mapped[Usuario | None] = relationship()

    @property
    def texto(self):
        return STATUS_INFO[self.status][0]
