% rebase('app/views/html/base', titulo='Cardápio da semana', ativo=('admin-cardapio' if sessao['tipo'] == 'admin' else 'cardapio'), sessao=sessao, flash=flash)
<h1>Cardápio da semana</h1>
% if cardapio and cardapio.exibir_cardapio():
<p class="nota">Atualizado em {{data_br(cardapio.enviado_em)}}.
    <a href="{{cardapio.exibir_cardapio()}}" target="_blank" rel="noopener">Abrir o PDF em outra aba</a></p>
<div class="moldura">
    <object data="{{cardapio.exibir_cardapio()}}" type="application/pdf" aria-label="Cardápio semanal em PDF">
        <p class="vazio">Seu navegador não mostra PDF aqui. <a href="{{cardapio.exibir_cardapio()}}" target="_blank" rel="noopener">Abra o cardápio em outra aba</a>.</p>
    </object>
</div>
% else:
<p class="vazio">O cardápio desta semana ainda não foi publicado. Volte mais tarde.
    % if sessao['tipo'] == 'admin':
    <a href="/admin">Publicar o cardápio</a>
    % end
</p>
% end
