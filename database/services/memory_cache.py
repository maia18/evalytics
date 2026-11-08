"""Cache curto em memória para leituras repetidas do Firestore."""

from threading import RLock
from time import monotonic

_cache: dict[str, tuple[float, object]] = {}
_lock = RLock()


def obter_cache(chave: str) -> tuple[bool, object | None]:
    agora = monotonic()
    with _lock:
        entrada = _cache.get(chave)
        if entrada is None:
            return False, None
        expira_em, valor = entrada
        if agora >= expira_em:
            _cache.pop(chave, None)
            return False, None
        return True, valor


def salvar_cache(chave: str, valor: object, ttl_segundos: float = 5.0) -> None:
    with _lock:
        _cache[chave] = (monotonic() + ttl_segundos, valor)


def invalidar_cache(prefixo: str) -> None:
    with _lock:
        for chave in tuple(_cache):
            if chave.startswith(prefixo):
                _cache.pop(chave, None)
