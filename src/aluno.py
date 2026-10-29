class aluno:

    def __init__(self, matricula, email, nome, foto_url):

        self.matricula = matricula
        self.email = email
        self.nome = nome
        self.foto_url = foto_url
        self.carteira = CarteiraRU()


    def realizar_recarga(self, valor):
        return self.carteira.realizar_recarga(valor)

    def consultar_saldo(self):
        return self.carteira.consultar_saldo()
    