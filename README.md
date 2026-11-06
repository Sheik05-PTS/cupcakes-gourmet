# Cupcakes Gourmet

App web mobile-first para uma loja de cupcakes gourmet vender pela internet: vitrine, carrinho com personalização, cupom, pagamento (simulado), acompanhamento da entrega e painel da loja.

Projeto Integrador Transdisciplinar em Engenharia de Software II, Cruzeiro do Sul Virtual.
Autor: Petterson Teixeira

## Andamento

| Etapa | Situação |
|---|---|
| Situação 1: revisão do planejamento, UML, telas e banco de dados | Concluída; aguardando o feedback dos colegas |
| Situação 2: desenvolvimento (front-end, back-end MVC e testes) | Em andamento |
| Situação 3: testes com usuários, correções e laudo de qualidade | Pendente |

O controle completo das exigências da disciplina está em [docs/00-checklist-exigencias.md](docs/00-checklist-exigencias.md).

## Links

- Aplicação em funcionamento: *em breve*
- Vídeo de demonstração (Situação 2): *em breve*
- Vídeo das melhorias após os testes (Situação 3): *em breve*

## Tecnologias

| Camada | Tecnologia |
|---|---|
| Back-end | Python 3 + Flask, padrão MVC |
| Banco de dados | PostgreSQL 16 |
| Front-end | HTML (templates Jinja2), CSS e JavaScript |
| Testes | Pytest |
| Hospedagem | Render (aplicação) + Neon (PostgreSQL) |

> O pagamento é **simulado**: nenhuma cobrança real é feita. Pix gera um código fictício e, no cartão, números terminados em 0002 são recusados para testar o fluxo de erro.

## Estrutura do repositório

```
cupcakes-gourmet/
├── README.md
├── database/              script do banco, dados iniciais e verificação
├── docs/
│   ├── 00-checklist-exigencias.md
│   ├── situacao-1/        planejamento revisado, UML, telas e modelo de dados
│   ├── situacao-2/        manual de uso e decisões técnicas
│   └── situacao-3/        testes, avaliações e laudo de qualidade
├── app/                   código da aplicação (models, views, controllers)
└── tests/                 testes automatizados
```

## Documentação da Situação 1

| Documento | Conteúdo |
|---|---|
| [Revisão do PIT I](docs/situacao-1/01-revisao-pit1.md) | O que mudou em relação ao Projeto Integrador I e por quê |
| [Escopo e MVP](docs/situacao-1/02-escopo-mvp.md) | Atores, histórias do MVP e decisões de projeto |
| [Requisitos](docs/situacao-1/03-requisitos.md) | Regras de negócio, critérios de aceitação e requisitos não funcionais |
| [Casos de uso expandidos](docs/situacao-1/04-casos-de-uso-expandidos.md) | Fluxos principais, alternativos e de exceção |
| [Feedback dos colegas](docs/situacao-1/05-feedback-colegas.md) | Críticas recebidas e o que foi aceito |
| [Interface (IHC)](docs/situacao-1/06-ihc.md) | Telas, mapa navegacional, mapa conceitual e catálogo de mensagens |
| [UML](docs/situacao-1/uml/) | Casos de uso, classes, sequência, atividades e estados |
| [Banco de dados](docs/situacao-1/dados/) | Modelo conceitual, lógico, dicionário de dados e verificação |
| [Protótipo navegável](docs/situacao-1/ihc/prototipo/index.html) | As 21 telas em HTML |
| [Projeto do PIT I (original)](docs/situacao-1/00-pit1-projeto-de-intervencao.pdf) | Documento de partida |

## Banco de dados

Com o PostgreSQL instalado, crie um banco vazio e rode os scripts:

```bash
createdb cupcakes
psql -d cupcakes -f database/schema.sql
psql -d cupcakes -f database/seed.sql
```

Para conferir as restrições de integridade num banco de teste vazio:

```bash
python database/verificar_schema.py "postgresql://usuario:senha@localhost/cupcakes_teste"
```

As instruções para rodar a aplicação entram aqui assim que o código da Situação 2 estiver no repositório.
