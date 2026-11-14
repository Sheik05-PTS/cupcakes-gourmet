/* Cupcakes Gourmet — comportamento das telas.
   Tudo aqui é melhoria: as páginas funcionam sem JavaScript, e as regras
   sempre são conferidas de novo no servidor. */
(function () {
  "use strict";

  const moeda = (valor) =>
    "R$ " + valor.toFixed(2).replace(".", ",").replace(/\B(?=(\d{3})+(?!\d))/g, ".");

  // Mensagens flutuantes somem sozinhas
  document.querySelectorAll(".toast[data-duracao]").forEach((toast) => {
    setTimeout(() => toast.remove(), Number(toast.dataset.duracao));
  });

  // Abrir e fechar folhas (filtros) e diálogos de confirmação
  document.querySelectorAll("[data-abrir]").forEach((botao) => {
    const dialogo = document.getElementById(botao.dataset.abrir);
    if (!dialogo || typeof dialogo.showModal !== "function") return;
    botao.addEventListener("click", () => dialogo.showModal());
    dialogo.addEventListener("click", (e) => { if (e.target === dialogo) dialogo.close(); });
    dialogo.querySelectorAll("[data-fechar]").forEach((b) => b.addEventListener("click", () => dialogo.close()));
  });

  // Contador de caracteres (mensagem do topper, RN04)
  document.querySelectorAll("[data-contador]").forEach((campo) => {
    const alvo = document.getElementById(campo.dataset.contador);
    const atualizar = () => { alvo.textContent = `${campo.value.length}/${campo.maxLength}`; };
    campo.addEventListener("input", atualizar);
    atualizar();
  });

  // Botões de + e - nas quantidades
  document.querySelectorAll("[data-stepper]").forEach((stepper) => {
    const campo = stepper.querySelector("input");
    stepper.querySelectorAll("[data-passo]").forEach((botao) => {
      botao.addEventListener("click", () => {
        const max = Number(campo.max) || 20;
        const novo = Math.min(max, Math.max(1, (Number(campo.value) || 1) + Number(botao.dataset.passo)));
        campo.value = novo;
        campo.dispatchEvent(new Event("input", { bubbles: true }));
      });
    });
  });

  // Preço do botão "Adicionar" acompanha quantidade e acréscimos (CA05.2)
  const formAdicionar = document.getElementById("form-adicionar");
  if (formAdicionar) {
    const precoBase = Number(formAdicionar.dataset.preco);
    const alvo = formAdicionar.querySelector("[data-total]");
    const recalcular = () => {
      let unitario = precoBase;
      formAdicionar.querySelectorAll("select[data-acrescimo]").forEach((sel) => {
        unitario += Number(sel.selectedOptions[0]?.dataset.acrescimo || 0);
      });
      const qtd = Math.max(1, Number(formAdicionar.querySelector("[name=quantidade]").value) || 1);
      alvo.textContent = moeda(unitario * qtd);
    };
    formAdicionar.addEventListener("input", recalcular);
    formAdicionar.addEventListener("change", recalcular);
    recalcular();
  }

  // No carrinho, mudar o número já envia a nova quantidade
  document.querySelectorAll("[data-enviar-ao-mudar]").forEach((campo) => {
    campo.addEventListener("change", () => campo.form.requestSubmit());
  });

  // Máscaras simples de digitação
  const mascara = (seletor, formatar) => {
    document.querySelectorAll(seletor).forEach((campo) => {
      campo.addEventListener("input", () => { campo.value = formatar(campo.value.replace(/\D/g, "")); });
    });
  };
  mascara("[data-mascara-cep]", (d) => { d = d.slice(0, 8); return d.length > 5 ? `${d.slice(0, 5)}-${d.slice(5)}` : d; });
  mascara("[data-mascara-cartao]", (d) => d.slice(0, 19).replace(/(\d{4})(?=\d)/g, "$1 "));
  mascara("[data-mascara-validade]", (d) => { d = d.slice(0, 4); return d.length > 2 ? `${d.slice(0, 2)}/${d.slice(2)}` : d; });
  mascara("[data-mascara-telefone]", (d) => {
    d = d.slice(0, 11);
    if (d.length <= 2) return d.length ? `(${d}` : "";
    if (d.length <= 6) return `(${d.slice(0, 2)}) ${d.slice(2)}`;
    if (d.length <= 10) return `(${d.slice(0, 2)}) ${d.slice(2, 6)}-${d.slice(6)}`;
    return `(${d.slice(0, 2)}) ${d.slice(2, 7)}-${d.slice(7)}`;
  });

  // Copiar o código Pix
  document.querySelectorAll("[data-copiar]").forEach((botao) => {
    botao.addEventListener("click", async () => {
      const texto = document.getElementById(botao.dataset.copiar).textContent.trim();
      try { await navigator.clipboard.writeText(texto); botao.lastChild.textContent = "Copiado!"; } catch (e) { /* sem permissão */ }
    });
  });

  // Contagem regressiva do Pix (RN11); ao zerar, recarrega para oferecer um novo código
  document.querySelectorAll("[data-contagem]").forEach((alvo) => {
    let restante = Number(alvo.dataset.contagem);
    const tique = () => {
      restante -= 1;
      if (restante <= 0) { window.location.reload(); return; }
      alvo.textContent = `${String(Math.floor(restante / 60)).padStart(2, "0")}:${String(restante % 60).padStart(2, "0")}`;
    };
    setInterval(tique, 1000);
  });

  // Acompanhamento do pedido: consulta o status e atualiza a tela quando mudar (CA12.2)
  document.querySelectorAll("[data-acompanhar]").forEach((caixa) => {
    const finais = ["ENTREGUE", "CANCELADO"];
    if (finais.includes(caixa.dataset.status)) return;
    const intervalo = (Number(caixa.dataset.intervalo) || 30) * 1000;
    setInterval(async () => {
      try {
        const resposta = await fetch(caixa.dataset.acompanhar, { headers: { Accept: "application/json" } });
        if (!resposta.ok) return;
        const dados = await resposta.json();
        if (dados.status !== caixa.dataset.status) window.location.reload();
      } catch (e) { /* sem conexão: tenta de novo no próximo ciclo */ }
    }, intervalo);
  });
})();
