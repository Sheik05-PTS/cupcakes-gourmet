"""Serviços que coordenam várias entidades: criar o pedido e processar o pagamento."""
from datetime import date

from sqlalchemy.orm import lazyload

from ..extensions import db
from .carrinho import Carrinho
from .catalogo import Cupcake
from .entrega import AreaEntrega
from .erros import EstoqueInsuficiente, RegraDeNegocio
from .gateway import DadosCartao, GatewayPagamento
from .pedido import ItemPedido, MetodoPagamento, Pagamento, Pedido, StatusPagamento, StatusPedido, agora
from .promocao import validar_cupom


class ServicoPedido:
    """UC10 — Finalizar pedido."""

    @staticmethod
    def resumo(carrinho, endereco, codigo_cupom, hoje):
        """Valores do checkout: subtotal, desconto, frete e total (RN07, RN08, RN09)."""
        linhas = carrinho.linhas()
        subtotal = Carrinho.subtotal(linhas)
        area = AreaEntrega.para_cep(endereco.cep) if endereco else None
        cupom = validar_cupom(codigo_cupom, subtotal, hoje) if codigo_cupom else None
        desconto = cupom.calcular_desconto(subtotal) if cupom else 0
        frete = area.valor_frete if area else 0
        return {"linhas": linhas, "subtotal": subtotal, "area": area, "cupom": cupom,
                "desconto": desconto, "frete": frete, "total": subtotal - desconto + frete}

    @staticmethod
    def criar_pedido(usuario, carrinho, endereco, codigo_cupom, hoje: date):
        if carrinho.vazio():
            raise RegraDeNegocio("Seu carrinho está vazio.")
        if endereco is None or endereco.usuario_id != usuario.id:
            raise RegraDeNegocio("Escolha o endereço de entrega.")
        resumo = ServicoPedido.resumo(carrinho, endereco, codigo_cupom, hoje)
        for linha in resumo["linhas"]:  # FE2 do UC10: confere de novo antes de criar
            if linha.indisponivel:
                raise EstoqueInsuficiente(f"{linha.cupcake.nome} ficou indisponível. Ajuste seu carrinho para continuar.")
        area = resumo["area"]
        pedido = Pedido(
            cliente=usuario, cupom=resumo["cupom"], subtotal=resumo["subtotal"], desconto=resumo["desconto"],
            frete=area.valor_frete, total=resumo["total"], prazo_minutos=area.prazo_minutos,
            entrega_cep=endereco.cep, entrega_logradouro=endereco.logradouro, entrega_numero=endereco.numero,
            entrega_complemento=endereco.complemento, entrega_bairro=endereco.bairro,
            entrega_cidade=endereco.cidade, entrega_uf=endereco.uf)
        for linha in resumo["linhas"]:  # RN10: preço congelado no pedido
            pedido.itens.append(ItemPedido(cupcake=linha.cupcake, quantidade=linha.quantidade,
                                           preco_unitario=linha.preco_unitario, recheio=linha.recheio,
                                           cobertura=linha.cobertura, mensagem=linha.mensagem or None))
        pedido.registrar(StatusPedido.AGUARDANDO_PAGAMENTO)
        db.session.add(pedido)
        db.session.commit()
        return pedido


class ServicoPagamento:
    """UC12 — Pagar pedido (simulado)."""

    def __init__(self, gateway: GatewayPagamento):
        self.gateway = gateway

    @staticmethod
    def _exigir_aguardando(pedido):
        if pedido.status != StatusPedido.AGUARDANDO_PAGAMENTO:
            raise RegraDeNegocio("Este pedido já foi pago ou cancelado.")

    def pagar_com_cartao(self, pedido, dados: DadosCartao, hoje):
        self._exigir_aguardando(pedido)
        dados.validar(hoje)
        pagamento = Pagamento(pedido=pedido, metodo=MetodoPagamento.CARTAO, valor=pedido.total,
                              cartao_bandeira=dados.bandeira(), cartao_final=dados.final())  # RN12
        db.session.add(pagamento)
        db.session.commit()
        resultado = self.gateway.cobrar_cartao(dados, pedido.total)
        if not resultado.aprovado:
            self._recusar(pagamento, resultado.motivo)
            raise RegraDeNegocio("Pagamento recusado. Tente outro cartão ou pague com Pix.")
        self._aprovar(pagamento)
        return pagamento

    def gerar_pix(self, pedido):
        self._exigir_aguardando(pedido)
        resultado = self.gateway.gerar_pix(pedido.total, pedido.numero.lstrip("#"))
        pagamento = Pagamento(pedido=pedido, metodo=MetodoPagamento.PIX, valor=pedido.total,
                              pix_codigo=resultado.codigo, pix_expira_em=resultado.expira_em)
        db.session.add(pagamento)
        db.session.commit()
        return pagamento

    def confirmar_pix(self, pagamento, momento=None):
        self._exigir_aguardando(pagamento.pedido)
        if pagamento.status != StatusPagamento.PENDENTE:
            raise RegraDeNegocio("Este código Pix já foi usado. Gere um novo código para pagar.")
        if pagamento.pix_expirado(momento):
            pagamento.status = StatusPagamento.EXPIRADO
            db.session.commit()
            raise RegraDeNegocio("Código Pix expirado. Gere um novo código para pagar.")
        resultado = self.gateway.confirmar_pix(pagamento.pix_codigo)
        if not resultado.aprovado:
            self._recusar(pagamento, resultado.motivo)
            raise RegraDeNegocio("Pagamento não confirmado. Tente de novo.")
        self._aprovar(pagamento)
        return pagamento

    @staticmethod
    def _recusar(pagamento, motivo):
        pagamento.status = StatusPagamento.RECUSADO
        pagamento.motivo_recusa = (motivo or "Recusado")[:120]
        db.session.commit()

    def _aprovar(self, pagamento):
        """Uma única transação: trava os cupcakes, confere e baixa o estoque, aprova (RN13, RNF07)."""
        pedido = pagamento.pedido
        ids = sorted({item.cupcake_id for item in pedido.itens})
        try:
            cupcakes = {c.id: c for c in db.session.scalars(
                db.select(Cupcake).options(lazyload(Cupcake.sabor)).where(Cupcake.id.in_(ids))
                .order_by(Cupcake.id).with_for_update(of=Cupcake).execution_options(populate_existing=True))}
            for item in pedido.itens:
                cupcake = cupcakes[item.cupcake_id]
                if not cupcake.ativo:
                    raise EstoqueInsuficiente(f"{cupcake.nome} ficou indisponível. Ajuste seu carrinho para continuar.")
                cupcake.baixar_estoque(item.quantidade)
            pagamento.status = StatusPagamento.APROVADO
            pedido.registrar(StatusPedido.PAGO)
            db.session.commit()
        except EstoqueInsuficiente as erro:
            db.session.rollback()
            pagamento = db.session.get(Pagamento, pagamento.id)
            self._recusar(pagamento, "Estoque insuficiente no momento da aprovação.")
            raise erro


def pix_restante_segundos(pagamento):
    if not pagamento or not pagamento.pix_expira_em:
        return 0
    return max(0, int((pagamento.pix_expira_em - agora()).total_seconds()))
