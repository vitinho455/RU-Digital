"""Conexão com o SQLite, criação das tabelas e dados de exemplo."""
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone

from app.models import seguranca

_APP = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.environ.get('RU_DB', os.path.join(_APP, 'controllers', 'db', 'ru.db'))
UPLOADS_DIR = os.environ.get('RU_UPLOADS', os.path.join(_APP, 'uploads', 'cardapios'))

FUSO = timezone(timedelta(hours=-3))  # Brasília


def agora() -> str:
    return datetime.now(FUSO).isoformat(timespec='seconds')


SCHEMA = """
CREATE TABLE IF NOT EXISTS alunos (
    matricula       TEXT PRIMARY KEY,
    email           TEXT NOT NULL UNIQUE COLLATE NOCASE,
    nome            TEXT NOT NULL,
    foto_url        TEXT NOT NULL DEFAULT '',
    senha_hash      TEXT NOT NULL,
    saldo_atual     INTEGER NOT NULL DEFAULT 0 CHECK (saldo_atual >= 0),   -- em centavos
    saldo_anterior  INTEGER NOT NULL DEFAULT 0,
    criado_em       TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS transacoes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    matricula   TEXT NOT NULL REFERENCES alunos(matricula),
    tipo        TEXT NOT NULL CHECK (tipo IN ('recarga', 'refeicao')),
    valor       INTEGER NOT NULL CHECK (valor > 0),
    saldo_apos  INTEGER NOT NULL,
    descricao   TEXT NOT NULL DEFAULT '',
    criado_em   TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_transacoes_aluno ON transacoes (matricula, id DESC);
CREATE TABLE IF NOT EXISTS cartoes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    matricula   TEXT NOT NULL REFERENCES alunos(matricula),
    ultimos4    TEXT NOT NULL,
    bandeira    TEXT NOT NULL,
    apelido     TEXT NOT NULL DEFAULT '',
    titular     TEXT NOT NULL,
    validade    TEXT NOT NULL,      -- MM/AA
    criado_em   TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_cartoes_aluno ON cartoes (matricula);
CREATE TABLE IF NOT EXISTS admins (
    id_admin    TEXT PRIMARY KEY,
    email       TEXT NOT NULL UNIQUE COLLATE NOCASE,
    nome        TEXT NOT NULL,
    senha_hash  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS cardapios (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    url_documento  TEXT NOT NULL,
    formato        TEXT NOT NULL,
    enviado_por    TEXT NOT NULL REFERENCES admins(id_admin),
    enviado_em     TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sessoes (
    token_hash  TEXT PRIMARY KEY,
    tipo        TEXT NOT NULL CHECK (tipo IN ('aluno', 'admin')),
    usuario_id  TEXT NOT NULL,
    csrf        TEXT NOT NULL,
    flash       TEXT,
    expira_em   INTEGER NOT NULL
);
"""


def conectar() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA foreign_keys = ON')
    return con


@contextmanager
def transacao():
    """Abre uma conexão; confirma ao sair ou desfaz se ocorrer erro."""
    con = conectar()
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def inicializar():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    with transacao() as con:
        con.executescript(SCHEMA)
        _migrar(con)
        vazio = not con.execute('SELECT 1 FROM alunos UNION SELECT 1 FROM admins').fetchone()
        if vazio and os.environ.get('RU_SEED', '1') == '1':
            _dados_de_exemplo(con)


def _migrar(con):
    """Atualiza bancos criados por versões anteriores."""
    colunas = [c['name'] for c in con.execute('PRAGMA table_info(alunos)')]
    if 'criado_em' not in colunas:
        con.execute("ALTER TABLE alunos ADD COLUMN criado_em TEXT NOT NULL DEFAULT ''")


def _dados_de_exemplo(con):
    """Contas de demonstração. Troque as senhas (ou use RU_SEED=0) fora do ambiente de testes."""
    con.execute(
        'INSERT INTO admins (id_admin, email, nome, senha_hash) VALUES (?,?,?,?)',
        ('ADM001', 'admin@unb.br', 'Coordenação do RU', seguranca.gerar_hash('admin123')))
    con.execute(
        'INSERT INTO alunos (matricula, email, nome, foto_url, senha_hash, saldo_atual, saldo_anterior, criado_em) '
        'VALUES (?,?,?,?,?,?,?,?)',
        ('190012345', 'maria.souza@aluno.unb.br', 'Maria Souza', '',
         seguranca.gerar_hash('aluno123'), 2500, 3000, agora()))
    for tipo, valor, saldo, desc in (('recarga', 3000, 3000, 'Recarga via PIX (simulada)'),
                                     ('refeicao', 500, 2500, 'Refeição')):
        con.execute(
            'INSERT INTO transacoes (matricula, tipo, valor, saldo_apos, descricao, criado_em) '
            'VALUES (?,?,?,?,?,?)', ('190012345', tipo, valor, saldo, desc, agora()))
