# Cupcakes Gourmet — Checklist de Exigências do PIT II

Projeto Integrador Transdisciplinar em Engenharia de Software II
Aluno: Petterson Teixeira · Base: Projeto de Intervenção do PIT I (App Mobile para Loja de Cupcakes Gourmet)

Fontes das exigências:
- **MT** = Material Teórico
- **SP1/SP2/SP3** = Situações-Problema 1, 2 e 3
- **PF** = Problema em Foco
- **FE** = Formulário de Entrega (PIT_atividade.docx)
- **PIT I** = Itens prometidos no Anexo D do Projeto de Intervenção

Status: Pendente · Em andamento · Concluído

---

## Situação 1 — Revisão do planejamento e projeto de dados

| ID | Exigência | Fonte | Entregável | Status |
|---|---|---|---|---|
| R01 | Revisitar e revisar todos os documentos do PIT I | SP1, PF | `docs/situacao-1/01-revisao-pit1.md` (o que mudou e por quê) | Concluído |
| R02 | Verificar e adequar escopo/ideia e preparar para execução | SP1 | `docs/situacao-1/02-escopo-mvp.md` (escopo, MVP, fora de escopo, decisões) | Concluído |
| R03 | Ciclo de melhoria contínua (Kaizen): documentação mais robusta e clara | SP1, PF | Registro de alterações em cada documento | Em andamento |
| R04 | Especificação ágil: histórias com critérios de aceitação, regras de negócio | PIT I (Anexo D) | `docs/situacao-1/03-requisitos.md` | Concluído |
| R05 | Requisitos não funcionais (qualidade: confiabilidade, usabilidade, segurança, desempenho, manutenibilidade) | MT, PIT I | `docs/situacao-1/03-requisitos.md` | Concluído |
| R06 | Validação dos requisitos (corretos, sem ambiguidade, modificáveis, rastreáveis a código e testes) | MT | Matriz de rastreabilidade história → código → teste | Em andamento |
| R07 | UML: diagrama de casos de uso geral | SP1, PIT I | `docs/situacao-1/uml/01-casos-de-uso.md` | Concluído |
| R08 | UML: casos de uso expandidos | PIT I | `docs/situacao-1/04-casos-de-uso-expandidos.md` | Concluído |
| R09 | UML: diagrama de classes (inclui classes de persistência) | SP1, PIT I | `docs/situacao-1/uml/02-classes.md` | Concluído |
| R10 | UML: diagramas de sequência | SP1, PIT I | `docs/situacao-1/uml/03-sequencia.md` (5 diagramas) | Concluído |
| R11 | UML: diagramas de atividades | SP1 | `docs/situacao-1/uml/04-atividades-e-estados.md` (3 atividades + 2 estados) | Concluído |
| R12 | IHC: telas (wireframes/mockups) revisadas e incrementadas | SP1, PIT I | `docs/situacao-1/06-ihc.md` §2 + protótipo em `ihc/prototipo/` (21 telas) | Concluído |
| R13 | IHC: mensagens de erro, sucesso e confirmação | SP1, PIT I | `06-ihc.md` §6 (catálogo com 48 mensagens) + telas T18–T21 | Concluído |
| R14 | IHC: mapa conceitual | SP1, PIT I | `06-ihc.md` §4 | Concluído |
| R15 | IHC: mapa navegacional | PIT I | `06-ihc.md` §3 | Concluído |
| R16 | IHC aplicando os princípios do material (clareza, consistência, simplicidade, controle do usuário, reversibilidade, feedback, estética) | MT | `06-ihc.md` §5 | Concluído |
| R17 | Projeto conceitual de dados (a partir do diagrama de classes de persistência) | SP1 | `docs/situacao-1/dados/01-modelo-conceitual.md` | Concluído |
| R18 | Projeto lógico **normalizado** (até 3FN, com justificativa) | SP1 | `docs/situacao-1/dados/02-modelo-logico.md` | Concluído |
| R19 | Projeto físico do banco em SGBD popular (domínios, NOT NULL, chaves, integridade referencial, cardinalidade) | SP1, PF, MT | `database/schema.sql` + `seed.sql`, testado (`dados/04-verificacao-do-banco.md`) | Concluído |
| R20 | Documentação do banco + dicionário de dados | SP1 | `docs/situacao-1/dados/03-dicionario-de-dados.md` | Concluído |
| R21 | Pedir crítica da solução a colegas e incorporar as melhores sugestões | PF, MT | `docs/situacao-1/05-feedback-colegas.md` (quem, o quê, decisão) | Em andamento |
| R22 | Documentação de planejamento versionada no GitHub | PF, FE | Link do repositório (FE: "Documentação") | Concluído |

## Situação 2 — Desenvolvimento

| ID | Exigência | Fonte | Entregável | Status |
|---|---|---|---|---|
| R23 | Criar usuário no GitHub e repositório público | SP2 | Conta `Sheik05-PTS` + https://github.com/Sheik05-PTS/cupcakes-gourmet | Concluído |
| R24 | Front-end em HTML, CSS e JavaScript | SP2 | `app/views`, `app/static` | Pendente |
| R25 | Back-end com padrão MVC | SP2, MT | `app/models`, `app/controllers` | Pendente |
| R26 | Linguagem entre Java, PHP, C#/.NET ou Python | SP2 | Definida em `README.md` e no FE | Concluído |
| R27 | Testes unitários do back-end (framework xUnit) | SP2, MT | `tests/unit` | Pendente |
| R28 | Testes do front-end | SP2 | `tests/` (front) | Pendente |
| R29 | Erros tratados (validação de entrada, páginas de erro, mensagens amigáveis) | SP2 | Código + catálogo de mensagens (R13) | Pendente |
| R30 | Solução funcional e completa (todas as histórias do MVP) | SP2 | Matriz de rastreabilidade (R06) toda verde | Pendente |
| R31 | Código-fonte de front e back + bibliotecas (dependências declaradas) | PF | Repositório + `requirements.txt` | Pendente |
| R32 | Manual de uso | PF | `docs/situacao-2/manual-de-uso.md` (com prints) | Pendente |
| R33 | Solução hospedada e acessível por link | FE | Link da solução em funcionamento | Pendente |
| R34 | Revisitar UI/design durante o desenvolvimento e atualizar a documentação | PF | Registro de alterações de IHC | Pendente |
| R35 | Vídeo narrado pelo aluno, **mínimo 5 min**, demonstrando o funcionamento | PF, FE | Link do vídeo (FE: "Codificação") | Pendente |
| R36 | Preencher tabela do FE: linguagem, banco, hospedagem, plataforma, modo de codificação | FE | PIT_atividade.docx | Pendente |

## Situação 3 — Testes, validação e fechamento

| ID | Exigência | Fonte | Entregável | Status |
|---|---|---|---|---|
| R37 | Testes de integração | SP3, MT (Modelo V) | `tests/integration` | Pendente |
| R38 | Testes de sistema | MT (Modelo V) | `docs/situacao-3/plano-de-testes.md` | Pendente |
| R39 | Testes de aceitação no formato Dado/Quando/Então | PIT I, MT | `docs/situacao-3/testes-aceitacao.md` | Em andamento |
| R40 | Documentar verificação e validação mostrando o comportamento esperado | SP3 | Relatório de testes com evidências | Pendente |
| R41 | Formulário/template para testadores (bugs, sugestões, prints) com no mínimo: nome, data, o que funcionou, o que não funcionou e o que corrigir, funcionalidade não testada e motivo | SP3, PF | `docs/situacao-3/formulario-de-teste.docx` (Word, 9 seções, roteiro com 18 itens ligados às histórias) | Em andamento |
| R42 | 5 testadores reais (colegas ou profissionais) | SP3, PF, FE | 5 respostas | Pendente |
| R43 | PDF com as 5 avaliações, sem esconder falhas | PF | `docs/situacao-3/avaliacoes-testadores.pdf` | Pendente |
| R44 | Corrigir e melhorar conforme sugestões pertinentes, registrando na documentação | SP3 | Issues/commits vinculados + registro de alterações | Pendente |
| R45 | Laudo de Qualidade: erros, correções e evidências | FE | `docs/situacao-3/laudo-de-qualidade.md` | Pendente |
| R46 | Vídeo de **até 5 min** com as modificações feitas | SP3, FE | Link do vídeo (FE: "Vídeo da Solução atualizada") | Pendente |
| R47 | Estrutura de diretórios no GitHub para todas as situações + código | SP3 | Estrutura abaixo | Em andamento |

## Entrega final

| ID | Exigência | Fonte | Entregável | Status |
|---|---|---|---|---|
| R48 | Formulário PIT_atividade.docx preenchido (nome, RGM, links, tabela, 5 testes, laudo, vídeo) | FE | PIT_atividade.docx | Pendente |
| R49 | Repositório mantido no GitHub em qualquer situação | PF | Repositório público | Em andamento |

---

## Estrutura planejada do repositório

```
cupcakes-gourmet/
├── README.md                  # visão geral, como rodar, links
├── docs/
│   ├── 00-checklist-exigencias.md
│   ├── situacao-1/            # planejamento revisado, UML, IHC, dados
│   ├── situacao-2/            # manual de uso, decisões técnicas
│   └── situacao-3/            # testes, avaliações, laudo
├── database/                  # schema.sql, seed.sql
├── app/
│   ├── models/                # M
│   ├── views/                 # V (templates HTML)
│   ├── controllers/           # C
│   └── static/                # CSS, JS, imagens
└── tests/
    ├── unit/
    └── integration/
```

## Lacunas encontradas no documento do PIT I

1. O Anexo D **promete** especificação ágil, UML, protótipos e testes de aceitação, mas o documento não traz nenhum deles. Esses itens precisam ser **produzidos** agora, não só revisados (R04, R07–R15, R39).
2. O backlog não tem critérios de aceitação nem regras de negócio por história (R04).
3. O corte do MVP é citado ("vitrine, pedidos, pagamento e entrega"), mas não está definido história por história (R02).
4. Não há requisitos não funcionais (R05).
5. Não há modelo de dados (R17–R20).
6. O campo RGM está em branco.
