% rebase('app/views/html/base', titulo='Criar conta', ativo='', sessao=sessao, flash=flash)
<section class="entrada">
    <h1>Crie sua conta no RU</h1>
    <form method="post" action="/cadastro" class="formulario">
        <label for="nome">Nome completo</label>
        <input id="nome" name="nome" value="{{nome}}" autocomplete="name" maxlength="100" required autofocus>
        <label for="email">E-mail institucional</label>
        <input id="email" name="email" type="email" value="{{email}}" autocomplete="username" placeholder="nome@aluno.{{dominio}}" maxlength="120" required>
        <p class="ajuda">Precisa terminar em @{{dominio}}.</p>
        <label for="senha">Senha</label>
        <input id="senha" name="senha" type="password" autocomplete="new-password" minlength="{{senha_min}}" required>
        <p class="ajuda">Mínimo de {{senha_min}} caracteres.</p>
        <label class="opcao"><input type="checkbox" data-mostrar-senha="senha"> Mostrar senha</label>
        <button type="submit" class="primario">Criar conta</button>
    </form>
    <p class="alternativa">Já tem conta? <a href="/login">Entre</a></p>
</section>
