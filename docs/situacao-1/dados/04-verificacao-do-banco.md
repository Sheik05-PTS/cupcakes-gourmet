# Dados — 04. Verificação do Banco

> Complementa **R19**: o script físico não foi só escrito, foi **executado e testado** no PostgreSQL 16.
> Script de verificação: [`database/verificar_schema.py`](../../../database/verificar_schema.py).

## Como foi feito

1. Criação de um banco vazio e execução de `schema.sql` e `seed.sql`.
2. Inserção de um pedido completo e válido (pedido, item personalizado, histórico e pagamento aprovado).
3. Tentativa de gravar **30 dados inválidos**, um de cada vez. Cada tentativa deve ser recusada pelo banco.
4. Consultas de exemplo usadas pela aplicação (frete por CEP e filtro da vitrine).

Data da execução: 06/11/2026 · PostgreSQL 16.2.

## Resultado da criação

- `schema.sql` e `seed.sql` executados sem erro; 15 tabelas criadas.
- Dados iniciais carregados:
  - `sabores`: 5 linhas
  - `ocasioes`: 5 linhas
  - `restricoes_alimentares`: 3 linhas
  - `opcoes_personalizacao`: 8 linhas
  - `cupcakes`: 8 linhas
  - `cupcake_ocasioes`: 15 linhas
  - `cupcake_restricoes`: 3 linhas
  - `areas_entrega`: 3 linhas
  - `cupons`: 3 linhas

## Casos inválidos (todos devem ser recusados)

| # | Tentativa | Recusado? | Código PostgreSQL | Restrição que barrou |
|---|---|---|---|---|
| 1 | e-mail duplicado (maiúsculas) | Sim | 23505 (violação de unicidade) | `uq_usuarios_email` |
| 2 | e-mail inválido | Sim | 23514 (violação de CHECK) | `usuarios_email_check` |
| 3 | telefone com letras | Sim | 23514 (violação de CHECK) | `usuarios_telefone_check` |
| 4 | perfil inexistente | Sim | 22P02 (valor fora do tipo enumerado) | tipo da coluna |
| 5 | CEP com 7 dígitos | Sim | 23514 (violação de CHECK) | `cep_check` |
| 6 | UF inexistente | Sim | 23514 (violação de CHECK) | `uf_check` |
| 7 | cupcake com preço zero (RN01) | Sim | 23514 (violação de CHECK) | `cupcakes_preco_check` |
| 8 | cupcake com estoque negativo (RN01) | Sim | 23514 (violação de CHECK) | `cupcakes_estoque_check` |
| 9 | cupcake com nome repetido | Sim | 23505 (violação de unicidade) | `cupcakes_nome_key` |
| 10 | excluir cupcake já vendido (RN19) | Sim | 23503 (violação de chave estrangeira) | `itens_pedido_cupcake_id_fkey` |
| 11 | excluir sabor em uso | Sim | 23503 (violação de chave estrangeira) | `cupcakes_sabor_id_fkey` |
| 12 | cupom percentual acima de 100% | Sim | 23514 (violação de CHECK) | `cupons_check1` |
| 13 | cupom com validade invertida | Sim | 23514 (violação de CHECK) | `cupons_check` |
| 14 | cupom com código minúsculo | Sim | 23514 (violação de CHECK) | `cupons_codigo_check` |
| 15 | área de entrega sobreposta (RN08) | Sim | 23P01 (violação de exclusão) | `areas_entrega_int4range_excl` |
| 16 | área com CEP final menor que inicial | Sim | 23514 (violação de CHECK) | `areas_entrega_check` |
| 17 | total diferente de subtotal - desconto + frete (RN09) | Sim | 23514 (violação de CHECK) | `pedidos_check1` |
| 18 | desconto maior que o subtotal (RN07) | Sim | 23514 (violação de CHECK) | `pedidos_check` |
| 19 | item com quantidade 21 (RN03) | Sim | 23514 (violação de CHECK) | `itens_pedido_quantidade_check` |
| 20 | item com quantidade 0 (RN03) | Sim | 23514 (violação de CHECK) | `itens_pedido_quantidade_check` |
| 21 | mensagem com 61 caracteres (RN04) | Sim | 22001 (texto maior que o permitido) | tipo da coluna |
| 22 | cobertura usada como recheio | Sim | 23503 (violação de chave estrangeira) | `itens_pedido_recheio_id_recheio_tipo_fkey` |
| 23 | recheio usado como cobertura | Sim | 23503 (violação de chave estrangeira) | `itens_pedido_cobertura_id_cobertura_tipo_fkey` |
| 24 | segundo pagamento aprovado no mesmo pedido | Sim | 23505 (violação de unicidade) | `uq_pagamento_aprovado` |
| 25 | cartão com número completo no campo final (RN12) | Sim | 22001 (texto maior que o permitido) | tipo da coluna |
| 26 | Pix sem código | Sim | 23514 (violação de CHECK) | `pagamentos_check` |
| 27 | Pix com dados de cartão | Sim | 23514 (violação de CHECK) | `pagamentos_check` |
| 28 | motivo de recusa em pagamento não recusado | Sim | 23514 (violação de CHECK) | `pagamentos_check1` |
| 29 | status de pedido inexistente | Sim | 22P02 (valor fora do tipo enumerado) | tipo da coluna |
| 30 | excluir cliente com pedidos | Sim | 23503 (violação de chave estrangeira) | `pedidos_usuario_id_fkey` |

## Consultas de exemplo

- schema.sql executado
- seed.sql executado
- pedido válido completo inserido (pedido, item personalizado, histórico, pagamento)
- busca de frete para CEP 01310-100: ('Centro e Bela Vista', Decimal('8.00'), 90)
- CEP fora da área encontra 0 faixa(s)
- filtro 'Sem lactose' + 'até R$ 15': ['Cacau 70% Vegano']

**Resultado: 30 de 30 tentativas inválidas recusadas.** Nenhuma regra de integridade deixou passar dado errado.
