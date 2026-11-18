"""Admin: gerencia o cardápio semanal e os usuários."""
import re
import sqlite3

from app.models import db, perfil, seguranca
from app.models.aluno import Aluno
from app.models.perfil import email_em_uso, normalizar


class Admin:
    def __init__(self, id_admin, nome, email, foto_url=''):
        self.id_admin = id_admin
        self.nome = nome
        self.email = email
        self.foto_url = foto_url

    @classmethod
    def _de_linha(cls, row):
        return cls(row['id_admin'], row['nome'], row['email'], row['foto_url']) if row else None

    @classmethod
    def buscar(cls, id_admin):
        with db.transacao() as con:
            row = con.execute('SELECT * FROM admins WHERE id_admin = ?', (id_admin,)).fetchone()
        return cls._de_linha(row)

    @classmethod
    def autenticar(cls, email, senha):
        with db.transacao() as con:
            row = con.execute('SELECT * FROM admins WHERE email = ?', (email,)).fetchone()
        if row is None:
            seguranca.verificar(senha, seguranca.HASH_FALSO)
            return None
        return cls._de_linha(row) if seguranca.verificar(senha, row['senha_hash']) else None

    def atualizar_cardapio(self, cardapio) -> str:
        """Publica o cardápio como o vigente e devolve uma mensagem de confirmação."""
        if not cardapio.url_documento:
            raise ValueError('Carregue um documento antes de publicar o cardápio.')
        cardapio.salvar(self.id_admin)
        return 'Cardápio publicado. Os alunos já podem ver a nova versão.'

    # ------------------------------------------------------------- perfil

    def atualizar_perfil(self, nome, email, foto=None, remover_foto=False):
        """Cada admin altera só os próprios dados. Levanta ValueError; nada é alterado nesse caso."""
        self.nome, self.email, self.foto_url = perfil.salvar_perfil(
            'admins', 'id_admin', self.id_admin, self.foto_url, nome, email, foto, remover_foto)

    # ----------------------------------------------------------- usuários

    def listar_usuarios(self) -> dict:
        """Todos os cadastrados: {'alunos': [...], 'admins': [...]} (sem senhas)."""
        with db.transacao() as con:
            alunos = con.execute(
                'SELECT matricula, nome, email, saldo_atual, criado_em FROM alunos ORDER BY nome COLLATE NOCASE').fetchall()
            admins = con.execute(
                'SELECT id_admin, nome, email FROM admins ORDER BY nome COLLATE NOCASE').fetchall()
        return {'alunos': [dict(a, saldo=a['saldo_atual'] / 100) for a in alunos],
                'admins': [dict(a) for a in admins]}

    def cadastrar_aluno(self, nome, email, senha):
        """Cadastra um aluno (carteira zerada), por exemplo para ajudar em caso de dificuldade ou para testes."""
        return Aluno.cadastrar(nome, email, senha)

    def cadastrar_admin(self, nome, email, senha):
        """Cadastra outro administrador. Levanta ValueError com a mensagem a mostrar."""
        nome, email = normalizar(nome, email)
        erro = Aluno.validar_cadastro(nome, email, senha)
        if erro:
            raise ValueError(erro)
        try:
            with db.transacao() as con:
                if email_em_uso(con, email):
                    raise ValueError('Já existe uma conta com esse e-mail.')
                # Ids de admins excluídos (que ainda aparecem no histórico de cardápios) não são reaproveitados.
                usados = con.execute('SELECT id_admin FROM admins UNION SELECT enviado_por FROM cardapios').fetchall()
                numeros = [int(r[0][3:]) for r in usados if re.fullmatch(r'ADM\d+', r[0])]
                novo_id = f'ADM{max(numeros, default=0) + 1:03d}'
                con.execute('INSERT INTO admins (id_admin, email, nome, senha_hash) VALUES (?,?,?,?)',
                            (novo_id, email, nome, seguranca.gerar_hash(senha)))
        except sqlite3.IntegrityError:
            raise ValueError('Já existe uma conta com esse e-mail.')
        return Admin(novo_id, nome, email)

    def excluir_admin(self, id_admin):
        """Remove outro administrador e encerra as sessões dele. Devolve o nome. Levanta ValueError."""
        if id_admin == self.id_admin:
            raise ValueError('Você não pode excluir a sua própria conta.')
        with db.transacao() as con:
            row = con.execute('SELECT nome, foto_url FROM admins WHERE id_admin = ?', (id_admin,)).fetchone()
            if row is None:
                raise ValueError('Administrador não encontrado.')
            con.execute("DELETE FROM sessoes WHERE tipo = 'admin' AND usuario_id = ?", (id_admin,))
            con.execute('DELETE FROM admins WHERE id_admin = ?', (id_admin,))
        perfil.apagar_foto(row['foto_url'])
        return row['nome']

    def excluir_aluno(self, matricula):
        """Remove um aluno (que se formou ou saiu da universidade) com saldo, histórico, cartões e sessões.

        Devolve o nome. Levanta ValueError.
        """
        with db.transacao() as con:
            row = con.execute('SELECT nome, foto_url FROM alunos WHERE matricula = ?', (matricula,)).fetchone()
            if row is None:
                raise ValueError('Aluno não encontrado.')
            con.execute("DELETE FROM sessoes WHERE tipo = 'aluno' AND usuario_id = ?", (matricula,))
            con.execute('DELETE FROM cartoes WHERE matricula = ?', (matricula,))
            con.execute('DELETE FROM transacoes WHERE matricula = ?', (matricula,))
            con.execute('DELETE FROM alunos WHERE matricula = ?', (matricula,))
        perfil.apagar_foto(row['foto_url'])
        return row['nome']
