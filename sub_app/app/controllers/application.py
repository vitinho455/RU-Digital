import hmac
import re
from datetime import datetime
from urllib.parse import urlencode

from bottle import BaseTemplate, abort, redirect, request, response, static_file, template

from app.models import db, sessoes
from app.models.admin import Admin
from app.models.aluno import DOMINIO_INSTITUCIONAL, Aluno
from app.models.cardapio_semanal import LIMITE_BYTES, CardapioSemanal
from app.models.cartao_credito import CartaoCredito

COOKIE = 'ru_sessao'


# Funções de apoio disponíveis em todos os templates ------------------------

def brl(valor: float) -> str:
    texto = f'{valor:,.2f}'.replace(',', '_').replace('.', ',').replace('_', '.')
    return f'R$ {texto}'


def data_br(iso: str) -> str:
    return datetime.fromisoformat(iso).strftime('%d/%m/%Y às %H:%M') if iso else 'não informado'


def iniciais(nome: str) -> str:
    partes = nome.split()
    return (partes[0][0] + (partes[-1][0] if len(partes) > 1 else '')).upper()


BaseTemplate.defaults.update(brl=brl, data_br=data_br, iniciais=iniciais)


def _erro(texto):
    return {'tipo': 'erro', 'texto': texto}


class Application():

    def __init__(self):
        db.inicializar()
        self.pages = {
        }

    def render(self, page):
        content = self.pages.get(page, self.helper)
        return content()

    def helper(self):
        return template('app/views/html/helper')

    # ---------------------------------------------------------------- sessão

    def _sessao(self):
        token = request.get_cookie(COOKIE)
        return sessoes.obter(token) if token else None

    def _inicio(self, sessao):
        return '/admin' if sessao['tipo'] == 'admin' else '/painel'

    def _exigir(self, tipo=None):
        """Garante um usuário logado (do tipo pedido, se houver); senão redireciona."""
        sessao = self._sessao()
        if sessao is None:
            redirect('/login')
        if tipo and sessao['tipo'] != tipo:
            redirect(self._inicio(sessao))
        return sessao

    def _checar_csrf(self, sessao):
        if not hmac.compare_digest(request.forms.get('csrf', ''), sessao['csrf']):
            abort(403, 'Requisição inválida. Recarregue a página e tente de novo.')

    def _flash(self, sessao, tipo, texto):
        sessoes.definir_flash(sessao['token'], tipo, texto)

    def _abrir_sessao(self, tipo, usuario_id):
        """Troca qualquer sessão anterior por uma nova e grava o cookie."""
        antiga = request.get_cookie(COOKIE)
        if antiga:
            sessoes.encerrar(antiga)
        token = sessoes.criar(tipo, usuario_id)
        response.set_cookie(COOKIE, token, path='/', httponly=True, samesite='lax', max_age=sessoes.DURACAO)
        return token

    def _view(self, pagina, sessao=None, flash=None, **ctx):
        if sessao and flash is None:
            flash = sessoes.consumir_flash(sessao['token'])
        response.set_header('Cache-Control', 'no-store')
        return template(f'app/views/html/{pagina}', sessao=sessao, flash=flash, **ctx)

    # ------------------------------------------------- autenticação e cadastro

    def inicio(self):
        sessao = self._sessao()
        redirect(self._inicio(sessao) if sessao else '/login')

    def login_form(self):
        sessao = self._sessao()
        if sessao:
            redirect(self._inicio(sessao))
        return self._view('login', email='')

    def login(self):
        email = (request.forms.getunicode('email') or '').strip()
        senha = request.forms.getunicode('senha') or ''
        aluno = Aluno.autenticar(email, senha)
        admin = None if aluno else Admin.autenticar(email, senha)
        if not aluno and not admin:
            response.status = 401
            return self._view('login', flash=_erro('E-mail ou senha incorretos.'), email=email)
        self._abrir_sessao(*(('aluno', aluno.matricula) if aluno else ('admin', admin.id_admin)))
        redirect('/admin' if admin else '/painel')

    def cadastro_form(self):
        sessao = self._sessao()
        if sessao:
            redirect(self._inicio(sessao))
        return self._view('cadastro', nome='', email='', dominio=DOMINIO_INSTITUCIONAL, senha_min=Aluno.SENHA_MIN)

    def cadastro(self):
        if self._sessao():
            redirect('/')
        nome = request.forms.getunicode('nome') or ''
        email = (request.forms.getunicode('email') or '').strip()
        senha = request.forms.getunicode('senha') or ''
        try:
            aluno = Aluno.cadastrar(nome, email, senha)
        except ValueError as erro:
            response.status = 400
            return self._view('cadastro', flash=_erro(str(erro)), nome=nome, email=email,
                              dominio=DOMINIO_INSTITUCIONAL, senha_min=Aluno.SENHA_MIN)
        token = self._abrir_sessao('aluno', aluno.matricula)
        sessoes.definir_flash(token, 'ok', 'Conta criada! Faça sua primeira recarga para usar o RU.')
        redirect('/painel')

    def logout(self):
        sessao = self._exigir()
        self._checar_csrf(sessao)
        sessoes.encerrar(sessao['token'])
        response.delete_cookie(COOKIE, path='/')
        redirect('/login')

    # ------------------------------------------------------------------ aluno

    def _aluno_logado(self, sessao):
        aluno = Aluno.buscar_por_matricula(sessao['usuario_id'])
        if aluno is None:
            sessoes.encerrar(sessao['token'])
            redirect('/login')
        return aluno

    def painel(self):
        sessao = self._exigir('aluno')
        aluno = self._aluno_logado(sessao)
        # Depois de salvar um cartão a página é recarregada com o valor digitado e o cartão já escolhido.
        valor = request.query.getunicode('valor') or ''
        if not re.fullmatch(r'[0-9.,]{0,15}', valor):
            valor = ''
        return self._view('painel', sessao, aluno=aluno, carteira=aluno.carteira, minimo=Aluno.VALOR_MIN,
                          cartoes=CartaoCredito.listar(aluno.matricula), valor=valor,
                          pagamento=request.query.get('pagamento', ''), senha_min=Aluno.SENHA_MIN)

    def recarregar(self):
        """Recarga simulada com PIX ou com um cartão já salvo."""
        sessao = self._exigir('aluno')
        self._checar_csrf(sessao)
        aluno = self._aluno_logado(sessao)
        valor = (request.forms.getunicode('valor') or '').strip()
        pagamento = request.forms.get('pagamento', '')
        erro = Aluno.validar_recarga(valor)
        cartao = None
        if not erro and pagamento.startswith('cartao:') and pagamento[7:].isdigit():
            cartao = CartaoCredito.buscar(int(pagamento[7:]), aluno.matricula)
            if cartao is None:
                erro = 'Cartão não encontrado. Escolha outra forma de pagamento.'
            elif cartao.vencido():
                erro = f'O cartão {cartao.rotulo} está vencido. Escolha outra forma de pagamento.'
        elif not erro and pagamento != 'pix':
            erro = 'Escolha a forma de pagamento.'

        if erro:
            self._flash(sessao, 'erro', erro)
            redirect('/painel?' + urlencode({'valor': valor[:15], 'pagamento': pagamento[:20]}))
        forma = cartao.rotulo if cartao else 'PIX'
        if aluno.realizar_recarga(valor, f'Recarga via {forma} (simulada)'):
            self._flash(sessao, 'ok', f'Recarga via {forma} concluída. Saldo atual: {brl(aluno.consultar_saldo())}.')
        redirect('/painel')

    def adicionar_cartao(self):
        """Chamada pelo pop-up do painel (fetch). Responde JSON; nada além dos dados seguros é guardado."""
        sessao = self._exigir('aluno')
        self._checar_csrf(sessao)
        aluno = self._aluno_logado(sessao)
        response.set_header('Cache-Control', 'no-store')
        try:
            cartao = CartaoCredito(request.forms.getunicode('numero'), request.forms.getunicode('titular'),
                                   request.forms.getunicode('validade'), request.forms.getunicode('cvv'),
                                   request.forms.getunicode('apelido'))
            cartao.salvar(aluno.matricula)
        except ValueError as erro:
            response.status = 400
            return {'ok': False, 'erro': str(erro)}
        self._flash(sessao, 'ok', f'Cartão {cartao.rotulo} adicionado. Ele já está selecionado como forma de pagamento.')
        return {'ok': True, 'id': cartao.id, 'rotulo': cartao.rotulo}

    def remover_cartao(self, id_cartao):
        sessao = self._exigir('aluno')
        self._checar_csrf(sessao)
        aluno = self._aluno_logado(sessao)
        if CartaoCredito.remover(id_cartao, aluno.matricula):
            self._flash(sessao, 'ok', 'Cartão removido.')
        redirect('/painel')

    # --------------------------------------------------------------- cardápio

    def cardapio(self):
        sessao = self._exigir()
        return self._view('cardapio', sessao, cardapio=CardapioSemanal.atual())

    def arquivo_cardapio(self, nome):
        self._exigir()
        caminho = CardapioSemanal.caminho_arquivo(nome)
        if caminho is None:
            abort(404, 'Cardápio não encontrado.')
        resposta = static_file(nome, root=db.UPLOADS_DIR, mimetype='application/pdf')
        resposta.set_header('X-Content-Type-Options', 'nosniff')
        return resposta

    # ------------------------------------------------------------------ admin

    def admin_usuarios(self, erro='', form=None):
        """Tela inicial do admin: quem está cadastrado, e o pop-up para cadastrar usuários."""
        sessao = self._exigir('admin')
        usuarios = Admin.buscar(sessao['usuario_id']).listar_usuarios()
        if erro:
            response.status = 400
        return self._view('admin_usuarios', sessao, alunos=usuarios['alunos'], admins=usuarios['admins'],
                          erro=erro, form=form or {'tipo': 'aluno', 'nome': '', 'email': ''},
                          dominio=DOMINIO_INSTITUCIONAL, senha_min=Aluno.SENHA_MIN)

    def cadastrar_usuario(self):
        sessao = self._exigir('admin')
        self._checar_csrf(sessao)
        admin = Admin.buscar(sessao['usuario_id'])
        tipo = request.forms.get('tipo', '')
        nome = request.forms.getunicode('nome') or ''
        email = (request.forms.getunicode('email') or '').strip()
        senha = request.forms.getunicode('senha') or ''
        try:
            if tipo == 'aluno':
                novo = admin.cadastrar_aluno(nome, email, senha)
                mensagem = f'Aluno {novo.nome} cadastrado (código RU {novo.matricula}).'
            elif tipo == 'admin':
                novo = admin.cadastrar_admin(nome, email, senha)
                mensagem = f'Administrador {novo.nome} cadastrado ({novo.id_admin}).'
            else:
                raise ValueError('Escolha o tipo de usuário.')
        except ValueError as erro:
            return self.admin_usuarios(str(erro), {'tipo': tipo if tipo in ('aluno', 'admin') else 'aluno',
                                                   'nome': nome, 'email': email})
        self._flash(sessao, 'ok', mensagem)
        redirect('/admin')

    def admin_cardapio(self):
        sessao = self._exigir('admin')
        historico = CardapioSemanal.historico(10)
        return self._view('admin_cardapio', sessao, atual=historico[0] if historico else None,
                          anteriores=historico[1:], limite_mb=LIMITE_BYTES // (1024 * 1024))

    def enviar_cardapio(self):
        sessao = self._exigir('admin')
        self._checar_csrf(sessao)
        admin = Admin.buscar(sessao['usuario_id'])
        arquivo = request.files.get('arquivo')
        if arquivo is None or not arquivo.filename:
            self._flash(sessao, 'erro', 'Escolha um arquivo PDF para enviar.')
            redirect('/admin/cardapio')
        try:
            if not arquivo.filename.lower().endswith('.pdf'):
                raise ValueError('O cardápio precisa ser um arquivo PDF.')
            url = CardapioSemanal.armazenar_arquivo(arquivo.file.read(LIMITE_BYTES + 1))
            cardapio = CardapioSemanal()
            cardapio.carregar_documento(url)
            self._flash(sessao, 'ok', admin.atualizar_cardapio(cardapio))
        except ValueError as erro:
            self._flash(sessao, 'erro', str(erro))
        redirect('/admin/cardapio')

    # ------------------------------------------------------------------- erros

    def erro(self, codigo, mensagem):
        return self._view('erro', self._sessao(), codigo=codigo, mensagem=mensagem)
