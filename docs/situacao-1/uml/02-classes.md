# UML — Diagrama de Classes e Arquitetura MVC

> Exigência atendida: **R09** (diagrama de classes, incluindo as classes de persistência que dão origem ao banco de dados).
> As classes de persistência (seção 1) são a base do projeto de dados: [dados/](../dados/).
> Diagramas em Mermaid (o GitHub exibe como imagem). Versões em SVG na pasta [img/](img/).

## 1. Classes de persistência (modelo de domínio)

Classes que viram tabelas no banco. Tipos em Python: `str`, `int`, `bool`, `Decimal` (valores em reais), `date` e `datetime`.

```mermaid
classDiagram
  direction LR

  class Usuario {
    +int id
    +str nome
    +str email
    +str telefone
    +str senha_hash
    +Perfil perfil
    +datetime criado_em
    +definir_senha(senha)
    +verificar_senha(senha) bool
    +eh_admin() bool
  }

  class Endereco {
    +int id
    +str apelido
    +str cep
    +str logradouro
    +str numero
    +str complemento
    +str bairro
    +str cidade
    +str uf
    +formatado() str
  }

  class Cupcake {
    +int id
    +str nome
    +str descricao
    +str ingredientes
    +Decimal preco
    +str foto_url
    +int estoque
    +bool ativo
    +bool personalizavel
    +datetime criado_em
    +datetime atualizado_em
    +disponivel() bool
    +baixar_estoque(qtd)
    +devolver_estoque(qtd)
  }

  class Sabor {
    +int id
    +str nome
  }

  class Ocasiao {
    +int id
    +str nome
  }

  class RestricaoAlimentar {
    +int id
    +str nome
  }

  class OpcaoPersonalizacao {
    +int id
    +TipoOpcao tipo
    +str nome
    +Decimal acrescimo
    +bool ativo
  }

  class Cupom {
    +int id
    +str codigo
    +TipoCupom tipo
    +Decimal valor
    +Decimal valor_minimo
    +date valido_de
    +date valido_ate
    +bool ativo
    +validar(subtotal, hoje)
    +calcular_desconto(subtotal) Decimal
  }

  class AreaEntrega {
    +int id
    +str nome
    +str cep_inicial
    +str cep_final
    +Decimal valor_frete
    +int prazo_minutos
    +atende(cep) bool
  }

  class Pedido {
    +int id
    +StatusPedido status
    +Decimal subtotal
    +Decimal desconto
    +Decimal frete
    +Decimal total
    +int prazo_minutos
    +str entrega_cep
    +str entrega_logradouro
    +str entrega_numero
    +str entrega_complemento
    +str entrega_bairro
    +str entrega_cidade
    +str entrega_uf
    +bool visto_pelo_admin
    +datetime criado_em
    +pode_avancar() bool
    +pode_cancelar() bool
    +avancar_status(responsavel)
    +cancelar(responsavel)
    +marcar_como_pago()
  }

  class ItemPedido {
    +int id
    +int quantidade
    +Decimal preco_unitario
    +str mensagem
    +subtotal() Decimal
  }

  class Pagamento {
    +int id
    +MetodoPagamento metodo
    +StatusPagamento status
    +Decimal valor
    +str pix_codigo
    +datetime pix_expira_em
    +str cartao_bandeira
    +str cartao_final
    +str motivo_recusa
    +datetime criado_em
    +datetime atualizado_em
    +pix_expirado(agora) bool
  }

  class HistoricoStatus {
    +int id
    +StatusPedido status
    +datetime registrado_em
  }

  Usuario "1" --> "0..*" Endereco : possui
  Usuario "1" --> "0..*" Pedido : faz
  Cupcake "0..*" --> "1" Sabor : tem
  Cupcake "0..*" -- "0..*" Ocasiao : indicado para
  Cupcake "0..*" -- "0..*" RestricaoAlimentar : atende
  Pedido "1" *-- "1..*" ItemPedido : contém
  ItemPedido "0..*" --> "1" Cupcake : refere-se a
  ItemPedido "0..*" --> "0..1" OpcaoPersonalizacao : recheio
  ItemPedido "0..*" --> "0..1" OpcaoPersonalizacao : cobertura
  Pedido "0..*" --> "0..1" Cupom : usa
  Pedido "1" *-- "0..*" Pagamento : tentativas
  Pedido "1" *-- "1..*" HistoricoStatus : registra
  HistoricoStatus "0..*" --> "0..1" Usuario : responsável
  Pedido ..> AreaEntrega : frete e prazo copiados de
```

### Enumerações

```mermaid
classDiagram
  direction LR
  class Perfil {
    <<enumeration>>
    CLIENTE
    ADMINISTRADOR
  }
  class StatusPedido {
    <<enumeration>>
    AGUARDANDO_PAGAMENTO
    PAGO
    EM_PREPARO
    SAIU_PARA_ENTREGA
    ENTREGUE
    CANCELADO
  }
  class MetodoPagamento {
    <<enumeration>>
    PIX
    CARTAO
  }
  class StatusPagamento {
    <<enumeration>>
    PENDENTE
    APROVADO
    RECUSADO
    EXPIRADO
  }
  class TipoCupom {
    <<enumeration>>
    PERCENTUAL
    VALOR_FIXO
  }
  class TipoOpcao {
    <<enumeration>>
    RECHEIO
    COBERTURA
  }
```

### Decisões de modelagem

| # | Decisão | Motivo |
|---|---|---|
| M1 | `ItemPedido.preco_unitario` guarda o preço no momento da compra, já com os acréscimos | RN10: mudança de preço no catálogo não altera pedidos feitos |
| M2 | `Pedido` guarda uma **cópia** do endereço de entrega (`entrega_*`) em vez de apontar para `Endereco` | O cliente pode editar ou excluir o endereço depois (UC09); o pedido precisa manter o endereço usado na entrega |
| M3 | `Pedido` guarda `subtotal`, `desconto`, `frete` e `total` | Registro do valor efetivamente cobrado, que não pode mudar se cupom, frete ou preços mudarem depois |
| M4 | `Pagamento` é uma classe separada, com várias tentativas por pedido | RN14: depois de recusa ou expiração, o cliente pode tentar de novo; cada tentativa fica registrada |
| M5 | `Pagamento` guarda só `cartao_bandeira` e `cartao_final` | RN12 e RNF05: nunca armazenar número completo nem código de segurança |
| M6 | `HistoricoStatus` registra cada mudança de status com data, hora e responsável | Linha do tempo do cliente (CA12.1) e auditoria da loja (CA17.3) |
| M7 | `Sabor`, `Ocasiao` e `RestricaoAlimentar` são classes, não texto livre | Filtros consistentes (US02) e normalização do banco |
| M8 | `Pedido.visto_pelo_admin` | Destaque de pedidos novos no painel (CA17.6) |

## 2. Classes de sessão e de serviço (não persistidas)

Classes que **não** viram tabelas: o carrinho fica na sessão do usuário e o pagamento usa um serviço com gateway trocável.

```mermaid
classDiagram
  direction LR

  class Carrinho {
    +list~ItemCarrinho~ itens
    +adicionar(cupcake, qtd, recheio, cobertura, mensagem)
    +alterar_quantidade(chave, qtd)
    +remover(chave)
    +subtotal() Decimal
    +total_itens() int
    +limpar()
  }

  class ItemCarrinho {
    +int cupcake_id
    +int quantidade
    +int recheio_id
    +int cobertura_id
    +str mensagem
    +chave() str
  }

  class ServicoPedido {
    +criar_pedido(usuario, carrinho, endereco, cupom) Pedido
    +calcular_frete(cep) AreaEntrega
  }

  class ServicoPagamento {
    -GatewayPagamento gateway
    +pagar_com_cartao(pedido, dados) ResultadoPagamento
    +gerar_pix(pedido) Pagamento
    +confirmar_pix(pagamento) ResultadoPagamento
    -aprovar(pedido, pagamento)
  }

  class GatewayPagamento {
    <<interface>>
    +cobrar_cartao(dados, valor) ResultadoPagamento
    +gerar_pix(valor) ResultadoPix
    +confirmar_pix(codigo) ResultadoPagamento
  }

  class GatewaySimulado {
    +cobrar_cartao(dados, valor) ResultadoPagamento
    +gerar_pix(valor) ResultadoPix
    +confirmar_pix(codigo) ResultadoPagamento
  }

  class DadosCartao {
    +str numero
    +str nome
    +str validade
    +str cvv
    +numero_valido() bool
    +bandeira() str
    +final() str
  }

  class ResultadoPagamento {
    +bool aprovado
    +str motivo
  }

  class ResultadoPix {
    +str codigo
    +datetime expira_em
  }

  Carrinho "1" *-- "0..*" ItemCarrinho
  ServicoPedido ..> Carrinho : lê
  ServicoPagamento --> GatewayPagamento : usa
  GatewayPagamento <|.. GatewaySimulado : implementa
  ServicoPagamento ..> DadosCartao
  GatewayPagamento ..> ResultadoPagamento
  GatewayPagamento ..> ResultadoPix
```

**Por que uma interface `GatewayPagamento`?** O MVP usa o `GatewaySimulado` (RN11). Para usar um gateway real no futuro, basta criar outra classe que implemente a mesma interface, sem mexer em controllers nem em telas.

## 3. Arquitetura MVC

Mesma estrutura da Figura 2 do material teórico (Usuário → Router → Controller ↔ Model; Controller → View → HTML).

```mermaid
flowchart LR
  usuario(["Usuário<br/>navegador do celular"])
  router["Router<br/>rotas do Flask"]
  C["CONTROLLERS<br/>Blueprints do Flask<br/>────────────<br/>vitrine · carrinho<br/>autenticacao · conta<br/>checkout · pagamento<br/>pedidos<br/>admin_cupcakes · admin_pedidos"]
  M["MODELS<br/>────────────<br/>Entidades SQLAlchemy<br/>Carrinho (sessão)<br/>ServicoPedido · ServicoPagamento<br/>GatewaySimulado"]
  V["VIEWS<br/>────────────<br/>Templates Jinja2 (HTML)<br/>CSS mobile-first<br/>JavaScript"]
  db[("PostgreSQL")]

  usuario -->|"requisição HTTP"| router
  router --> C
  C <-->|"dados"| M
  M <-->|"SQL via ORM"| db
  C -->|"dados"| V
  V -->|"HTML"| usuario
```

| Camada | Responsabilidade | Não pode |
|---|---|---|
| **Model** | Regras de negócio (RN01–RN21), validação dos dados e acesso ao banco | Conhecer HTML ou requisições HTTP |
| **View** | Apresentar dados e coletar entradas; validação visual imediata em JavaScript | Conter regra de negócio (a regra sempre é conferida de novo no Model) |
| **Controller** | Receber a requisição, chamar o Model, escolher a View e tratar erros | Acessar o banco diretamente |
