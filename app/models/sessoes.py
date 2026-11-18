"""Sessões de login guardadas no SQLite. O cookie traz só um token aleatório."""
import hashlib
import json
import secrets
import time

from app.models import db

DURACAO = 8 * 3600  # segundos


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def criar(tipo: str, usuario_id: str) -> str:
    token = secrets.token_urlsafe(32)
    with db.transacao() as con:
        con.execute('DELETE FROM sessoes WHERE expira_em < ?', (int(time.time()),))
        con.execute(
            'INSERT INTO sessoes (token_hash, tipo, usuario_id, csrf, flash, expira_em) VALUES (?,?,?,?,NULL,?)',
            (_hash(token), tipo, usuario_id, secrets.token_hex(16), int(time.time()) + DURACAO))
    return token


def obter(token):
    with db.transacao() as con:
        row = con.execute(
            'SELECT tipo, usuario_id, csrf FROM sessoes WHERE token_hash = ? AND expira_em >= ?',
            (_hash(token), int(time.time()))).fetchone()
    if row is None:
        return None
    return {'token': token, 'tipo': row['tipo'], 'usuario_id': row['usuario_id'], 'csrf': row['csrf']}


def encerrar(token: str):
    with db.transacao() as con:
        con.execute('DELETE FROM sessoes WHERE token_hash = ?', (_hash(token),))


def definir_flash(token: str, tipo: str, texto: str):
    with db.transacao() as con:
        con.execute('UPDATE sessoes SET flash = ? WHERE token_hash = ?',
                    (json.dumps({'tipo': tipo, 'texto': texto}), _hash(token)))


def consumir_flash(token: str):
    with db.transacao() as con:
        row = con.execute('SELECT flash FROM sessoes WHERE token_hash = ?', (_hash(token),)).fetchone()
        if row is None or row['flash'] is None:
            return None
        con.execute('UPDATE sessoes SET flash = NULL WHERE token_hash = ?', (_hash(token),))
    return json.loads(row['flash'])
