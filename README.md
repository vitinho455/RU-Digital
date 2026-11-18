# RU UnB (BMVC + Bottle + SQLite)

App do Restaurante Universitário feito sobre o template BMVC, seguindo o diagrama de casos de uso e o diagrama de classes.

- **Aluno:** cria a conta (nome completo, e-mail institucional e senha), entra no app, consulta saldo e dados, recarrega o saldo (simulação, por PIX ou cartão de crédito salvo) e vê o cardápio semanal. Na aba **Perfil** troca foto, nome e e-mail e adiciona/remove cartões.
- **Admin:** entra no app, vê quem está cadastrado (tela inicial), cadastra e exclui alunos e outros admins e publica o cardápio da semana em PDF. Na aba **Perfil** troca a própria foto, nome e e-mail; nenhum admin altera os dados de outro.

## Como rodar

Local:

    pip install bottle
    python3 route.py          # http://localhost:8080

Docker (como no template):

    docker build -t bmvci .
    docker run -d -p 8080:8080 -v $(pwd):/bmeta bmvci

O banco (`app/controllers/db/ru.db`) e os PDFs (`app/uploads/cardapios/`) são criados na primeira execução e ficam na pasta do projeto.

## Contas de exemplo (criadas só na primeira execução)

| Perfil | E-mail                    | Senha    |
|--------|---------------------------|----------|
| Aluno  | maria.souza@aluno.unb.br  | aluno123 |
| Admin  | admin@unb.br              | admin123 |

Para não criar essas contas: `RU_SEED=0 python3 route.py`. Há um PDF para testar o envio em `exemplos/cardapio_exemplo.pdf`.

## Do diagrama para o código

| Classe (diagrama)  | Arquivo                              | Observações |
|--------------------|--------------------------------------|-------------|
| `Aluno`            | `app/models/aluno.py`                | `realizar_recarga(valor) -> bool`, `consultar_saldo() -> float` |
| `Admin`            | `app/models/admin.py`                | `atualizar_cardapio(cardapio) -> str` |
| `CarteiraRU`       | `app/models/carteira_ru.py`          | `adicionar_credito`, `debitar_refeicao`; saldo nunca fica negativo |
| `CardapioSemanal`  | `app/models/cardapio_semanal.py`     | `carregar_documento(url)`, `exibir_cardapio()`; aceita PDF (ver `FORMATOS_ACEITOS`) |
| (apoio) `perfil` | `app/models/perfil.py` | validação de nome/e-mail/senha e foto, comuns a aluno e admin |
| (apoio) `CartaoCredito` | `app/models/cartao_credito.py`  | valida e guarda os cartões do aluno **sem** número completo nem CVV |

Fora do diagrama, foram necessários: `seguranca.py` (hash de senha), `sessoes.py` (login) e `db.py` (SQLite).

Controller: `app/controllers/application.py`. Rotas: `route.py`. Telas: `app/views/html/*.tpl`. Estilo: `app/static/css/ru.css`.

## Decisões

- **Valores em centavos** no banco (INTEGER), para evitar erro de arredondamento. As classes expõem `float`, como no diagrama.
- **Recarga simulada:** mínimo de R$ 1,00 (`Aluno.VALOR_MIN`) e sem máximo. Nenhum pagamento real acontece. Na forma de pagamento, "+ Novo cartão de crédito…" abre um pop-up; ao salvar, o cartão entra nas opções (ex.: `Nubank •••• 1111`) e já fica selecionado. Número de teste: `4111 1111 1111 1111`.
- **Cartões salvos:** o banco guarda só bandeira, 4 últimos dígitos, apelido, titular e validade. O número completo e o CVV nunca são gravados. Cada aluno pode ter até 5 cartões; eles são adicionados pela forma de pagamento (painel) ou pelo Perfil, e removidos no Perfil. A bandeira é detectada pelo número (Visa, Mastercard, Amex); o nome do banco vem do apelido que o aluno digita.
- **Cadastro pelo admin:** botão "Cadastrar usuário" na tela de Usuários (aluno ou administrador), com a senha inicial definida pelo admin. Admins recebem identificador automático (ADM002, ADM003...).
- **Cadastro:** o e-mail precisa terminar em `unb.br` (`DOMINIO_INSTITUCIONAL` em `aluno.py`), mas o sistema não confirma que o e-mail é do aluno. Como o formulário não pede matrícula, cada aluno recebe um **Código RU** gerado pelo sistema (ex.: RU482913), guardado no atributo `matricula`.
- **Senha:** o diagrama não tem esse campo, mas a autenticação exige. Fica só no banco (PBKDF2), não nas classes.
- **Cardápio:** só PDF, até 10 MB, validado pelo conteúdo do arquivo. Só usuários logados acessam o arquivo. O último PDF enviado é o vigente e os anteriores ficam listados para o admin.
- **Débito de refeição** (`CarteiraRU.debitar_refeicao`) existe na classe, mas não tem tela, pois não consta nos casos de uso.
- Formulários têm proteção CSRF e o `debug=True` do `route.py` é do template: desligue fora de testes.
- **Exclusão de usuários:** um admin não pode excluir a própria conta (assim sempre sobra pelo menos um). Excluir um aluno (formado ou desligado) apaga também saldo, histórico e cartões; o pop-up de confirmação mostra o saldo que será perdido. Em ambos os casos as sessões abertas da pessoa são encerradas. O histórico de cardápios guarda o identificador de quem publicou e esses identificadores não são reaproveitados.
- **Foto de perfil** (aluno e admin): PNG, JPG ou WebP de até 2 MB, conferido pelo conteúdo do arquivo. Fica em `app/uploads/fotos/` com nome aleatório e só é servida para quem está logado (`/perfil/foto/...`).
- **Valor da recarga:** o campo formata enquanto se digita (`120000000` vira `R$ 120.000.000` e, ao sair do campo, `R$ 120.000.000,00`); o servidor aceita esse formato e também `20`, `20,5` ou `20.50`.
