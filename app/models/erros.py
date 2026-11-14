"""Erros de regra de negócio, com a mensagem que será mostrada ao usuário."""


class RegraDeNegocio(Exception):
    """Violação de uma regra de negócio. A mensagem já vem pronta para a tela."""

    def __init__(self, mensagem, campo=None):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.campo = campo


class EstoqueInsuficiente(RegraDeNegocio):
    pass


class ErrosDeValidacao(RegraDeNegocio):
    """Vários campos de um formulário com erro ao mesmo tempo: {campo: mensagem}."""

    def __init__(self, erros):
        super().__init__("Confira os campos destacados.")
        self.erros = erros


class Validador:
    """Junta os erros de cada campo e levanta tudo de uma vez no final."""

    def __init__(self):
        self.erros = {}

    def exigir(self, condicao, campo, mensagem):
        if not condicao and campo not in self.erros:
            self.erros[campo] = mensagem
        return condicao

    def conferir(self):
        if self.erros:
            raise ErrosDeValidacao(self.erros)
