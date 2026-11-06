"""Gera o dicionário de dados em Markdown a partir do banco já criado.

Lê tabelas, colunas, tipos, restrições, índices e os comentários (COMMENT ON)
do próprio PostgreSQL, então o dicionário nunca fica diferente do banco.

Uso:
    python database/gerar_dicionario.py "postgresql://usuario:senha@host/banco" saida.md
"""
import re
import sys

import psycopg2

ORDEM = [
    "usuarios", "enderecos", "sabores", "ocasioes", "restricoes_alimentares", "cupcakes",
    "cupcake_ocasioes", "cupcake_restricoes", "opcoes_personalizacao", "cupons",
    "areas_entrega", "pedidos", "itens_pedido", "pagamentos", "historico_status",
]


def envolvida_por_parenteses(expr):
    """True se o primeiro "(" da expressão fecha exatamente no último caractere."""
    if not (expr.startswith("(") and expr.endswith(")")):
        return False
    nivel = 0
    for i, ch in enumerate(expr):
        nivel += ch == "("
        nivel -= ch == ")"
        if nivel == 0 and i < len(expr) - 1:
            return False
    return True


def limpar(expr):
    """Deixa a expressão de CHECK legível: tira conversões de tipo e parênteses extras."""
    expr = expr.replace("CHECK ", "")
    expr = re.sub(r"::(character varying|character|text|bpchar|numeric|integer|date)(\[\])?", "", expr)
    expr = re.sub(r"::[a-z_]+", "", expr)
    expr = re.sub(r"\(([a-z_]+|\d+)\)", r"\1", expr)
    expr = re.sub(r"\(\(([a-z_]+)\)", r"(\1", expr)
    while envolvida_por_parenteses(expr):
        expr = expr[1:-1]
    m = re.match(r"\(?VALUE = ANY \(ARRAY\[(.*)\]\)\)?$", expr)
    if m:
        expr = "VALUE IN (" + m.group(1).replace("'", "") + ")"
    return expr


def consultar(cur, sql, params=()):
    cur.execute(sql, params)
    return cur.fetchall()


def restricoes_por_coluna(cur, tabela):
    """Mapeia coluna -> lista de restrições de uma única coluna (PK, FK, UNIQUE, CHECK)."""
    linhas = consultar(cur, """
        SELECT c.contype, a.attname, pg_get_constraintdef(c.oid), cardinality(c.conkey)
        FROM pg_constraint c
        JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = ANY (c.conkey)
        WHERE c.conrelid = %s::regclass
        ORDER BY c.contype
    """, (tabela,))
    mapa = {}
    for tipo, coluna, definicao, qtd in linhas:
        if qtd > 1 and tipo != "p":
            continue
        if tipo == "p":
            texto = "PK"
        elif tipo == "f":
            ref = definicao.split("REFERENCES ")[1].split(")")[0] + ")"
            acao = re.search(r"ON DELETE (CASCADE|SET NULL|RESTRICT)", definicao)
            texto = f"FK → {ref}" + (f" ({acao.group(0)})" if acao else "")
        elif tipo == "u":
            texto = "Único"
        elif tipo == "c":
            texto = limpar(definicao)
        else:
            continue
        mapa.setdefault(coluna, []).append(texto)
    return mapa


def restricoes_de_tabela(cur, tabela):
    """Restrições que envolvem mais de uma coluna e índices que não vêm de restrições."""
    itens = []
    for nome, definicao in consultar(cur, """
        SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint
        WHERE conrelid = %s::regclass AND cardinality(conkey) > 1 AND contype <> 'p'
        ORDER BY conname
    """, (tabela,)):
        itens.append(f"`{nome}`: `{limpar(definicao)}`")
    for nome, definicao in consultar(cur, """
        SELECT i.relname, pg_get_indexdef(i.oid)
        FROM pg_index x JOIN pg_class i ON i.oid = x.indexrelid
        WHERE x.indrelid = %s::regclass
          AND NOT EXISTS (SELECT 1 FROM pg_constraint c WHERE c.conindid = i.oid)
        ORDER BY i.relname
    """, (tabela,)):
        itens.append(f"`{nome}` (índice): `{limpar(definicao.split(' USING ')[1])}`")
    return itens


def main(uri, saida):
    con = psycopg2.connect(uri)
    cur = con.cursor()
    md = ["# Dados — 03. Dicionário de Dados", "",
          "> Exigência atendida: **R20** (documentação do banco e dicionário de dados).",
          "> Gerado automaticamente a partir do banco por `database/gerar_dicionario.py`, "
          "usando os comentários gravados no `schema.sql`.", ""]

    md += ["## Tipos enumerados", "", "| Tipo | Valores |", "|---|---|"]
    for nome, valores in consultar(cur, """
        SELECT t.typname, string_agg(e.enumlabel, ', ' ORDER BY e.enumsortorder)
        FROM pg_type t JOIN pg_enum e ON e.enumtypid = t.oid GROUP BY t.typname ORDER BY t.typname"""):
        md.append(f"| `{nome}` | {valores} |")
    md += ["", "## Domínios", "", "| Domínio | Tipo base | Regra |", "|---|---|---|"]
    for nome, base, regra in consultar(cur, """
        SELECT t.typname, format_type(t.typbasetype, t.typtypmod), pg_get_constraintdef(c.oid)
        FROM pg_type t JOIN pg_constraint c ON c.contypid = t.oid
        WHERE t.typtype = 'd' AND t.typnamespace = 'public'::regnamespace ORDER BY t.typname"""):
        md.append(f"| `{nome}` | {base} | `{limpar(regra)}` |")
    md.append("")

    for tabela in ORDEM:
        comentario = consultar(cur, "SELECT obj_description(%s::regclass, 'pg_class')", (tabela,))[0][0]
        md += [f"## {tabela}", "", comentario or "", "",
               "| Coluna | Tipo | Nulo | Padrão | Restrições | Descrição |", "|---|---|---|---|---|---|"]
        restricoes = restricoes_por_coluna(cur, tabela)
        for coluna, tipo, nulo, padrao, gerada, descricao in consultar(cur, """
            SELECT a.attname,
                   CASE WHEN t.typtype = 'd' THEN t.typname ELSE format_type(a.atttypid, a.atttypmod) END,
                   NOT a.attnotnull, pg_get_expr(d.adbin, d.adrelid), a.attgenerated,
                   col_description(a.attrelid, a.attnum)
            FROM pg_attribute a
            JOIN pg_type t ON t.oid = a.atttypid
            LEFT JOIN pg_attrdef d ON d.adrelid = a.attrelid AND d.adnum = a.attnum
            WHERE a.attrelid = %s::regclass AND a.attnum > 0 AND NOT a.attisdropped
            ORDER BY a.attnum
        """, (tabela,)):
            if a_identity := consultar(cur, "SELECT attidentity FROM pg_attribute WHERE attrelid=%s::regclass AND attname=%s",
                                       (tabela, coluna))[0][0]:
                padrao = "automático (identity)" if a_identity == "a" else padrao
            if gerada:
                padrao = f"gerado: {padrao}"
            tipo = tipo.replace("character varying", "varchar").replace("timestamp with time zone", "timestamptz")
            md.append("| `{}` | {} | {} | {} | {} | {} |".format(
                coluna, tipo, "sim" if nulo else "não", (padrao or "—").replace("|", "\\|"),
                "; ".join(restricoes.get(coluna, [])).replace("|", "\\|") or "—", descricao or ""))
        extras = restricoes_de_tabela(cur, tabela)
        if extras:
            md += ["", "Restrições e índices da tabela:", ""] + [f"- {e}" for e in extras]
        md.append("")

    open(saida, "w", encoding="utf8").write("\n".join(md))
    con.close()
    print("Dicionário gerado em", saida)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
