# Dados — 03. Dicionário de Dados

> Exigência atendida: **R20** (documentação do banco e dicionário de dados).
> Gerado automaticamente a partir do banco por `database/gerar_dicionario.py`, usando os comentários gravados no `schema.sql`.

## Tipos enumerados

| Tipo | Valores |
|---|---|
| `metodo_pagamento` | PIX, CARTAO |
| `perfil_usuario` | CLIENTE, ADMINISTRADOR |
| `status_pagamento` | PENDENTE, APROVADO, RECUSADO, EXPIRADO |
| `status_pedido` | AGUARDANDO_PAGAMENTO, PAGO, EM_PREPARO, SAIU_PARA_ENTREGA, ENTREGUE, CANCELADO |
| `tipo_cupom` | PERCENTUAL, VALOR_FIXO |
| `tipo_opcao` | RECHEIO, COBERTURA |

## Domínios

| Domínio | Tipo base | Regra |
|---|---|---|
| `cep` | character(8) | `VALUE ~ '^[0-9]{8}$'` |
| `dinheiro` | numeric(10,2) | `VALUE >= 0` |
| `uf` | character(2) | `VALUE IN (AC, AL, AP, AM, BA, CE, DF, ES, GO, MA, MT, MS, MG, PA, PB, PR, PE, PI, RJ, RN, RS, RO, RR, SC, SP, SE, TO)` |

## usuarios

Pessoas com conta no sistema: clientes e administradores da loja.

| Coluna | Tipo | Nulo | Padrão | Restrições | Descrição |
|---|---|---|---|---|---|
| `id` | integer | não | automático (identity) | PK | Identificador do usuário. |
| `nome` | varchar(100) | não | — | length(TRIM(BOTH FROM nome)) >= 3 | Nome completo, no mínimo 3 caracteres. |
| `email` | varchar(254) | não | — | email ~ '^[^@[:space:]]+@[^@[:space:]]+\.[^@[:space:]]+$' | E-mail de acesso. Único, sem diferenciar maiúsculas e minúsculas (RN17). |
| `telefone` | varchar(11) | não | — | telefone ~ '^[0-9]{10,11}$' | Celular só com dígitos (DDD + número), 10 ou 11 dígitos. |
| `senha_hash` | varchar(255) | não | — | — | Hash da senha. A senha em texto nunca é gravada (RN17, RNF04). |
| `perfil` | perfil_usuario | não | 'CLIENTE'::perfil_usuario | — | CLIENTE ou ADMINISTRADOR. Só ADMINISTRADOR acessa o painel (RN20). |
| `criado_em` | timestamptz | não | now() | — | Data e hora do cadastro. |

Restrições e índices da tabela:

- `uq_usuarios_email` (índice): `btree (lower(email))`

## enderecos

Endereços de entrega cadastrados pelos clientes (RN18).

| Coluna | Tipo | Nulo | Padrão | Restrições | Descrição |
|---|---|---|---|---|---|
| `id` | integer | não | automático (identity) | PK | Identificador do endereço. |
| `usuario_id` | integer | não | — | FK → usuarios(id) (ON DELETE CASCADE) | Dono do endereço. Excluir o usuário exclui seus endereços. |
| `apelido` | varchar(30) | sim | — | — | Identificação opcional dada pelo cliente, ex.: Casa, Trabalho. |
| `cep` | cep | não | — | — | CEP só com dígitos (8). |
| `logradouro` | varchar(120) | não | — | — | Rua, avenida etc. |
| `numero` | varchar(10) | não | — | — | Número do imóvel. Texto para aceitar valores como "S/N" e "120A". |
| `complemento` | varchar(60) | sim | — | — | Complemento opcional, ex.: apartamento, bloco. |
| `bairro` | varchar(60) | não | — | — | Bairro. |
| `cidade` | varchar(60) | não | — | — | Cidade. |
| `uf` | uf | não | — | — | Sigla do estado. |
| `criado_em` | timestamptz | não | now() | — | Data e hora do cadastro do endereço. |

Restrições e índices da tabela:

- `ix_enderecos_usuario` (índice): `btree usuario_id`

## sabores

Famílias de sabor usadas no filtro da vitrine (US02).

| Coluna | Tipo | Nulo | Padrão | Restrições | Descrição |
|---|---|---|---|---|---|
| `id` | integer | não | automático (identity) | PK | Identificador do sabor. |
| `nome` | varchar(40) | não | — | Único | Nome do sabor, único. Ex.: Chocolate, Frutas. |

## ocasioes

Ocasiões para as quais um cupcake é indicado (US02).

| Coluna | Tipo | Nulo | Padrão | Restrições | Descrição |
|---|---|---|---|---|---|
| `id` | integer | não | automático (identity) | PK | Identificador da ocasião. |
| `nome` | varchar(40) | não | — | Único | Nome da ocasião, único. Ex.: Aniversário, Casamento. |

## restricoes_alimentares

Restrições alimentares atendidas pelos cupcakes (US02).

| Coluna | Tipo | Nulo | Padrão | Restrições | Descrição |
|---|---|---|---|---|---|
| `id` | integer | não | automático (identity) | PK | Identificador da restrição. |
| `nome` | varchar(40) | não | — | Único | Nome da restrição, único. Ex.: Sem lactose, Vegano. |

## cupcakes

Produtos do cardápio.

| Coluna | Tipo | Nulo | Padrão | Restrições | Descrição |
|---|---|---|---|---|---|
| `id` | integer | não | automático (identity) | PK | Identificador do cupcake. |
| `sabor_id` | integer | não | — | FK → sabores(id) (ON DELETE RESTRICT) | Sabor do cupcake. |
| `nome` | varchar(80) | não | — | length(TRIM(BOTH FROM nome)) > 0; Único | Nome exibido na vitrine, único, até 80 caracteres (RN01). |
| `descricao` | varchar(500) | não | — | — | Descrição exibida na página do produto. |
| `ingredientes` | varchar(500) | não | — | — | Lista de ingredientes exibida na página do produto (US03). |
| `preco` | numeric(8,2) | não | — | preco > 0 | Preço unitário atual em reais, maior que zero (RN01). |
| `foto_url` | varchar(500) | sim | — | — | Endereço da imagem do produto. |
| `estoque` | integer | não | 0 | estoque >= 0 | Unidades disponíveis. Zero = esgotado na vitrine (RN01, RN02). |
| `ativo` | boolean | não | true | — | Se falso, o cupcake não aparece na vitrine (RN02, RN19). |
| `personalizavel` | boolean | não | false | — | Se verdadeiro, aceita recheio, cobertura e mensagem (RN04). |
| `criado_em` | timestamptz | não | now() | — | Data e hora do cadastro. |
| `atualizado_em` | timestamptz | não | now() | — | Data e hora da última alteração. |

Restrições e índices da tabela:

- `ix_cupcakes_vitrine` (índice): `btree (ativo, sabor_id, preco)`

## cupcake_ocasioes

Associação N:N entre cupcakes e ocasiões.

| Coluna | Tipo | Nulo | Padrão | Restrições | Descrição |
|---|---|---|---|---|---|
| `cupcake_id` | integer | não | — | FK → cupcakes(id) (ON DELETE CASCADE); PK | Cupcake. |
| `ocasiao_id` | integer | não | — | FK → ocasioes(id) (ON DELETE RESTRICT); PK | Ocasião indicada. |

Restrições e índices da tabela:

- `ix_cupcake_ocasioes_ocasiao` (índice): `btree ocasiao_id`

## cupcake_restricoes

Associação N:N entre cupcakes e restrições alimentares.

| Coluna | Tipo | Nulo | Padrão | Restrições | Descrição |
|---|---|---|---|---|---|
| `cupcake_id` | integer | não | — | FK → cupcakes(id) (ON DELETE CASCADE); PK | Cupcake. |
| `restricao_id` | integer | não | — | FK → restricoes_alimentares(id) (ON DELETE RESTRICT); PK | Restrição atendida. |

Restrições e índices da tabela:

- `ix_cupcake_restricoes_restricao` (índice): `btree restricao_id`

## opcoes_personalizacao

Recheios e coberturas disponíveis para cupcakes personalizáveis (RN04).

| Coluna | Tipo | Nulo | Padrão | Restrições | Descrição |
|---|---|---|---|---|---|
| `id` | integer | não | automático (identity) | PK | Identificador da opção. |
| `tipo` | tipo_opcao | não | — | — | RECHEIO ou COBERTURA. |
| `nome` | varchar(40) | não | — | — | Nome da opção, único dentro do tipo. |
| `acrescimo` | numeric(6,2) | não | 0 | acrescimo >= 0 | Valor somado ao preço unitário quando a opção é escolhida. |
| `ativo` | boolean | não | true | — | Se falso, a opção não é oferecida em novos pedidos. |

Restrições e índices da tabela:

- `opcoes_personalizacao_id_tipo_key`: `UNIQUE (id, tipo)`
- `opcoes_personalizacao_tipo_nome_key`: `UNIQUE (tipo, nome)`

## cupons

Cupons de desconto. No MVP são carregados por script (L11).

| Coluna | Tipo | Nulo | Padrão | Restrições | Descrição |
|---|---|---|---|---|---|
| `id` | integer | não | automático (identity) | PK | Identificador do cupom. |
| `codigo` | varchar(20) | não | — | codigo ~ '^[A-Z0-9]{3,20}$'; Único | Código digitado pelo cliente: letras maiúsculas e números, único. |
| `tipo` | tipo_cupom | não | — | — | PERCENTUAL ou VALOR_FIXO (RN07). |
| `valor` | numeric(8,2) | não | — | valor > 0 | Percentual (1 a 100) ou valor em reais, conforme o tipo. |
| `valor_minimo` | dinheiro | não | 0 | — | Subtotal mínimo do pedido para o cupom valer (RN07). |
| `valido_de` | date | não | — | — | Primeiro dia de validade. |
| `valido_ate` | date | não | — | — | Último dia de validade. |
| `ativo` | boolean | não | true | — | Se falso, o cupom não é aceito mesmo dentro da validade. |

Restrições e índices da tabela:

- `cupons_check`: `valido_ate >= valido_de`
- `cupons_check1`: `(tipo <> 'PERCENTUAL') OR (valor <= 100)`

## areas_entrega

Faixas de CEP atendidas pela loja, com frete e prazo (RN08). As faixas não podem se sobrepor.

| Coluna | Tipo | Nulo | Padrão | Restrições | Descrição |
|---|---|---|---|---|---|
| `id` | integer | não | automático (identity) | PK | Identificador da área. |
| `nome` | varchar(60) | não | — | — | Nome da região, ex.: Centro. |
| `cep_inicial` | cep | não | — | — | Primeiro CEP da faixa. |
| `cep_final` | cep | não | — | — | Último CEP da faixa (inclusive). |
| `valor_frete` | numeric(6,2) | não | — | valor_frete >= 0 | Frete cobrado para a faixa, em reais. |
| `prazo_minutos` | integer | não | — | prazo_minutos > 0 | Prazo de entrega em minutos. |

Restrições e índices da tabela:

- `areas_entrega_check`: `cep_final >= cep_inicial`

## pedidos

Pedidos feitos pelos clientes. Valores e endereço são copiados no momento da compra (RN10).

| Coluna | Tipo | Nulo | Padrão | Restrições | Descrição |
|---|---|---|---|---|---|
| `id` | integer | não | automático (identity) | PK | Número do pedido (exibido com 6 dígitos, ex.: #000128). |
| `usuario_id` | integer | não | — | FK → usuarios(id) (ON DELETE RESTRICT) | Cliente que fez o pedido. |
| `cupom_id` | integer | sim | — | FK → cupons(id) (ON DELETE RESTRICT) | Cupom aplicado, se houver (no máximo um, RN07). |
| `status` | status_pedido | não | 'AGUARDANDO_PAGAMENTO'::status_pedido | — | Etapa atual do pedido (RN15). |
| `subtotal` | dinheiro | não | — | — | Soma de quantidade x preço unitário dos itens. |
| `desconto` | dinheiro | não | 0 | — | Desconto do cupom, nunca maior que o subtotal (RN07). |
| `frete` | dinheiro | não | — | — | Frete da área de entrega no momento da compra. |
| `total` | dinheiro | não | — | — | Valor cobrado: subtotal - desconto + frete (RN09). |
| `prazo_minutos` | integer | não | — | prazo_minutos > 0 | Prazo de entrega informado ao cliente na compra. |
| `entrega_cep` | cep | não | — | — | Cópia do CEP de entrega. |
| `entrega_logradouro` | varchar(120) | não | — | — | Cópia do logradouro de entrega. |
| `entrega_numero` | varchar(10) | não | — | — | Cópia do número de entrega. |
| `entrega_complemento` | varchar(60) | sim | — | — | Cópia do complemento de entrega. |
| `entrega_bairro` | varchar(60) | não | — | — | Cópia do bairro de entrega. |
| `entrega_cidade` | varchar(60) | não | — | — | Cópia da cidade de entrega. |
| `entrega_uf` | uf | não | — | — | Cópia da UF de entrega. |
| `visto_pelo_admin` | boolean | não | false | — | Falso enquanto a loja não abrir o pedido; usado no destaque "Novo" (CA17.6). |
| `criado_em` | timestamptz | não | now() | — | Data e hora em que o pedido foi criado. |

Restrições e índices da tabela:

- `pedidos_check`: `desconto <= subtotal`
- `pedidos_check1`: `total = ((subtotal - desconto) + frete)`
- `ix_pedidos_cliente` (índice): `btree (usuario_id, criado_em DESC)`
- `ix_pedidos_novos` (índice): `btree criado_em WHERE ((status = 'PAGO') AND (NOT visto_pelo_admin))`
- `ix_pedidos_status` (índice): `btree (status, criado_em DESC)`

## itens_pedido

Itens de cada pedido, com o preço da época da compra (RN10).

| Coluna | Tipo | Nulo | Padrão | Restrições | Descrição |
|---|---|---|---|---|---|
| `id` | integer | não | automático (identity) | PK | Identificador do item. |
| `pedido_id` | integer | não | — | FK → pedidos(id) (ON DELETE CASCADE) | Pedido ao qual o item pertence. |
| `cupcake_id` | integer | não | — | FK → cupcakes(id) (ON DELETE RESTRICT) | Cupcake vendido. |
| `quantidade` | integer | não | — | (quantidade >= 1) AND (quantidade <= 20) | Quantidade, de 1 a 20 (RN03). |
| `preco_unitario` | numeric(8,2) | não | — | preco_unitario > 0 | Preço unitário cobrado, já com acréscimos de personalização. |
| `recheio_id` | integer | sim | — | — | Recheio escolhido, se houver. |
| `recheio_tipo` | tipo_opcao | sim | gerado: 'RECHEIO'::tipo_opcao | — | Coluna técnica fixa em RECHEIO; garante pela chave estrangeira que recheio_id aponta para um recheio. |
| `cobertura_id` | integer | sim | — | — | Cobertura escolhida, se houver. |
| `cobertura_tipo` | tipo_opcao | sim | gerado: 'COBERTURA'::tipo_opcao | — | Coluna técnica fixa em COBERTURA; garante pela chave estrangeira que cobertura_id aponta para uma cobertura. |
| `mensagem` | varchar(60) | sim | — | — | Mensagem do topper, até 60 caracteres (RN04). |

Restrições e índices da tabela:

- `itens_pedido_cobertura_id_cobertura_tipo_fkey`: `FOREIGN KEY (cobertura_id, cobertura_tipo) REFERENCES opcoes_personalizacao(id, tipo) ON DELETE RESTRICT`
- `itens_pedido_recheio_id_recheio_tipo_fkey`: `FOREIGN KEY (recheio_id, recheio_tipo) REFERENCES opcoes_personalizacao(id, tipo) ON DELETE RESTRICT`
- `ix_itens_pedido_cupcake` (índice): `btree cupcake_id`
- `ix_itens_pedido_pedido` (índice): `btree pedido_id`

## pagamentos

Tentativas de pagamento de cada pedido (RN14). Pagamento simulado no MVP (RN11).

| Coluna | Tipo | Nulo | Padrão | Restrições | Descrição |
|---|---|---|---|---|---|
| `id` | integer | não | automático (identity) | PK | Identificador da tentativa. |
| `pedido_id` | integer | não | — | FK → pedidos(id) (ON DELETE CASCADE) | Pedido pago por esta tentativa. |
| `metodo` | metodo_pagamento | não | — | — | PIX ou CARTAO. |
| `status` | status_pagamento | não | 'PENDENTE'::status_pagamento | — | PENDENTE, APROVADO, RECUSADO ou EXPIRADO. Só um aprovado por pedido. |
| `valor` | numeric(10,2) | não | — | valor > 0 | Valor da tentativa (igual ao total do pedido). |
| `pix_codigo` | varchar(200) | sim | — | — | Código Pix fictício (somente método PIX). |
| `pix_expira_em` | timestamptz | sim | — | — | Fim da validade do código Pix: criação + 15 minutos (RN11). |
| `cartao_bandeira` | varchar(20) | sim | — | — | Bandeira do cartão (somente método CARTAO). |
| `cartao_final` | character(4) | sim | — | cartao_final ~ '^[0-9]{4}$' | Quatro últimos dígitos do cartão. Número completo e CVV nunca são gravados (RN12). |
| `motivo_recusa` | varchar(120) | sim | — | — | Motivo informado quando o status é RECUSADO. |
| `criado_em` | timestamptz | não | now() | — | Data e hora da tentativa. |
| `atualizado_em` | timestamptz | não | now() | — | Data e hora da última mudança de status. |

Restrições e índices da tabela:

- `pagamentos_check`: `((metodo = 'PIX') AND (pix_codigo IS NOT NULL) AND (pix_expira_em IS NOT NULL) AND (cartao_bandeira IS NULL) AND (cartao_final IS NULL)) OR ((metodo = 'CARTAO') AND (cartao_bandeira IS NOT NULL) AND (cartao_final IS NOT NULL) AND (pix_codigo IS NULL) AND (pix_expira_em IS NULL))`
- `pagamentos_check1`: `(status = 'RECUSADO') OR (motivo_recusa IS NULL)`
- `ix_pagamentos_pedido` (índice): `btree pedido_id`
- `uq_pagamento_aprovado` (índice): `btree pedido_id WHERE (status = 'APROVADO')`

## historico_status

Linha do tempo de cada pedido (CA12.1, CA17.3).

| Coluna | Tipo | Nulo | Padrão | Restrições | Descrição |
|---|---|---|---|---|---|
| `id` | integer | não | automático (identity) | PK | Identificador do registro. |
| `pedido_id` | integer | não | — | FK → pedidos(id) (ON DELETE CASCADE) | Pedido. |
| `status` | status_pedido | não | — | — | Status assumido pelo pedido. |
| `responsavel_id` | integer | sim | — | FK → usuarios(id) (ON DELETE SET NULL) | Administrador que fez a mudança; nulo quando a mudança é automática. |
| `registrado_em` | timestamptz | não | now() | — | Data e hora da mudança. |

Restrições e índices da tabela:

- `ix_historico_pedido` (índice): `btree (pedido_id, registrado_em)`
