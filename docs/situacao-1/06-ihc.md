# 06 — Interface Humano-Computador (IHC)

> Exigências atendidas: **R12** (telas revisadas e incrementadas), **R13** (mensagens de erro, sucesso e confirmação), **R14** (mapa conceitual), **R15** (mapa navegacional) e **R16** (princípios de IHC do material teórico).

O PIT I prometia wireframes e mockups, mas o documento não trazia nenhuma tela. Aqui o protótipo foi feito em **média fidelidade**, já com cores, tipografia e componentes definidos, para que sirva também de referência direta para o front-end na Situação 2.

- Protótipo navegável (todas as telas numa página): [ihc/prototipo/index.html](ihc/prototipo/index.html)
- Imagens de cada tela: [ihc/telas/](ihc/telas/)

## 1. Identidade visual

| Elemento | Definição | Motivo |
|---|---|---|
| Cor principal | Framboesa `#9C2F5B` (botões, links, item ativo) | Remete a confeitaria sem ser infantil; contraste AA com branco |
| Fundo | Creme `#FFF9F5`; cartões em branco `#FFFFFF` | Tom quente e leve, deixa as fotos dos produtos em destaque |
| Texto | `#2A1F24` (principal) e `#75656C` (secundário) | Contraste suficiente para leitura no sol, no celular |
| Cores de estado | Verde (sucesso), amarelo (aviso), vermelho (erro), azul (informação) | Sempre acompanhadas de ícone e texto, nunca só a cor (RNF10) |
| Tipografia | Fonte padrão do sistema (San Francisco no iPhone, Roboto no Android) | Carrega instantaneamente e o usuário já está acostumado com ela |
| Hierarquia | Título da tela 17 px · nome do produto 13–19 px · texto 13,5 px · apoio 12 px | Separar o que é principal do que é detalhe |
| Botões | Principal cheio, secundário com contorno, destrutivo em vermelho; 46 px de altura | Área de toque confortável para o polegar |
| Layout | Coluna única, margens de 16 px, ação principal fixa no rodapé | Uso com uma mão; o botão principal fica sempre visível |

## 2. Telas

Fluxo do cliente:

| | | |
|---|---|---|
| ![T01](ihc/telas/t01.png) **T01 · Vitrine** (US01, US02) | ![T02](ihc/telas/t02.png) **T02 · Filtros** (US02) | ![T03](ihc/telas/t03.png) **T03 · Detalhe e personalização** (US03, US05) |
| ![T04](ihc/telas/t04.png) **T04 · Carrinho** (US04, US06, US11) | ![T05](ihc/telas/t05.png) **T05 · Entrar** (US13) | ![T06](ihc/telas/t06.png) **T06 · Criar conta** (US13) |
| ![T07](ihc/telas/t07.png) **T07 · Finalizar pedido** (US07, US10, US11) | ![T08](ihc/telas/t08.png) **T08 · Novo endereço** (US10) | ![T09](ihc/telas/t09.png) **T09 · Pagamento com cartão** (US08) |
| ![T10](ihc/telas/t10.png) **T10 · Pagamento com Pix** (US08) | ![T11](ihc/telas/t11.png) **T11 · Pedido confirmado** (US09) | ![T12](ihc/telas/t12.png) **T12 · Meus pedidos** (US13) |
| ![T13](ihc/telas/t13.png) **T13 · Acompanhar pedido** (US12) | | |

Painel da loja:

| | | |
|---|---|---|
| ![T14](ihc/telas/t14.png) **T14 · Pedidos** (US17) | ![T15](ihc/telas/t15.png) **T15 · Detalhe do pedido** (US17) | ![T16](ihc/telas/t16.png) **T16 · Cupcakes** (US16) |
| ![T17](ihc/telas/t17.png) **T17 · Cadastro de cupcake** (US15) | | |

Estados de erro, vazio e confirmação:

| | | |
|---|---|---|
| ![T18](ihc/telas/t18.png) **T18 · Filtros sem resultado** (CA02.6) | ![T19](ihc/telas/t19.png) **T19 · Carrinho vazio e "Desfazer"** (CA06.3, CA06.4) | ![T20](ihc/telas/t20.png) **T20 · Pagamento recusado e erro de campo** (CA08.5, CA08.6) |
| ![T21](ihc/telas/t21.png) **T21 · Confirmação de cancelamento** (CA17.4) | | |

### Observações sobre as telas

- **T01:** o cupcake esgotado continua visível, com a tarja "ESGOTADO" e sem botão de adicionar. Esconder o produto confundiria quem já comprou antes e voltou para procurá-lo.
- **T03:** o botão mostra o valor final já com quantidade e acréscimos ("Adicionar · R$ 28,80"), então o cliente não precisa fazer conta.
- **T04:** o frete pode ser consultado no carrinho, antes do login. Essa mudança veio da revisão crítica (C1).
- **T07:** o resumo mostra subtotal, desconto, frete e total separados, para o cliente conferir antes de pagar.
- **T09 e T10:** o aviso de ambiente de demonstração aparece no topo de toda tela de pagamento (RN21).
- **T13:** cada etapa tem ícone e texto; a etapa atual tem contorno e as futuras ficam acinzentadas.
- **T15:** o botão diz para qual etapa o pedido vai ("Avançar para 'Saiu para entrega'"), evitando clique por engano.
- **T21:** o cancelamento só acontece depois de um diálogo que explica a consequência (estoque devolvido, ação sem volta).

## 3. Mapa navegacional

Mostra como o usuário se move entre as telas. Linhas tracejadas são caminhos de erro ou exceção.

```mermaid
flowchart TD
  subgraph cliente["Área do cliente"]
    T01["T01 Vitrine"]
    T02["T02 Filtros"]
    T18["T18 Sem resultado"]
    T03["T03 Detalhe"]
    T04["T04 Carrinho"]
    T19["T19 Carrinho vazio"]
    T05["T05 Entrar"]
    T06["T06 Criar conta"]
    T07["T07 Finalizar pedido"]
    T08["T08 Novo endereço"]
    T09["T09 Pagamento cartão"]
    T10["T10 Pagamento Pix"]
    T20["T20 Pagamento recusado"]
    T11["T11 Pedido confirmado"]
    T12["T12 Meus pedidos"]
    T13["T13 Acompanhar pedido"]
  end

  subgraph loja["Painel da loja"]
    T14["T14 Pedidos"]
    T15["T15 Detalhe do pedido"]
    T21["T21 Confirmar cancelamento"]
    T16["T16 Cupcakes"]
    T17["T17 Cadastro de cupcake"]
  end

  T01 <--> T02
  T02 -.-> T18
  T01 --> T03
  T03 -->|"adicionar"| T04
  T01 -->|"ícone do carrinho"| T04
  T04 -.-> T19
  T04 -->|"não logado"| T05
  T05 <--> T06
  T05 --> T07
  T06 --> T07
  T04 -->|"logado"| T07
  T07 <--> T08
  T07 --> T09
  T09 <--> T10
  T09 -.-> T20
  T20 --> T09
  T09 --> T11
  T10 --> T11
  T11 --> T13
  T11 --> T01
  T01 -->|"menu Pedidos"| T12
  T12 --> T13
  T13 -.->|"aguardando pagamento"| T09

  T05 -->|"perfil Administrador"| T14
  T14 --> T15
  T15 -.-> T21
  T14 <--> T16
  T16 <--> T17
```

**Caminho mínimo de compra (RNF02):** T01 Vitrine → T03 Detalhe → T04 Carrinho → T07 Finalizar pedido → T09 Pagamento → T11 Confirmado. São **6 telas**; para quem ainda não está logado, soma-se a tela de entrar ou criar conta.

## 4. Mapa conceitual

Relaciona os conceitos do negócio na linguagem da loja, sem termos técnicos. Serviu de base para o diagrama de classes e para os textos das telas.

```mermaid
flowchart TD
  Loja(["Loja de cupcakes"])
  Cupcake(["Cupcake"])
  Sabor(["Sabor"])
  Ocasiao(["Ocasião"])
  Restricao(["Restrição alimentar"])
  Personalizacao(["Personalização<br/>recheio · cobertura · mensagem"])
  Estoque(["Estoque"])
  Cliente(["Cliente"])
  Carrinho(["Carrinho"])
  Endereco(["Endereço"])
  Area(["Área de entrega"])
  Frete(["Frete e prazo"])
  Cupom(["Cupom"])
  Pedido(["Pedido"])
  Pagamento(["Pagamento<br/>Pix ou cartão"])
  Status(["Status do pedido"])

  Loja -->|"oferece"| Cupcake
  Loja -->|"controla"| Estoque
  Loja -->|"define"| Area
  Loja -->|"cria"| Cupom
  Loja -->|"atualiza"| Status
  Cupcake -->|"tem um"| Sabor
  Cupcake -->|"é indicado para"| Ocasiao
  Cupcake -->|"atende"| Restricao
  Cupcake -->|"pode receber"| Personalizacao
  Estoque -->|"limita a venda de"| Cupcake
  Cliente -->|"monta o"| Carrinho
  Carrinho -->|"reúne"| Cupcake
  Cliente -->|"cadastra"| Endereco
  Endereco -->|"precisa estar na"| Area
  Area -->|"determina"| Frete
  Carrinho -->|"se transforma em"| Pedido
  Pedido -->|"é entregue no"| Endereco
  Pedido -->|"pode usar"| Cupom
  Pedido -->|"inclui"| Frete
  Pedido -->|"é quitado por"| Pagamento
  Pedido -->|"passa por"| Status
```

## 5. Princípios de IHC aplicados

Os princípios abaixo são os listados no material teórico da disciplina.

| Princípio | Como foi aplicado | Telas |
|---|---|---|
| **Clara** | Cada tela tem um único objetivo e um único botão principal; textos curtos, sem termos técnicos | Todas |
| **Consistente** | Mesmos componentes em todo o app: botão principal sempre no rodapé, voltar sempre no canto superior esquerdo, status sempre como etiqueta com ícone | Todas |
| **Simples** | Personalização só aparece quando o cupcake aceita; filtros ficam numa folha separada para não poluir a vitrine (divulgação progressiva) | T02, T03 |
| **Controlada pelo usuário** | Nada acontece sozinho: o cliente escolhe endereço, aplica ou remove cupom e decide quando pagar; a loja escolhe quando avançar cada etapa | T07, T15 |
| **Direta** | Toda ação tem efeito visível na hora: preço do botão muda com a quantidade, subtotal recalcula ao alterar o carrinho, ícone do carrinho mostra a contagem | T01, T03, T04 |
| **Empática e reversível** | Remover item tem "Desfazer"; erros de formulário não apagam o que foi digitado; ações sem volta pedem confirmação explicando a consequência | T19, T06, T21 |
| **Dá resposta** | Mensagem para cada resultado (sucesso, erro, aviso); linha do tempo e painel se atualizam sozinhos | T11, T13, T14 |
| **Esteticamente agradável** | Paleta reduzida, espaço em branco, ilustração do produto em destaque; cor só onde chama atenção para algo importante | Todas |
| **Padrões (defaults)** | Endereço mais recente já vem marcado; quantidade começa em 1; cobertura padrão já selecionada | T03, T07 |
| **Comunica o que está acontecendo** | Contagem regressiva do Pix, "Atualizado há 12 segundos" no painel, aviso de demonstração no pagamento | T10, T14, T09 |

## 6. Catálogo de mensagens

Regras de redação seguidas em todas as mensagens:

1. Dizer **o que aconteceu** e, quando houver, **o que fazer**.
2. Não culpar o usuário e não mostrar códigos técnicos.
3. A mensagem aparece **perto de onde está o problema** (no campo, no topo do formulário ou num aviso flutuante).

### Sucesso

| ID | Mensagem | Onde | Ref. |
|---|---|---|---|
| MS01 | Adicionado ao carrinho. | Aviso flutuante após adicionar | CA04.1 |
| MS02 | Item removido do carrinho. **Desfazer** | Aviso flutuante no carrinho (T19) | CA06.3 |
| MS03 | Cupom aplicado: {valor} de desconto nos produtos. | Abaixo do campo de cupom (T07) | CA07.1 |
| MS04 | Pedido confirmado! | Tela de confirmação (T11) | CA09.1 |
| MS05 | Endereço salvo. | Aviso flutuante | CA10.1 |
| MS06 | Conta criada. Bem-vindo(a), {nome}! | Aviso flutuante | CA13.1 |
| MS07 | Cupcake salvo. | Aviso flutuante no painel | CA15.1 |
| MS08 | Pedido #{número} agora está "{status}". | Aviso flutuante no painel (T15) | CA17.3 |
| MS09 | Pedido #{número} cancelado. O estoque foi devolvido. | Aviso flutuante no painel | CA17.4 |

### Erros de preenchimento (aparecem no campo)

| ID | Mensagem | Campo | Ref. |
|---|---|---|---|
| EC01 | Obrigatório. | Qualquer campo obrigatório | CA10.2, CA15.2 |
| EC02 | A quantidade deve ser de 1 a 20. | Quantidade | CA04.4, RN03 |
| EC03 | Só temos {n} unidades disponíveis. | Quantidade | CA04.4, RN03 |
| EC04 | O preço mínimo não pode ser maior que o máximo. | Filtro de preço | CA02.7 |
| EC05 | Informe um CEP com 8 dígitos. | CEP | CA10.2, RN18 |
| EC06 | Este e-mail já está cadastrado. **Entrar** | E-mail (cadastro) | CA13.2 |
| EC07 | Use no mínimo 8 caracteres, com letras e números. | Senha | CA13.3, RN17 |
| EC08 | Número de cartão inválido. | Número do cartão | CA08.6 |
| EC09 | Cartão vencido. | Validade | CA08.6 |
| EC10 | O CVV tem 3 ou 4 dígitos. | CVV | CA08.6 |
| EC11 | Deve ser maior que zero. | Preço (painel) | CA15.2, RN01 |
| EC12 | Informe um número inteiro maior ou igual a zero. | Estoque (painel) | CA15.2, RN01 |

### Erros de regra de negócio (aparecem em aviso)

| ID | Mensagem | Onde | Ref. |
|---|---|---|---|
| EN01 | E-mail ou senha inválidos. | Topo do formulário de entrar (T05) | CA13.5 |
| EN02 | Cupom inválido ou expirado. | Campo de cupom | CA07.2 |
| EN03 | Este cupom vale para pedidos a partir de R$ {valor}. | Campo de cupom | CA07.3 |
| EN04 | Ainda não entregamos neste CEP. | Carrinho e checkout | CA11.2, RN08 |
| EN05 | Pagamento recusado. Tente outro cartão ou pague com Pix. | Topo do pagamento (T20) | CA08.5 |
| EN06 | Código Pix expirado. Gere um novo código para pagar. | Tela do Pix | CA08.3 |
| EN07 | {Cupcake} ficou indisponível. Ajuste seu carrinho para continuar. | Checkout ou pagamento | CA08.8, RN13 |
| EN08 | Este cupcake já foi vendido. Você pode inativá-lo. | Painel, ao excluir | CA15.4, RN19 |
| EN09 | Este pedido ainda está aguardando pagamento do cliente. | Painel, ao tentar avançar | UC16 FE2 |

### Avisos e informações

| ID | Mensagem | Onde | Ref. |
|---|---|---|---|
| AV01 | Ambiente de demonstração: nenhuma cobrança real é feita. | Topo de toda tela de pagamento | RN21 |
| AV02 | Não guardamos o número nem o CVV do seu cartão. | Abaixo do formulário de cartão | RN12 |
| AV03 | Entre para finalizar o pedido. Seu carrinho continua salvo. | Tela de entrar vinda do carrinho | RN06 |
| AV04 | Esta tela se atualiza sozinha. | Acompanhar pedido (T13) | CA12.2 |
| AV05 | Atualizado há {n} segundos. | Painel de pedidos (T14) | CA17.6 |
| AV06 | Expira em {mm:ss}. | Tela do Pix (T10) | CA08.1 |

### Estados vazios

| ID | Mensagem | Onde | Ref. |
|---|---|---|---|
| EV01 | Nenhum cupcake disponível no momento. | Vitrine sem produtos | CA01.4 |
| EV02 | Nenhum cupcake encontrado com esses filtros. **Limpar filtros** | Vitrine filtrada (T18) | CA02.6 |
| EV03 | Seu carrinho está vazio. **Ver cupcakes** | Carrinho (T19) | CA06.4 |
| EV04 | Você ainda não fez pedidos. **Ver cupcakes** | Meus pedidos | CA13.7 |

### Páginas de erro

| ID | Título | Texto | Ref. |
|---|---|---|---|
| PE01 | Cupcake não encontrado | Ele pode ter saído do cardápio. **Voltar à vitrine** | CA03.2 |
| PE02 | Pedido não encontrado | Confira o número do pedido em "Meus pedidos". | CA12.4 |
| PE03 | Acesso negado | Esta área é exclusiva da equipe da loja. | CA17.5, RN20 |
| PE04 | Página não encontrada | O endereço pode estar errado. **Voltar à vitrine** | RNF06 |
| PE05 | Algo deu errado | Tivemos um problema do nosso lado. Tente de novo em alguns instantes. | RNF06 |

### Confirmações (ações sem volta)

| ID | Pergunta | Detalhe | Ref. |
|---|---|---|---|
| CF01 | Cancelar o pedido #{número}? | Se pago: "Os itens voltam para o estoque." Sempre: "Esta ação não pode ser desfeita." | CA17.4 (T21) |
| CF02 | Excluir o cupcake {nome}? | "Ele sai do cardápio definitivamente." | UC14 FA2 |
| CF03 | Excluir este endereço? | "Pedidos já feitos não são alterados." | UC09 FA1 |
