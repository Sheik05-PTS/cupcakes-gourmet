# UML — Diagramas de Atividades e de Estados

> Exigência atendida: **R11** (diagramas de atividades). Também inclui os diagramas de **máquina de estados** do pedido e do pagamento, que deixam explícitas as regras RN14, RN15 e RN16.
> Legenda das atividades: caixas rosadas = ação do ator · caixas cinzas = ação do sistema · losangos = decisão.

## AD1 — Processo de compra

```mermaid
flowchart TD
  ini(["● Início"])
  a1["Cliente: navega na vitrine"]
  d1{"Quer filtrar?"}
  a2["Cliente: aplica filtros"]
  a3["Cliente: abre o detalhe do cupcake"]
  d2{"Personalizável e<br/>quer personalizar?"}
  a4["Cliente: escolhe recheio,<br/>cobertura e mensagem"]
  a5["Cliente: escolhe a quantidade<br/>e toca em Adicionar"]
  s1["Sistema: valida quantidade e estoque"]
  d3{"Válido?"}
  s2["Sistema: exibe o limite permitido"]
  s3["Sistema: adiciona ao carrinho"]
  d4{"Continuar<br/>comprando?"}
  a6["Cliente: abre o carrinho e<br/>toca em Finalizar pedido"]
  d5{"Está logado?"}
  a7["Cliente: entra ou cria conta"]
  a8["Cliente: escolhe o endereço"]
  s4["Sistema: calcula frete e prazo"]
  d6{"CEP atendido?"}
  s5["Sistema: Ainda não entregamos neste CEP"]
  d7{"Tem cupom?"}
  a9["Cliente: aplica o cupom"]
  s6["Sistema: valida o cupom<br/>e recalcula o total"]
  a10["Cliente: confirma o pedido"]
  s7["Sistema: cria o pedido<br/>Aguardando pagamento"]
  a11["Cliente: paga (ver AD2)"]
  d8{"Pagamento<br/>aprovado?"}
  d9{"Tentar de novo?"}
  s8["Sistema: exibe Pedido confirmado!"]
  a12["Cliente: acompanha o pedido"]
  fim(["◉ Fim"])
  fim2(["◉ Fim — pedido segue<br/>aguardando pagamento"])

  ini --> a1 --> d1
  d1 -- sim --> a2 --> a3
  d1 -- não --> a3
  a3 --> d2
  d2 -- sim --> a4 --> a5
  d2 -- não --> a5
  a5 --> s1 --> d3
  d3 -- não --> s2 --> a5
  d3 -- sim --> s3 --> d4
  d4 -- sim --> a1
  d4 -- não --> a6 --> d5
  d5 -- não --> a7 --> a8
  d5 -- sim --> a8
  a8 --> s4 --> d6
  d6 -- não --> s5 --> a8
  d6 -- sim --> d7
  d7 -- sim --> a9 --> s6 --> a10
  d7 -- não --> a10
  a10 --> s7 --> a11 --> d8
  d8 -- sim --> s8 --> a12 --> fim
  d8 -- não --> d9
  d9 -- sim --> a11
  d9 -- não --> fim2

  classDef ator fill:#fbf1f4,stroke:#b8456b,color:#1f2433
  classDef sistema fill:#eef0f5,stroke:#4a5063,color:#1f2433
  class a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11,a12 ator
  class s1,s2,s3,s4,s5,s6,s7,s8 sistema
```

## AD2 — Processamento do pagamento

```mermaid
flowchart TD
  ini(["● Início"])
  d1{"Forma de pagamento"}

  c1["Cliente: informa dados do cartão"]
  c2["Sistema: valida campos<br/>Luhn · validade · CVV"]
  c3{"Dados válidos?"}
  c4["Sistema: mensagem no campo com erro"]
  c5["Gateway simulado: processa cobrança"]
  c6{"Aprovado?"}
  c7["Sistema: registra RECUSADO e<br/>exibe Pagamento recusado"]

  p1["Sistema: gera código Pix fictício<br/>válido por 15 minutos"]
  p2["Cliente: toca em Simular pagamento"]
  p3{"Dentro do prazo?"}
  p4["Sistema: registra EXPIRADO e<br/>oferece gerar outro código"]

  t1["Sistema: inicia transação e<br/>trava os cupcakes do pedido"]
  t2{"Estoque<br/>suficiente?"}
  t3["Sistema: desfaz a transação, registra RECUSADO<br/>e informa o item indisponível"]
  t4["Sistema: baixa o estoque, aprova o pagamento,<br/>marca o pedido como PAGO e registra histórico"]
  t5["Sistema: confirma a transação<br/>e esvazia o carrinho"]

  ok(["◉ Fim — pedido pago"])
  falha(["◉ Fim — pedido segue<br/>aguardando pagamento"])

  ini --> d1
  d1 -- cartão --> c1 --> c2 --> c3
  c3 -- não --> c4 --> c1
  c3 -- sim --> c5 --> c6
  c6 -- não --> c7 --> falha
  c6 -- sim --> t1
  d1 -- Pix --> p1 --> p2 --> p3
  p3 -- não --> p4 --> falha
  p3 -- sim --> t1
  t1 --> t2
  t2 -- não --> t3 --> falha
  t2 -- sim --> t4 --> t5 --> ok

  classDef ator fill:#fbf1f4,stroke:#b8456b,color:#1f2433
  classDef sistema fill:#eef0f5,stroke:#4a5063,color:#1f2433
  class c1,p2 ator
  class c2,c4,c5,c7,p1,p4,t1,t3,t4,t5 sistema
```

## AD3 — Atendimento do pedido pela loja

```mermaid
flowchart TD
  ini(["● Início"])
  a1["Administrador: abre o painel de pedidos"]
  s1["Sistema: lista pedidos e atualiza<br/>a cada 30 s, destacando os novos"]
  a2["Administrador: abre um pedido"]
  s2["Sistema: mostra detalhes e<br/>marca o pedido como visto"]
  d1{"Ação"}
  s3{"Pode avançar?<br/>pago, em preparo ou<br/>saiu para entrega"}
  s4["Sistema: Aguardando pagamento<br/>do cliente / nada a avançar"]
  s5["Sistema: muda para a próxima etapa<br/>e registra no histórico"]
  d2{"Chegou em<br/>Entregue?"}
  s6{"Pode cancelar?<br/>até Em preparo"}
  a3["Administrador: confirma o cancelamento"]
  d3{"Pedido já<br/>estava pago?"}
  s7["Sistema: devolve o estoque"]
  s8["Sistema: muda para Cancelado<br/>e registra no histórico"]
  s9["Sistema: botão Cancelar não aparece"]
  fim(["◉ Fim"])

  ini --> a1 --> s1 --> a2 --> s2 --> d1
  d1 -- avançar status --> s3
  s3 -- não --> s4 --> fim
  s3 -- sim --> s5 --> d2
  d2 -- não --> d1
  d2 -- sim --> fim
  d1 -- cancelar --> s6
  s6 -- não --> s9 --> fim
  s6 -- sim --> a3 --> d3
  d3 -- sim --> s7 --> s8
  d3 -- não --> s8
  s8 --> fim

  classDef ator fill:#fbf1f4,stroke:#b8456b,color:#1f2433
  classDef sistema fill:#eef0f5,stroke:#4a5063,color:#1f2433
  class a1,a2,a3 ator
  class s1,s2,s4,s5,s7,s8,s9 sistema
```

## DE1 — Máquina de estados do Pedido

```mermaid
stateDiagram-v2
  direction LR
  state "Aguardando pagamento" as AG
  state "Pago" as PG
  state "Em preparo" as EP
  state "Saiu para entrega" as SE
  state "Entregue" as EN
  state "Cancelado" as CA

  [*] --> AG : cliente confirma o pedido
  AG --> AG : pagamento recusado ou Pix expirado
  AG --> PG : pagamento aprovado [estoque suficiente]
  PG --> EP : administrador avança
  EP --> SE : administrador avança
  SE --> EN : administrador avança
  AG --> CA : administrador cancela
  PG --> CA : administrador cancela / devolve estoque
  EP --> CA : administrador cancela / devolve estoque
  EN --> [*]
  CA --> [*]
```

| Regra | Onde aparece |
|---|---|
| RN14 — recusa ou expiração mantém o pedido aguardando | Transição AG → AG |
| RN13 — estoque conferido na aprovação | Condição [estoque suficiente] em AG → PG |
| RN15 — etapas só avançam, sem voltar | Não há transições de volta |
| RN16 — cancelamento até "Em preparo", com devolução de estoque se pago | Transições para Cancelado só a partir de AG, PG e EP |

## DE2 — Máquina de estados do Pagamento

```mermaid
stateDiagram-v2
  direction LR
  state "Pendente" as PE
  state "Aprovado" as AP
  state "Recusado" as RE
  state "Expirado" as EX

  [*] --> PE : cliente inicia pagamento
  PE --> AP : gateway aprova [estoque suficiente]
  PE --> RE : gateway recusa (cartão final 0002)
  PE --> RE : estoque insuficiente na aprovação
  PE --> EX : Pix confirmado depois de 15 minutos
  AP --> [*]
  RE --> [*]
  EX --> [*]
```

Cada tentativa de pagamento é um registro novo. Depois de uma recusa ou expiração, uma nova tentativa começa de novo em "Pendente".
