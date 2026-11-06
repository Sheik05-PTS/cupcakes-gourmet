"""Executa schema.sql + seed.sql num banco VAZIO e testa as restrições de integridade.

Uso (o banco informado precisa existir e estar vazio):
    python database/verificar_schema.py "postgresql://usuario:senha@host/cupcakes_teste"

Cada caso inválido deve ser recusado pelo PostgreSQL. No final, mostra quantas
restrições funcionaram.
"""
import os
import sys

import psycopg2

db_dir = os.path.dirname(os.path.abspath(__file__))
uri = sys.argv[1]

con = psycopg2.connect(uri)
con.autocommit = True
cur = con.cursor()
for arquivo in ("schema.sql", "seed.sql"):
    cur.execute(open(f"{db_dir}/{arquivo}", encoding="utf8").read())
    print(f"[ok] {arquivo} executado")

cur.execute("SELECT count(*) FROM information_schema.tables WHERE table_schema='public'")
print("tabelas criadas:", cur.fetchone()[0])
for t in ("sabores", "ocasioes", "restricoes_alimentares", "opcoes_personalizacao", "cupcakes",
          "cupcake_ocasioes", "cupcake_restricoes", "areas_entrega", "cupons"):
    cur.execute(f"SELECT count(*) FROM {t}")
    print(f"  {t}: {cur.fetchone()[0]} linhas")

# dados de apoio para os testes
cur.execute("INSERT INTO usuarios (nome, email, telefone, senha_hash) VALUES "
            "('Cliente Teste', 'cliente@teste.com', '11987654321', 'hash') RETURNING id")
uid = cur.fetchone()[0]
cur.execute("SELECT id FROM cupcakes WHERE nome='Red Velvet'")
cup = cur.fetchone()[0]
cur.execute("SELECT id FROM opcoes_personalizacao WHERE tipo='RECHEIO' AND nome='Ganache'")
recheio = cur.fetchone()[0]
cur.execute("SELECT id FROM opcoes_personalizacao WHERE tipo='COBERTURA' AND nome='Cream cheese'")
cobertura = cur.fetchone()[0]

PEDIDO = ("INSERT INTO pedidos (usuario_id, subtotal, desconto, frete, total, prazo_minutos, entrega_cep, "
          "entrega_logradouro, entrega_numero, entrega_bairro, entrega_cidade, entrega_uf) "
          "VALUES (%s, %s, %s, %s, %s, 90, '01310100', 'Av. Paulista', '1000', 'Bela Vista', 'São Paulo', 'SP') RETURNING id")

# caso válido completo
cur.execute(PEDIDO, (uid, 61.50, 6.15, 8.00, 63.35))
pid = cur.fetchone()[0]
cur.execute("INSERT INTO itens_pedido (pedido_id, cupcake_id, quantidade, preco_unitario, recheio_id, cobertura_id, mensagem) "
            "VALUES (%s, %s, 2, 14.40, %s, %s, 'Feliz aniversário, Ana!')", (pid, cup, recheio, cobertura))
cur.execute("INSERT INTO historico_status (pedido_id, status) VALUES (%s, 'AGUARDANDO_PAGAMENTO')", (pid,))
cur.execute("INSERT INTO pagamentos (pedido_id, metodo, status, valor, cartao_bandeira, cartao_final) "
            "VALUES (%s, 'CARTAO', 'APROVADO', 63.35, 'Visa', '1111')", (pid,))
print("[ok] pedido válido completo inserido (pedido, item personalizado, histórico, pagamento)")

falhas = 0
def deve_falhar(descricao, sql, params=()):
    global falhas
    try:
        cur.execute("SAVEPOINT t")
        cur.execute(sql, params)
        cur.execute("ROLLBACK TO SAVEPOINT t")
        print(f"[FALHOU] aceitou: {descricao}")
        falhas += 1
    except psycopg2.Error as e:
        cur.execute("ROLLBACK TO SAVEPOINT t")
        print(f"[ok] recusou {descricao}  ->  {e.pgcode} {e.diag.constraint_name or ''}".rstrip())

cur.execute("BEGIN")
deve_falhar("e-mail duplicado (maiúsculas)", "INSERT INTO usuarios (nome,email,telefone,senha_hash) VALUES ('Outro','CLIENTE@teste.com','11999999999','h')")
deve_falhar("e-mail inválido", "INSERT INTO usuarios (nome,email,telefone,senha_hash) VALUES ('Outro','semarroba','11999999999','h')")
deve_falhar("telefone com letras", "INSERT INTO usuarios (nome,email,telefone,senha_hash) VALUES ('Outro','o@t.com','11abc','h')")
deve_falhar("perfil inexistente", "INSERT INTO usuarios (nome,email,telefone,senha_hash,perfil) VALUES ('Outro','o@t.com','11999999999','h','GERENTE')")
deve_falhar("CEP com 7 dígitos", "INSERT INTO enderecos (usuario_id,cep,logradouro,numero,bairro,cidade,uf) VALUES (%s,'0131010','Rua','1','B','C','SP')", (uid,))
deve_falhar("UF inexistente", "INSERT INTO enderecos (usuario_id,cep,logradouro,numero,bairro,cidade,uf) VALUES (%s,'01310100','Rua','1','B','C','XX')", (uid,))
deve_falhar("cupcake com preço zero (RN01)", "INSERT INTO cupcakes (sabor_id,nome,descricao,ingredientes,preco) VALUES (1,'Teste','d','i',0)")
deve_falhar("cupcake com estoque negativo (RN01)", "UPDATE cupcakes SET estoque = -1 WHERE id = %s", (cup,))
deve_falhar("cupcake com nome repetido", "INSERT INTO cupcakes (sabor_id,nome,descricao,ingredientes,preco) VALUES (1,'Red Velvet','d','i',10)")
deve_falhar("excluir cupcake já vendido (RN19)", "DELETE FROM cupcakes WHERE id = %s", (cup,))
deve_falhar("excluir sabor em uso", "DELETE FROM sabores WHERE nome = 'Chocolate'")
deve_falhar("cupom percentual acima de 100%", "INSERT INTO cupons (codigo,tipo,valor,valido_de,valido_ate) VALUES ('X150','PERCENTUAL',150,'2026-01-01','2026-12-31')")
deve_falhar("cupom com validade invertida", "INSERT INTO cupons (codigo,tipo,valor,valido_de,valido_ate) VALUES ('XDATA','VALOR_FIXO',5,'2026-12-31','2026-01-01')")
deve_falhar("cupom com código minúsculo", "INSERT INTO cupons (codigo,tipo,valor,valido_de,valido_ate) VALUES ('doce','VALOR_FIXO',5,'2026-01-01','2026-12-31')")
deve_falhar("área de entrega sobreposta (RN08)", "INSERT INTO areas_entrega (nome,cep_inicial,cep_final,valor_frete,prazo_minutos) VALUES ('X','01500000','01600000',5,60)")
deve_falhar("área com CEP final menor que inicial", "INSERT INTO areas_entrega (nome,cep_inicial,cep_final,valor_frete,prazo_minutos) VALUES ('X','09000000','08000000',5,60)")
deve_falhar("total diferente de subtotal - desconto + frete (RN09)", PEDIDO, (uid, 61.50, 6.15, 8.00, 70.00))
deve_falhar("desconto maior que o subtotal (RN07)", PEDIDO, (uid, 10.00, 15.00, 8.00, 3.00))
deve_falhar("item com quantidade 21 (RN03)", "INSERT INTO itens_pedido (pedido_id,cupcake_id,quantidade,preco_unitario) VALUES (%s,%s,21,12.90)", (pid, cup))
deve_falhar("item com quantidade 0 (RN03)", "INSERT INTO itens_pedido (pedido_id,cupcake_id,quantidade,preco_unitario) VALUES (%s,%s,0,12.90)", (pid, cup))
deve_falhar("mensagem com 61 caracteres (RN04)", "INSERT INTO itens_pedido (pedido_id,cupcake_id,quantidade,preco_unitario,mensagem) VALUES (%s,%s,1,12.90,%s)", (pid, cup, "x" * 61))
deve_falhar("cobertura usada como recheio", "INSERT INTO itens_pedido (pedido_id,cupcake_id,quantidade,preco_unitario,recheio_id) VALUES (%s,%s,1,12.90,%s)", (pid, cup, cobertura))
deve_falhar("recheio usado como cobertura", "INSERT INTO itens_pedido (pedido_id,cupcake_id,quantidade,preco_unitario,cobertura_id) VALUES (%s,%s,1,12.90,%s)", (pid, cup, recheio))
deve_falhar("segundo pagamento aprovado no mesmo pedido", "INSERT INTO pagamentos (pedido_id,metodo,status,valor,cartao_bandeira,cartao_final) VALUES (%s,'CARTAO','APROVADO',63.35,'Visa','4242')", (pid,))
deve_falhar("cartão com número completo no campo final (RN12)", "INSERT INTO pagamentos (pedido_id,metodo,valor,cartao_bandeira,cartao_final) VALUES (%s,'CARTAO',63.35,'Visa','4111111111111111')", (pid,))
deve_falhar("Pix sem código", "INSERT INTO pagamentos (pedido_id,metodo,valor,pix_expira_em) VALUES (%s,'PIX',63.35,now())", (pid,))
deve_falhar("Pix com dados de cartão", "INSERT INTO pagamentos (pedido_id,metodo,valor,pix_codigo,pix_expira_em,cartao_final,cartao_bandeira) VALUES (%s,'PIX',63.35,'abc',now(),'1111','Visa')", (pid,))
deve_falhar("motivo de recusa em pagamento não recusado", "INSERT INTO pagamentos (pedido_id,metodo,status,valor,cartao_bandeira,cartao_final,motivo_recusa) VALUES (%s,'CARTAO','PENDENTE',63.35,'Visa','0002','x')", (pid,))
deve_falhar("status de pedido inexistente", "UPDATE pedidos SET status = 'DEVOLVIDO' WHERE id = %s", (pid,))
deve_falhar("excluir cliente com pedidos", "DELETE FROM usuarios WHERE id = %s", (uid,))
cur.execute("ROLLBACK")

# comportamentos esperados que devem funcionar
cur.execute("INSERT INTO pagamentos (pedido_id,metodo,status,valor,cartao_bandeira,cartao_final,motivo_recusa) "
            "VALUES (%s,'CARTAO','RECUSADO',63.35,'Visa','0002','Cartão recusado pelo emissor')", (pid,))
cur.execute("SELECT nome, valor_frete, prazo_minutos FROM areas_entrega "
            "WHERE '01310100'::integer BETWEEN cep_inicial::integer AND cep_final::integer")
print("[ok] busca de frete para CEP 01310-100:", cur.fetchone())
cur.execute("SELECT count(*) FROM areas_entrega WHERE '09999999'::integer BETWEEN cep_inicial::integer AND cep_final::integer")
print("[ok] CEP fora da área encontra", cur.fetchone()[0], "faixa(s)")
cur.execute("SELECT c.nome FROM cupcakes c JOIN cupcake_restricoes cr ON cr.cupcake_id=c.id "
            "JOIN restricoes_alimentares r ON r.id=cr.restricao_id WHERE r.nome='Sem lactose' AND c.ativo AND c.preco <= 15")
print("[ok] filtro 'Sem lactose' + 'até R$ 15':", [r[0] for r in cur.fetchall()])

print()
print("RESULTADO:", "todas as restrições funcionaram" if falhas == 0 else f"{falhas} restrição(ões) não funcionaram")
con.close()
