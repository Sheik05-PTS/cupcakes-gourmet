# 04 — Casos de Uso Expandidos

> Exigência atendida: **R08** (casos de uso expandidos, prometidos no Anexo D do PIT I).
> Diagramas: [uml/01-casos-de-uso.md](uml/01-casos-de-uso.md). Regras (RN) e critérios (CA): [03-requisitos.md](03-requisitos.md).

**Convenções:** **FP** = fluxo principal · **FA** = fluxo alternativo (caminho válido diferente) · **FE** = fluxo de exceção (erro tratado).

---

## UC01 — Navegar na vitrine
| | |
|---|---|
| **Ator** | Visitante (e Cliente, por generalização) |
| **Histórias** | US01 |
| **Pré-condição** | Nenhuma |
| **Pós-condição** | O ator vê os cupcakes disponíveis |

**FP**
1. O ator acessa a página inicial.
2. O sistema lista os cupcakes ativos, cada um com foto, nome e preço.
3. Para cupcakes sem estoque, o sistema mostra "Esgotado" e oculta o botão de adicionar.
4. O ator escolhe um cupcake (segue para UC03) ou filtra a lista (UC02).

**FE1 — Vitrine vazia** (passo 2): não há cupcakes ativos. O sistema exibe "Nenhum cupcake disponível no momento."

**Regras:** RN02.

---

## UC02 — Filtrar cupcakes («extend» UC01)
| | |
|---|---|
| **Ator** | Visitante |
| **Histórias** | US02 |
| **Pré-condição** | O ator está na vitrine |
| **Pós-condição** | A vitrine mostra só os cupcakes que atendem aos filtros |

**FP**
1. O ator abre os filtros.
2. O sistema oferece: sabor, faixa de preço (mínimo e máximo), ocasião e restrição alimentar.
3. O ator escolhe um ou mais filtros e aplica.
4. O sistema mostra os cupcakes que atendem a **todos** os filtros e indica quais filtros estão ativos.

**FA1 — Limpar filtros:** o ator toca em "Limpar filtros" e o sistema volta à vitrine completa.
**FE1 — Nenhum resultado** (passo 4): o sistema exibe "Nenhum cupcake encontrado com esses filtros" e o botão "Limpar filtros".
**FE2 — Faixa de preço inválida** (passo 3): mínimo maior que máximo. O sistema exibe "O preço mínimo não pode ser maior que o máximo." e não aplica.

---

## UC03 — Ver detalhes do cupcake
| | |
|---|---|
| **Ator** | Visitante |
| **Histórias** | US03 |
| **Pré-condição** | Nenhuma |
| **Pós-condição** | O ator vê as informações completas do cupcake |

**FP**
1. O ator toca em um cupcake na vitrine.
2. O sistema mostra foto, nome, descrição, ingredientes, restrições alimentares, preço e disponibilidade.
3. Se o cupcake for personalizável, o sistema mostra as opções de personalização (UC05).
4. O ator escolhe a quantidade e adiciona ao carrinho (UC04).

**FE1 — Cupcake inexistente ou inativo** (passo 2): o sistema exibe "Cupcake não encontrado" com link para a vitrine.

---

## UC04 — Gerenciar carrinho
| | |
|---|---|
| **Ator** | Visitante |
| **Histórias** | US04, US06 |
| **Pré-condição** | Nenhuma |
| **Pós-condição** | O carrinho reflete as escolhas do ator e fica guardado durante a navegação |

**FP — Adicionar item**
1. Na página do cupcake, o ator escolhe a quantidade e toca em "Adicionar".
2. O sistema valida quantidade (1 a 20) e estoque.
3. O sistema adiciona o item e exibe "Adicionado ao carrinho". O ícone do carrinho mostra o novo total de itens.

**FA1 — Item já está no carrinho com a mesma personalização** (passo 3): o sistema soma a quantidade na linha existente.
**FA2 — Revisar carrinho:** o ator abre o carrinho. O sistema mostra cada linha (foto, nome, personalização, preço unitário, quantidade, subtotal) e o subtotal geral.
**FA3 — Alterar quantidade:** o ator muda a quantidade de uma linha. O sistema valida (passo 2) e recalcula os valores.
**FA4 — Remover item:** o ator toca em "Remover". O sistema retira a linha e oferece "Desfazer" por alguns segundos.
**FA5 — Estimar frete:** no carrinho, o ator informa um CEP (UC06).
**FA6 — Login durante a compra:** ao entrar (UC08) ou criar conta (UC07), o carrinho é mantido.
**FE1 — Quantidade fora do limite ou acima do estoque** (passo 2): o sistema informa o limite permitido e não altera o carrinho.
**FE2 — Carrinho vazio** (FA2): o sistema exibe "Seu carrinho está vazio" e o botão "Ver cupcakes".

**Regras:** RN03, RN05, RN06.

---

## UC05 — Personalizar cupcake («extend» UC04)
| | |
|---|---|
| **Ator** | Visitante |
| **Histórias** | US05 |
| **Pré-condição** | O cupcake é personalizável |
| **Pós-condição** | O item vai para o carrinho com a personalização e o preço ajustado |

**FP**
1. Na página do cupcake, o sistema mostra as listas de recheio e cobertura e o campo de mensagem com contador (até 60 caracteres).
2. O ator escolhe recheio e cobertura e, se quiser, escreve a mensagem.
3. O sistema atualiza o preço unitário somando os acréscimos.
4. O ator adiciona ao carrinho (UC04, passo 2).

**FE1 — Mensagem acima de 60 caracteres** (passo 2): o campo não aceita além do limite.

**Regras:** RN04, RN05.

---

## UC06 — Calcular frete e prazo
| | |
|---|---|
| **Ator** | Visitante (no carrinho) · incluído por UC10 |
| **Histórias** | US11 |
| **Pré-condição** | Existe pelo menos um item no carrinho |
| **Pós-condição** | O ator conhece o frete, o prazo e o total estimado |

**FP**
1. O ator informa um CEP (no carrinho) ou o sistema usa o CEP do endereço escolhido (no checkout).
2. O sistema valida o formato (8 dígitos).
3. O sistema procura a faixa de CEP atendida.
4. O sistema exibe valor do frete, prazo de entrega e total (subtotal − desconto + frete).

**FE1 — CEP com formato inválido** (passo 2): o sistema exibe "Informe um CEP com 8 dígitos."
**FE2 — CEP fora da área** (passo 3): o sistema exibe "Ainda não entregamos neste CEP". No checkout, o botão de pagamento fica desabilitado.

**Regras:** RN08, RN09.

---

## UC07 — Criar conta
| | |
|---|---|
| **Ator** | Visitante |
| **Histórias** | US13 |
| **Pré-condição** | O ator não está logado |
| **Pós-condição** | A conta existe e o ator está logado como Cliente, com o carrinho preservado |

**FP**
1. O ator abre "Criar conta".
2. O ator informa nome, e-mail, telefone e senha.
3. O sistema valida os dados e a regra de senha.
4. O sistema cria a conta com perfil Cliente, guarda a senha só como hash e inicia a sessão.
5. O sistema leva o ator de volta para onde estava (ex.: checkout).

**FE1 — E-mail já cadastrado** (passo 3): "Este e-mail já está cadastrado", com link para entrar.
**FE2 — Senha fraca** (passo 3): o sistema mostra a regra (mínimo 8 caracteres, com letra e número).
**FE3 — Campo obrigatório vazio ou inválido** (passo 3): mensagem no próprio campo, sem apagar os outros dados.

**Regras:** RN06, RN17.

---

## UC08 — Entrar e sair
| | |
|---|---|
| **Ator** | Visitante, Administrador |
| **Histórias** | US13, US17 |
| **Pré-condição** | O ator tem conta |
| **Pós-condição** | Sessão iniciada (ou encerrada) com o perfil correto |

**FP — Entrar**
1. O ator abre "Entrar" e informa e-mail e senha.
2. O sistema confere as credenciais.
3. O sistema inicia a sessão e leva o ator à página onde estava. Administradores vão para o painel.

**FA1 — Sair:** o ator toca em "Sair". O sistema encerra a sessão e volta à vitrine.
**FE1 — Credenciais incorretas** (passo 2): "E-mail ou senha inválidos", sem dizer qual dos dois está errado.

**Regras:** RN06, RN17, RN20.

---

## UC09 — Gerenciar endereços
| | |
|---|---|
| **Ator** | Cliente |
| **Histórias** | US10 |
| **Pré-condição** | Cliente logado |
| **Pós-condição** | Endereço salvo e disponível no checkout |

**FP**
1. O cliente abre "Meus endereços" (ou "Novo endereço" no checkout).
2. O cliente informa CEP, logradouro, número, complemento (opcional), bairro, cidade e UF.
3. O sistema valida e salva o endereço na conta do cliente.

**FA1 — Editar ou excluir endereço:** o cliente escolhe um endereço salvo e altera ou exclui. Pedidos antigos não mudam, pois guardam uma cópia do endereço.
**FE1 — Dados inválidos** (passo 3): mensagem em cada campo com erro.

**Regras:** RN18.

---

## UC10 — Finalizar pedido
| | |
|---|---|
| **Ator** | Cliente |
| **Histórias** | US06, US11 |
| **Pré-condição** | Cliente logado e carrinho com itens |
| **Pós-condição** | Pedido criado com status "Aguardando pagamento", com preços e endereço congelados |

**FP**
1. No carrinho, o cliente toca em "Finalizar pedido".
2. O sistema mostra o resumo dos itens e os endereços do cliente.
3. O cliente escolhe o endereço de entrega.
4. O sistema calcula frete e prazo (**«include» UC06**) e mostra subtotal, frete e total.
5. O cliente confirma.
6. O sistema confere de novo estoque e disponibilidade dos itens.
7. O sistema cria o pedido, copiando preço unitário e personalização de cada item e o endereço de entrega, e registra o status "Aguardando pagamento" no histórico.
8. O sistema segue para o pagamento (**«include» UC12**).

**FA1 — Visitante não logado** (passo 1): o sistema pede login ou cadastro (UC08/UC07) e volta ao passo 2 com o carrinho preservado.
**FA2 — Sem endereço cadastrado** (passo 2): o sistema abre o cadastro de endereço (UC09).
**FA3 — Aplicar cupom** (passo 4): **«extend» UC11**.
**FE1 — CEP fora da área** (passo 4): o botão de confirmar fica desabilitado, com a mensagem de UC06.
**FE2 — Item indisponível** (passo 6): o sistema informa qual item ficou indisponível e volta ao carrinho para ajuste.

**Regras:** RN06, RN08, RN09, RN10.

---

## UC11 — Aplicar cupom («extend» UC10)
| | |
|---|---|
| **Ator** | Cliente |
| **Histórias** | US07 |
| **Pré-condição** | Checkout aberto |
| **Pós-condição** | Desconto aplicado e total recalculado |

**FP**
1. O cliente digita o código do cupom e toca em "Aplicar".
2. O sistema verifica se o cupom existe, está ativo e dentro da validade.
3. O sistema verifica o valor mínimo do pedido.
4. O sistema calcula o desconto (percentual ou fixo), limitado ao subtotal e sem incidir no frete.
5. O sistema mostra o desconto e o novo total.

**FA1 — Trocar cupom:** um novo cupom substitui o anterior.
**FA2 — Remover cupom:** o cliente remove o cupom e o total volta ao original.
**FE1 — Cupom inválido ou vencido** (passo 2): "Cupom inválido ou expirado".
**FE2 — Abaixo do mínimo** (passo 3): "Este cupom vale para pedidos a partir de R$ X".

**Regras:** RN07, RN09.

---

## UC12 — Pagar pedido
| | |
|---|---|
| **Ator** | Cliente · **Ator secundário:** Gateway de pagamento (simulado) |
| **Histórias** | US08, US09 |
| **Pré-condição** | Pedido em "Aguardando pagamento" |
| **Pós-condição (sucesso)** | Pagamento aprovado, estoque baixado, pedido "Pago", carrinho vazio |

**FP — Cartão**
1. O sistema mostra o total, o aviso "Ambiente de demonstração: nenhuma cobrança real é feita" e as formas de pagamento.
2. O cliente escolhe cartão e informa número, nome, validade e código de segurança.
3. O sistema valida os campos (número pelo algoritmo de Luhn, validade futura, código com 3 ou 4 dígitos).
4. O sistema envia a cobrança ao gateway simulado.
5. O gateway aprova.
6. Numa única transação, o sistema trava os registros dos cupcakes, confere o estoque, baixa o estoque, registra o pagamento como aprovado (só bandeira e 4 últimos dígitos), muda o pedido para "Pago" e registra no histórico.
7. O sistema esvazia o carrinho e mostra "Pedido confirmado!" com número, itens, total, endereço e prazo.

**FA1 — Pix:**
 1. O cliente escolhe Pix.
 2. O sistema pede ao gateway um código fictício "copia e cola", válido por 15 minutos, e mostra o código com a contagem regressiva e o botão "Simular pagamento".
 3. O cliente toca em "Simular pagamento" dentro do prazo e o fluxo segue do passo 6.

**FA2 — Nova tentativa:** depois de uma recusa ou expiração, o cliente pode tentar de novo pelo detalhe do pedido.
**FE1 — Dados de cartão inválidos** (passo 3): mensagem no campo com erro, sem apagar os demais.
**FE2 — Cartão recusado** (passo 5, cartões terminados em 0002): "Pagamento recusado. Tente outro cartão ou pague com Pix." O pedido continua aguardando pagamento.
**FE3 — Pix expirado** (FA1.3): "Código Pix expirado", com a opção de gerar outro.
**FE4 — Estoque insuficiente na aprovação** (passo 6): a transação é desfeita, o pagamento não é aprovado e o sistema informa o item indisponível.

**Regras:** RN09–RN14, RN21.

---

## UC13 — Acompanhar pedidos
| | |
|---|---|
| **Ator** | Cliente |
| **Histórias** | US12, US13 |
| **Pré-condição** | Cliente logado |
| **Pós-condição** | O cliente sabe em que etapa está cada pedido |

**FP**
1. O cliente abre "Meus pedidos".
2. O sistema lista os pedidos do cliente, do mais recente para o mais antigo, com número, data, total e status.
3. O cliente abre um pedido.
4. O sistema mostra itens, endereço, pagamento e a linha do tempo de status (ícone + texto, com data e hora de cada etapa concluída).
5. Enquanto a tela está aberta, o sistema consulta o status a cada 30 segundos e atualiza sem recarregar a página.

**FA1 — Pedido aguardando pagamento** (passo 4): o sistema oferece "Pagar agora" (UC12, FA2).
**FE1 — Pedido de outro cliente** (passo 3): "Pedido não encontrado".
**FE2 — Pedido cancelado** (passo 4): status "Cancelado" em destaque.

**Regras:** RN15.

---

## UC14 — Manter cupcakes
| | |
|---|---|
| **Ator** | Administrador |
| **Histórias** | US15 |
| **Pré-condição** | Administrador logado |
| **Pós-condição** | Catálogo atualizado |

**FP — Cadastrar**
1. O administrador abre "Cupcakes" → "Novo".
2. Informa nome, descrição, ingredientes, preço, sabor, ocasiões, restrições alimentares, URL da foto, estoque e se é personalizável.
3. O sistema valida e salva. O cupcake ativo aparece na vitrine.

**FA1 — Editar:** o administrador altera um cupcake existente. Pedidos antigos mantêm o preço original.
**FA2 — Excluir cupcake nunca vendido:** o sistema pede confirmação e exclui.
**FE1 — Dados inválidos** (passo 3): mensagem em cada campo (nome vazio, preço ≤ 0, estoque negativo).
**FE2 — Excluir cupcake já vendido:** "Este cupcake já foi vendido. Você pode inativá-lo."

**Regras:** RN01, RN10, RN19, RN20.

---

## UC15 — Controlar disponibilidade
| | |
|---|---|
| **Ator** | Administrador |
| **Histórias** | US16 |
| **Pré-condição** | Administrador logado |
| **Pós-condição** | A vitrine reflete o estoque e a situação (ativo/inativo) de cada cupcake |

**FP**
1. O administrador abre a lista de cupcakes. Os que estão com estoque zero aparecem destacados como "Esgotado".
2. O administrador altera o estoque de um cupcake.
3. O sistema valida (número inteiro ≥ 0) e salva. A vitrine passa a refletir o novo estoque.

**FA1 — Inativar ou reativar:** o administrador muda a situação. Inativo some da vitrine; reativado volta.
**FE1 — Estoque inválido** (passo 3): "Informe um número inteiro maior ou igual a zero."

**Regras:** RN02.

---

## UC16 — Gerenciar pedidos
| | |
|---|---|
| **Ator** | Administrador |
| **Histórias** | US17 |
| **Pré-condição** | Administrador logado |
| **Pós-condição** | Pedido na etapa correta, com a mudança registrada no histórico |

**FP**
1. O administrador abre o painel de pedidos.
2. O sistema lista os pedidos do mais recente para o mais antigo (número, cliente, total, status, data), com filtro por status. Pedidos pagos ainda não abertos aparecem como "Novo".
3. Com o painel aberto, o sistema atualiza a lista a cada 30 segundos.
4. O administrador abre um pedido. O sistema mostra itens com personalização, endereço, pagamento e histórico, e o pedido deixa de ser "Novo".
5. O administrador toca em "Avançar status".
6. O sistema muda para a próxima etapa (Pago → Em preparo → Saiu para entrega → Entregue) e registra data, hora e responsável no histórico.

**FA1 — Cancelar pedido:** **«extend» UC17**.
**FE1 — Pedido já entregue ou cancelado** (passo 5): o botão "Avançar status" não aparece.
**FE2 — Pedido aguardando pagamento** (passo 5): não é possível avançar. O sistema informa "Aguardando pagamento do cliente".

**Regras:** RN15, RN20.

---

## UC17 — Cancelar pedido («extend» UC16)
| | |
|---|---|
| **Ator** | Administrador |
| **Histórias** | US17 |
| **Pré-condição** | Pedido em "Aguardando pagamento", "Pago" ou "Em preparo" |
| **Pós-condição** | Pedido "Cancelado" e, se estava pago, estoque devolvido |

**FP**
1. No detalhe do pedido, o administrador toca em "Cancelar pedido".
2. O sistema pede confirmação, informando que a ação não pode ser desfeita.
3. O administrador confirma.
4. Numa única transação, o sistema muda o status para "Cancelado", devolve o estoque (se o pedido estava pago) e registra no histórico.

**FA1 — Desistir:** no passo 3, o administrador cancela a confirmação e nada muda.
**FE1 — Pedido já saiu para entrega:** o botão "Cancelar pedido" não aparece.

**Regras:** RN16.
