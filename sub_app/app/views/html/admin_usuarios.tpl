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
            <thead><tr><th scope="col">Nome</th><th scope="col">E-mail</th><th scope="col">Código RU</th><th scope="col">Cadastro em</th></tr></thead>
            <tbody>
            % for a in alunos:
                <tr>
                    <td>{{a['nome']}}</td>
                    <td>{{a['email']}}</td>
                    <td>{{a['matricula']}}</td>
                    <td>{{data_br(a['criado_em'])}}</td>
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
            <thead><tr><th scope="col">Nome</th><th scope="col">E-mail</th><th scope="col">Identificador</th></tr></thead>
            <tbody>
            % for a in admins:
                <tr><td>{{a['nome']}}</td><td>{{a['email']}}</td><td>{{a['id_admin']}}</td></tr>
            % end
            </tbody>
        </table>
    </div>
</section>

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
