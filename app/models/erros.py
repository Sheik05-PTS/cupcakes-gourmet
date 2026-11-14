"""Erros de regra de negócio, com a mensagem que será mostrada ao usuário."""


class RegraDeNegocio(Exception):
    """Violação de uma regra de negócio. A mensagem já vem pronta para a tela."""

    def __init__(self, mensagem, campo=None):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.campo = campo


class EstoqueInsuficiente(RegraDeNegocio):
    pass
