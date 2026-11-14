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

  // Máscara simples de CEP: 00000-000
  document.querySelectorAll("[data-mascara-cep]").forEach((campo) => {
    campo.addEventListener("input", () => {
      const d = campo.value.replace(/\D/g, "").slice(0, 8);
      campo.value = d.length > 5 ? `${d.slice(0, 5)}-${d.slice(5)}` : d;
    });
  });
})();
