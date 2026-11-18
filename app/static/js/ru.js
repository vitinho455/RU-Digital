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

    // Valor em reais: "120000000" vira "R$ 120.000.000" ao digitar e "R$ 120.000.000,00" ao sair do campo.
    // Os pontos de milhar são colocados sozinhos; vírgula (ou ponto) digitada separa os centavos.
    function formatarReais(texto, completar) {
        var limpo = texto.replace(/^\s*R\$/i, '').replace(/[^\d,]/g, '');
        var virgula = limpo.indexOf(',');
        var inteiro = (virgula < 0 ? limpo : limpo.slice(0, virgula)).replace(/^0+(?=\d)/, '').slice(0, 12);
        var centavos = virgula < 0 ? null : limpo.slice(virgula + 1).replace(/,/g, '').slice(0, 2);
        if (!inteiro && centavos === null) return '';
        if (completar) centavos = ((centavos || '') + '00').slice(0, 2);
        var reais = (inteiro || '0').replace(/\B(?=(\d{3})+(?!\d))/g, '.');
        return 'R$ ' + reais + (centavos === null ? '' : ',' + centavos);
    }
    document.querySelectorAll('[data-dinheiro]').forEach(function (campo) {
        // O ponto digitado (ou colado em "25.50") vale como vírgula: os pontos de milhar quem põe é a máscara.
        campo.addEventListener('beforeinput', function (evento) {
            var dado = evento.data;
            if (!dado || dado.indexOf('.') < 0 || campo.value.indexOf(',') >= 0) return;
            if (dado === '.' || /^\d+\.\d{1,2}$/.test(dado)) {
                evento.preventDefault();
                campo.setRangeText(dado.replace('.', ','), campo.selectionStart, campo.selectionEnd, 'end');
                campo.dispatchEvent(new Event('input', { bubbles: true }));
            }
        });
        campo.addEventListener('input', function () {
            // Mantém o cursor depois do mesmo dígito em que ele estava
            var antes = campo.value.slice(0, campo.selectionStart).replace(/^\s*R\$/i, '').replace(/[^\d,]/g, '').length;
            var novo = formatarReais(campo.value, false);
            campo.value = novo;
            var pos = novo.indexOf('R$ ') === 0 ? 3 : 0, contados = 0;
            while (pos < novo.length && contados < antes) {
                if (/[\d,]/.test(novo[pos])) contados++;
                pos++;
            }
            campo.setSelectionRange(pos, pos);
        });
        campo.addEventListener('blur', function () { campo.value = formatarReais(campo.value, true); });
        campo.value = formatarReais(campo.value, true);
    });

    // Perfil: prévia da foto escolhida; "Remover foto atual" esconde a foto
    var campoFoto = document.getElementById('foto');
    var previa = document.getElementById('foto-previa');
    var semFoto = document.getElementById('foto-iniciais');
    var removerFoto = document.getElementById('remover-foto');
    if (campoFoto && previa && semFoto) {
        var urlPrevia = null;
        function mostrarFoto(src) {
            previa.hidden = !src;
            semFoto.hidden = !!src;
            if (src) previa.src = src;
        }
        campoFoto.addEventListener('change', function () {
            if (urlPrevia) URL.revokeObjectURL(urlPrevia);
            urlPrevia = campoFoto.files[0] ? URL.createObjectURL(campoFoto.files[0]) : null;
            if (urlPrevia && removerFoto) removerFoto.checked = false;
            mostrarFoto(urlPrevia || (removerFoto && removerFoto.checked ? '' : previa.dataset.original));
        });
        if (removerFoto) removerFoto.addEventListener('change', function () {
            if (removerFoto.checked) {
                campoFoto.value = '';
                if (urlPrevia) { URL.revokeObjectURL(urlPrevia); urlPrevia = null; }
            }
            mostrarFoto(removerFoto.checked ? '' : previa.dataset.original);
        });
    }

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

    // Novo cartão: no painel, a opção "+ Novo cartão" da forma de pagamento abre o pop-up e, ao salvar,
    // o cartão entra nas opções já selecionado. No perfil, o botão "+ Adicionar cartão" abre o mesmo pop-up.
    var selecao = document.getElementById('pagamento');
    var dialogo = document.getElementById('dialogo-cartao');
    var formCartao = document.getElementById('form-cartao');
    if (dialogo && formCartao) {
        var erro = document.getElementById('erro-cartao');

        function mostrarErro(texto) { erro.textContent = texto; erro.hidden = false; }
        function abrirCartao() {
            formCartao.reset();
            erro.hidden = true;
            dialogo.showModal();
            document.getElementById('numero').focus();
        }

        if (selecao) {
            var anterior = selecao.value;
            selecao.addEventListener('change', function () {
                if (selecao.value !== 'novo') { anterior = selecao.value; return; }
                selecao.value = anterior;          // se cancelar, continua na opção de antes
                abrirCartao();
            });
        }
        document.querySelectorAll('[data-novo-cartao]').forEach(function (botao) {
            botao.addEventListener('click', abrirCartao);
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
                    formCartao.reset();        // apaga número e código do formulário
                    if (formCartao.dataset.origem === 'perfil') {
                        window.location.href = '/perfil';
                    } else {
                        var valor = document.getElementById('valor').value;
                        window.location.href = '/painel?' + new URLSearchParams({ valor: valor, pagamento: 'cartao:' + res.dados.id });
                    }
                } else {
                    mostrarErro(res.dados.erro || 'Não foi possível salvar o cartão.');
                }
            }).catch(function () {
                mostrarErro('Não foi possível salvar o cartão. Recarregue a página e tente de novo.');
            }).finally(function () { botao.disabled = false; });
        });

        // Limpa o endereço (valor e cartão escolhidos voltam preenchidos só uma vez)
        if (selecao && window.location.search) history.replaceState(null, '', window.location.pathname);
    }
});
