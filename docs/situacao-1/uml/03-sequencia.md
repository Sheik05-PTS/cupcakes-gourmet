# UML — Diagramas de Sequência

> Exigência atendida: **R10** (diagramas de sequência).
> Mostram a troca de mensagens entre View, Controller e Model (arquitetura MVC) nos fluxos mais críticos do sistema.

| # | Diagrama | Casos de uso | Por que foi escolhido |
|---|---|---|---|
| SD1 | Adicionar ao carrinho | UC04, UC05 | Fluxo mais usado do app |
| SD2 | Finalizar pedido | UC10, UC06, UC11 | Congela preços e endereço e cria o pedido |
| SD3 | Pagar com cartão | UC12 | Fluxo crítico: transação, trava de estoque e dados sensíveis |
| SD4 | Pagar com Pix | UC12 (FA1) | Regra de expiração em 15 minutos |
| SD5 | Atualizar e acompanhar status | UC16, UC13 | Integração entre painel da loja e tela do cliente |

## SD1 — Adicionar ao carrinho

```mermaid
sequenceDiagram
  autonumber
  actor Cli as Cliente
  participant V as View<br/>detalhe do cupcake
  participant C as CarrinhoController
  participant Cup as Cupcake<br/>(Model)
  participant Car as Carrinho<br/>(sessão)
  participant DB as PostgreSQL

  Cli->>V: escolhe quantidade (e personalização) e toca "Adicionar"
  V->>V: valida quantidade de 1 a 20 (JavaScript)
  V->>C: POST /carrinho/itens
  C->>Cup: buscar(cupcake_id)
  Cup->>DB: SELECT cupcake
  DB-->>Cup: dados do cupcake
  alt inativo, esgotado ou quantidade acima do estoque
    C-->>V: erro 422 + mensagem com o limite
    V-->>Cli: exibe a mensagem, carrinho não muda
  else disponível
    C->>Car: adicionar(cupcake, qtd, recheio, cobertura, mensagem)
    Car->>Car: mesma chave? soma quantidade : cria nova linha
    C-->>V: 200 + total de itens
    V-->>Cli: "Adicionado ao carrinho" e atualiza o ícone
  end
```

## SD2 — Finalizar pedido

```mermaid
sequenceDiagram
  autonumber
  actor Cli as Cliente
  participant V as View<br/>checkout
  participant C as CheckoutController
  participant S as ServicoPedido
  participant M as Models<br/>AreaEntrega · Cupom · Cupcake
  participant DB as PostgreSQL

  Cli->>V: toca "Finalizar pedido"
  V->>C: GET /checkout
  C->>C: exige login (senão, redireciona para entrar)
  C-->>V: resumo do carrinho + endereços do cliente
  Cli->>V: escolhe o endereço
  V->>C: POST /checkout/frete
  C->>S: calcular_frete(cep)
  S->>M: AreaEntrega.atende(cep)
  alt CEP fora da área
    C-->>V: "Ainda não entregamos neste CEP"
  else CEP atendido
    C-->>V: frete, prazo e total
  end
  opt cliente informa cupom
    Cli->>V: digita o código e toca "Aplicar"
    V->>C: POST /checkout/cupom
    C->>M: Cupom.validar(subtotal, hoje) e calcular_desconto(subtotal)
    C-->>V: desconto e novo total, ou mensagem de cupom inválido
  end
  Cli->>V: toca "Confirmar pedido"
  V->>C: POST /checkout/confirmar
  C->>S: criar_pedido(usuario, carrinho, endereco, cupom)
  S->>M: confere disponibilidade e estoque dos itens
  alt item indisponível
    S-->>C: erro com o item
    C-->>V: volta ao carrinho com a mensagem
  else tudo disponível
    S->>DB: BEGIN
    S->>DB: INSERT pedido (valores e cópia do endereço)
    S->>DB: INSERT itens (preço unitário congelado)
    S->>DB: INSERT histórico "Aguardando pagamento"
    S->>DB: COMMIT
    C-->>V: redireciona para o pagamento do pedido
  end
```

## SD3 — Pagar com cartão (simulado)

```mermaid
sequenceDiagram
  autonumber
  actor Cli as Cliente
  participant V as View<br/>pagamento
  participant C as PagamentoController
  participant S as ServicoPagamento
  participant G as GatewaySimulado
  participant DB as PostgreSQL

  Cli->>V: informa número, nome, validade e CVV
  V->>C: POST /pedidos/{id}/pagamento/cartao
  C->>C: DadosCartao: Luhn, validade futura, CVV com 3 ou 4 dígitos
  alt dados inválidos
    C-->>V: 422 + mensagem no campo com erro
  else dados válidos
    C->>S: pagar_com_cartao(pedido, dados)
    S->>DB: INSERT pagamento PENDENTE (só bandeira e 4 últimos dígitos)
    S->>G: cobrar_cartao(dados, total)
    alt cartão terminado em 0002
      G-->>S: recusado
      S->>DB: UPDATE pagamento RECUSADO
      C-->>V: "Pagamento recusado. Tente outro cartão ou pague com Pix."
    else aprovado
      G-->>S: aprovado
      S->>DB: BEGIN
      S->>DB: SELECT cupcakes do pedido FOR UPDATE (trava)
      alt estoque insuficiente
        S->>DB: ROLLBACK
        S->>DB: UPDATE pagamento RECUSADO (estoque insuficiente)
        C-->>V: informa o item que ficou indisponível
      else estoque suficiente
        S->>DB: UPDATE estoque dos cupcakes
        S->>DB: UPDATE pagamento APROVADO
        S->>DB: UPDATE pedido PAGO + INSERT histórico
        S->>DB: COMMIT
        C->>C: esvazia o carrinho da sessão
        C-->>V: redireciona para "Pedido confirmado!"
      end
    end
  end
```

> Os dados completos do cartão existem só na memória durante a requisição e nunca são gravados (RN12).

## SD4 — Pagar com Pix (simulado)

```mermaid
sequenceDiagram
  autonumber
  actor Cli as Cliente
  participant V as View<br/>pagamento
  participant C as PagamentoController
  participant S as ServicoPagamento
  participant G as GatewaySimulado
  participant DB as PostgreSQL

  Cli->>V: escolhe Pix
  V->>C: POST /pedidos/{id}/pagamento/pix
  C->>S: gerar_pix(pedido)
  S->>G: gerar_pix(total)
  G-->>S: código fictício + expira_em (agora + 15 min)
  S->>DB: INSERT pagamento PENDENTE (Pix)
  C-->>V: código "copia e cola", contagem regressiva e botão "Simular pagamento"
  Cli->>V: toca "Simular pagamento"
  V->>C: POST /pagamentos/{id}/confirmar
  C->>S: confirmar_pix(pagamento)
  alt prazo vencido
    S->>DB: UPDATE pagamento EXPIRADO
    C-->>V: "Código Pix expirado" + opção de gerar outro
  else dentro do prazo
    S->>G: confirmar_pix(código)
    G-->>S: aprovado
    Note over S,DB: mesma transação do SD3: trava, confere e baixa estoque,<br/>aprova pagamento, marca pedido como PAGO
    C-->>V: redireciona para "Pedido confirmado!"
  end
```

## SD5 — Atualizar status (loja) e acompanhar (cliente)

```mermaid
sequenceDiagram
  autonumber
  actor Adm as Administrador
  participant PV as View<br/>painel de pedidos
  participant AC as AdminPedidosController
  participant P as Pedido<br/>(Model)
  participant DB as PostgreSQL
  participant CV as View<br/>detalhe do pedido
  participant PC as PedidosController
  actor Cli as Cliente

  loop a cada 30 segundos (painel aberto)
    PV->>AC: GET /admin/pedidos?desde=...
    AC->>DB: SELECT pedidos novos
    AC-->>PV: lista atualizada, novos destacados
  end
  Adm->>PV: toca "Avançar status"
  PV->>AC: POST /admin/pedidos/{id}/avancar
  AC->>AC: exige perfil Administrador
  AC->>P: pode_avancar()
  alt pedido aguardando pagamento, entregue ou cancelado
    AC-->>PV: mensagem, nada muda
  else pode avançar
    AC->>P: avancar_status(responsavel)
    P->>DB: UPDATE status + INSERT histórico
    AC-->>PV: novo status
  end
  loop a cada 30 segundos (tela do cliente aberta)
    CV->>PC: GET /pedidos/{id}/status (JSON)
    PC->>PC: confere se o pedido é do cliente logado
    PC->>DB: SELECT status e histórico
    PC-->>CV: status e linha do tempo
    CV-->>Cli: atualiza a linha do tempo sem recarregar
  end
```
