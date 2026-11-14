"""Gera o formulário de teste da solução (Situação 3) em Word.

Uso: python gerar_formulario_teste.py <saida.docx> [link_do_app]
Requer: python-docx
"""
import sys

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_ROW_HEIGHT_RULE, WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

SAIDA = sys.argv[1]
LINK_APP = sys.argv[2] if len(sys.argv) > 2 else None
LINK_REPO = "https://github.com/Sheik05-PTS/cupcakes-gourmet"

FRAMBOESA = RGBColor(0x9C, 0x2F, 0x5B)
CINZA = RGBColor(0x5B, 0x62, 0x75)
FUNDO_TITULO = "F7DBE4"
FUNDO_CAMPO = "FBF1F4"
FUNDO_AVISO = "FFF2D1"

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
sec.orientation = WD_ORIENT.PORTRAIT
sec.left_margin = sec.right_margin = Cm(2)
sec.top_margin = Cm(1.8)
sec.bottom_margin = Cm(1.8)

normal = doc.styles["Normal"]
normal.font.name = "Arial"
normal.font.size = Pt(10.5)
normal.element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
normal.paragraph_format.space_after = Pt(4)
normal.paragraph_format.line_spacing = 1.15

for nome, tamanho in (("Heading 1", 13), ("Heading 2", 11.5)):
    est = doc.styles[nome]
    est.font.name = "Arial"
    est.font.size = Pt(tamanho)
    est.font.bold = True
    est.font.color.rgb = FRAMBOESA
    est.element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
    est.paragraph_format.space_before = Pt(12)
    est.paragraph_format.space_after = Pt(5)
    est.paragraph_format.keep_with_next = True

LARGURA = 17.0  # cm úteis


def sombrear(celula, cor):
    tc_pr = celula._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), cor)
    tc_pr.append(shd)


def bordas(tabela, cor="D9CDD2"):
    tbl_pr = tabela._tbl.tblPr
    b = OxmlElement("w:tblBorders")
    for lado in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement(f"w:{lado}")
        e.set(qn("w:val"), "single")
        e.set(qn("w:sz"), "6")
        e.set(qn("w:color"), cor)
        b.append(e)
    tbl_pr.append(b)


def nao_quebrar_linha(linha):
    tr_pr = linha._tr.get_or_add_trPr()
    e = OxmlElement("w:cantSplit")
    tr_pr.append(e)


def repetir_cabecalho(linha):
    tr_pr = linha._tr.get_or_add_trPr()
    e = OxmlElement("w:tblHeader")
    tr_pr.append(e)


def tabela(colunas_cm, linhas, cabecalho=True, altura_cm=None, fundo_primeira_coluna=None):
    t = doc.add_table(rows=0, cols=len(colunas_cm))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    bordas(t)
    for i, valores in enumerate(linhas):
        linha = t.add_row()
        nao_quebrar_linha(linha)
        if altura_cm and not (cabecalho and i == 0):
            linha.height = Cm(altura_cm)
            linha.height_rule = WD_ROW_HEIGHT_RULE.AT_LEAST
        for j, valor in enumerate(valores):
            c = linha.cells[j]
            c.width = Cm(colunas_cm[j])
            c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER if (cabecalho and i == 0) else WD_CELL_VERTICAL_ALIGNMENT.TOP
            p = c.paragraphs[0]
            p.paragraph_format.space_after = Pt(1)
            run = p.add_run(valor)
            run.font.size = Pt(9.5)
            if cabecalho and i == 0:
                run.bold = True
                sombrear(c, FUNDO_TITULO)
            elif fundo_primeira_coluna and j == 0:
                run.bold = True
                sombrear(c, fundo_primeira_coluna)
        if cabecalho and i == 0:
            repetir_cabecalho(linha)
    for j, w in enumerate(colunas_cm):
        t.columns[j].width = Cm(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def caixa(texto_partes, cor=FUNDO_AVISO):
    """Caixa de destaque (tabela de uma célula)."""
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    bordas(t, "E8D9A8" if cor == FUNDO_AVISO else "D9CDD2")
    c = t.rows[0].cells[0]
    c.width = Cm(LARGURA)
    sombrear(c, cor)
    p = c.paragraphs[0]
    for texto, negrito in texto_partes:
        r = p.add_run(texto)
        r.bold = negrito
        r.font.size = Pt(9.8)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def paragrafo(texto, negrito=False, cor=None, tamanho=None, alinhamento=None, depois=None):
    p = doc.add_paragraph()
    r = p.add_run(texto)
    r.bold = negrito
    if cor:
        r.font.color.rgb = cor
    if tamanho:
        r.font.size = Pt(tamanho)
    if alinhamento:
        p.alignment = alinhamento
    if depois is not None:
        p.paragraph_format.space_after = Pt(depois)
    p.paragraph_format.keep_with_next = True
    return p


def linhas_resposta(qtd):
    """Caixa em branco para resposta livre (cerca de 0,8 cm por linha)."""
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    bordas(t)
    linha = t.rows[0]
    linha.height = Cm(0.8 * qtd)
    linha.height_rule = WD_ROW_HEIGHT_RULE.AT_LEAST
    nao_quebrar_linha(linha)
    linha.cells[0].width = Cm(LARGURA)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


# --------------------------------------------------------------- cabeçalho
p = paragrafo("PROJETO INTEGRADOR II · ENGENHARIA DE SOFTWARE", negrito=True, cor=FRAMBOESA, tamanho=8.5, depois=0)
p = paragrafo("Cupcakes Gourmet — Formulário de Teste da Solução", negrito=True, tamanho=17, depois=0)
p = paragrafo("Autor do projeto: Petterson Teixeira · Cruzeiro do Sul Virtual", cor=CINZA, tamanho=9.5, depois=6)
p_pr = p._p.get_or_add_pPr()
borda = OxmlElement("w:pBdr")
inf = OxmlElement("w:bottom")
inf.set(qn("w:val"), "single"); inf.set(qn("w:sz"), "18"); inf.set(qn("w:color"), "9C2F5B"); inf.set(qn("w:space"), "4")
borda.append(inf); p_pr.append(borda)

paragrafo(
    "Obrigado por aceitar testar o app! Ele foi feito para uma loja de cupcakes gourmet vender pelo celular. "
    "Use o app como se fosse um cliente de verdade e depois como funcionário da loja, e registre aqui o que "
    "funcionou, o que não funcionou e o que você não conseguiu testar. Aponte os problemas sem receio: "
    "é para isso que o teste serve. Tempo estimado: 15 a 20 minutos."
)

# --------------------------------------------------------------- acesso
doc.add_heading("1. Como acessar", level=1)
tabela([4.2, 12.8], [
    ["Endereço do app", LINK_APP or "[o link será enviado junto com este formulário]"],
    ["Código e documentação", LINK_REPO],
    ["Onde testar", "De preferência no celular (navegador Chrome ou Safari). Também funciona no computador."],
], cabecalho=False, fundo_primeira_coluna=FUNDO_CAMPO)
caixa([("Ambiente de demonstração: ", True),
       ("nenhum pagamento é real e nenhum cupcake será entregue. Não use dados verdadeiros de cartão. "
        "Se o app demorar uns 30 segundos para abrir na primeira vez, é normal: a hospedagem gratuita "
        "\"acorda\" quando alguém acessa.", False)])

doc.add_heading("Dados para usar no teste", level=2)
tabela([4.2, 12.8], [
    ["Conta de cliente", "Crie a sua no próprio app. Pode usar um e-mail inventado (ex.: seunome@teste.com)."],
    ["Conta da loja", "E-mail: loja.teste@example.com · Senha: Cupcake2026"],
    ["Cartão aprovado", "4111 1111 1111 1111 · validade futura qualquer (ex.: 12/28) · CVV 123"],
    ["Cartão recusado", "4000 0000 0000 0002 (serve para ver a mensagem de pagamento recusado)"],
    ["Pix", "Escolha Pix e toque em \"Simular pagamento\" (o código é fictício e vale 15 minutos)"],
    ["Cupons", "DOCE10 (10% de desconto acima de R$ 30) · BEMVINDO5 (R$ 5 acima de R$ 40)"],
    ["CEP atendido", "01310-100 (Av. Paulista) · outros: 01000-000 a 01599-999, 04000-000 a 04299-999, 05000-000 a 05099-999"],
    ["CEP fora da área", "20040-020 (Rio de Janeiro), para ver a mensagem de área não atendida"],
], cabecalho=False, fundo_primeira_coluna=FUNDO_CAMPO)

# --------------------------------------------------------------- identificação
doc.add_heading("2. Identificação", level=1)
tabela([5.5, 11.5], [
    ["Nome de quem testou", ""],
    ["Vínculo (colega do curso, profissional da área…)", ""],
    ["Data do teste", "____ / ____ / ________"],
    ["Aparelho e navegador usados", "Ex.: iPhone 13 / Safari · Samsung A54 / Chrome · notebook / Chrome"],
    ["Posso citar seu nome no trabalho?", "(   ) Sim, nome completo     (   ) Só as iniciais     (   ) Não"],
], cabecalho=False, altura_cm=0.75, fundo_primeira_coluna=FUNDO_CAMPO)

# --------------------------------------------------------------- roteiro
doc.add_heading("3. Roteiro de testes", level=1)
paragrafo("Siga os itens na ordem e marque um X no resultado. Use a última coluna para qualquer comentário rápido.",
          cor=CINZA, tamanho=9.5)
roteiro = [
    ("Como cliente", None),
    ("1", "Abrir a vitrine e ver os detalhes de um cupcake (foto, ingredientes, preço)"),
    ("2", "Filtrar cupcakes por sabor, preço, ocasião e restrição alimentar"),
    ("3", "Adicionar cupcakes ao carrinho, mudar a quantidade e remover um item"),
    ("4", "Personalizar um cupcake (recheio, cobertura e mensagem) e ver o preço mudar"),
    ("5", "Calcular o frete pelo CEP no carrinho, inclusive com um CEP fora da área"),
    ("6", "Criar sua conta e entrar com ela"),
    ("7", "Cadastrar um endereço de entrega"),
    ("8", "Aplicar o cupom DOCE10 e ver o desconto"),
    ("9", "Pagar com o cartão aprovado e ver a tela de pedido confirmado"),
    ("10", "Tentar pagar com o cartão recusado e ver a mensagem de erro"),
    ("11", "Pagar com Pix usando \"Simular pagamento\""),
    ("12", "Acompanhar o pedido em \"Meus pedidos\""),
    ("Como funcionário da loja (conta da loja)", None),
    ("13", "Entrar no painel e encontrar o pedido que você fez"),
    ("14", "Avançar o status do pedido e conferir a mudança na tela do cliente"),
    ("15", "Cancelar um pedido"),
    ("16", "Cadastrar ou editar um cupcake"),
    ("17", "Mudar o estoque ou desativar um cupcake e conferir na vitrine"),
    ("Geral", None),
    ("18", "Usar no celular: as telas cabem, os textos são legíveis e os botões são fáceis de tocar"),
]
t = doc.add_table(rows=1, cols=6)
t.alignment = WD_TABLE_ALIGNMENT.CENTER
t.autofit = False
bordas(t)
larguras = [0.8, 7.0, 2.0, 2.0, 1.6, 3.6]
cab = ["Nº", "O que testar", "Funcionou", "Não funcionou", "Não testei", "Comentário"]
repetir_cabecalho(t.rows[0])
for j, texto in enumerate(cab):
    c = t.rows[0].cells[j]
    c.width = Cm(larguras[j])
    sombrear(c, FUNDO_TITULO)
    c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    p = c.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if j in (0, 2, 3, 4) else WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run(texto); r.bold = True; r.font.size = Pt(8.8)
for num, texto in roteiro:
    linha = t.add_row()
    nao_quebrar_linha(linha)
    if texto is None:
        mesclada = linha.cells[0].merge(linha.cells[5])
        sombrear(mesclada, FUNDO_CAMPO)
        r = mesclada.paragraphs[0].add_run(num); r.bold = True; r.font.size = Pt(9.3)
        mesclada.paragraphs[0].paragraph_format.space_after = Pt(1)
        continue
    linha.height = Cm(0.8)
    linha.height_rule = WD_ROW_HEIGHT_RULE.AT_LEAST
    valores = [num, texto, "(   )", "(   )", "(   )", ""]
    for j, v in enumerate(valores):
        c = linha.cells[j]
        c.width = Cm(larguras[j])
        c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        p = c.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        if j in (0, 2, 3, 4):
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(v); r.font.size = Pt(9.3)
for j, w in enumerate(larguras):
    t.columns[j].width = Cm(w)
doc.add_paragraph().paragraph_format.space_after = Pt(2)

# --------------------------------------------------------------- campos obrigatórios
doc.add_heading("4. O que testou e funcionou", level=1)
paragrafo("Descreva com suas palavras as funcionalidades que funcionaram bem.", cor=CINZA, tamanho=9.5)
linhas_resposta(5)

doc.add_heading("5. O que testou e não funcionou — o que deve ser corrigido", level=1)
paragrafo("Uma linha por problema. Se tirou print da tela, anote o número do print (seção 8).", cor=CINZA, tamanho=9.5)
tabela([3.4, 4.6, 4.6, 2.6, 1.8], [
    ["Funcionalidade", "O que aconteceu", "O que deveria acontecer / o que corrigir", "Gravidade", "Print nº"],
    *[["", "", "", "(  ) Alta\n(  ) Média\n(  ) Baixa", ""] for _ in range(5)],
], altura_cm=1.9)

doc.add_heading("6. Funcionalidade não testada", level=1)
paragrafo("Se algum item ficou sem testar, diga qual e por quê.", cor=CINZA, tamanho=9.5)
tabela([5.5, 11.5], [
    ["Funcionalidade", "Motivo"],
    *[["", "(  ) Faltou tempo   (  ) Não encontrei no app   (  ) O app não tem essa função   (  ) Outro: __________"] for _ in range(3)],
], altura_cm=1.1)

doc.add_heading("7. Sugestões de melhoria", level=1)
paragrafo("O que deixaria o app melhor, mais fácil ou mais bonito?", cor=CINZA, tamanho=9.5)
linhas_resposta(5)

doc.add_heading("8. Prints das telas com erro", level=1)
paragrafo("Cole abaixo os prints das telas onde algo deu errado. Numere cada um (Print 1, Print 2…) "
          "e use o mesmo número na seção 5.", cor=CINZA, tamanho=9.5)
paragrafo("No celular: tire o print, envie para você mesmo e cole aqui. Se preferir, mande os prints junto "
          "com este arquivo, já com o número no nome (ex.: print1.png).", cor=CINZA, tamanho=9.5)
for n in (1, 2):
    tabela([LARGURA], [[f"Print {n} — tela: ____________________________"], [""]], cabecalho=True, altura_cm=6.5)

doc.add_heading("9. Avaliação geral (opcional)", level=1)
tabela([9.0, 8.0], [
    ["Pergunta", "Resposta"],
    ["Facilidade de uso (1 = muito difícil, 5 = muito fácil)", "1 (  )   2 (  )   3 (  )   4 (  )   5 (  )"],
    ["Aparência das telas (1 = ruim, 5 = ótima)", "1 (  )   2 (  )   3 (  )   4 (  )   5 (  )"],
    ["Você compraria cupcakes por um app assim?", "(  ) Sim   (  ) Talvez   (  ) Não"],
], altura_cm=0.8)

doc.add_heading("Devolução", level=2)
paragrafo("Salve este arquivo com o seu nome (ex.: Teste_AnaSouza.docx) e devolva ao autor pelo mesmo canal em que "
          "recebeu. As respostas serão usadas apenas neste trabalho acadêmico, e as falhas apontadas serão corrigidas "
          "e registradas no laudo de qualidade do projeto. Obrigado!", tamanho=9.8)

# rodapé com número de página
rodape = sec.footer.paragraphs[0]
rodape.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = rodape.add_run("Cupcakes Gourmet · Formulário de Teste da Solução · página ")
r.font.size = Pt(8); r.font.color.rgb = CINZA
for tipo, texto in (("begin", None), (None, "PAGE"), ("end", None)):
    run = rodape.add_run()
    run.font.size = Pt(8); run.font.color.rgb = CINZA
    if tipo:
        fld = OxmlElement("w:fldChar"); fld.set(qn("w:fldCharType"), tipo); run._r.append(fld)
    else:
        instr = OxmlElement("w:instrText"); instr.set(qn("xml:space"), "preserve"); instr.text = texto; run._r.append(instr)

doc.save(SAIDA)
print("Formulário gerado em", SAIDA)
