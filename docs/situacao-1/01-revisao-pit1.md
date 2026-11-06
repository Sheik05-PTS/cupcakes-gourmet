# 01 — Revisão do Planejamento do PIT I

> Exigências atendidas: **R01** (revisitar e revisar os documentos do PIT I) e **R03** (ciclo de melhoria contínua).

## 1. Documento revisado

**Projeto de Intervenção — Situação-Problema 1: App Mobile para Loja de Cupcakes Gourmet** (PIT I).

Resumo do que o PIT I definiu:

- **Problema:** uma loja de cupcakes gourmet quer vender pela internet. Na tentativa anterior, com outro fornecedor, os requisitos foram mal levantados e o app entregue não atendeu ao cliente.
- **Objetivo:** estruturar o desenvolvimento do app com vitrine virtual, pedido eletrônico, pagamento e entrega, com requisitos compreendidos, documentados, priorizados e validados antes da construção.
- **Metodologia:** práticas ágeis (histórias de usuário, mapa de afinidade, backlog priorizado) combinadas com modelagem UML e prototipação.
- **Artefatos produzidos:** mapa de afinidade (Anexo A), backlog de 18 histórias com pontos e prioridade (Anexo B) e exemplos de tarefas (Anexo C).
- **Artefatos prometidos (Anexo D):** especificação ágil completa, artefatos UML, protótipos de telas e testes de aceitação.

## 2. Pontos fortes mantidos

1. O foco do problema, **requisitos mal levantados**, continua como eixo do projeto. Toda história agora tem critérios de aceitação verificáveis.
2. O backlog do Anexo B é mantido como base, com os mesmos IDs (US01 a US18), o que preserva a rastreabilidade com o PIT I.
3. Os temas do mapa de afinidade (vitrine, pedido, pagamento, entrega, conta, administração) viram os módulos do sistema.

## 3. Lacunas encontradas

| # | Lacuna | Impacto | Tratamento no PIT II |
|---|---|---|---|
| L1 | Critérios de aceitação e regras de negócio prometidos no Anexo D não constam no documento | Sem eles, repete-se o erro do fornecedor anterior: requisitos ambíguos | Escritos para todas as histórias do MVP no formato Dado/Quando/Então ([03-requisitos.md](03-requisitos.md)) |
| L2 | Nenhum requisito não funcional | Qualidade (segurança, usabilidade, desempenho) fica sem critério de verificação | RNF01 a RNF11 definidos e mensuráveis |
| L3 | Diagramas UML prometidos, mas ausentes | Estrutura e comportamento do sistema não documentados | Produzidos na pasta `uml/` |
| L4 | Wireframes, mapa conceitual e mapa navegacional prometidos, mas ausentes | Experiência do usuário não validada antes do código | Produzidos na pasta `ihc/` |
| L5 | Sem modelo de dados | O PIT II exige projeto conceitual, lógico, físico e dicionário de dados | Produzidos na pasta `dados/` |
| L6 | O MVP é citado ("vitrine, pedidos, pagamento e entrega"), mas não definido história por história | Escopo aberto, risco de não terminar | Corte do MVP explícito em [02-escopo-mvp.md](02-escopo-mvp.md) |
| L7 | Itens do mapa de afinidade sem história no backlog (favoritar, combos e kits presente, agendar entrega, programa de pontos) | Inconsistência entre anexos | Declarados como fora de escopo do MVP |
| L8 | A persona "entregador" é citada no procedimento, mas nenhuma história a atende | Ator sem função definida | No MVP, o administrador atualiza o status da entrega; app do entregador vira evolução futura |
| L9 | "Acompanhar status em tempo real" (US12) sem definição do que é "tempo real" | Requisito impossível de verificar | Redefinido: o status atualiza automaticamente na tela a cada 30 segundos |
| L10 | Pagamento por Pix e cartão sem definir integração | Integração real exige conta empresarial e dados financeiros reais | Gateway **simulado** no MVP, isolado numa camada própria para troca futura |
| L11 | Cadastro de cupons não tem história de administração | Não fica claro quem cria os cupons | No MVP, os cupons são carregados por script de dados iniciais; tela de gestão de cupons fica para evolução |
| L12 | Campo RGM em branco | Identificação incompleta | Corrigido na entrega final |

## 4. Alterações aplicadas (registro de melhoria contínua)

| Item | PIT I | PIT II | Motivo |
|---|---|---|---|
| Plataforma | "App mobile" | App web **mobile-first**, instalável no celular (PWA) | Atende ao uso no celular, usa HTML/CSS/JS como pede o PIT II, e os testadores acessam por um link, sem instalar nada pela loja de apps |
| Escopo | 18 histórias sem corte de MVP | MVP com 16 histórias; US14 e US18 em versão futura | Viabilidade dentro do prazo, mantendo o fluxo completo de compra |
| Pagamento | Pix e cartão | Pix e cartão **simulados**, com cenários de aprovado, recusado e expirado | É um MVP: valida o fluxo e a experiência sem transações financeiras reais |
| Status do pedido | "Tempo real" | Atualização automática a cada 30 s | Torna o requisito verificável |
| Entregador | Persona citada | Sem acesso no MVP; status atualizado pelo administrador | Nenhuma história do backlog atende o entregador |
| Requisitos | Só histórias | Histórias + critérios de aceitação + regras de negócio + RNF | Corrigir a causa raiz do problema original |
| Rastreabilidade | Inexistente | Matriz história → código → teste | Permite validar que cada requisito foi entregue |
| Frete (revisão interna C1) | Só no checkout | Estimativa por CEP no carrinho, sem login (CA11.3) | Evita desistência por custo desconhecido |
| Pagamento (revisão interna C2) | — | Aviso de ambiente de demonstração (RN21) | Transparência com quem testa |
| Painel de pedidos (revisão interna L1) | — | Atualização automática e destaque de pedidos novos (CA17.6) | A loja percebe pedidos novos sem recarregar |
| Estoque (revisão interna Q1) | — | Trava de registro na baixa de estoque (RNF07) | Evita estoque negativo com pagamentos simultâneos |
| Acessibilidade (revisão interna Q2) | — | Status com ícone + texto (RNF10) | Inclusão de pessoas com daltonismo |

## 5. Próximas revisões

Este documento é atualizado a cada nova rodada de feedback (colegas na Situação 1, testadores na Situação 3). Cada alteração entra na tabela da seção 4 com o motivo.
