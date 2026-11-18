% rebase('app/views/html/base', titulo='Gestão do cardápio', ativo='admin-cardapio', sessao=sessao, flash=flash)
<h1>Gestão do cardápio</h1>
<div class="grade">
    <div class="coluna">
        <form class="formulario" method="post" action="/admin/cardapio" enctype="multipart/form-data">
            <input type="hidden" name="csrf" value="{{sessao['csrf']}}">
            <h2>Publicar novo cardápio</h2>
            <p class="nota">O novo PDF substitui o atual para todos os alunos. Tamanho máximo: {{limite_mb}} MB.</p>
            <label for="arquivo">Arquivo PDF</label>
            <input id="arquivo" name="arquivo" type="file" accept="application/pdf,.pdf" required>
            <button type="submit" class="primario">Publicar cardápio</button>
        </form>
    </div>

    <div class="coluna">
        <section aria-labelledby="titulo-atual">
            <h2 id="titulo-atual">Cardápio no ar</h2>
            % if atual:
            <p>Publicado em {{data_br(atual.enviado_em)}}.
                <a href="/cardapio">Ver como o aluno vê</a></p>
            % else:
            <p class="vazio">Nenhum cardápio publicado ainda. Envie o primeiro PDF ao lado.</p>
            % end
        </section>

        % if anteriores:
        <section aria-labelledby="titulo-anteriores">
            <h2 id="titulo-anteriores">Versões anteriores</h2>
            <ul class="lista">
                % for c in anteriores:
                <li><a href="{{c.url_documento}}" target="_blank" rel="noopener">PDF de {{data_br(c.enviado_em)}}</a></li>
                % end
            </ul>
        </section>
        % end
    </div>
</div>
