"""Hash e verificação de senhas (PBKDF2-SHA256, apenas biblioteca padrão)."""
import hashlib
import hmac
import os

ITERACOES = 200_000


def gerar_hash(senha: str) -> str:
    sal = os.urandom(16)
    dk = hashlib.pbkdf2_hmac('sha256', senha.encode(), sal, ITERACOES)
    return f'pbkdf2_sha256${ITERACOES}${sal.hex()}${dk.hex()}'


def verificar(senha: str, armazenado: str) -> bool:
    try:
        _, iteracoes, sal, esperado = armazenado.split('$')
        dk = hashlib.pbkdf2_hmac('sha256', senha.encode(), bytes.fromhex(sal), int(iteracoes))
        return hmac.compare_digest(dk.hex(), esperado)
    except (ValueError, AttributeError):
        return False


# Usado quando o e-mail não existe, para o tempo de resposta não revelar isso.
HASH_FALSO = gerar_hash('senha-que-ninguem-usa')
