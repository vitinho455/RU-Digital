% rebase('app/views/html/base', titulo='Meu perfil', ativo='perfil', sessao=sessao, flash=flash)
<h1>Meu perfil</h1>
<div class="{{'grade' if cartoes is not None else 'estreito'}}">
    <div class="coluna">
        <form class="formulario" method="post" action="/perfil" enctype="multipart/form-data" id="form-perfil">
            <input type="hidden" name="csrf" value="{{sessao['csrf']}}">
            <h2>Dados pessoais</h2>

            <div class="foto-perfil">
                <img class="foto" id="foto-previa" alt="Foto de {{usuario.nome}}"
                     src="{{usuario.foto_url}}" data-original="{{usuario.foto_url}}" {{'' if usuario.foto_url else 'hidden'}}>
                <span class="foto iniciais" id="foto-iniciais" aria-hidden="true" {{'hidden' if usuario.foto_url else ''}}>{{iniciais(usuario.nome)}}</span>
                <div>
                    <label for="foto">Foto de perfil</label>
                    <input id="foto" name="foto" type="file" accept="image/png,image/jpeg,image/webp">
                    <p class="ajuda">PNG, JPG ou WebP, até {{foto_limite_mb}} MB.</p>
                    % if usuario.foto_url:
                    <label class="opcao"><input type="checkbox" name="remover_foto" value="1" id="remover-foto"> Remover foto atual</label>
                    % end
                </div>
            </div>

            <label for="nome">Nome completo</label>
            <input id="nome" name="nome" value="{{form['nome']}}" autocomplete="name" maxlength="100" required>
            <label for="email">E-mail institucional</label>
            <input id="email" name="email" type="email" value="{{form['email']}}" autocomplete="email" maxlength="120" required>
            <p class="ajuda">Precisa terminar em @{{dominio}}. É com ele que você entra no app.</p>
            <p class="nota codigo">{{codigo[0]}}: <strong>{{codigo[1]}}</strong></p>

            <div class="acoes">
                <a class="secundario" href="{{'/admin' if sessao['tipo'] == 'admin' else '/painel'}}">Cancelar</a>
                <button type="submit" class="primario">Atualizar</button>
            </div>
        </form>
    </div>

    % if cartoes is not None:
    <div class="coluna">
        <section class="cartoes" aria-labelledby="titulo-cartoes">
            <div class="cabecalho">
                <h2 id="titulo-cartoes">Meus cartões</h2>
                <button type="button" class="secundario" data-novo-cartao>+ Adicionar cartão</button>
            </div>
            % if cartoes:
            <ul>
                % for c in cartoes:
                <li>
                    <span>{{c.rotulo}}<small>{{c.titular}} - vence {{c.validade}}{{' (vencido)' if c.vencido() else ''}}</small></span>
                    <form method="post" action="/cartoes/{{c.id}}/remover">
                        <input type="hidden" name="csrf" value="{{sessao['csrf']}}">
                        <button type="submit" class="remover" aria-label="Remover o cartão {{c.rotulo}}">Remover</button>
                    </form>
                </li>
                % end
            </ul>
            % else:
            <p class="vazio">Nenhum cartão salvo. Os cartões que você adicionar aparecem como forma de pagamento na recarga.</p>
            % end
        </section>
    </div>
    % end
</div>

% if cartoes is not None:
% include('app/views/html/cartao_dialogo', sessao=sessao, origem='perfil')
% end
