% rebase('app/views/html/base', titulo='Usuários cadastrados', ativo='admin', sessao=sessao, flash=flash)
<div class="cabecalho">
    <h1>Usuários cadastrados</h1>
    <button type="button" class="primario" data-abrir-dialogo="dialogo-usuario">Cadastrar usuário</button>
</div>
<p class="nota contagem">{{len(alunos)}} {{'aluno' if len(alunos) == 1 else 'alunos'}} e {{len(admins)}} {{'administrador' if len(admins) == 1 else 'administradores'}} no sistema.</p>

<section aria-labelledby="titulo-alunos">
    <h2 id="titulo-alunos">Alunos</h2>
    % if alunos:
    <div class="rolagem">
        <table>
            <thead><tr><th scope="col">Nome</th><th scope="col">E-mail</th><th scope="col">Código RU</th><th scope="col">Cadastro em</th><th scope="col" class="num">Ações</th></tr></thead>
            <tbody>
            % for a in alunos:
                <tr>
                    <td>{{a['nome']}}</td>
                    <td>{{a['email']}}</td>
                    <td>{{a['matricula']}}</td>
                    <td>{{data_br(a['criado_em'])}}</td>
                    <td class="num acoes-linha">
                        <button type="button" class="link perigo" data-abrir-dialogo="excluir-aluno-{{a['matricula']}}" aria-label="Excluir {{a['nome']}}">Excluir</button>
                    </td>
                </tr>
            % end
            </tbody>
        </table>
    </div>
    % else:
    <p class="vazio">Nenhum aluno se cadastrou ainda.</p>
    % end
</section>

<section aria-labelledby="titulo-admins" class="secao">
    <h2 id="titulo-admins">Administradores</h2>
    <div class="rolagem">
        <table>
            <thead><tr><th scope="col">Nome</th><th scope="col">E-mail</th><th scope="col">Identificador</th><th scope="col" class="num">Ações</th></tr></thead>
            <tbody>
            % for a in admins:
                % eu = a['id_admin'] == sessao['usuario_id']
                <tr>
                    <td>{{a['nome']}}{{!' <span class="etiqueta">você</span>' if eu else ''}}</td>
                    <td>{{a['email']}}</td>
                    <td>{{a['id_admin']}}</td>
                    <td class="num acoes-linha">
                        % if not eu:
                        <button type="button" class="link perigo" data-abrir-dialogo="excluir-admin-{{a['id_admin']}}" aria-label="Excluir {{a['nome']}}">Excluir</button>
                        % end
                    </td>
                </tr>
            % end
            </tbody>
        </table>
    </div>
</section>

% for a in alunos:
<dialog id="excluir-aluno-{{a['matricula']}}" aria-labelledby="titulo-excluir-aluno-{{a['matricula']}}">
    <form method="post" action="/admin/alunos/{{a['matricula']}}/excluir" class="formulario">
        <input type="hidden" name="csrf" value="{{sessao['csrf']}}">
        <h2 id="titulo-excluir-aluno-{{a['matricula']}}">Excluir aluno?</h2>
        <p><strong>{{a['nome']}}</strong> ({{a['email']}}, {{a['matricula']}}) perde o acesso ao app na hora.
            O saldo de <strong>{{brl(a['saldo'])}}</strong>, o histórico de movimentações e os cartões salvos também são apagados.
            Essa ação não pode ser desfeita.</p>
        <div class="acoes">
            <button type="button" class="secundario" data-fechar-dialogo>Cancelar</button>
            <button type="submit" class="primario perigo">Excluir aluno</button>
        </div>
    </form>
</dialog>
% end
% for a in admins:
%   if a['id_admin'] != sessao['usuario_id']:
<dialog id="excluir-admin-{{a['id_admin']}}" aria-labelledby="titulo-excluir-admin-{{a['id_admin']}}">
    <form method="post" action="/admin/admins/{{a['id_admin']}}/excluir" class="formulario">
        <input type="hidden" name="csrf" value="{{sessao['csrf']}}">
        <h2 id="titulo-excluir-admin-{{a['id_admin']}}">Excluir administrador?</h2>
        <p><strong>{{a['nome']}}</strong> ({{a['email']}}) perde o acesso ao app na hora. Essa ação não pode ser desfeita.</p>
        <div class="acoes">
            <button type="button" class="secundario" data-fechar-dialogo>Cancelar</button>
            <button type="submit" class="primario perigo">Excluir administrador</button>
        </div>
    </form>
</dialog>
%   end
% end

<dialog id="dialogo-usuario" aria-labelledby="titulo-dialogo-usuario" {{!'data-abrir="1"' if erro else ''}}>
    <form method="post" action="/admin/usuarios" class="formulario">
        <input type="hidden" name="csrf" value="{{sessao['csrf']}}">
        <h2 id="titulo-dialogo-usuario">Cadastrar usuário</h2>
        % if erro:
        <p class="aviso erro" role="alert">{{erro}}</p>
        % end
        <fieldset class="tipo">
            <legend>Tipo de usuário</legend>
            <label class="opcao"><input type="radio" name="tipo" value="aluno" {{'checked' if form['tipo'] == 'aluno' else ''}}> Aluno</label>
            <label class="opcao"><input type="radio" name="tipo" value="admin" {{'checked' if form['tipo'] == 'admin' else ''}}> Administrador</label>
        </fieldset>
        <label for="nome-usuario">Nome completo</label>
        <input id="nome-usuario" name="nome" value="{{form['nome']}}" maxlength="100" required>
        <label for="email-usuario">E-mail institucional</label>
        <input id="email-usuario" name="email" type="email" value="{{form['email']}}" placeholder="nome@aluno.{{dominio}}" maxlength="120" required>
        <p class="ajuda">Precisa terminar em @{{dominio}}.</p>
        <label for="senha-usuario">Senha inicial</label>
        <input id="senha-usuario" name="senha" type="password" autocomplete="new-password" minlength="{{senha_min}}" required>
        <p class="ajuda">Mínimo de {{senha_min}} caracteres. Informe-a ao usuário.</p>
        <label class="opcao"><input type="checkbox" data-mostrar-senha="senha-usuario"> Mostrar senha</label>
        <div class="acoes">
            <button type="button" class="secundario" data-fechar-dialogo>Cancelar</button>
            <button type="submit" class="primario">Cadastrar</button>
        </div>
    </form>
</dialog>
