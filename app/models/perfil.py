"""Dados de conta comuns a alunos e admins: validação de nome/e-mail/senha e foto de perfil."""
import os
import re
import secrets
import sqlite3

from app.models import db

DOMINIO_INSTITUCIONAL = 'unb.br'   # aceita também subdomínios (aluno.unb.br, cic.unb.br...)
_EMAIL = re.compile(r'[^@\s]+@([a-z0-9-]+\.)*' + re.escape(DOMINIO_INSTITUCIONAL), re.IGNORECASE)

# Foto de perfil: o tipo é conferido pelo conteúdo do arquivo, não pelo nome.
FOTO_LIMITE_BYTES = 2 * 1024 * 1024
_FOTO_NOME = re.compile(r'[0-9a-f]{32}\.(png|jpg|webp)')
FOTO_MIMETYPES = {'png': 'image/png', 'jpg': 'image/jpeg', 'webp': 'image/webp'}


def _extensao_imagem(conteudo: bytes):
    if conteudo.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'png'
    if conteudo.startswith(b'\xff\xd8\xff'):
        return 'jpg'
    if conteudo[:4] == b'RIFF' and conteudo[8:12] == b'WEBP':
        return 'webp'
    return None


def caminho_foto(nome: str):
    """Caminho no disco de uma foto de perfil, ou None se o nome não for válido ou o arquivo não existir."""
    if not _FOTO_NOME.fullmatch(nome or ''):
        return None
    caminho = os.path.join(db.FOTOS_DIR, nome)
    return caminho if os.path.isfile(caminho) else None


def apagar_foto(foto_url: str):
    caminho = caminho_foto(foto_url.rsplit('/', 1)[-1]) if foto_url else None
    if caminho:
        os.remove(caminho)


def normalizar(nome, email):
    return ' '.join((nome or '').split()), (email or '').strip().lower()


def validar_nome(nome):
    if len(nome.split()) < 2:
        return 'Informe o nome completo (nome e sobrenome).'
    if len(nome) > 100:
        return 'O nome pode ter no máximo 100 caracteres.'
    return None


def validar_email(email):
    if len(email) > 120 or not _EMAIL.fullmatch(email):
        return f'Use um e-mail institucional (terminado em @{DOMINIO_INSTITUCIONAL}).'
    return None


def validar_senha(senha, minimo=8):
    if len(senha) < minimo:
        return f'A senha precisa ter pelo menos {minimo} caracteres.'
    if len(senha) > 200:
        return 'A senha é longa demais.'
    return None


def email_em_uso(con, email, matricula=None, id_admin=None) -> bool:
    """True se outro aluno ou admin (que não o indicado) já usa o e-mail."""
    return bool(
        con.execute('SELECT 1 FROM alunos WHERE email = ? AND matricula IS NOT ?', (email, matricula)).fetchone()
        or con.execute('SELECT 1 FROM admins WHERE email = ? AND id_admin IS NOT ?', (email, id_admin)).fetchone())


def salvar_perfil(tabela, coluna_id, valor_id, foto_url_atual, nome, email, foto=None, remover_foto=False):
    """Atualiza nome, e-mail e foto (bytes de PNG, JPEG ou WebP) de um aluno ou admin.

    Devolve (nome, email, foto_url) já gravados. Levanta ValueError com a mensagem a mostrar;
    nesse caso nada é alterado.
    """
    assert (tabela, coluna_id) in (('alunos', 'matricula'), ('admins', 'id_admin'))
    nome, email = normalizar(nome, email)
    erro = validar_nome(nome) or validar_email(email)
    extensao = None
    if not erro and foto:
        extensao = _extensao_imagem(foto)
        if len(foto) > FOTO_LIMITE_BYTES:
            erro = f'A foto pode ter no máximo {FOTO_LIMITE_BYTES // (1024 * 1024)} MB.'
        elif extensao is None:
            erro = 'A foto precisa ser uma imagem PNG, JPG ou WebP.'
    if erro:
        raise ValueError(erro)

    foto_url, novo_arquivo = foto_url_atual, None
    if extensao:
        nome_arquivo = f'{secrets.token_hex(16)}.{extensao}'
        novo_arquivo = os.path.join(db.FOTOS_DIR, nome_arquivo)
        with open(novo_arquivo, 'wb') as arquivo:
            arquivo.write(foto)
        foto_url = f'/perfil/foto/{nome_arquivo}'
    elif remover_foto:
        foto_url = ''
    ignorar = {'matricula': valor_id} if tabela == 'alunos' else {'id_admin': valor_id}
    try:
        with db.transacao() as con:
            if email_em_uso(con, email, **ignorar):
                raise ValueError('Já existe uma conta com esse e-mail.')
            con.execute(f'UPDATE {tabela} SET nome = ?, email = ?, foto_url = ? WHERE {coluna_id} = ?',
                        (nome, email, foto_url, valor_id))
    except (ValueError, sqlite3.IntegrityError) as erro_banco:
        if novo_arquivo:
            os.remove(novo_arquivo)
        if isinstance(erro_banco, sqlite3.IntegrityError):
            raise ValueError('Já existe uma conta com esse e-mail.')
        raise
    if foto_url != foto_url_atual:
        apagar_foto(foto_url_atual)
    return nome, email, foto_url
