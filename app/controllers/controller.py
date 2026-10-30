import os 
from app.models.CardapioSemanal import CardapioSemanal

cardapio = CardapioSemanal()

def Upload_Cardapio(upload_file):

        if not upload_file:
            return "Nenhum arquivo selecionado/encontrado"
        nome_arquivo = upload_file.filename
        nome_arquivo_extensao = nome_arquivo.split(".")[-1].lower()

        if nome_arquivo_extensao != CardapioSemanal.formatos_permitidos:
            return "Formato de arquivo inválido!"
        pasta_destino = "app/uploads/upload"
        os.makedirs(pasta_destino, exist_ok=True)

        caminho_arquivo = os.path.join(pasta_destino, nome_arquivo)
        upload_file.save(caminho_arquivo)

        caminho_relativo = f"app/uploads/upload/{nome_arquivo}"
        cardapio.atualizar_cardapio(caminho_relativo, nome_arquivo_extensao)

        return "Cardápio atualizado com sucesso!"