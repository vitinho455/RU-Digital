"""CardapioSemanal: documento (por ora, PDF) com o cardápio da semana."""
import os
import re
import uuid

from app.models import db

FORMATOS_ACEITOS = ('pdf',)          # para aceitar outros formatos, inclua aqui e valide em armazenar_arquivo
PREFIXO_URL = '/cardapio/arquivo/'
LIMITE_BYTES = 10 * 1024 * 1024
_NOME_VALIDO = re.compile(r'[0-9a-f]{32}\.(pdf)')


class CardapioSemanal:
    def __init__(self, url_documento='', formato='', enviado_em=None):
        self.url_documento = url_documento
        self.formato = formato
        self.enviado_em = enviado_em

    @staticmethod
    def armazenar_arquivo(conteudo: bytes) -> str:
        """Valida o PDF, grava em disco com nome aleatório e devolve a URL interna."""
        if not conteudo:
            raise ValueError('O arquivo está vazio.')
        if len(conteudo) > LIMITE_BYTES:
            raise ValueError(f'O arquivo passa de {LIMITE_BYTES // (1024 * 1024)} MB.')
        if not conteudo.startswith(b'%PDF-'):
            raise ValueError('O arquivo enviado não é um PDF válido.')
        nome = f'{uuid.uuid4().hex}.pdf'
        with open(os.path.join(db.UPLOADS_DIR, nome), 'wb') as arquivo:
            arquivo.write(conteudo)
        return PREFIXO_URL + nome

    @staticmethod
    def caminho_arquivo(nome):
        """Caminho no disco de um arquivo de cardápio, ou None se o nome for inválido ou não existir."""
        if not _NOME_VALIDO.fullmatch(nome):
            return None
        caminho = os.path.join(db.UPLOADS_DIR, nome)
        return caminho if os.path.isfile(caminho) else None

    def carregar_documento(self, url: str) -> None:
        nome = url[len(PREFIXO_URL):] if url.startswith(PREFIXO_URL) else ''
        if self.caminho_arquivo(nome) is None:
            raise ValueError('Documento do cardápio não encontrado.')
        formato = nome.rsplit('.', 1)[1]
        if formato not in FORMATOS_ACEITOS:
            raise ValueError('Formato de cardápio não suportado.')
        self.url_documento, self.formato = url, formato

    def exibir_cardapio(self) -> str:
        """URL do documento a ser exibido ('' se não houver cardápio)."""
        return self.url_documento

    def salvar(self, id_admin: str) -> None:
        self.enviado_em = db.agora()
        with db.transacao() as con:
            con.execute('INSERT INTO cardapios (url_documento, formato, enviado_por, enviado_em) VALUES (?,?,?,?)',
                        (self.url_documento, self.formato, id_admin, self.enviado_em))

    @classmethod
    def historico(cls, limite=10):
        """Cardápios publicados, do mais recente para o mais antigo."""
        with db.transacao() as con:
            linhas = con.execute('SELECT url_documento, formato, enviado_em FROM cardapios '
                                 'ORDER BY id DESC LIMIT ?', (limite,)).fetchall()
        return [cls(l['url_documento'], l['formato'], l['enviado_em']) for l in linhas]

    @classmethod
    def atual(cls):
        lista = cls.historico(1)
        return lista[0] if lista else None
