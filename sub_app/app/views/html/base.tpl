<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{titulo}} - RU UnB</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..800&display=swap">
    <link rel="stylesheet" href="/static/css/ru.css">
    <script src="/static/js/ru.js" defer></script>
</head>
<body>
<a class="pular" href="#conteudo">Ir para o conteúdo</a>
<header class="topo">
    <a class="marca" href="/">RU UnB</a>
    % if sessao:
    <nav aria-label="Principal">
        % if sessao['tipo'] == 'admin':
        <a href="/admin" {{!'aria-current="page"' if ativo == 'admin' else ''}}>Usuários</a>
        <a href="/admin/cardapio" {{!'aria-current="page"' if ativo == 'admin-cardapio' else ''}}>Cardápio</a>
        % else:
        <a href="/painel" {{!'aria-current="page"' if ativo == 'painel' else ''}}>Meu painel</a>
        % end
        % if sessao['tipo'] == 'aluno':
        <a href="/cardapio" {{!'aria-current="page"' if ativo == 'cardapio' else ''}}>Cardápio</a>
        % end
        <form method="post" action="/logout">
            <input type="hidden" name="csrf" value="{{sessao['csrf']}}">
            <button type="submit" class="sair">Sair</button>
        </form>
    </nav>
    % end
</header>
<main id="conteudo">
    % if flash:
    <p class="aviso {{flash['tipo']}}" role="{{'alert' if flash['tipo'] == 'erro' else 'status'}}">{{flash['texto']}}</p>
    % end
    {{!base}}
</main>
</body>
</html>
