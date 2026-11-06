"""Gera os diagramas de casos de uso (notação UML) em SVG.

Uso: python3 gerar_casos_de_uso.py
Saída: ../img/casos-de-uso-compra.svg e ../img/casos-de-uso-administracao.svg
"""
from pathlib import Path

SAIDA = Path(__file__).resolve().parent.parent / "img"

TINTA = "#1f2433"
LINHA = "#4a5063"
FUNDO_UC = "#fbf1f4"
BORDA_UC = "#b8456b"
FONTE = "Helvetica, Arial, sans-serif"

RX, RY = 122, 24


def svg_inicio(largura, altura, titulo):
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{largura}" height="{altura}" '
        f'viewBox="0 0 {largura} {altura}" font-family="{FONTE}">',
        "<defs>",
        f'<marker id="seta" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="9" markerHeight="9" orient="auto-start-reverse">'
        f'<path d="M0,0 L10,5 L0,10" fill="none" stroke="{LINHA}" stroke-width="1.5"/></marker>',
        f'<marker id="heranca" viewBox="0 0 12 12" refX="12" refY="6" markerWidth="14" markerHeight="14" orient="auto-start-reverse">'
        f'<path d="M0,0 L12,6 L0,12 Z" fill="#fff" stroke="{LINHA}" stroke-width="1.3"/></marker>',
        "</defs>",
        f'<rect width="{largura}" height="{altura}" fill="#fff"/>',
        f'<text x="20" y="30" font-size="16" font-weight="700" fill="{TINTA}">{titulo}</text>',
    ]


def ator(x, y, nome):
    """Boneco UML com o centro da cabeça em (x, y)."""
    return [
        f'<g stroke="{TINTA}" stroke-width="2" fill="none">'
        f'<circle cx="{x}" cy="{y}" r="11" fill="#fff"/>'
        f'<line x1="{x}" y1="{y + 11}" x2="{x}" y2="{y + 42}"/>'
        f'<line x1="{x - 18}" y1="{y + 22}" x2="{x + 18}" y2="{y + 22}"/>'
        f'<line x1="{x}" y1="{y + 42}" x2="{x - 15}" y2="{y + 66}"/>'
        f'<line x1="{x}" y1="{y + 42}" x2="{x + 15}" y2="{y + 66}"/></g>',
        f'<text x="{x}" y="{y + 86}" font-size="13" font-weight="700" fill="{TINTA}" text-anchor="middle">{nome}</text>',
    ]


def caso(cx, cy, rotulo):
    return [
        f'<ellipse cx="{cx}" cy="{cy}" rx="{RX}" ry="{RY}" fill="{FUNDO_UC}" stroke="{BORDA_UC}" stroke-width="1.5"/>',
        f'<text x="{cx}" y="{cy + 4.5}" font-size="12.5" fill="{TINTA}" text-anchor="middle">{rotulo}</text>',
    ]


def linha(x1, y1, x2, y2):
    return [f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{LINHA}" stroke-width="1.3"/>']


def dependencia(pontos, rotulo, rx, ry):
    """Seta tracejada («include»/«extend») passando pelos pontos, com rótulo em (rx, ry)."""
    caminho = " ".join(f"{x},{y}" for x, y in pontos)
    return [
        f'<polyline points="{caminho}" fill="none" stroke="{LINHA}" stroke-width="1.3" '
        f'stroke-dasharray="6 4" marker-end="url(#seta)"/>',
        f'<text x="{rx}" y="{ry}" font-size="11.5" fill="{LINHA}" text-anchor="middle" '
        f'paint-order="stroke" stroke="#fff" stroke-width="4">{rotulo}</text>',
    ]


def fronteira(x, y, w, h, nome):
    return [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="none" stroke="{TINTA}" stroke-width="1.5"/>',
        f'<text x="{x + w / 2}" y="{y + 22}" font-size="13.5" font-weight="700" fill="{TINTA}" text-anchor="middle">{nome}</text>',
    ]


def borda_esq(cx):
    return cx - RX


def borda_dir(cx):
    return cx + RX


def diagrama_compra():
    A, B = 420, 740  # colunas dos casos de uso
    ys = {"UC01": 100, "UC03": 160, "UC04": 220, "UC06": 280, "UC07": 340, "UC08": 400,
          "UC09": 500, "UC10": 560, "UC12": 640, "UC13": 700}
    yb = {"UC02": 100, "UC05": 220, "UC11": 490}
    nomes = {
        "UC01": "UC01 Navegar na vitrine", "UC02": "UC02 Filtrar cupcakes",
        "UC03": "UC03 Ver detalhes do cupcake", "UC04": "UC04 Gerenciar carrinho",
        "UC05": "UC05 Personalizar cupcake", "UC06": "UC06 Calcular frete e prazo",
        "UC07": "UC07 Criar conta", "UC08": "UC08 Entrar e sair",
        "UC09": "UC09 Gerenciar endereços", "UC10": "UC10 Finalizar pedido",
        "UC11": "UC11 Aplicar cupom", "UC12": "UC12 Pagar pedido",
        "UC13": "UC13 Acompanhar pedidos",
    }
    s = svg_inicio(1120, 760, "Casos de Uso — Visão de Compra")
    s += fronteira(250, 50, 650, 690, "Sistema Cupcakes Gourmet")

    vis = (110, 210)   # cabeça do Visitante
    cli = (110, 570)   # cabeça do Cliente
    gw = (1020, 618)   # cabeça do Gateway

    # associações do Visitante
    for uc in ["UC01", "UC03", "UC04", "UC06", "UC07", "UC08"]:
        s += linha(vis[0] + 20, vis[1] + 22, borda_esq(A), ys[uc])
    # associações do Cliente
    for uc in ["UC09", "UC10", "UC12", "UC13"]:
        s += linha(cli[0] + 20, cli[1] + 22, borda_esq(A), ys[uc])
    # generalização Cliente -> Visitante
    s += [f'<line x1="{cli[0]}" y1="{cli[1] - 13}" x2="{vis[0]}" y2="{vis[1] + 94}" '
          f'stroke="{LINHA}" stroke-width="1.3" marker-end="url(#heranca)"/>']
    # Gateway <-> UC12
    s += linha(borda_dir(A), ys["UC12"], gw[0] - 22, ys["UC12"])

    # «extend» e «include»
    s += dependencia([(borda_esq(B), yb["UC02"]), (borda_dir(A), ys["UC01"])], "«extend»", 580, 94)
    s += dependencia([(borda_esq(B), yb["UC05"]), (borda_dir(A), ys["UC04"])], "«extend»", 580, 214)
    s += dependencia([(borda_dir(A), ys["UC10"]), (880, ys["UC10"]), (880, ys["UC06"]),
                      (borda_dir(A), ys["UC06"])], "«include»", 852, 420)
    s += dependencia([(A, ys["UC10"] + RY), (A, ys["UC12"] - RY)], "«include»", A + 46, 604)
    s += dependencia([(borda_esq(B) + 22, yb["UC11"] + 15), (borda_dir(A) - 24, ys["UC10"] - 14)],
                     "«extend»", 610, 510)

    for uc, y in ys.items():
        s += caso(A, y, nomes[uc])
    for uc, y in yb.items():
        s += caso(B, y, nomes[uc])

    s += ator(*vis, "Visitante")
    s += ator(*cli, "Cliente")
    s += ator(*gw, "Gateway de pagamento")
    s += [f'<text x="{gw[0]}" y="{gw[1] + 102}" font-size="11.5" fill="{LINHA}" text-anchor="middle">(simulado)</text>']
    s.append("</svg>")
    return "\n".join(s)


def diagrama_admin():
    A, B = 420, 740
    ys = {"UC08": 100, "UC14": 160, "UC15": 220, "UC16": 280}
    nomes = {"UC08": "UC08 Entrar e sair", "UC14": "UC14 Manter cupcakes",
             "UC15": "UC15 Controlar disponibilidade", "UC16": "UC16 Gerenciar pedidos",
             "UC17": "UC17 Cancelar pedido"}
    s = svg_inicio(960, 350, "Casos de Uso — Visão de Administração")
    s += fronteira(250, 50, 650, 280, "Sistema Cupcakes Gourmet — Painel administrativo")
    adm = (110, 150)
    for uc in ys:
        s += linha(adm[0] + 20, adm[1] + 22, borda_esq(A), ys[uc])
    s += dependencia([(borda_esq(B), 280), (borda_dir(A), 280)], "«extend»", 580, 274)
    for uc, y in ys.items():
        s += caso(A, y, nomes[uc])
    s += caso(B, 280, nomes["UC17"])
    s += ator(*adm, "Administrador")
    s.append("</svg>")
    return "\n".join(s)


if __name__ == "__main__":
    SAIDA.mkdir(parents=True, exist_ok=True)
    (SAIDA / "casos-de-uso-compra.svg").write_text(diagrama_compra(), encoding="utf8")
    (SAIDA / "casos-de-uso-administracao.svg").write_text(diagrama_admin(), encoding="utf8")
    print("SVGs gerados em", SAIDA)
