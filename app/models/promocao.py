"""Cupons de desconto (US07, RN07)."""
import enum
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column

from ..extensions import db
from .erros import RegraDeNegocio

CENTAVO = Decimal("0.01")


class TipoCupom(enum.Enum):
    PERCENTUAL = "PERCENTUAL"
    VALOR_FIXO = "VALOR_FIXO"


class Cupom(db.Model):
    __tablename__ = "cupons"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str]
    tipo: Mapped[TipoCupom] = mapped_column(Enum(TipoCupom, name="tipo_cupom", create_type=False))
    valor: Mapped[Decimal]
    valor_minimo: Mapped[Decimal]
    valido_de: Mapped[date]
    valido_ate: Mapped[date]
    ativo: Mapped[bool]

    @staticmethod
    def por_codigo(codigo):
        codigo = (codigo or "").strip().upper()
        if not codigo:
            return None
        return db.session.scalar(db.select(Cupom).where(Cupom.codigo == codigo))

    def validar(self, subtotal, hoje):
        """CA07.2 e CA07.3."""
        if not self.ativo or not (self.valido_de <= hoje <= self.valido_ate):
            raise RegraDeNegocio("Cupom inválido ou expirado.", campo="cupom")
        if subtotal < self.valor_minimo:
            minimo = f"{self.valor_minimo:.2f}".replace(".", ",")
            raise RegraDeNegocio(f"Este cupom vale para pedidos a partir de R$ {minimo}.", campo="cupom")

    def calcular_desconto(self, subtotal):
        """Desconto sobre os produtos, nunca maior que o subtotal e sem incidir no frete (RN07, CA07.5)."""
        if self.tipo == TipoCupom.PERCENTUAL:
            desconto = (subtotal * self.valor / 100).quantize(CENTAVO, rounding=ROUND_HALF_UP)
        else:
            desconto = self.valor
        return min(desconto, subtotal)

    def descricao(self):
        if self.tipo == TipoCupom.PERCENTUAL:
            percentual = f"{self.valor.normalize():f}".replace(".", ",")
            return f"{percentual}% de desconto nos produtos"
        return f"R$ {self.valor:.2f} de desconto nos produtos".replace(".", ",")


def validar_cupom(codigo, subtotal, hoje):
    """Busca e valida o cupom digitado. Levanta RegraDeNegocio com a mensagem certa."""
    cupom = Cupom.por_codigo(codigo)
    if cupom is None:
        raise RegraDeNegocio("Cupom inválido ou expirado.", campo="cupom")
    cupom.validar(subtotal, hoje)
    return cupom
