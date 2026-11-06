-- =====================================================================
-- Cupcakes Gourmet — Dados iniciais (catálogo, entrega e cupons)
-- Executar depois do schema.sql:  psql -d cupcakes -f database/seed.sql
-- Usuários (inclusive o administrador) são criados pela aplicação,
-- porque a senha precisa ser gravada como hash.
-- =====================================================================

BEGIN;

INSERT INTO sabores (nome) VALUES
  ('Chocolate'), ('Frutas'), ('Baunilha'), ('Doce de leite'), ('Castanhas');

INSERT INTO ocasioes (nome) VALUES
  ('Aniversário'), ('Casamento'), ('Corporativo'), ('Dia a dia'), ('Presente');

INSERT INTO restricoes_alimentares (nome) VALUES
  ('Sem glúten'), ('Sem lactose'), ('Vegano');

INSERT INTO opcoes_personalizacao (tipo, nome, acrescimo) VALUES
  ('RECHEIO',   'Brigadeiro',     0.00),
  ('RECHEIO',   'Ganache',        1.50),
  ('RECHEIO',   'Doce de leite',  1.00),
  ('RECHEIO',   'Geleia de frutas vermelhas', 1.00),
  ('COBERTURA', 'Cream cheese',   0.00),
  ('COBERTURA', 'Chantilly',      0.00),
  ('COBERTURA', 'Buttercream',    0.00),
  ('COBERTURA', 'Ganache branca', 1.50);

INSERT INTO cupcakes (sabor_id, nome, descricao, ingredientes, preco, foto_url, estoque, ativo, personalizavel) VALUES
  ((SELECT id FROM sabores WHERE nome = 'Chocolate'), 'Red Velvet',
   'Massa aveludada de cacau com toque de baunilha e cobertura de cream cheese.',
   'Farinha de trigo, cacau, leite, ovos, manteiga, açúcar, cream cheese.',
   12.90, '/static/img/cupcakes/red-velvet.svg', 18, TRUE, TRUE),
  ((SELECT id FROM sabores WHERE nome = 'Chocolate'), 'Brigadeiro Belga',
   'Massa de chocolate meio amargo com brigadeiro feito com chocolate belga.',
   'Farinha de trigo, chocolate belga, leite condensado, manteiga, ovos, açúcar.',
   11.90, '/static/img/cupcakes/brigadeiro-belga.svg', 24, TRUE, TRUE),
  ((SELECT id FROM sabores WHERE nome = 'Frutas'), 'Limão Siciliano',
   'Massa cítrica com raspas de limão siciliano e cobertura de merengue.',
   'Farinha de trigo, limão siciliano, ovos, manteiga, açúcar, leite.',
   10.90, '/static/img/cupcakes/limao-siciliano.svg', 30, TRUE, FALSE),
  ((SELECT id FROM sabores WHERE nome = 'Castanhas'), 'Pistache',
   'Massa de pistache com creme de pistache siciliano.',
   'Farinha de trigo, pistache, leite, ovos, manteiga, açúcar.',
   14.90, '/static/img/cupcakes/pistache.svg', 0, TRUE, FALSE),
  ((SELECT id FROM sabores WHERE nome = 'Doce de leite'), 'Doce de Leite com Flor de Sal',
   'Massa amanteigada recheada com doce de leite e finalizada com flor de sal.',
   'Farinha de trigo, doce de leite, manteiga, ovos, açúcar mascavo, flor de sal.',
   12.50, '/static/img/cupcakes/doce-de-leite.svg', 15, TRUE, TRUE),
  ((SELECT id FROM sabores WHERE nome = 'Frutas'), 'Morango com Chantilly',
   'Massa de baunilha com morangos frescos e chantilly.',
   'Farinha de trigo, morango, creme de leite, ovos, manteiga, açúcar.',
   11.50, '/static/img/cupcakes/morango.svg', 20, TRUE, TRUE),
  ((SELECT id FROM sabores WHERE nome = 'Chocolate'), 'Cacau 70% Vegano',
   'Massa de cacau 70% sem ingredientes de origem animal, com ganache de coco.',
   'Farinha de arroz, cacau 70%, leite de coco, óleo de coco, açúcar demerara.',
   13.90, '/static/img/cupcakes/cacau-vegano.svg', 12, TRUE, FALSE),
  ((SELECT id FROM sabores WHERE nome = 'Baunilha'), 'Abóbora com Especiarias',
   'Edição de outono: abóbora assada, canela, cravo e noz-moscada.',
   'Farinha de trigo, abóbora, ovos, manteiga, açúcar mascavo, especiarias.',
   11.50, '/static/img/cupcakes/abobora.svg', 0, FALSE, FALSE);

INSERT INTO cupcake_ocasioes (cupcake_id, ocasiao_id)
SELECT c.id, o.id
FROM (VALUES
  ('Red Velvet', 'Aniversário'), ('Red Velvet', 'Casamento'),
  ('Brigadeiro Belga', 'Dia a dia'), ('Brigadeiro Belga', 'Aniversário'),
  ('Limão Siciliano', 'Dia a dia'), ('Limão Siciliano', 'Corporativo'),
  ('Pistache', 'Casamento'), ('Pistache', 'Presente'),
  ('Doce de Leite com Flor de Sal', 'Presente'), ('Doce de Leite com Flor de Sal', 'Dia a dia'),
  ('Morango com Chantilly', 'Aniversário'), ('Morango com Chantilly', 'Casamento'),
  ('Cacau 70% Vegano', 'Dia a dia'), ('Cacau 70% Vegano', 'Corporativo'),
  ('Abóbora com Especiarias', 'Presente')
) AS v (cupcake, ocasiao)
JOIN cupcakes c ON c.nome = v.cupcake
JOIN ocasioes o ON o.nome = v.ocasiao;

INSERT INTO cupcake_restricoes (cupcake_id, restricao_id)
SELECT c.id, r.id
FROM (VALUES
  ('Cacau 70% Vegano', 'Vegano'), ('Cacau 70% Vegano', 'Sem lactose'), ('Cacau 70% Vegano', 'Sem glúten')
) AS v (cupcake, restricao)
JOIN cupcakes c ON c.nome = v.cupcake
JOIN restricoes_alimentares r ON r.nome = v.restricao;

INSERT INTO areas_entrega (nome, cep_inicial, cep_final, valor_frete, prazo_minutos) VALUES
  ('Centro e Bela Vista',     '01000000', '01599999',  8.00,  90),
  ('Vila Mariana e Paraíso',  '04000000', '04299999', 12.00, 120),
  ('Pinheiros e Perdizes',    '05000000', '05099999', 12.00, 120);

INSERT INTO cupons (codigo, tipo, valor, valor_minimo, valido_de, valido_ate, ativo) VALUES
  ('DOCE10',     'PERCENTUAL', 10.00, 30.00, DATE '2026-01-01', DATE '2026-12-31', TRUE),
  ('BEMVINDO5',  'VALOR_FIXO',  5.00, 40.00, DATE '2026-01-01', DATE '2026-12-31', TRUE),
  ('VERAO2025',  'PERCENTUAL', 15.00,  0.00, DATE '2025-01-01', DATE '2025-03-31', TRUE);  -- vencido, usado nos testes

COMMIT;
