"""Entrega: faixas de CEP atendidas, com frete e prazo (RN08)."""
import re
from decimal import Decimal

from sqlalchemy import Integer, cast
from sqlalchemy.orm import Mapped, mapped_column

from ..extensions import db
from .erros import RegraDeNegocio

MSG_CEP_INVALIDO = "Informe um CEP com 8 dígitos."
MSG_FORA_DA_AREA = "Ainda não entregamos neste CEP."


def normalizar_cep(cep):
    """Mantém só os dígitos. Levanta RegraDeNegocio se não sobrarem exatamente 8 (RN18)."""
    digitos = re.sub(r"\D", "", cep or "")
    if len(digitos) != 8:
        raise RegraDeNegocio(MSG_CEP_INVALIDO, campo="cep")
    return digitos


class AreaEntrega(db.Model):
    __tablename__ = "areas_entrega"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str]
    cep_inicial: Mapped[str]
    cep_final: Mapped[str]
    valor_frete: Mapped[Decimal]
    prazo_minutos: Mapped[int]

    def atende(self, cep):
        return int(self.cep_inicial) <= int(cep) <= int(self.cep_final)

    @staticmethod
    def para_cep(cep):
        """Área que atende o CEP. Levanta RegraDeNegocio se o CEP for inválido ou estiver fora da área."""
        cep = normalizar_cep(cep)
        numero = int(cep)
        consulta = db.select(AreaEntrega).where(
            cast(AreaEntrega.cep_inicial, Integer) <= numero, cast(AreaEntrega.cep_final, Integer) >= numero)
        area = db.session.scalar(consulta)
        if area is None:
            raise RegraDeNegocio(MSG_FORA_DA_AREA, campo="cep")
        return area

    def prazo_texto(self):
        if self.prazo_minutos < 120:
            return f"até {self.prazo_minutos} minutos"
        horas = self.prazo_minutos / 60
        return f"até {horas:g} horas".replace(".", ",")
