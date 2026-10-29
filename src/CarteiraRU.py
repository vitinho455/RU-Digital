class CareiraRU:
    def __init__(self, saldo_atual, saldo_anterior, historico_transacoes):
        self.saldo_atual = saldo_atual
        self.saldo_anterior = saldo_anterior
        self.historico_transacoes = historico_transacoes

    def adicionar_credito(self, valor):
        self.saldo_atual += valor

    def debitar_refeicao(self, valor):
        self.saldo_atual -= valor