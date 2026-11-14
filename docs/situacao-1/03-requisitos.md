# 03 — Especificação de Requisitos

> Exigências atendidas: **R04** (histórias com critérios de aceitação e regras de negócio), **R05** (requisitos não funcionais) e **R06** (validação e rastreabilidade dos requisitos).
> Os critérios estão no formato **Dado / Quando / Então** e servem de base para os testes de aceitação da Situação 3 (**R39**).

## 1. Regras de negócio

| ID | Regra |
|---|---|
| RN01 | Todo cupcake tem nome (até 80 caracteres), preço maior que zero com 2 casas decimais e estoque maior ou igual a zero. |
| RN02 | Cupcake **inativo** não aparece na vitrine. Cupcake **ativo com estoque zero** aparece como "Esgotado" e não pode ser adicionado ao carrinho. |
| RN03 | A quantidade de cada item no carrinho vai de 1 a 20 e não pode passar do estoque disponível. |
| RN04 | Apenas cupcakes marcados como personalizáveis aceitam personalização: um recheio, uma cobertura e uma mensagem opcional de até 60 caracteres. Recheio e cobertura podem ter acréscimo de preço. |
| RN05 | O mesmo cupcake com personalizações diferentes ocupa linhas diferentes no carrinho. |
| RN06 | Visitante pode montar o carrinho, mas só finaliza o pedido logado. O carrinho é preservado ao fazer login ou se cadastrar. |
| RN07 | Cada pedido aceita **um** cupom. O cupom precisa estar ativo, dentro da validade e o subtotal precisa atingir o valor mínimo do cupom. O desconto é percentual ou em valor fixo, nunca maior que o subtotal, e não se aplica ao frete. |
| RN08 | A loja entrega apenas em faixas de CEP cadastradas. Cada faixa tem valor de frete e prazo de entrega. CEP fora das faixas não pode finalizar o pedido. |
| RN09 | **Total do pedido = subtotal − desconto + frete.** |
| RN10 | O preço de cada item é **congelado** no pedido. Mudanças posteriores de preço no catálogo não alteram pedidos já feitos. |
| RN11 | O pagamento é **simulado**. Pix gera um código fictício que expira em 15 minutos. Cartão: número validado pelo algoritmo de Luhn; cartões terminados em **0002** são recusados (cenário de teste); os demais são aprovados. |
| RN12 | O sistema **nunca armazena** o número completo nem o código de segurança do cartão. Guarda só a bandeira e os 4 últimos dígitos. |
| RN13 | O estoque é baixado quando o pagamento é aprovado. Se algum item ficou sem estoque nesse momento, o pagamento não é aprovado e o cliente é avisado. |
| RN14 | Pagamento recusado ou Pix expirado: o pedido continua "Aguardando pagamento" e o cliente pode tentar de novo. |
| RN15 | O status do pedido segue a ordem: **Aguardando pagamento → Pago → Em preparo → Saiu para entrega → Entregue**. Não é possível voltar etapas. |
| RN16 | O administrador pode **cancelar** um pedido até a etapa "Em preparo". Se o pedido já estava pago, o estoque dos itens é devolvido. |
| RN17 | E-mail é único por conta. A senha tem no mínimo 8 caracteres, com pelo menos uma letra e um número, e é armazenada apenas como hash. |
| RN18 | O CEP tem 8 dígitos; número e logradouro são obrigatórios. O cliente pode ter vários endereços e escolhe um no checkout. |
| RN19 | Cupcake que já está em algum pedido não pode ser excluído, apenas inativado. |
| RN20 | Apenas usuários com perfil **Administrador** acessam o painel administrativo. |
| RN21 | As telas de pagamento exibem o aviso "Ambiente de demonstração: nenhuma cobrança real é feita". |

## 2. Histórias de usuário e critérios de aceitação

### Módulo Vitrine

#### US01 — Visualizar a vitrine
**Como** cliente visitante, **quero** visualizar a vitrine de cupcakes **para** conhecer os produtos antes de comprar.

- **CA01.1** Dado que existem cupcakes ativos, quando acesso a página inicial, então vejo um card por cupcake com foto, nome e preço.
- **CA01.2** Dado um cupcake ativo com estoque zero, quando vejo a vitrine, então o card mostra "Esgotado" e não tem botão de adicionar. *(RN02)*
- **CA01.3** Dado um cupcake inativo, quando vejo a vitrine, então ele não aparece. *(RN02)*
- **CA01.4** Dado que não há cupcakes ativos, quando acesso a vitrine, então vejo a mensagem "Nenhum cupcake disponível no momento."

#### US02 — Filtrar cupcakes
**Como** cliente, **quero** filtrar cupcakes por sabor, preço, ocasião e restrição alimentar **para** encontrar rapidamente o produto ideal.

- **CA02.1** Dado a vitrine, quando escolho um sabor, então vejo apenas cupcakes daquele sabor.
- **CA02.2** Dado a vitrine, quando informo preço mínimo e/ou máximo, então vejo apenas cupcakes dentro da faixa.
- **CA02.3** Dado a vitrine, quando escolho uma ocasião (ex.: aniversário), então vejo apenas cupcakes indicados para ela.
- **CA02.4** Dado a vitrine, quando escolho uma restrição alimentar (ex.: sem lactose), então vejo apenas cupcakes que atendem a ela.
- **CA02.5** Dado vários filtros aplicados, quando a lista é exibida, então ela respeita todos ao mesmo tempo.
- **CA02.6** Dado filtros sem resultado, quando a lista é exibida, então vejo "Nenhum cupcake encontrado com esses filtros" e a opção "Limpar filtros".
- **CA02.7** Dado preço mínimo maior que o máximo, quando aplico o filtro, então vejo a mensagem "O preço mínimo não pode ser maior que o máximo."

#### US03 — Ver detalhes do cupcake
**Como** cliente, **quero** ver fotos, ingredientes e descrição do cupcake **para** decidir com segurança o que comprar.

- **CA03.1** Dado um cupcake ativo, quando toco no card, então vejo foto, nome, descrição, ingredientes, restrições alimentares, preço e disponibilidade.
- **CA03.2** Dado um endereço de cupcake inexistente ou inativo, quando acesso, então vejo a página "Cupcake não encontrado" com link para voltar à vitrine.

### Módulo Pedido

#### US04 — Adicionar ao carrinho
**Como** cliente, **quero** adicionar cupcakes ao carrinho **para** montar meu pedido.

- **CA04.1** Dado um cupcake disponível, quando escolho a quantidade e toco em "Adicionar", então o item entra no carrinho e vejo a confirmação "Adicionado ao carrinho".
- **CA04.2** Dado o carrinho com itens, quando navego pelo app, então o ícone do carrinho mostra a quantidade total de itens.
- **CA04.3** Dado um cupcake que já está no carrinho com a mesma personalização, quando adiciono de novo, então a quantidade da linha existente é somada. *(RN05)*
- **CA04.4** Dado uma quantidade acima do estoque ou fora de 1 a 20, quando tento adicionar, então vejo a mensagem com o limite permitido e o item não é adicionado. *(RN03)*
- **CA04.5** Dado que estou como visitante, quando faço login, então os itens do meu carrinho continuam lá. *(RN06)*

#### US05 — Personalizar cupcake
**Como** cliente, **quero** personalizar recheio, cobertura e mensagem **para** comprar cupcakes sob medida.

- **CA05.1** Dado um cupcake personalizável, quando abro os detalhes, então posso escolher um recheio, uma cobertura e escrever uma mensagem. *(RN04)*
- **CA05.2** Dado opções com acréscimo, quando escolho, então o preço exibido é atualizado na hora com o acréscimo.
- **CA05.3** Dado uma mensagem com mais de 60 caracteres, quando tento digitar, então o campo não aceita além do limite e mostra o contador de caracteres.
- **CA05.4** Dado um cupcake não personalizável, quando abro os detalhes, então as opções de personalização não aparecem.
- **CA05.5** Dado o mesmo cupcake com personalizações diferentes, quando adiciono ambos, então aparecem em linhas separadas no carrinho. *(RN05)*

#### US06 — Revisar o carrinho
**Como** cliente, **quero** revisar quantidades e valores no carrinho **para** evitar erros antes de pagar.

- **CA06.1** Dado o carrinho com itens, quando abro o carrinho, então vejo para cada linha: foto, nome, personalização, preço unitário, quantidade e subtotal da linha, além do subtotal geral.
- **CA06.2** Dado uma linha do carrinho, quando altero a quantidade, então os subtotais são recalculados na hora, respeitando RN03.
- **CA06.3** Dado uma linha do carrinho, quando toco em "Remover", então o item sai e vejo a opção "Desfazer" por alguns segundos.
- **CA06.4** Dado o carrinho vazio, quando abro o carrinho, então vejo "Seu carrinho está vazio" e um botão "Ver cupcakes".

### Módulo Pagamento

#### US07 — Aplicar cupom
**Como** cliente, **quero** aplicar cupom de desconto **para** aproveitar promoções.

- **CA07.1** Dado um cupom válido, quando aplico no checkout, então vejo o desconto e o total recalculado. *(RN07, RN09)*
- **CA07.2** Dado um cupom inexistente, inativo ou vencido, quando aplico, então vejo "Cupom inválido ou expirado" e o total não muda.
- **CA07.3** Dado um subtotal abaixo do mínimo do cupom, quando aplico, então vejo "Este cupom vale para pedidos a partir de R$ X".
- **CA07.4** Dado um cupom já aplicado, quando aplico outro, então o novo substitui o anterior.
- **CA07.5** Dado um cupom com desconto maior que o subtotal, quando aplico, então o desconto fica limitado ao subtotal.

#### US08 — Pagar por Pix ou cartão (simulado)
**Como** cliente, **quero** pagar por Pix ou cartão **para** finalizar a compra com praticidade.

- **CA08.1** Dado o checkout com endereço válido, quando escolho Pix, então vejo um código "copia e cola" fictício, o tempo restante (15 minutos) e o botão "Simular pagamento". *(RN11)*
- **CA08.2** Dado um Pix gerado, quando toco em "Simular pagamento" dentro do prazo, então o pagamento é aprovado.
- **CA08.3** Dado um Pix com prazo vencido, quando tento pagar, então vejo "Código Pix expirado" e a opção de gerar outro. *(RN14)*
- **CA08.4** Dado o pagamento com cartão, quando informo um número válido (Luhn), nome, validade futura e código de segurança, então o pagamento é aprovado.
- **CA08.5** Dado um cartão terminado em 0002, quando pago, então vejo "Pagamento recusado. Tente outro cartão ou pague com Pix." *(RN11, RN14)*
- **CA08.6** Dado dados de cartão inválidos (número, validade vencida, código de segurança fora de 3 ou 4 dígitos), quando envio, então vejo a mensagem no campo com erro, sem perder os outros dados digitados.
- **CA08.7** Dado um pagamento aprovado, quando consulto os dados salvos, então só existem a bandeira e os 4 últimos dígitos do cartão. *(RN12)*
- **CA08.8** Dado um item que ficou sem estoque durante o pagamento, quando o pagamento seria aprovado, então ele não é aprovado e vejo qual item ficou indisponível. *(RN13)*

#### US09 — Confirmação do pedido
**Como** cliente, **quero** receber confirmação do pagamento e do pedido **para** ter segurança na compra.

- **CA09.1** Dado um pagamento aprovado, quando a tela é atualizada, então vejo "Pedido confirmado!", o número do pedido, os itens, o total pago, o endereço e o prazo de entrega.
- **CA09.2** Dado um pedido confirmado, quando acesso "Meus pedidos", então ele aparece com status "Pago".
- **CA09.3** Dado um pagamento aprovado, quando a confirmação é exibida, então o carrinho está vazio.

### Módulo Entrega

#### US10 — Cadastrar endereço
**Como** cliente, **quero** cadastrar endereço de entrega **para** receber os cupcakes no local correto.

- **CA10.1** Dado que estou logado, quando cadastro CEP, logradouro, número, complemento (opcional), bairro e cidade, então o endereço fica salvo na minha conta. *(RN18)*
- **CA10.2** Dado campos obrigatórios vazios ou CEP com formato inválido, quando salvo, então vejo a mensagem em cada campo com erro.
- **CA10.3** Dado vários endereços salvos, quando vou ao checkout, então escolho um deles ou cadastro um novo.

#### US11 — Calcular frete e prazo
**Como** cliente, **quero** calcular frete e prazo antes de finalizar **para** saber o custo total.

- **CA11.1** Dado um endereço dentro da área de entrega, quando ele é escolhido no checkout, então vejo valor do frete, prazo de entrega e total do pedido. *(RN08, RN09)*
- **CA11.2** Dado um endereço fora da área de entrega, quando ele é escolhido, então vejo "Ainda não entregamos neste CEP" e não consigo seguir para o pagamento.
- **CA11.3** Dado que estou no carrinho, mesmo sem login, quando informo um CEP, então vejo o frete e o prazo estimados para aquele CEP, ou a mensagem de CEP fora da área. *(RN08)*

#### US12 — Acompanhar status do pedido
**Como** cliente, **quero** acompanhar o status do pedido **para** saber quando ele será preparado, enviado e entregue.

- **CA12.1** Dado um pedido meu, quando abro os detalhes, então vejo uma linha do tempo com as etapas e a data e hora de cada etapa já concluída. *(RN15)*
- **CA12.2** Dado a tela do pedido aberta, quando o administrador muda o status, então a tela mostra o novo status em até 30 segundos, sem recarregar a página.
- **CA12.3** Dado um pedido cancelado, quando abro os detalhes, então vejo o status "Cancelado" em destaque.
- **CA12.4** Dado um pedido de outro cliente, quando tento acessar pelo endereço, então vejo "Pedido não encontrado". *(segurança)*

### Módulo Conta

#### US13 — Criar conta e fazer login
**Como** cliente, **quero** criar uma conta e fazer login **para** salvar dados, endereços e histórico de pedidos.

- **CA13.1** Dado o formulário de cadastro com nome, e-mail, telefone e senha válidos, quando envio, então a conta é criada e já entro logado. *(RN17)*
- **CA13.2** Dado um e-mail já cadastrado, quando envio o cadastro, então vejo "Este e-mail já está cadastrado" e o link para entrar.
- **CA13.3** Dado uma senha fraca, quando envio o cadastro, então vejo a regra da senha (mínimo 8 caracteres, com letra e número).
- **CA13.4** Dado e-mail e senha corretos, quando faço login, então entro e volto para a página onde estava.
- **CA13.5** Dado e-mail ou senha incorretos, quando faço login, então vejo "E-mail ou senha inválidos", sem informar qual dos dois está errado.
- **CA13.6** Dado que estou logado, quando toco em "Sair", então a sessão é encerrada.
- **CA13.7** Dado que estou logado, quando acesso "Meus pedidos", então vejo meus pedidos do mais recente para o mais antigo.

### Módulo Administração

#### US15 — Cadastrar e editar cupcakes
**Como** administrador, **quero** cadastrar e editar cupcakes **para** manter a vitrine atualizada.

- **CA15.1** Dado o painel administrativo, quando cadastro nome, descrição, ingredientes, preço, sabor, ocasiões, restrições, URL da foto, estoque e se é personalizável, então o cupcake aparece na vitrine. *(RN01)*
- **CA15.2** Dado dados inválidos (nome vazio, preço menor ou igual a zero, estoque negativo), quando salvo, então vejo a mensagem em cada campo com erro.
- **CA15.3** Dado um cupcake existente, quando edito e salvo, então a vitrine mostra os novos dados e pedidos antigos mantêm o preço original. *(RN10)*
- **CA15.4** Dado um cupcake que está em algum pedido, quando tento excluir, então vejo "Este cupcake já foi vendido. Você pode inativá-lo." *(RN19)*

#### US16 — Controlar disponibilidade
**Como** administrador, **quero** controlar a disponibilidade dos produtos **para** evitar venda de itens esgotados.

- **CA16.1** Dado a lista de cupcakes no painel, quando altero o estoque, então a vitrine passa a refletir o novo estoque. *(RN02)*
- **CA16.2** Dado um cupcake ativo, quando o inativo, então ele some da vitrine; quando o reativo, ele volta.
- **CA16.3** Dado a lista no painel, quando a vejo, então cupcakes com estoque zero aparecem destacados como "Esgotado".

#### US17 — Gerenciar pedidos
**Como** administrador, **quero** gerenciar os pedidos recebidos **para** organizar preparo, pagamento e entrega.

- **CA17.1** Dado o painel de pedidos, quando o abro, então vejo os pedidos do mais recente para o mais antigo, com número, cliente, total, status e data, e posso filtrar por status.
- **CA17.2** Dado um pedido, quando abro os detalhes, então vejo itens com personalização, endereço, pagamento e histórico de status.
- **CA17.3** Dado um pedido pago, quando toco em "Avançar status", então ele vai para a próxima etapa e a mudança fica registrada com data e hora. *(RN15)*
- **CA17.4** Dado um pedido em "Aguardando pagamento", "Pago" ou "Em preparo", quando cancelo, então o status vira "Cancelado" e, se já estava pago, o estoque é devolvido. *(RN16)*
- **CA17.5** Dado um usuário sem perfil de administrador, quando tenta acessar o painel, então vê "Acesso negado". *(RN20)*
- **CA17.6** Dado o painel de pedidos aberto, quando um novo pedido é pago, então ele aparece na lista em até 30 segundos, sem recarregar a página, destacado como "Novo" até ser aberto.

## 3. Requisitos não funcionais

| ID | Categoria | Requisito | Como verificar |
|---|---|---|---|
| RNF01 | Usabilidade | Layout mobile-first, utilizável a partir de 360 px de largura, sem rolagem horizontal | Teste manual em celular e no modo responsivo do navegador |
| RNF02 | Usabilidade | Compra completa (vitrine → pedido confirmado) em até 6 telas | Contagem no mapa navegacional |
| RNF03 | Usabilidade | Toda ação do usuário tem retorno visual (mensagem de sucesso, erro ou carregamento) | Catálogo de mensagens + teste manual |
| RNF04 | Segurança | Senhas armazenadas com hash; proteção contra CSRF em formulários; consultas ao banco parametrizadas (ORM); rotas do painel restritas ao perfil Administrador | Revisão de código + testes automatizados de acesso |
| RNF05 | Segurança / LGPD | Nenhum dado completo de cartão é armazenado; dados pessoais coletados se limitam ao necessário para a entrega | Inspeção do banco + dicionário de dados |
| RNF06 | Confiabilidade | Erros inesperados exibem página amigável (404 e 500) e não expõem detalhes técnicos | Teste manual e automatizado |
| RNF07 | Confiabilidade | A finalização do pedido e a baixa de estoque acontecem numa única transação no banco, com trava nos registros dos produtos para que dois pagamentos simultâneos não deixem o estoque negativo | Teste de integração com pagamentos concorrentes |
| RNF08 | Desempenho | Páginas carregam em até 2 segundos com a aplicação ativa (exceto a primeira visita após inatividade na hospedagem gratuita) | Medição com as ferramentas do navegador |
| RNF09 | Manutenibilidade | Código organizado em MVC, seguindo a PEP 8, com cobertura de testes de pelo menos 70% em models e controllers | Relatório do pytest-cov |
| RNF10 | Acessibilidade | Contraste de texto nível AA, imagens com texto alternativo, campos de formulário com rótulo e status sempre indicados por ícone + texto, nunca só por cor | Ferramenta Lighthouse do navegador + revisão das telas |
| RNF11 | Portabilidade | Funciona nas versões atuais do Chrome, Safari e Firefox; pode ser instalado na tela inicial do celular (PWA) | Teste manual nos navegadores |

## 4. Validação dos requisitos

Checagem feita sobre cada requisito, conforme o material teórico:

| Característica | Como foi garantida |
|---|---|
| Descreve corretamente a necessidade do usuário | Histórias mantidas do PIT I no formato "como / quero / para" |
| Tem um único significado | Critérios no formato Dado/Quando/Então, com valores concretos (ex.: 15 minutos, 60 caracteres, 30 segundos) |
| Pode ser modificado | IDs estáveis (US, CA, RN, RNF); alterações registradas em [01-revisao-pit1.md](01-revisao-pit1.md) |
| Atributos documentados | Pontos, prioridade e módulo em [02-escopo-mvp.md](02-escopo-mvp.md) |
| Vinculado a código e testes | Matriz de rastreabilidade abaixo |

A validação com pessoas (colegas) está em [05-feedback-colegas.md](05-feedback-colegas.md).

## 5. Matriz de rastreabilidade

Preenchida ao longo da Situação 2 (código) e da Situação 3 (testes).

| História | Regras | Controller | Model(s) | Testes unitários | Testes de integração | Aceitação |
|---|---|---|---|---|---|---|
| US01 | RN02 | vitrine | Cupcake | `tests/unit/test_regras_catalogo.py` (rn02) | `tests/integration/test_vitrine.py` (ca01_1 a ca01_4) | Pendente |
| US02 | — | vitrine | FiltrosVitrine | `tests/unit/test_regras_catalogo.py` (ca02) | `tests/integration/test_vitrine.py` (ca02_1 a ca02_7) | Pendente |
| US03 | RN02 | vitrine | Cupcake | — | `tests/integration/test_vitrine.py` (ca03_1, ca03_2) | Pendente |
| US04 | RN03, RN05, RN06 | carrinho | Carrinho, Cupcake | `tests/unit/test_regras_catalogo.py` (rn03, rn05) | `tests/integration/test_carrinho.py` (ca04_1 a ca04_4) | Pendente |
| US05 | RN04, RN05 | carrinho | Carrinho, OpcaoPersonalizacao | `tests/unit/test_regras_catalogo.py` (rn04) | `tests/integration/test_vitrine.py` (ca05_1, ca05_4); `tests/integration/test_carrinho.py` (ca05_2 a ca05_5) | Pendente |
| US06 | RN03 | carrinho | Carrinho | `tests/unit/test_regras_catalogo.py` (carrinho) | `tests/integration/test_carrinho.py` (ca06_1 a ca06_4) | Pendente |
| US07 | RN07, RN09 | checkout | Cupom | `tests/unit/test_regras_pedido.py` (ca07) | `tests/integration/test_checkout.py` (ca07_1 a ca07_4) | Pendente |
| US08 | RN11–RN14, RN21 | pagamento | Pagamento, GatewaySimulado, ServicoPagamento | `tests/unit/test_regras_pedido.py` (ca08, rn11, rn12) | `tests/integration/test_pagamento.py` (ca08_1 a ca08_8, rn14, rnf07) | Pendente |
| US09 | RN10 | pagamento | Pedido | — | `tests/integration/test_pagamento.py` (ca09_1, ca09_3) | Pendente |
| US10 | RN18 | conta, checkout | Endereco | `tests/unit/test_utilitarios.py` (rn18) | `tests/integration/test_conta.py` (ca10_1, ca10_2); `tests/integration/test_checkout.py` (ca10_3) | Pendente |
| US11 | RN08, RN09 | carrinho, checkout | AreaEntrega | `tests/unit/test_utilitarios.py` (rn18) | `tests/integration/test_carrinho.py` (ca11_3); `tests/integration/test_checkout.py` (ca10_3, ca11_2) | Pendente |
| US12 | RN15 | pedidos | Pedido, HistoricoStatus | `tests/unit/test_regras_pedido.py` (rn15) | `tests/integration/test_pedidos.py` (ca12_1 a ca12_4) | Pendente |
| US13 | RN06, RN17 | autenticacao, conta, pedidos | Usuario | `tests/unit/test_utilitarios.py` (rn17) | `tests/integration/test_conta.py` (ca13_1 a ca13_6, rn06); `tests/integration/test_pedidos.py` (ca13_7) | Pendente |
| US15 | RN01, RN10, RN19 | admin_cupcakes | Cupcake | | | Pendente |
| US16 | RN02 | admin_cupcakes | Cupcake | | | Pendente |
| US17 | RN15, RN16, RN20 | admin_pedidos | Pedido, HistoricoStatus | | | Pendente |
