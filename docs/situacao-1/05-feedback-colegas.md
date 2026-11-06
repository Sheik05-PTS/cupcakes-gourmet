# 05 — Feedback dos Colegas sobre o Planejamento

> Exigência atendida: **R21** (pedir crítica da solução a colegas e incorporar as melhores sugestões).
> Esta etapa é diferente dos 5 testadores da Situação 3: aqui os colegas avaliam o **planejamento**, antes do código.

## 1. Como coletar

1. Envie a 3 a 5 pessoas (colegas do curso ou profissionais da área) o arquivo [avaliacao/Cupcakes_Gourmet_Avaliacao_do_Planejamento.pdf](avaliacao/Cupcakes_Gourmet_Avaliacao_do_Planejamento.pdf). Ele reúne resumo do projeto, regras, 12 telas, mapa de navegação e, numa parte opcional, os diagramas e o modelo de dados.
2. Cada pessoa responde às perguntas da última página, pelo próprio PDF, por mensagem ou por áudio.
3. Registre as respostas na seção 4 e a decisão sobre cada sugestão na seção 5.
4. Quem marcar "Sim, pode me chamar" vira candidato a testador na Situação 3.

## 2. Mensagem para enviar junto com o PDF

> Oi! Estou fazendo o Projeto Integrador II: um app para uma loja de cupcakes vender pelo celular. Antes de começar a programar, queria sua opinião sincera sobre o que planejei. Leva uns 10 minutos: dá uma olhada no PDF e responde as perguntas da última página (pode ser por áudio). Pode apontar problema sem medo, é justamente para melhorar. Valeu!

## 3. Perguntas (iguais às do PDF)

1. O que entrou na primeira versão faz sentido para uma loja que quer começar a vender online? Falta algo essencial ou sobra alguma coisa?
2. Alguma regra ficou confusa ou dá para entender de mais de um jeito? Alguma parece injusta, para o cliente ou para a loja?
3. Olhando as telas: alguma coisa é difícil de entender ou de encontrar? Mudaria algo no visual ou nos textos?
4. Pensando como cliente, o que te faria desistir de uma compra num app desse tipo?
5. (Opcional, para quem é da área) Viu algum problema nos diagramas, no modelo de dados ou na arquitetura?
6. Mais alguma sugestão?

Também pergunta: **topa testar o app quando estiver pronto?** (Sim / Não)

## 4. Respostas recebidas

| # | Nome (ou iniciais) | Vínculo | Data | Resumo da crítica ou sugestão | Topa testar? |
|---|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

## 5. Decisões sobre as sugestões

| Sugestão | Aceita? | Justificativa | Documento alterado |
|---|---|---|---|
| | | | |

As sugestões aceitas também entram na tabela de alterações de [01-revisao-pit1.md](01-revisao-pit1.md).

## 6. Revisão crítica interna (feita antes do retorno dos colegas)

> Esta seção **não** é feedback de colegas. É uma revisão do próprio autor, que relê os requisitos a partir de três perspectivas para encontrar falhas antes de enviá-los para a crítica externa. O feedback real dos colegas fica nas seções 4 e 5.

### 6.1 Perspectiva do cliente comprador

| # | Ponto levantado | Decisão | Justificativa |
|---|---|---|---|
| C1 | O frete só aparece no checkout, depois do login. Quem quer saber o custo total antes de criar conta pode desistir. | Aceito | Novo critério **CA11.3**: o visitante informa o CEP no carrinho e vê frete e prazo estimados, sem precisar de conta |
| C2 | O cliente não sabe se o pagamento é real e pode ficar inseguro ao ver um botão "Simular pagamento". | Aceito | Nova regra **RN21**: as telas de pagamento exibem o aviso "Ambiente de demonstração: nenhuma cobrança real é feita" |
| C3 | O cliente pode querer cancelar um pedido que ainda não pagou. | Adiado | O pedido não pago não baixa estoque nem gera cobrança, então não traz prejuízo. Fica para versão futura, mantendo o escopo do MVP |

### 6.2 Perspectiva do dono da loja

| # | Ponto levantado | Decisão | Justificativa |
|---|---|---|---|
| L1 | Com o painel aberto, a loja não percebe quando entra um pedido novo e pode atrasar o preparo. | Aceito | Novo critério **CA17.6**: a lista de pedidos atualiza sozinha a cada 30 segundos e destaca os pedidos pagos ainda não vistos |
| L2 | Pedidos feitos fora do horário de funcionamento. | Adiado | Exige regra de agenda e capacidade de produção. Registrado como evolução futura |

### 6.3 Perspectiva de testes e qualidade

| # | Ponto levantado | Decisão | Justificativa |
|---|---|---|---|
| Q1 | Dois clientes pagando a última unidade ao mesmo tempo podem gerar estoque negativo. | Aceito | **RNF07** ampliado: a baixa de estoque trava o registro do produto durante a transação, e o caso vira teste de integração |
| Q2 | Na linha do tempo do pedido, diferenciar etapas só por cor prejudica pessoas com daltonismo. | Aceito | **RNF10** ampliado: status sempre com ícone + texto, nunca só cor |
