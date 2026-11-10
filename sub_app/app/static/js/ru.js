document.addEventListener('DOMContentLoaded', function () {
    // Só dígitos, com a formatação que o campo pedir
    function mascara(id, formatar) {
        var campo = document.getElementById(id);
        if (!campo) return;
        campo.addEventListener('input', function () {
            campo.value = formatar(campo.value.replace(/\D/g, ''));
        });
    }
    mascara('numero', function (d) { return d.slice(0, 19).replace(/(\d{4})(?=\d)/g, '$1 '); });
    mascara('validade', function (d) { d = d.slice(0, 4); return d.length > 2 ? d.slice(0, 2) + '/' + d.slice(2) : d; });
    mascara('cvv', function (d) { return d.slice(0, 4); });

    // "Mostrar senha": o checkbox indica o id do campo
    document.querySelectorAll('[data-mostrar-senha]').forEach(function (caixa) {
        caixa.addEventListener('change', function () {
            document.getElementById(caixa.dataset.mostrarSenha).type = caixa.checked ? 'text' : 'password';
        });
    });

    // Pop-ups (<dialog>): botões que abrem e fecham; Esc também fecha
    document.querySelectorAll('[data-abrir-dialogo]').forEach(function (botao) {
        botao.addEventListener('click', function () {
            document.getElementById(botao.dataset.abrirDialogo).showModal();
        });
    });
    document.querySelectorAll('[data-fechar-dialogo]').forEach(function (botao) {
        botao.addEventListener('click', function () { botao.closest('dialog').close(); });
    });
    var reaberto = document.querySelector('dialog[data-abrir]');   // o servidor devolveu um erro de formulário
    if (reaberto) reaberto.showModal();

    // Painel do aluno: "+ Novo cartão" abre o pop-up e, ao salvar, o cartão entra nas opções
    var selecao = document.getElementById('pagamento');
    var dialogo = document.getElementById('dialogo-cartao');
    var formCartao = document.getElementById('form-cartao');
    if (selecao && dialogo && formCartao) {
        var anterior = selecao.value;
        var erro = document.getElementById('erro-cartao');

        function mostrarErro(texto) { erro.textContent = texto; erro.hidden = false; }

        selecao.addEventListener('change', function () {
            if (selecao.value !== 'novo') { anterior = selecao.value; return; }
            selecao.value = anterior;          // se cancelar, continua na opção de antes
            formCartao.reset();
            erro.hidden = true;
            dialogo.showModal();
            document.getElementById('numero').focus();
        });

        formCartao.addEventListener('submit', function (evento) {
            evento.preventDefault();
            var botao = formCartao.querySelector('button[type=submit]');
            botao.disabled = true;
            erro.hidden = true;
            fetch(formCartao.action, {
                method: 'POST', body: new FormData(formCartao), credentials: 'same-origin',
                headers: { 'X-Requested-With': 'fetch', 'Accept': 'application/json' }
            }).then(function (resposta) {
                return resposta.json().then(function (dados) { return { ok: resposta.ok, dados: dados }; });
            }).then(function (res) {
                if (res.ok && res.dados.ok) {
                    var valor = document.getElementById('valor').value;
                    formCartao.reset();        // apaga número e código do formulário
                    window.location.href = '/painel?' + new URLSearchParams({ valor: valor, pagamento: 'cartao:' + res.dados.id });
                } else {
                    mostrarErro(res.dados.erro || 'Não foi possível salvar o cartão.');
                }
            }).catch(function () {
                mostrarErro('Não foi possível salvar o cartão. Recarregue a página e tente de novo.');
            }).finally(function () { botao.disabled = false; });
        });

        // Limpa o endereço (valor e cartão escolhidos voltam preenchidos só uma vez)
        if (window.location.search) history.replaceState(null, '', window.location.pathname);
    }
});
