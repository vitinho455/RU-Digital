"""Aluno: dados cadastrais e carteira do RU."""
import re
import secrets
import sqlite3

from app.models import db, seguranca
from app.models.carteira_ru import CarteiraRU, para_centavos

DOMINIO_INSTITUCIONAL = 'unb.br'   # aceita também subdomínios (aluno.unb.br, cic.unb.br...)
_EMAIL = re.compile(r'[^@\s]+@([a-z0-9-]+\.)*' + re.escape(DOMINIO_INSTITUCIONAL), re.IGNORECASE)


class Aluno:
    VALOR_MIN = 1.0      # recarga mínima; não há valor máximo
    SENHA_MIN = 8

    def __init__(self, matricula, email, nome, foto_url, carteira):
        self.matricula = matricula
        self.email = email
        self.nome = nome
        self.foto_url = foto_url
        self.carteira = carteira

    # ----------------------------------------------------------- consulta

    @classmethod
    def _de_linha(cls, row):
        if row is None:
            return None
        carteira = CarteiraRU.carregar(row['matricula'])
        return cls(row['matricula'], row['email'], row['nome'], row['foto_url'], carteira)

    @classmethod
    def buscar_por_matricula(cls, matricula):
        with db.transacao() as con:
            row = con.execute('SELECT * FROM alunos WHERE matricula = ?', (matricula,)).fetchone()
        return cls._de_linha(row)

    @classmethod
    def autenticar(cls, email, senha):
        """Retorna o Aluno se e-mail e senha conferem; senão, None."""
        with db.transacao() as con:
            row = con.execute('SELECT * FROM alunos WHERE email = ?', (email,)).fetchone()
        if row is None:
            seguranca.verificar(senha, seguranca.HASH_FALSO)
            return None
        return cls._de_linha(row) if seguranca.verificar(senha, row['senha_hash']) else None

    # ----------------------------------------------------------- cadastro

    @classmethod
    def validar_cadastro(cls, nome, email, senha):
        """Retorna a mensagem de erro, ou None se os dados são aceitos."""
        if len(nome.split()) < 2:
            return 'Informe seu nome completo (nome e sobrenome).'
        if len(nome) > 100:
            return 'O nome pode ter no máximo 100 caracteres.'
        if len(email) > 120 or not _EMAIL.fullmatch(email):
            return f'Use seu e-mail institucional (terminado em @{DOMINIO_INSTITUCIONAL}).'
        if len(senha) < cls.SENHA_MIN:
            return f'A senha precisa ter pelo menos {cls.SENHA_MIN} caracteres.'
        if len(senha) > 200:
            return 'A senha é longa demais.'
        return None

    @classmethod
    def cadastrar(cls, nome, email, senha):
        """Cria o aluno com carteira zerada. Levanta ValueError com a mensagem a mostrar."""
        nome, email = ' '.join(nome.split()), email.strip().lower()
        erro = cls.validar_cadastro(nome, email, senha)
        if erro:
            raise ValueError(erro)
        for _ in range(10):
            # Código gerado pelo sistema (o formulário de cadastro não pede matrícula).
            matricula = f'RU{secrets.randbelow(900000) + 100000}'
            try:
                with db.transacao() as con:
                    if con.execute('SELECT 1 FROM admins WHERE email = ?', (email,)).fetchone():
                        raise ValueError('Já existe uma conta com esse e-mail.')
                    con.execute(
                        'INSERT INTO alunos (matricula, email, nome, foto_url, senha_hash, criado_em) '
                        "VALUES (?,?,?,'',?,?)",
                        (matricula, email, nome, seguranca.gerar_hash(senha), db.agora()))
                return cls.buscar_por_matricula(matricula)
            except sqlite3.IntegrityError as erro_banco:
                if 'email' in str(erro_banco).lower():
                    raise ValueError('Já existe uma conta com esse e-mail.')
                # senão, o código gerado já existia: tenta outro
        raise RuntimeError('Não foi possível gerar um código para o aluno.')

    # ------------------------------------------------------------ recarga

    @classmethod
    def validar_recarga(cls, valor):
        """Retorna a mensagem de erro, ou None se o valor é aceito."""
        try:
            centavos = para_centavos(valor)
        except ValueError as erro:
            return str(erro)
        if centavos < cls.VALOR_MIN * 100:
            return f'A recarga mínima é de R$ {cls.VALOR_MIN:.2f}.'.replace('.', ',')
        return None

    def realizar_recarga(self, valor, descricao='Recarga (simulada)') -> bool:
        """Simula uma recarga: nenhum pagamento real é feito. False se o valor for recusado."""
        if self.validar_recarga(valor) is not None:
            return False
        self.carteira.adicionar_credito(valor, descricao)
        return True

    def consultar_saldo(self) -> float:
        self.carteira.atualizar()
        return self.carteira.saldo_atual
