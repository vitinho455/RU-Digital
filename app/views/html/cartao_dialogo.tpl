<dialog id="dialogo-cartao" aria-labelledby="titulo-dialogo-cartao">
    <form method="post" action="/cartoes" id="form-cartao" class="formulario" autocomplete="on" data-origem="{{origem}}">
        <input type="hidden" name="csrf" value="{{sessao['csrf']}}">
        <input type="hidden" name="origem" value="{{origem}}">
        <h2 id="titulo-dialogo-cartao">Novo cartão de crédito</h2>
        <p class="nota">Simulação: nada é cobrado. Guardamos só a bandeira, os 4 últimos dígitos, o nome e a validade. O número completo e o código de segurança nunca são guardados. Para testar, use 4111 1111 1111 1111.</p>
        <p class="aviso erro" id="erro-cartao" role="alert" hidden></p>
        <label for="numero">Número do cartão</label>
        <input id="numero" name="numero" inputmode="numeric" autocomplete="cc-number" placeholder="0000 0000 0000 0000" maxlength="23" required>
        <label for="titular">Nome impresso no cartão</label>
        <input id="titular" name="titular" autocomplete="cc-name" maxlength="60" required>
        <div class="linha-dupla">
            <div>
                <label for="validade">Validade</label>
                <input id="validade" name="validade" inputmode="numeric" autocomplete="cc-exp" placeholder="MM/AA" maxlength="5" required>
            </div>
            <div>
                <label for="cvv">Código de segurança</label>
                <input id="cvv" name="cvv" inputmode="numeric" autocomplete="cc-csc" placeholder="123" maxlength="4" required>
            </div>
        </div>
        <label for="apelido">Apelido do cartão (opcional)</label>
        <input id="apelido" name="apelido" autocomplete="off" placeholder="Ex.: Nubank" maxlength="20">
        <div class="acoes">
            <button type="button" class="secundario" data-fechar-dialogo>Cancelar</button>
            <button type="submit" class="primario">Salvar cartão</button>
        </div>
    </form>
</dialog>
