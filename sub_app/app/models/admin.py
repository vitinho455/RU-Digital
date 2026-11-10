"""Admin: gerencia o cardápio semanal e os usuários."""
import re
import sqlite3

from app.models import db, seguranca
from app.models.aluno import Aluno


class Admin:
    def __init__(self, id_admin, nome, email):
        self.id_admin = id_admin
        self.nome = nome
        self.email = email

    @classmethod
    def buscar(cls, id_admin):
        with db.transacao() as con:
            row = con.execute('SELECT * FROM admins WHERE id_admin = ?', (id_admin,)).fetchone()
        return cls(row['id_admin'], row['nome'], row['email']) if row else None

    @classmethod
    def autenticar(cls, email, senha):
        with db.transacao() as con:
            row = con.execute('SELECT * FROM admins WHERE email = ?', (email,)).fetchone()
        if row is None:
            seguranca.verificar(senha, seguranca.HASH_FALSO)
            return None
        if not seguranca.verificar(senha, row['senha_hash']):
            return None
        return cls(row['id_admin'], row['nome'], row['email'])

    def atualizar_cardapio(self, cardapio) -> str:
        """Publica o cardápio como o vigente e devolve uma mensagem de confirmação."""
        if not cardapio.url_documento:
            raise ValueError('Carregue um documento antes de publicar o cardápio.')
        cardapio.salvar(self.id_admin)
        return 'Cardápio publicado. Os alunos já podem ver a nova versão.'

    def listar_usuarios(self) -> dict:
        """Todos os cadastrados: {'alunos': [...], 'admins': [...]} (sem senhas)."""
        with db.transacao() as con:
            alunos = con.execute(
                'SELECT matricula, nome, email, criado_em FROM alunos ORDER BY nome COLLATE NOCASE').fetchall()
            admins = con.execute(
                'SELECT id_admin, nome, email FROM admins ORDER BY nome COLLATE NOCASE').fetchall()
        return {'alunos': [dict(a) for a in alunos], 'admins': [dict(a) for a in admins]}

    def cadastrar_aluno(self, nome, email, senha):
        """Cadastra um aluno (carteira zerada), por exemplo para ajudar em caso de dificuldade ou para testes."""
        return Aluno.cadastrar(nome, email, senha)

    def cadastrar_admin(self, nome, email, senha):
        """Cadastra outro administrador. Levanta ValueError com a mensagem a mostrar."""
        nome, email = ' '.join(nome.split()), email.strip().lower()
        erro = Aluno.validar_cadastro(nome, email, senha)
        if erro:
            raise ValueError(erro)
        try:
            with db.transacao() as con:
                if con.execute('SELECT 1 FROM alunos WHERE email = ?', (email,)).fetchone():
                    raise ValueError('Já existe uma conta com esse e-mail.')
                numeros = [int(r[0][3:]) for r in con.execute('SELECT id_admin FROM admins')
                           if re.fullmatch(r'ADM\d+', r[0])]
                novo_id = f'ADM{max(numeros, default=0) + 1:03d}'
                con.execute('INSERT INTO admins (id_admin, email, nome, senha_hash) VALUES (?,?,?,?)',
                            (novo_id, email, nome, seguranca.gerar_hash(senha)))
        except sqlite3.IntegrityError:
            raise ValueError('Já existe uma conta com esse e-mail.')
        return Admin(novo_id, nome, email)
