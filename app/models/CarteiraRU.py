class CarteiraRU:
    def __init__(self, saldo_atual, saldo_anterior, historico_transacoes):
        self.saldo_atual = 0.0
        self.saldo_anterior = 0.0
        self.historico_transacoes = []

    def adicionar_credito(self, valor):
        self.saldo_atual += valor
        self.historico_transacoes.append(self.saldo_atual)

    def debitar_refeicao(self, valor):
        self.saldo_atual -= valor
        self.saldo_anterior = self.saldo_atual + valor
        self.historico_transacoes.append(self.saldo_atual) 