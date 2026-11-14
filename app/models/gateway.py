"""Gateway de pagamento. No MVP, um gateway SIMULADO: nenhuma cobrança real é feita (RN11, RN21).

A interface GatewayPagamento permite trocar o simulado por um gateway real sem mexer
em controllers nem em telas.
"""
import re
import secrets
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from .erros import Validador


@dataclass
class ResultadoPagamento:
    aprovado: bool
    motivo: str = ""


@dataclass
class ResultadoPix:
    codigo: str
    expira_em: datetime


@dataclass
class DadosCartao:
    """Dados digitados. Vivem só durante a requisição: nunca são gravados (RN12)."""
    numero: str
    nome: str
    validade: str
    cvv: str

    @property
    def digitos(self):
        return re.sub(r"\D", "", self.numero or "")

    def numero_valido(self):
        """Algoritmo de Luhn."""
        d = self.digitos
        if not 13 <= len(d) <= 19:
            return False
        soma = 0
        for i, c in enumerate(reversed(d)):
            n = int(c)
            if i % 2 == 1:
                n *= 2
                if n > 9:
                    n -= 9
            soma += n
        return soma % 10 == 0

    def validade_futura(self, hoje):
        m = re.fullmatch(r"\s*(\d{2})\s*/\s*(\d{2}|\d{4})\s*", self.validade or "")
        if not m:
            return False
        mes, ano = int(m.group(1)), int(m.group(2))
        ano = ano + 2000 if ano < 100 else ano
        return 1 <= mes <= 12 and (ano, mes) >= (hoje.year, hoje.month)

    def bandeira(self):
        d = self.digitos
        if re.match(r"^(4011|4312|4389|4514|4576|5041|5066|5067|509|6277|6362|6363|650|6516|6550)", d):
            return "Elo"
        if d.startswith("4"):
            return "Visa"
        if re.match(r"^(5[1-5]|2[2-7])", d):
            return "Mastercard"
        if re.match(r"^3[47]", d):
            return "Amex"
        return "Cartão"

    def final(self):
        return self.digitos[-4:]

    def validar(self, hoje):
        """CA08.6: mensagem em cada campo com erro."""
        v = Validador()
        v.exigir(self.numero_valido(), "numero", "Número de cartão inválido.")
        v.exigir(len((self.nome or "").strip()) >= 3, "nome", "Informe o nome impresso no cartão.")
        if v.exigir(re.fullmatch(r"\s*\d{2}\s*/\s*(\d{2}|\d{4})\s*", self.validade or ""), "validade", "Use o formato MM/AA."):
            v.exigir(self.validade_futura(hoje), "validade", "Cartão vencido.")
        v.exigir(re.fullmatch(r"\d{3,4}", (self.cvv or "").strip()), "cvv", "O CVV tem 3 ou 4 dígitos.")
        v.conferir()


class GatewayPagamento(ABC):
    @abstractmethod
    def cobrar_cartao(self, dados: DadosCartao, valor) -> ResultadoPagamento: ...

    @abstractmethod
    def gerar_pix(self, valor, referencia) -> ResultadoPix: ...

    @abstractmethod
    def confirmar_pix(self, codigo) -> ResultadoPagamento: ...


class GatewaySimulado(GatewayPagamento):
    """Imita um gateway: cartões terminados em 0002 são recusados; o resto é aprovado (RN11)."""

    def __init__(self, validade_pix_minutos=15):
        self.validade_pix = timedelta(minutes=validade_pix_minutos)

    def cobrar_cartao(self, dados, valor):
        if dados.final() == "0002":
            return ResultadoPagamento(False, "Cartão recusado pelo emissor (simulação).")
        return ResultadoPagamento(True)

    def gerar_pix(self, valor, referencia):
        valor_txt = f"{valor:.2f}"
        codigo = ("00020126580014BR.GOV.BCB.PIX0136demo-cupcakes-gourmet-"
                  f"{referencia}52040000530398654{len(valor_txt):02d}{valor_txt}5802BR"
                  f"5917CUPCAKES GOURMET6009SAO PAULO62070503***6304{secrets.token_hex(2).upper()}")
        return ResultadoPix(codigo, datetime.now(timezone.utc) + self.validade_pix)

    def confirmar_pix(self, codigo):
        return ResultadoPagamento(True)
