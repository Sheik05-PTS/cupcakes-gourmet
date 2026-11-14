# Situação 2 — 01. Publicação da aplicação

> Exigência atendida: **R33** (solução hospedada e acessível por link).

## Arquitetura de produção

| Parte | Serviço | Plano | Região |
|---|---|---|---|
| Aplicação Flask (Gunicorn) | Render — Web Service | Gratuito | Virginia (EUA) |
| Banco PostgreSQL | Neon | Gratuito | AWS US East (N. Virginia) |
| Código-fonte | GitHub — `Sheik05-PTS/cupcakes-gourmet` | Público | — |

A aplicação e o banco ficam na mesma região para reduzir o tempo de cada consulta.

## Como a publicação funciona

1. A configuração está no arquivo [`render.yaml`](../../render.yaml) (Blueprint do Render).
2. A cada `git push` na branch `main`, o Render publica a nova versão automaticamente.
3. Durante o build:
   - instala as dependências de `requirements.txt`;
   - executa `flask banco criar`, que cria as tabelas e os dados iniciais **somente se o banco estiver vazio**;
   - executa `flask criar-admin`, que cria ou atualiza a conta da loja usada nos testes.
4. A aplicação sobe com `gunicorn wsgi:app` (2 processos × 2 threads).

## Variáveis de ambiente

| Variável | Origem | Para que serve |
|---|---|---|
| `DATABASE_URL` | Copiada do Neon e colada no Render | Conexão com o banco |
| `SECRET_KEY` | Gerada pelo Render | Assinatura da sessão |
| `FLASK_ENV_PRODUCAO=1` | `render.yaml` | Cookie de sessão só por HTTPS e cabeçalhos do proxy |
| `ADMIN_EMAIL` / `ADMIN_SENHA` | `render.yaml` / informada no Render | Conta da loja para os testadores |
| `PYTHON_VERSION` | `render.yaml` | Versão do Python |

Nenhum segredo fica no repositório: o arquivo `.env` local está no `.gitignore`.

## Limitações conhecidas do plano gratuito

| Limitação | Efeito | Tratamento |
|---|---|---|
| O Render "adormece" o serviço após 15 minutos sem acesso | A primeira visita depois disso leva de 30 a 60 segundos | Avisado no formulário dos testadores; RNF08 já excluía esse caso |
| O Neon suspende o banco sem uso | A primeira consulta demora um pouco mais | Conexão com `pool_pre_ping` refaz a conexão automaticamente |
| As imagens são arquivos do próprio projeto | Não há envio de fotos pelo painel | Previsto como evolução (fotos em serviço de armazenamento) |

## Endereço publicado

- Aplicação: *preenchido após a publicação*
- Data da primeira publicação: *preenchido após a publicação*
