"""Carrinho de compras guardado na sessão do usuário (não vai para o banco).

Regras: RN03 (1 a 20 por item, sem passar do estoque), RN04 (personalização só em
cupcakes personalizáveis; mensagem até 60 caracteres), RN05 (mesmo cupcake com
personalização diferente ocupa outra linha) e RN06 (o carrinho sobrevive ao login).
"""
import hashlib
from dataclasses import dataclass
from decimal import Decimal

from ..extensions import db
from .catalogo import Cupcake, OpcaoPersonalizacao, TipoOpcao, validar_quantidade
from .erros import RegraDeNegocio

TAMANHO_MENSAGEM = 60


@dataclass
class LinhaCarrinho:
    chave: str
    cupcake: Cupcake
    quantidade: int
    recheio: OpcaoPersonalizacao | None
    cobertura: OpcaoPersonalizacao | None
    mensagem: str

    @property
    def preco_unitario(self):
        acrescimos = sum((o.acrescimo for o in (self.recheio, self.cobertura) if o), Decimal("0"))
        return self.cupcake.preco + acrescimos

    @property
    def subtotal(self):
        return self.preco_unitario * self.quantidade

    @property
    def personalizacao(self):
        partes = [o.nome for o in (self.recheio, self.cobertura) if o]
        if self.mensagem:
            partes.append(f"“{self.mensagem}”")
        return " · ".join(partes)

    @property
    def indisponivel(self):
        return not self.cupcake.disponivel() or self.quantidade > self.cupcake.estoque


class Carrinho:
    def __init__(self, itens=None, maximo_por_item=20):
        self.itens = [dict(i) for i in (itens or [])]
        self.maximo = maximo_por_item

    # ---------------------------------------------------------------- sessão
    @classmethod
    def da_sessao(cls, sessao, maximo_por_item=20):
        return cls(sessao.get("carrinho"), maximo_por_item)

    def salvar(self, sessao):
        sessao["carrinho"] = self.itens
        sessao.modified = True

    # ---------------------------------------------------------------- regras
    @staticmethod
    def chave_de(cupcake_id, recheio_id, cobertura_id, mensagem):
        """Identifica a linha: mesmo cupcake com a mesma personalização soma na mesma linha (RN05)."""
        resumo = hashlib.sha1(mensagem.encode("utf8")).hexdigest()[:8] if mensagem else "0"
        return f"{cupcake_id}-{recheio_id or 0}-{cobertura_id or 0}-{resumo}"

    def _opcao(self, opcao_id, tipo):
        if not opcao_id:
            return None
        opcao = db.session.get(OpcaoPersonalizacao, int(opcao_id))
        if opcao is None or opcao.tipo != tipo or not opcao.ativo:
            nome = "recheio" if tipo == TipoOpcao.RECHEIO else "cobertura"
            raise RegraDeNegocio(f"Escolha um {nome} da lista.", campo=nome)
        return opcao

    def _quantidade_no_carrinho(self, cupcake_id, exceto_chave=None):
        return sum(i["quantidade"] for i in self.itens if i["cupcake_id"] == cupcake_id and i["chave"] != exceto_chave)

    def _conferir_limites(self, cupcake, nova_quantidade_linha, exceto_chave=None):
        if nova_quantidade_linha > self.maximo:
            raise RegraDeNegocio(f"A quantidade deve ser de 1 a {self.maximo}.", campo="quantidade")
        total_do_cupcake = self._quantidade_no_carrinho(cupcake.id, exceto_chave) + nova_quantidade_linha
        if total_do_cupcake > cupcake.estoque:
            raise RegraDeNegocio(f"Só temos {cupcake.estoque} unidades disponíveis.", campo="quantidade")

    def adicionar(self, cupcake, quantidade, recheio_id=None, cobertura_id=None, mensagem=""):
        if cupcake is None or not cupcake.disponivel():
            raise RegraDeNegocio("Este cupcake está esgotado no momento.")
        quantidade = validar_quantidade(quantidade, self.maximo)
        mensagem = (mensagem or "").strip()
        if cupcake.personalizavel:
            recheio = self._opcao(recheio_id, TipoOpcao.RECHEIO)
            cobertura = self._opcao(cobertura_id, TipoOpcao.COBERTURA)
            if len(mensagem) > TAMANHO_MENSAGEM:
                raise RegraDeNegocio(f"A mensagem pode ter até {TAMANHO_MENSAGEM} caracteres.", campo="mensagem")
        else:
            recheio = cobertura = None
            mensagem = ""
        chave = self.chave_de(cupcake.id, recheio and recheio.id, cobertura and cobertura.id, mensagem)
        existente = next((i for i in self.itens if i["chave"] == chave), None)
        nova_qtd = quantidade + (existente["quantidade"] if existente else 0)
        self._conferir_limites(cupcake, nova_qtd, exceto_chave=chave)
        if existente:
            existente["quantidade"] = nova_qtd  # CA04.3
        else:
            self.itens.append({"chave": chave, "cupcake_id": cupcake.id, "quantidade": quantidade,
                               "recheio_id": recheio and recheio.id, "cobertura_id": cobertura and cobertura.id,
                               "mensagem": mensagem})
        return chave

    def alterar_quantidade(self, chave, quantidade):
        item = self._item(chave)
        quantidade = validar_quantidade(quantidade, self.maximo)
        cupcake = db.session.get(Cupcake, item["cupcake_id"])
        self._conferir_limites(cupcake, quantidade, exceto_chave=chave)
        item["quantidade"] = quantidade

    def remover(self, chave):
        item = self._item(chave)
        self.itens.remove(item)
        return item

    def restaurar(self, item):
        if item and not any(i["chave"] == item["chave"] for i in self.itens):
            self.itens.append(item)

    def limpar(self):
        self.itens = []

    def _item(self, chave):
        item = next((i for i in self.itens if i["chave"] == chave), None)
        if item is None:
            raise RegraDeNegocio("Este item não está mais no carrinho.")
        return item

    # ---------------------------------------------------------------- leitura
    def linhas(self):
        linhas = []
        for item in self.itens:
            cupcake = db.session.get(Cupcake, item["cupcake_id"])
            if cupcake is None:
                continue
            linhas.append(LinhaCarrinho(
                chave=item["chave"], cupcake=cupcake, quantidade=item["quantidade"],
                recheio=db.session.get(OpcaoPersonalizacao, item["recheio_id"]) if item.get("recheio_id") else None,
                cobertura=db.session.get(OpcaoPersonalizacao, item["cobertura_id"]) if item.get("cobertura_id") else None,
                mensagem=item.get("mensagem") or ""))
        return linhas

    def total_itens(self):
        return sum(i["quantidade"] for i in self.itens)

    def vazio(self):
        return not self.itens

    @staticmethod
    def subtotal(linhas):
        return sum((linha.subtotal for linha in linhas), Decimal("0"))
