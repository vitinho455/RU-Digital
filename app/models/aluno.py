import CarteiraRU

class aluno:

    def __init__(self, matricula, email, nome, foto_url):

        self.matricula = matricula
        self.email = email
        self.nome = nome
        self.foto_url = foto_url
        self.carteira = CarteiraRU()


    def realizar_recarga(self, valor):
        return self.carteira.adicionar_credito(valor)

    def consultar_saldo(self):
        return self.carteira.saldo_atual