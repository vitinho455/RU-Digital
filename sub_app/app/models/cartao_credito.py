"""CartaoCredito: cartão usado nas recargas simuladas.

O número completo e o código de segurança (CVV) só existem durante a validação e
NUNCA são guardados. O banco recebe apenas: bandeira, 4 últimos dígitos, apelido,
nome do titular e validade.
"""
import re
from datetime import datetime

from app.models import db


def _luhn_ok(digitos: str) -> bool:
    soma = 0
    for i, d in enumerate(reversed(digitos)):
        n = int(d)
        if i % 2 == 1:
            n = n * 2 - 9 if n > 4 else n * 2
        soma += n
    return soma % 10 == 0


def _bandeira(digitos: str) -> str:
    if digitos.startswith('4'):
        return 'Visa'
    if 51 <= int(digitos[:2]) <= 55 or 2221 <= int(digitos[:4]) <= 2720:
        return 'Mastercard'
    if digitos[:2] in ('34', '37'):
        return 'American Express'
    return 'Cartão'


class CartaoCredito:
    LIMITE_POR_ALUNO = 5

    def __init__(self, numero, titular, validade, cvv, apelido=''):
        """Valida os dados digitados. Levanta ValueError com a mensagem a mostrar."""
        digitos = re.sub(r'[\s-]', '', numero or '')
        if not digitos.isdigit() or not 13 <= len(digitos) <= 19 or not _luhn_ok(digitos):
            raise ValueError('Número do cartão inválido. Confira os dígitos.')

        titular = ' '.join((titular or '').split())
        if len(titular) < 3 or len(titular) > 60:
            raise ValueError('Informe o nome como está impresso no cartão.')

        achado = re.fullmatch(r'(\d{2})\s*/\s*(\d{2})', (validade or '').strip())
        if not achado or not 1 <= int(achado.group(1)) <= 12:
            raise ValueError('Validade inválida. Use o formato MM/AA.')
        validade = f'{achado.group(1)}/{achado.group(2)}'
        if self._vence_antes_de_hoje(validade):
            raise ValueError('Cartão vencido.')

        if not re.fullmatch(r'\d{3,4}', cvv or ''):
            raise ValueError('Código de segurança inválido (3 ou 4 dígitos).')

        apelido = ' '.join((apelido or '').split())
        if len(apelido) > 20:
            raise ValueError('O apelido pode ter no máximo 20 caracteres.')

        self.id = None
        self.titular = titular
        self.validade = validade
        self.ultimos4 = digitos[-4:]
        self.bandeira = _bandeira(digitos)
        self.apelido = apelido

    # ------------------------------------------------------------ apresentação

    @property
    def rotulo(self) -> str:
        """Como o cartão aparece nas opções de pagamento. Ex.: 'Nubank •••• 1111'."""
        return f'{self.apelido or self.bandeira} •••• {self.ultimos4}'

    @staticmethod
    def _vence_antes_de_hoje(validade: str) -> bool:
        hoje = datetime.now(db.FUSO)
        return (2000 + int(validade[3:]), int(validade[:2])) < (hoje.year, hoje.month)

    def vencido(self) -> bool:
        return self._vence_antes_de_hoje(self.validade)

    # ------------------------------------------------------------- persistência

    def salvar(self, matricula: str) -> None:
        """Guarda o cartão do aluno (sem número nem CVV). Se já existir, só atualiza nome e apelido."""
        with db.transacao() as con:
            existente = con.execute(
                'SELECT id, apelido FROM cartoes WHERE matricula = ? AND ultimos4 = ? AND bandeira = ? AND validade = ?',
                (matricula, self.ultimos4, self.bandeira, self.validade)).fetchone()
            if existente:
                self.id = existente['id']
                self.apelido = self.apelido or existente['apelido']
                con.execute('UPDATE cartoes SET titular = ?, apelido = ? WHERE id = ?',
                            (self.titular, self.apelido, self.id))
                return
            total = con.execute('SELECT COUNT(*) FROM cartoes WHERE matricula = ?', (matricula,)).fetchone()[0]
            if total >= self.LIMITE_POR_ALUNO:
                raise ValueError(f'Você já tem {self.LIMITE_POR_ALUNO} cartões salvos. Remova um para adicionar outro.')
            cur = con.execute(
                'INSERT INTO cartoes (matricula, ultimos4, bandeira, apelido, titular, validade, criado_em) '
                'VALUES (?,?,?,?,?,?,?)',
                (matricula, self.ultimos4, self.bandeira, self.apelido, self.titular, self.validade, db.agora()))
            self.id = cur.lastrowid

    @classmethod
    def _de_linha(cls, row):
        cartao = cls.__new__(cls)    # sem passar pela validação: o número completo não existe mais
        cartao.id, cartao.titular, cartao.validade = row['id'], row['titular'], row['validade']
        cartao.ultimos4, cartao.bandeira, cartao.apelido = row['ultimos4'], row['bandeira'], row['apelido']
        return cartao

    @classmethod
    def listar(cls, matricula: str) -> list:
        with db.transacao() as con:
            linhas = con.execute('SELECT * FROM cartoes WHERE matricula = ? ORDER BY id', (matricula,)).fetchall()
        return [cls._de_linha(l) for l in linhas]

    @classmethod
    def buscar(cls, id_cartao: int, matricula: str):
        """Só encontra cartões do próprio aluno."""
        with db.transacao() as con:
            row = con.execute('SELECT * FROM cartoes WHERE id = ? AND matricula = ?', (id_cartao, matricula)).fetchone()
        return cls._de_linha(row) if row else None

    @classmethod
    def remover(cls, id_cartao: int, matricula: str) -> bool:
        with db.transacao() as con:
            return con.execute('DELETE FROM cartoes WHERE id = ? AND matricula = ?',
                               (id_cartao, matricula)).rowcount > 0
