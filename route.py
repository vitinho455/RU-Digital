from app.controllers.application import Application
from bottle import Bottle, route, run, request, static_file
from bottle import redirect, template, response


app = Bottle()
ctl = Application()


#-----------------------------------------------------------------------------
# Rotas:

@app.route('/static/<filepath:path>')
def serve_static(filepath):
    resposta = static_file(filepath, root='./app/static')
    # Sempre revalida com o servidor: evita o navegador ficar com um ru.js/ru.css antigo
    resposta.set_header('Cache-Control', 'no-cache')
    return resposta

@app.route('/helper')
def helper(info= None):
    return ctl.render('helper')


#-----------------------------------------------------------------------------
# Suas rotas aqui:

@app.route('/')
def inicio():
    return ctl.inicio()

@app.route('/login', method='GET')
def login_form():
    return ctl.login_form()

@app.route('/login', method='POST')
def login():
    return ctl.login()

@app.route('/cadastro', method='GET')
def cadastro_form():
    return ctl.cadastro_form()

@app.route('/cadastro', method='POST')
def cadastro():
    return ctl.cadastro()

@app.route('/logout', method='POST')
def logout():
    return ctl.logout()

# Aluno
@app.route('/painel', method='GET')
def painel():
    return ctl.painel()

@app.route('/recarga', method='POST')
def recarga():
    return ctl.recarregar()

@app.route('/cartoes', method='POST')
def cartoes():
    return ctl.adicionar_cartao()

@app.route('/cartoes/<id_cartao:int>/remover', method='POST')
def cartoes_remover(id_cartao):
    return ctl.remover_cartao(id_cartao)

# Cardápio (aluno e admin)
@app.route('/cardapio', method='GET')
def cardapio():
    return ctl.cardapio()

@app.route('/cardapio/arquivo/<nome>', method='GET')
def arquivo_cardapio(nome):
    return ctl.arquivo_cardapio(nome)

# Admin
@app.route('/admin', method='GET')
def admin():
    return ctl.admin_usuarios()

@app.route('/admin/usuarios', method='POST')
def admin_usuarios_cadastrar():
    return ctl.cadastrar_usuario()

@app.route('/admin/cardapio', method='GET')
def admin_cardapio_gestao():
    return ctl.admin_cardapio()

@app.route('/admin/cardapio', method='POST')
def admin_cardapio():
    return ctl.enviar_cardapio()

# Páginas de erro
@app.error(403)
def erro_403(erro):
    return ctl.erro(403, erro.body)

@app.error(404)
def erro_404(erro):
    return ctl.erro(404, 'Página não encontrada.')



#-----------------------------------------------------------------------------


if __name__ == '__main__':

    run(app, host='0.0.0.0', port=8080, debug=True)
