-- =====================================================================
-- Cupcakes Gourmet — Projeto físico do banco de dados
-- SGBD: PostgreSQL 16
-- Origem: modelo lógico em docs/situacao-1/dados/02-modelo-logico.md
-- Executar em um banco vazio:  psql -d cupcakes -f database/schema.sql
-- =====================================================================

BEGIN;

-- ---------------------------------------------------------------------
-- Tipos enumerados (domínios fechados de valores)
-- ---------------------------------------------------------------------
CREATE TYPE perfil_usuario   AS ENUM ('CLIENTE', 'ADMINISTRADOR');
CREATE TYPE status_pedido    AS ENUM ('AGUARDANDO_PAGAMENTO', 'PAGO', 'EM_PREPARO',
                                      'SAIU_PARA_ENTREGA', 'ENTREGUE', 'CANCELADO');
CREATE TYPE metodo_pagamento AS ENUM ('PIX', 'CARTAO');
CREATE TYPE status_pagamento AS ENUM ('PENDENTE', 'APROVADO', 'RECUSADO', 'EXPIRADO');
CREATE TYPE tipo_cupom       AS ENUM ('PERCENTUAL', 'VALOR_FIXO');
CREATE TYPE tipo_opcao       AS ENUM ('RECHEIO', 'COBERTURA');

-- ---------------------------------------------------------------------
-- Domínios reutilizáveis
-- ---------------------------------------------------------------------
CREATE DOMAIN cep AS CHAR(8)
  CHECK (VALUE ~ '^[0-9]{8}$');

CREATE DOMAIN uf AS CHAR(2)
  CHECK (VALUE IN ('AC','AL','AP','AM','BA','CE','DF','ES','GO','MA','MT','MS','MG','PA',
                   'PB','PR','PE','PI','RJ','RN','RS','RO','RR','SC','SP','SE','TO'));

CREATE DOMAIN dinheiro AS NUMERIC(10,2)
  CHECK (VALUE >= 0);

-- ---------------------------------------------------------------------
-- Usuários e endereços
-- ---------------------------------------------------------------------
CREATE TABLE usuarios (
  id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  nome        VARCHAR(100)   NOT NULL CHECK (length(trim(nome)) >= 3),
  email       VARCHAR(254)   NOT NULL CHECK (email ~ '^[^@[:space:]]+@[^@[:space:]]+\.[^@[:space:]]+$'),
  telefone    VARCHAR(11)    NOT NULL CHECK (telefone ~ '^[0-9]{10,11}$'),
  senha_hash  VARCHAR(255)   NOT NULL,
  perfil      perfil_usuario NOT NULL DEFAULT 'CLIENTE',
  criado_em   TIMESTAMPTZ    NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX uq_usuarios_email ON usuarios (lower(email));

CREATE TABLE enderecos (
  id           INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  usuario_id   INTEGER      NOT NULL REFERENCES usuarios (id) ON DELETE CASCADE,
  apelido      VARCHAR(30),
  cep          cep          NOT NULL,
  logradouro   VARCHAR(120) NOT NULL,
  numero       VARCHAR(10)  NOT NULL,
  complemento  VARCHAR(60),
  bairro       VARCHAR(60)  NOT NULL,
  cidade       VARCHAR(60)  NOT NULL,
  uf           uf           NOT NULL,
  criado_em    TIMESTAMPTZ  NOT NULL DEFAULT now()
);
CREATE INDEX ix_enderecos_usuario ON enderecos (usuario_id);

-- ---------------------------------------------------------------------
-- Catálogo
-- ---------------------------------------------------------------------
CREATE TABLE sabores (
  id    INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  nome  VARCHAR(40) NOT NULL UNIQUE
);

CREATE TABLE ocasioes (
  id    INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  nome  VARCHAR(40) NOT NULL UNIQUE
);

CREATE TABLE restricoes_alimentares (
  id    INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  nome  VARCHAR(40) NOT NULL UNIQUE
);

CREATE TABLE cupcakes (
  id              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  sabor_id        INTEGER       NOT NULL REFERENCES sabores (id) ON DELETE RESTRICT,
  nome            VARCHAR(80)   NOT NULL UNIQUE CHECK (length(trim(nome)) > 0),
  descricao       VARCHAR(500)  NOT NULL,
  ingredientes    VARCHAR(500)  NOT NULL,
  preco           NUMERIC(8,2)  NOT NULL CHECK (preco > 0),
  foto_url        VARCHAR(500),
  estoque         INTEGER       NOT NULL DEFAULT 0 CHECK (estoque >= 0),
  ativo           BOOLEAN       NOT NULL DEFAULT TRUE,
  personalizavel  BOOLEAN       NOT NULL DEFAULT FALSE,
  criado_em       TIMESTAMPTZ   NOT NULL DEFAULT now(),
  atualizado_em   TIMESTAMPTZ   NOT NULL DEFAULT now()
);
CREATE INDEX ix_cupcakes_vitrine ON cupcakes (ativo, sabor_id, preco);

CREATE TABLE cupcake_ocasioes (
  cupcake_id  INTEGER NOT NULL REFERENCES cupcakes (id) ON DELETE CASCADE,
  ocasiao_id  INTEGER NOT NULL REFERENCES ocasioes (id) ON DELETE RESTRICT,
  PRIMARY KEY (cupcake_id, ocasiao_id)
);
CREATE INDEX ix_cupcake_ocasioes_ocasiao ON cupcake_ocasioes (ocasiao_id);

CREATE TABLE cupcake_restricoes (
  cupcake_id    INTEGER NOT NULL REFERENCES cupcakes (id) ON DELETE CASCADE,
  restricao_id  INTEGER NOT NULL REFERENCES restricoes_alimentares (id) ON DELETE RESTRICT,
  PRIMARY KEY (cupcake_id, restricao_id)
);
CREATE INDEX ix_cupcake_restricoes_restricao ON cupcake_restricoes (restricao_id);

CREATE TABLE opcoes_personalizacao (
  id         INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  tipo       tipo_opcao   NOT NULL,
  nome       VARCHAR(40)  NOT NULL,
  acrescimo  NUMERIC(6,2) NOT NULL DEFAULT 0 CHECK (acrescimo >= 0),
  ativo      BOOLEAN      NOT NULL DEFAULT TRUE,
  UNIQUE (tipo, nome),
  UNIQUE (id, tipo)            -- permite que itens_pedido garanta o tipo certo via FK composta
);

-- ---------------------------------------------------------------------
-- Promoções e entrega
-- ---------------------------------------------------------------------
CREATE TABLE cupons (
  id            INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  codigo        VARCHAR(20)  NOT NULL UNIQUE CHECK (codigo ~ '^[A-Z0-9]{3,20}$'),
  tipo          tipo_cupom   NOT NULL,
  valor         NUMERIC(8,2) NOT NULL CHECK (valor > 0),
  valor_minimo  dinheiro     NOT NULL DEFAULT 0,
  valido_de     DATE         NOT NULL,
  valido_ate    DATE         NOT NULL,
  ativo         BOOLEAN      NOT NULL DEFAULT TRUE,
  CHECK (valido_ate >= valido_de),
  CHECK (tipo <> 'PERCENTUAL' OR valor <= 100)
);

CREATE TABLE areas_entrega (
  id             INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  nome           VARCHAR(60)  NOT NULL,
  cep_inicial    cep          NOT NULL,
  cep_final      cep          NOT NULL,
  valor_frete    NUMERIC(6,2) NOT NULL CHECK (valor_frete >= 0),
  prazo_minutos  INTEGER      NOT NULL CHECK (prazo_minutos > 0),
  CHECK (cep_final >= cep_inicial),
  -- duas áreas não podem cobrir o mesmo CEP (RN08)
  EXCLUDE USING gist (int4range(cep_inicial::integer, cep_final::integer, '[]') WITH &&)
);

-- ---------------------------------------------------------------------
-- Pedidos
-- ---------------------------------------------------------------------
CREATE TABLE pedidos (
  id                   INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  usuario_id           INTEGER       NOT NULL REFERENCES usuarios (id) ON DELETE RESTRICT,
  cupom_id             INTEGER       REFERENCES cupons (id) ON DELETE RESTRICT,
  status               status_pedido NOT NULL DEFAULT 'AGUARDANDO_PAGAMENTO',
  subtotal             dinheiro      NOT NULL,
  desconto             dinheiro      NOT NULL DEFAULT 0,
  frete                dinheiro      NOT NULL,
  total                dinheiro      NOT NULL,
  prazo_minutos        INTEGER       NOT NULL CHECK (prazo_minutos > 0),
  entrega_cep          cep           NOT NULL,
  entrega_logradouro   VARCHAR(120)  NOT NULL,
  entrega_numero       VARCHAR(10)   NOT NULL,
  entrega_complemento  VARCHAR(60),
  entrega_bairro       VARCHAR(60)   NOT NULL,
  entrega_cidade       VARCHAR(60)   NOT NULL,
  entrega_uf           uf            NOT NULL,
  visto_pelo_admin     BOOLEAN       NOT NULL DEFAULT FALSE,
  criado_em            TIMESTAMPTZ   NOT NULL DEFAULT now(),
  CHECK (desconto <= subtotal),                          -- RN07
  CHECK (total = subtotal - desconto + frete)            -- RN09
);
CREATE INDEX ix_pedidos_cliente ON pedidos (usuario_id, criado_em DESC);
CREATE INDEX ix_pedidos_status  ON pedidos (status, criado_em DESC);
CREATE INDEX ix_pedidos_novos   ON pedidos (criado_em) WHERE status = 'PAGO' AND NOT visto_pelo_admin;

CREATE TABLE itens_pedido (
  id              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  pedido_id       INTEGER      NOT NULL REFERENCES pedidos (id) ON DELETE CASCADE,
  cupcake_id      INTEGER      NOT NULL REFERENCES cupcakes (id) ON DELETE RESTRICT,
  quantidade      INTEGER      NOT NULL CHECK (quantidade BETWEEN 1 AND 20),      -- RN03
  preco_unitario  NUMERIC(8,2) NOT NULL CHECK (preco_unitario > 0),              -- RN10
  recheio_id      INTEGER,
  recheio_tipo    tipo_opcao   GENERATED ALWAYS AS ('RECHEIO') STORED,
  cobertura_id    INTEGER,
  cobertura_tipo  tipo_opcao   GENERATED ALWAYS AS ('COBERTURA') STORED,
  mensagem        VARCHAR(60),                                                    -- RN04
  FOREIGN KEY (recheio_id, recheio_tipo)     REFERENCES opcoes_personalizacao (id, tipo) ON DELETE RESTRICT,
  FOREIGN KEY (cobertura_id, cobertura_tipo) REFERENCES opcoes_personalizacao (id, tipo) ON DELETE RESTRICT
);
CREATE INDEX ix_itens_pedido_pedido  ON itens_pedido (pedido_id);
CREATE INDEX ix_itens_pedido_cupcake ON itens_pedido (cupcake_id);

CREATE TABLE pagamentos (
  id               INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  pedido_id        INTEGER          NOT NULL REFERENCES pedidos (id) ON DELETE CASCADE,
  metodo           metodo_pagamento NOT NULL,
  status           status_pagamento NOT NULL DEFAULT 'PENDENTE',
  valor            NUMERIC(10,2)    NOT NULL CHECK (valor > 0),
  pix_codigo       VARCHAR(200),
  pix_expira_em    TIMESTAMPTZ,
  cartao_bandeira  VARCHAR(20),
  cartao_final     CHAR(4)          CHECK (cartao_final ~ '^[0-9]{4}$'),           -- RN12
  motivo_recusa    VARCHAR(120),
  criado_em        TIMESTAMPTZ      NOT NULL DEFAULT now(),
  atualizado_em    TIMESTAMPTZ      NOT NULL DEFAULT now(),
  CHECK (
    (metodo = 'PIX'    AND pix_codigo IS NOT NULL AND pix_expira_em IS NOT NULL
                       AND cartao_bandeira IS NULL AND cartao_final IS NULL)
    OR
    (metodo = 'CARTAO' AND cartao_bandeira IS NOT NULL AND cartao_final IS NOT NULL
                       AND pix_codigo IS NULL AND pix_expira_em IS NULL)
  ),
  CHECK (status = 'RECUSADO' OR motivo_recusa IS NULL)
);
CREATE INDEX ix_pagamentos_pedido ON pagamentos (pedido_id);
-- um pedido nunca pode ter dois pagamentos aprovados
CREATE UNIQUE INDEX uq_pagamento_aprovado ON pagamentos (pedido_id) WHERE status = 'APROVADO';

CREATE TABLE historico_status (
  id              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  pedido_id       INTEGER       NOT NULL REFERENCES pedidos (id) ON DELETE CASCADE,
  status          status_pedido NOT NULL,
  responsavel_id  INTEGER       REFERENCES usuarios (id) ON DELETE SET NULL,
  registrado_em   TIMESTAMPTZ   NOT NULL DEFAULT now()
);
CREATE INDEX ix_historico_pedido ON historico_status (pedido_id, registrado_em);

-- ---------------------------------------------------------------------
-- Documentação no próprio banco (base do dicionário de dados)
-- ---------------------------------------------------------------------
COMMENT ON TABLE usuarios IS 'Pessoas com conta no sistema: clientes e administradores da loja.';
COMMENT ON COLUMN usuarios.id IS 'Identificador do usuário.';
COMMENT ON COLUMN usuarios.nome IS 'Nome completo, no mínimo 3 caracteres.';
COMMENT ON COLUMN usuarios.email IS 'E-mail de acesso. Único, sem diferenciar maiúsculas e minúsculas (RN17).';
COMMENT ON COLUMN usuarios.telefone IS 'Celular só com dígitos (DDD + número), 10 ou 11 dígitos.';
COMMENT ON COLUMN usuarios.senha_hash IS 'Hash da senha. A senha em texto nunca é gravada (RN17, RNF04).';
COMMENT ON COLUMN usuarios.perfil IS 'CLIENTE ou ADMINISTRADOR. Só ADMINISTRADOR acessa o painel (RN20).';
COMMENT ON COLUMN usuarios.criado_em IS 'Data e hora do cadastro.';

COMMENT ON TABLE enderecos IS 'Endereços de entrega cadastrados pelos clientes (RN18).';
COMMENT ON COLUMN enderecos.id IS 'Identificador do endereço.';
COMMENT ON COLUMN enderecos.usuario_id IS 'Dono do endereço. Excluir o usuário exclui seus endereços.';
COMMENT ON COLUMN enderecos.apelido IS 'Identificação opcional dada pelo cliente, ex.: Casa, Trabalho.';
COMMENT ON COLUMN enderecos.cep IS 'CEP só com dígitos (8).';
COMMENT ON COLUMN enderecos.logradouro IS 'Rua, avenida etc.';
COMMENT ON COLUMN enderecos.numero IS 'Número do imóvel. Texto para aceitar valores como "S/N" e "120A".';
COMMENT ON COLUMN enderecos.complemento IS 'Complemento opcional, ex.: apartamento, bloco.';
COMMENT ON COLUMN enderecos.bairro IS 'Bairro.';
COMMENT ON COLUMN enderecos.cidade IS 'Cidade.';
COMMENT ON COLUMN enderecos.uf IS 'Sigla do estado.';
COMMENT ON COLUMN enderecos.criado_em IS 'Data e hora do cadastro do endereço.';

COMMENT ON TABLE sabores IS 'Famílias de sabor usadas no filtro da vitrine (US02).';
COMMENT ON COLUMN sabores.id IS 'Identificador do sabor.';
COMMENT ON COLUMN sabores.nome IS 'Nome do sabor, único. Ex.: Chocolate, Frutas.';

COMMENT ON TABLE ocasioes IS 'Ocasiões para as quais um cupcake é indicado (US02).';
COMMENT ON COLUMN ocasioes.id IS 'Identificador da ocasião.';
COMMENT ON COLUMN ocasioes.nome IS 'Nome da ocasião, único. Ex.: Aniversário, Casamento.';

COMMENT ON TABLE restricoes_alimentares IS 'Restrições alimentares atendidas pelos cupcakes (US02).';
COMMENT ON COLUMN restricoes_alimentares.id IS 'Identificador da restrição.';
COMMENT ON COLUMN restricoes_alimentares.nome IS 'Nome da restrição, único. Ex.: Sem lactose, Vegano.';

COMMENT ON TABLE cupcakes IS 'Produtos do cardápio.';
COMMENT ON COLUMN cupcakes.id IS 'Identificador do cupcake.';
COMMENT ON COLUMN cupcakes.sabor_id IS 'Sabor do cupcake.';
COMMENT ON COLUMN cupcakes.nome IS 'Nome exibido na vitrine, único, até 80 caracteres (RN01).';
COMMENT ON COLUMN cupcakes.descricao IS 'Descrição exibida na página do produto.';
COMMENT ON COLUMN cupcakes.ingredientes IS 'Lista de ingredientes exibida na página do produto (US03).';
COMMENT ON COLUMN cupcakes.preco IS 'Preço unitário atual em reais, maior que zero (RN01).';
COMMENT ON COLUMN cupcakes.foto_url IS 'Endereço da imagem do produto.';
COMMENT ON COLUMN cupcakes.estoque IS 'Unidades disponíveis. Zero = esgotado na vitrine (RN01, RN02).';
COMMENT ON COLUMN cupcakes.ativo IS 'Se falso, o cupcake não aparece na vitrine (RN02, RN19).';
COMMENT ON COLUMN cupcakes.personalizavel IS 'Se verdadeiro, aceita recheio, cobertura e mensagem (RN04).';
COMMENT ON COLUMN cupcakes.criado_em IS 'Data e hora do cadastro.';
COMMENT ON COLUMN cupcakes.atualizado_em IS 'Data e hora da última alteração.';

COMMENT ON TABLE cupcake_ocasioes IS 'Associação N:N entre cupcakes e ocasiões.';
COMMENT ON COLUMN cupcake_ocasioes.cupcake_id IS 'Cupcake.';
COMMENT ON COLUMN cupcake_ocasioes.ocasiao_id IS 'Ocasião indicada.';

COMMENT ON TABLE cupcake_restricoes IS 'Associação N:N entre cupcakes e restrições alimentares.';
COMMENT ON COLUMN cupcake_restricoes.cupcake_id IS 'Cupcake.';
COMMENT ON COLUMN cupcake_restricoes.restricao_id IS 'Restrição atendida.';

COMMENT ON TABLE opcoes_personalizacao IS 'Recheios e coberturas disponíveis para cupcakes personalizáveis (RN04).';
COMMENT ON COLUMN opcoes_personalizacao.id IS 'Identificador da opção.';
COMMENT ON COLUMN opcoes_personalizacao.tipo IS 'RECHEIO ou COBERTURA.';
COMMENT ON COLUMN opcoes_personalizacao.nome IS 'Nome da opção, único dentro do tipo.';
COMMENT ON COLUMN opcoes_personalizacao.acrescimo IS 'Valor somado ao preço unitário quando a opção é escolhida.';
COMMENT ON COLUMN opcoes_personalizacao.ativo IS 'Se falso, a opção não é oferecida em novos pedidos.';

COMMENT ON TABLE cupons IS 'Cupons de desconto. No MVP são carregados por script (L11).';
COMMENT ON COLUMN cupons.id IS 'Identificador do cupom.';
COMMENT ON COLUMN cupons.codigo IS 'Código digitado pelo cliente: letras maiúsculas e números, único.';
COMMENT ON COLUMN cupons.tipo IS 'PERCENTUAL ou VALOR_FIXO (RN07).';
COMMENT ON COLUMN cupons.valor IS 'Percentual (1 a 100) ou valor em reais, conforme o tipo.';
COMMENT ON COLUMN cupons.valor_minimo IS 'Subtotal mínimo do pedido para o cupom valer (RN07).';
COMMENT ON COLUMN cupons.valido_de IS 'Primeiro dia de validade.';
COMMENT ON COLUMN cupons.valido_ate IS 'Último dia de validade.';
COMMENT ON COLUMN cupons.ativo IS 'Se falso, o cupom não é aceito mesmo dentro da validade.';

COMMENT ON TABLE areas_entrega IS 'Faixas de CEP atendidas pela loja, com frete e prazo (RN08). As faixas não podem se sobrepor.';
COMMENT ON COLUMN areas_entrega.id IS 'Identificador da área.';
COMMENT ON COLUMN areas_entrega.nome IS 'Nome da região, ex.: Centro.';
COMMENT ON COLUMN areas_entrega.cep_inicial IS 'Primeiro CEP da faixa.';
COMMENT ON COLUMN areas_entrega.cep_final IS 'Último CEP da faixa (inclusive).';
COMMENT ON COLUMN areas_entrega.valor_frete IS 'Frete cobrado para a faixa, em reais.';
COMMENT ON COLUMN areas_entrega.prazo_minutos IS 'Prazo de entrega em minutos.';

COMMENT ON TABLE pedidos IS 'Pedidos feitos pelos clientes. Valores e endereço são copiados no momento da compra (RN10).';
COMMENT ON COLUMN pedidos.id IS 'Número do pedido (exibido com 6 dígitos, ex.: #000128).';
COMMENT ON COLUMN pedidos.usuario_id IS 'Cliente que fez o pedido.';
COMMENT ON COLUMN pedidos.cupom_id IS 'Cupom aplicado, se houver (no máximo um, RN07).';
COMMENT ON COLUMN pedidos.status IS 'Etapa atual do pedido (RN15).';
COMMENT ON COLUMN pedidos.subtotal IS 'Soma de quantidade x preço unitário dos itens.';
COMMENT ON COLUMN pedidos.desconto IS 'Desconto do cupom, nunca maior que o subtotal (RN07).';
COMMENT ON COLUMN pedidos.frete IS 'Frete da área de entrega no momento da compra.';
COMMENT ON COLUMN pedidos.total IS 'Valor cobrado: subtotal - desconto + frete (RN09).';
COMMENT ON COLUMN pedidos.prazo_minutos IS 'Prazo de entrega informado ao cliente na compra.';
COMMENT ON COLUMN pedidos.entrega_cep IS 'Cópia do CEP de entrega.';
COMMENT ON COLUMN pedidos.entrega_logradouro IS 'Cópia do logradouro de entrega.';
COMMENT ON COLUMN pedidos.entrega_numero IS 'Cópia do número de entrega.';
COMMENT ON COLUMN pedidos.entrega_complemento IS 'Cópia do complemento de entrega.';
COMMENT ON COLUMN pedidos.entrega_bairro IS 'Cópia do bairro de entrega.';
COMMENT ON COLUMN pedidos.entrega_cidade IS 'Cópia da cidade de entrega.';
COMMENT ON COLUMN pedidos.entrega_uf IS 'Cópia da UF de entrega.';
COMMENT ON COLUMN pedidos.visto_pelo_admin IS 'Falso enquanto a loja não abrir o pedido; usado no destaque "Novo" (CA17.6).';
COMMENT ON COLUMN pedidos.criado_em IS 'Data e hora em que o pedido foi criado.';

COMMENT ON TABLE itens_pedido IS 'Itens de cada pedido, com o preço da época da compra (RN10).';
COMMENT ON COLUMN itens_pedido.id IS 'Identificador do item.';
COMMENT ON COLUMN itens_pedido.pedido_id IS 'Pedido ao qual o item pertence.';
COMMENT ON COLUMN itens_pedido.cupcake_id IS 'Cupcake vendido.';
COMMENT ON COLUMN itens_pedido.quantidade IS 'Quantidade, de 1 a 20 (RN03).';
COMMENT ON COLUMN itens_pedido.preco_unitario IS 'Preço unitário cobrado, já com acréscimos de personalização.';
COMMENT ON COLUMN itens_pedido.recheio_id IS 'Recheio escolhido, se houver.';
COMMENT ON COLUMN itens_pedido.recheio_tipo IS 'Coluna técnica fixa em RECHEIO; garante pela chave estrangeira que recheio_id aponta para um recheio.';
COMMENT ON COLUMN itens_pedido.cobertura_id IS 'Cobertura escolhida, se houver.';
COMMENT ON COLUMN itens_pedido.cobertura_tipo IS 'Coluna técnica fixa em COBERTURA; garante pela chave estrangeira que cobertura_id aponta para uma cobertura.';
COMMENT ON COLUMN itens_pedido.mensagem IS 'Mensagem do topper, até 60 caracteres (RN04).';

COMMENT ON TABLE pagamentos IS 'Tentativas de pagamento de cada pedido (RN14). Pagamento simulado no MVP (RN11).';
COMMENT ON COLUMN pagamentos.id IS 'Identificador da tentativa.';
COMMENT ON COLUMN pagamentos.pedido_id IS 'Pedido pago por esta tentativa.';
COMMENT ON COLUMN pagamentos.metodo IS 'PIX ou CARTAO.';
COMMENT ON COLUMN pagamentos.status IS 'PENDENTE, APROVADO, RECUSADO ou EXPIRADO. Só um aprovado por pedido.';
COMMENT ON COLUMN pagamentos.valor IS 'Valor da tentativa (igual ao total do pedido).';
COMMENT ON COLUMN pagamentos.pix_codigo IS 'Código Pix fictício (somente método PIX).';
COMMENT ON COLUMN pagamentos.pix_expira_em IS 'Fim da validade do código Pix: criação + 15 minutos (RN11).';
COMMENT ON COLUMN pagamentos.cartao_bandeira IS 'Bandeira do cartão (somente método CARTAO).';
COMMENT ON COLUMN pagamentos.cartao_final IS 'Quatro últimos dígitos do cartão. Número completo e CVV nunca são gravados (RN12).';
COMMENT ON COLUMN pagamentos.motivo_recusa IS 'Motivo informado quando o status é RECUSADO.';
COMMENT ON COLUMN pagamentos.criado_em IS 'Data e hora da tentativa.';
COMMENT ON COLUMN pagamentos.atualizado_em IS 'Data e hora da última mudança de status.';

COMMENT ON TABLE historico_status IS 'Linha do tempo de cada pedido (CA12.1, CA17.3).';
COMMENT ON COLUMN historico_status.id IS 'Identificador do registro.';
COMMENT ON COLUMN historico_status.pedido_id IS 'Pedido.';
COMMENT ON COLUMN historico_status.status IS 'Status assumido pelo pedido.';
COMMENT ON COLUMN historico_status.responsavel_id IS 'Administrador que fez a mudança; nulo quando a mudança é automática.';
COMMENT ON COLUMN historico_status.registrado_em IS 'Data e hora da mudança.';

COMMIT;
