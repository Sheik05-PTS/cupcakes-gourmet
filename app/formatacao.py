"""Filtros de template para exibir valores no padrão brasileiro."""
from decimal import Decimal


def moeda(valor):
    """Decimal('1234.5') -> 'R$ 1.234,50'."""
    if valor is None:
        return ""
    texto = f"{Decimal(valor):,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


def data_hora(valor):
    return valor.strftime("%d/%m/%Y %H:%M") if valor else ""


def numero_pedido(pedido_id):
    return f"#{pedido_id:06d}"


def cep(valor):
    valor = valor or ""
    return f"{valor[:5]}-{valor[5:]}" if len(valor) == 8 else valor


def registrar(app):
    app.add_template_filter(moeda)
    app.add_template_filter(data_hora)
    app.add_template_filter(numero_pedido)
    app.add_template_filter(cep)
