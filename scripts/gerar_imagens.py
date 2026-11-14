"""Gera as ilustrações dos cupcakes (SVG) usadas enquanto a loja não tem fotos reais.

Uso: python scripts/gerar_imagens.py
Saída: app/static/img/cupcakes/*.svg e app/static/img/icone.svg
"""
from pathlib import Path

PASTA = Path(__file__).resolve().parent.parent / "app" / "static" / "img"

# nome do arquivo: (fundo, cobertura, forminha, topo, nome)
CUPCAKES = {
    "red-velvet": ("#fbe3e3", "#ffffff", "#c0392b", "#8e1b1b", "Red Velvet"),
    "brigadeiro-belga": ("#efe4dc", "#5b3a29", "#e8c9a8", "#2b1a12", "Brigadeiro Belga"),
    "limao-siciliano": ("#f6f7dc", "#fbf6d0", "#cddc39", "#9bb52a", "Limão Siciliano"),
    "pistache": ("#e8f2e1", "#b5d39a", "#7aa65a", "#4f7a35", "Pistache"),
    "doce-de-leite": ("#f8ecdc", "#d9a066", "#f3d2a2", "#a0612b", "Doce de Leite com Flor de Sal"),
    "morango": ("#fde7ec", "#fbd3dc", "#e57399", "#d21f3c", "Morango com Chantilly"),
    "cacau-vegano": ("#ece6e1", "#3e2a22", "#a8c686", "#1f140f", "Cacau 70% Vegano"),
    "abobora": ("#fbead9", "#f0b27a", "#d35400", "#a04000", "Abóbora com Especiarias"),
    "padrao": ("#fcf0f4", "#ffffff", "#e9b8c6", "#c2185b", "Cupcake"),
}


def cupcake_svg(fundo, cobertura, forminha, topo, titulo, com_fundo=True):
    fundo_svg = f'<rect width="400" height="300" fill="{fundo}"/>' if com_fundo else ""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" role="img" aria-label="Ilustração do cupcake {titulo}">
  <title>{titulo}</title>
  {fundo_svg}
  <ellipse cx="200" cy="262" rx="78" ry="10" fill="#000" opacity=".06"/>
  <g transform="translate(110 40) scale(1.8)">
    <path d="M26 58 L74 58 L67 90 Q50 94 33 90 Z" fill="{forminha}"/>
    <path d="M36 60 L39 89 M46 60 L47 91 M54 60 L53 91 M64 60 L61 89" stroke="#000" stroke-opacity=".12" stroke-width="2"/>
    <path d="M20 60 C16 49 27 42 34 45 C31 35 43 28 50 33 C57 27 70 33 66 43 C75 41 85 50 80 60 Q50 66 20 60 Z" fill="{cobertura}"/>
    <path d="M38 40 C38 27 62 27 62 40 Q50 44 38 40 Z" fill="{cobertura}"/>
    <path d="M30 52 C38 50 46 53 52 51" stroke="#fff" stroke-opacity=".55" stroke-width="3" fill="none" stroke-linecap="round"/>
    <circle cx="50" cy="25" r="6" fill="{topo}"/>
    <circle cx="48" cy="23" r="1.8" fill="#fff" fill-opacity=".6"/>
  </g>
</svg>
"""


def main():
    (PASTA / "cupcakes").mkdir(parents=True, exist_ok=True)
    for arquivo, (fundo, cobertura, forminha, topo, titulo) in CUPCAKES.items():
        (PASTA / "cupcakes" / f"{arquivo}.svg").write_text(cupcake_svg(fundo, cobertura, forminha, topo, titulo), encoding="utf8")
    icone = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="14" fill="#9c2f5b"/>
  <g transform="translate(7 4) scale(.5)">
    <path d="M26 58 L74 58 L67 90 Q50 94 33 90 Z" fill="#f7dbe4"/>
    <path d="M20 60 C16 49 27 42 34 45 C31 35 43 28 50 33 C57 27 70 33 66 43 C75 41 85 50 80 60 Q50 66 20 60 Z" fill="#fff"/>
    <path d="M38 40 C38 27 62 27 62 40 Q50 44 38 40 Z" fill="#fff"/>
    <circle cx="50" cy="25" r="6" fill="#f7dbe4"/>
  </g>
</svg>
"""
    (PASTA / "icone.svg").write_text(icone, encoding="utf8")
    print(f"{len(CUPCAKES)} ilustrações geradas em {PASTA / 'cupcakes'}")


if __name__ == "__main__":
    main()
