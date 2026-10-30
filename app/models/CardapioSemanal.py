class CardapioSemanal: 

    formatos_permitidos = ['pdf', 'jpeg', 'png', 'jpg']

    def __init__(self, url_documento: str, formato: str):
        self.url_documento = url_documento
        self.formato = formato.lower()

    def carregar_documento(url: str, formato: str):
        pass

    def exibir_cardapio(): 
        if self.caminho_documento:
            return f"Exibindo cardápio do RU:..."
        else:
            return "Não foi possível exibir o cardápio!"
        