# 02 — Escopo e MVP

> Exigência atendida: **R02** (verificar e adequar escopo/ideia e preparar para execução).

## 1. Visão do produto

**Cupcakes Gourmet** é um app web mobile-first para uma loja de cupcakes gourmet vender pela internet. O cliente navega pela vitrine, monta e personaliza o pedido, paga e acompanha a entrega. O administrador da loja mantém a vitrine e gerencia os pedidos.

**Proposta de valor:** comprar cupcakes gourmet pelo celular em poucos toques, com clareza de preço, frete e prazo antes de pagar.

## 2. Atores

| Ator | Descrição | Acesso |
|---|---|---|
| Visitante | Pessoa sem conta ou não logada | Vitrine, detalhes, filtros, carrinho, cadastro e login |
| Cliente | Pessoa cadastrada e logada | Tudo do visitante + endereços, checkout, pagamento, acompanhamento e histórico de pedidos |
| Administrador | Funcionário da loja | Painel administrativo: produtos, disponibilidade e pedidos |
| Gateway de pagamento (simulado) | Sistema externo representado por um módulo interno | Aprova, recusa ou expira pagamentos |

## 3. Escopo do MVP

O MVP cobre o **fluxo completo de compra**: vitrine → carrinho → checkout → pagamento → acompanhamento → gestão pela loja.

| ID | História | Prioridade (PIT I) | Pontos | Módulo |
|---|---|---|---|---|
| US01 | Visualizar a vitrine | 1 | 3 | Vitrine |
| US03 | Ver fotos, ingredientes e descrição | 2 | 3 | Vitrine |
| US04 | Adicionar ao carrinho | 3 | 5 | Pedido |
| US02 | Filtrar por sabor, preço, ocasião e restrição alimentar | 4 | 5 | Vitrine |
| US06 | Revisar quantidades e valores no carrinho | 5 | 3 | Pedido |
| US05 | Personalizar recheio, cobertura e mensagem | 6 | 8 | Pedido |
| US08 | Pagar por Pix ou cartão (simulado) | 7 | 8 | Pagamento |
| US07 | Aplicar cupom de desconto | 8 | 3 | Pagamento |
| US09 | Receber confirmação do pagamento e do pedido | 9 | 5 | Pagamento |
| US10 | Cadastrar endereço de entrega | 10 | 3 | Entrega |
| US11 | Calcular frete e prazo | 11 | 5 | Entrega |
| US12 | Acompanhar status do pedido | 12 | 8 | Entrega |
| US13 | Criar conta e fazer login | 13 | 5 | Conta |
| US15 | Cadastrar e editar cupcakes (admin) | 14 | 5 | Admin |
| US16 | Controlar disponibilidade (admin) | 15 | 5 | Admin |
| US17 | Gerenciar pedidos (admin) | 17 | 8 | Admin |
| | **Total do MVP** | | **82** | |

### Versão futura (fora do MVP)

| ID / Item | Motivo |
|---|---|
| US14 — Avaliar pedido | Não faz parte do fluxo de compra. Implementar se sobrar tempo |
| US18 — Relatórios de vendas | Não faz parte do fluxo de compra. Implementar se sobrar tempo |
| Pagamento real (Pix e cartão) | Exige conta empresarial e credenciais de produção. O MVP valida o fluxo com gateway simulado |
| App do entregador | Nenhuma história do backlog o atende |
| Favoritar produtos, combos e kits presente, agendar entrega, programa de pontos | Itens do mapa de afinidade sem história no backlog |
| Tela de gestão de cupons | Cupons carregados por script de dados iniciais |
| Notificações por e-mail ou push | A confirmação é exibida na tela e no histórico de pedidos |
| Cliente cancelar pedido não pago | Pedido não pago não baixa estoque nem gera cobrança (revisão interna C3) |
| Horário de funcionamento e capacidade de produção | Exige regras de agenda (revisão interna L2) |

## 4. Decisões de projeto

| # | Decisão | Alternativas consideradas | Justificativa |
|---|---|---|---|
| D1 | App web mobile-first instalável (PWA) | App nativo Android/iOS | Funciona no celular como app, usa HTML/CSS/JS exigidos pelo PIT II e os testadores acessam por um link |
| D2 | Back-end em **Python 3 + Flask**, padrão **MVC** | Java + Spring, PHP | Python está entre as linguagens indicadas; Flask é leve e deixa a separação MVC explícita |
| D3 | Banco **PostgreSQL** | MySQL, SQLite | SGBD popular, gratuito e de fácil manutenção, como pede o Problema em Foco |
| D4 | ORM **SQLAlchemy** | SQL puro | Consultas parametrizadas (segurança) e mapeamento direto do diagrama de classes para tabelas |
| D5 | Front-end com templates **Jinja2** + CSS + JavaScript puro | React, ferramenta no-code | Atende diretamente ao "HTML, CSS e JavaScript" do PIT II, sem camada extra para aprender |
| D6 | Testes com **Pytest** | unittest | Framework xUnit para Python, citado no material da disciplina |
| D7 | Hospedagem gratuita: **Render** (aplicação) + **Neon** (PostgreSQL) | Heroku, Railway | Planos gratuitos sem cartão de crédito. Limitação conhecida: a aplicação "dorme" sem uso e leva alguns segundos para acordar |
| D8 | Gateway de pagamento **simulado**, atrás de uma interface própria | Mercado Pago sandbox | É um MVP: valida o fluxo sem transações reais. A interface permite trocar pelo gateway real no futuro |
| D9 | Código e documentação em um único repositório no **GitHub** | Repositórios separados | Exigência do PIT II: tudo num lugar só |
| D10 | Modo de codificação **tradicional** | Low-code, no-code | Controle total do MVC e dos testes exigidos |

## 5. Premissas e restrições

- **Premissas:** a loja atende uma única cidade; os preços são em reais; o cliente tem um celular com navegador atualizado.
- **Restrições:** prazo da disciplina; hospedagem gratuita; nenhum dado de cartão real é processado ou armazenado.

## 6. Critério de "pronto" do MVP

O MVP está pronto quando:
1. todas as 16 histórias passam nos seus critérios de aceitação;
2. os testes unitários e de integração passam;
3. a aplicação está publicada e acessível por link;
4. o manual de uso está escrito.
