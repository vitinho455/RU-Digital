"""CarteiraRU: saldo e histórico de transações de um aluno."""
import re
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from app.models import db

_PADRAO_VALOR = re.compile(r'\d{1,12}([.,]\d{1,2})?')
_COM_MILHAR = re.compile(r'\d{1,3}(\.\d{3})+(,\d{0,2})?')


def _limpar(texto: str) -> str:
    """Aceita o formato da tela ('R$ 120.000.000,00'): tira o 'R$', os pontos de milhar e a vírgula solta no fim."""
    texto = re.sub(r'^R\$\s*', '', texto.strip(), flags=re.IGNORECASE)
    if _COM_MILHAR.fullmatch(texto):
        texto = texto.replace('.', '')
    return texto.rstrip(',')


def para_centavos(valor) -> int:
    """Converte 25, 25.5, '25,50', 'R$ 1.250,00' etc. em centavos. Levanta ValueError se for inválido ou <= 0."""
    if isinstance(valor, (int, float, Decimal)) and not isinstance(valor, bool):
        try:
            valor = f"{Decimal(str(valor)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP):f}"
        except InvalidOperation:
            raise ValueError('Informe um valor numérico.')
    texto = _limpar(str(valor))
    if not _PADRAO_VALOR.fullmatch(texto):
        raise ValueError('Informe um valor numérico, com até duas casas decimais (ex.: 20,00).')
    centavos = int((Decimal(texto.replace(',', '.')) * 100).quantize(Decimal('1')))
    if centavos <= 0:
        raise ValueError('O valor deve ser maior que zero.')
    return centavos


class CarteiraRU:
    LIMITE_HISTORICO = 30

    def __init__(self, matricula, saldo_atual=0.0, saldo_anterior=0.0, historico_transacoes=None):
        self.matricula = matricula
        self._saldo_atual = saldo_atual
        self._saldo_anterior = saldo_anterior
        self._historico_transacoes = historico_transacoes or []

    # Atributos privados do diagrama, expostos só para leitura
    @property
    def saldo_atual(self) -> float:
        return self._saldo_atual

    @property
    def saldo_anterior(self) -> float:
        return self._saldo_anterior

    @property
    def historico_transacoes(self) -> list:
        return list(self._historico_transacoes)

    @classmethod
    def carregar(cls, matricula):
        carteira = cls(matricula)
        return carteira if carteira.atualizar() else None

    def atualizar(self) -> bool:
        """Relê saldo e histórico do banco."""
        with db.transacao() as con:
            row = con.execute('SELECT saldo_atual, saldo_anterior FROM alunos WHERE matricula = ?',
                              (self.matricula,)).fetchone()
            if row is None:
                return False
            linhas = con.execute(
                'SELECT id, tipo, valor, saldo_apos, descricao, criado_em FROM transacoes '
                'WHERE matricula = ? ORDER BY id DESC LIMIT ?',
                (self.matricula, self.LIMITE_HISTORICO)).fetchall()
        self._saldo_atual = row['saldo_atual'] / 100
        self._saldo_anterior = row['saldo_anterior'] / 100
        self._historico_transacoes = [
            {'id': t['id'], 'tipo': t['tipo'], 'valor': t['valor'] / 100, 'saldo_apos': t['saldo_apos'] / 100,
             'descricao': t['descricao'], 'criado_em': t['criado_em']} for t in linhas]
        return True

    def adicionar_credito(self, valor, descricao='Recarga') -> None:
        if not self._movimentar('recarga', para_centavos(valor), descricao):
            raise LookupError('Carteira não encontrada.')

    def debitar_refeicao(self, valor, descricao='Refeição') -> bool:
        """Retorna False se o saldo for insuficiente."""
        return self._movimentar('refeicao', para_centavos(valor), descricao)

    def _movimentar(self, tipo, centavos, descricao) -> bool:
        delta = centavos if tipo == 'recarga' else -centavos
        with db.transacao() as con:
            # Uma única instrução: nunca deixa o saldo negativo, mesmo com acessos simultâneos.
            cur = con.execute(
                'UPDATE alunos SET saldo_anterior = saldo_atual, saldo_atual = saldo_atual + ? '
                'WHERE matricula = ? AND saldo_atual + ? >= 0', (delta, self.matricula, delta))
            if cur.rowcount == 0:
                return False
            saldo = con.execute('SELECT saldo_atual FROM alunos WHERE matricula = ?',
                                (self.matricula,)).fetchone()[0]
            con.execute(
                'INSERT INTO transacoes (matricula, tipo, valor, saldo_apos, descricao, criado_em) '
                'VALUES (?,?,?,?,?,?)', (self.matricula, tipo, centavos, saldo, descricao, db.agora()))
        self.atualizar()
        return True
