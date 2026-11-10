% rebase('app/views/html/base', titulo='Entrar', ativo='', sessao=sessao, flash=flash)
<section class="entrada">
    <h1>Entre para ver seu saldo e o cardápio da semana</h1>
    <form method="post" action="/login" class="formulario">
        <label for="email">E-mail</label>
        <input id="email" name="email" type="email" value="{{email}}" autocomplete="username" required autofocus>
        <label for="senha">Senha</label>
        <input id="senha" name="senha" type="password" autocomplete="current-password" required>
        <button type="submit" class="primario">Entrar</button>
    </form>
    <p class="alternativa">Ainda não tem conta? <a href="/cadastro">Cadastre-se</a></p>
</section>
