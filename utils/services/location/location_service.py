import json
import logging
import os
import urllib.request
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

URL_API_LOCALIZACAO = "http://ip-api.com/json/"
LOCALIZACAO_INDISPONIVEL = "Localização indisponível"
TIMEOUT_SEGUNDOS = 3

'''
Variável de Cache em memória.
    Como o app redesenha a TopBar a cada mudança de tela, isso impede que a API seja chamada excessivamente e atinja limites de requisição (Rate Limit).
'''
_localizacao_em_cache: Optional[str] = None
CHAVE_LOCALIDADE_INSTITUICAO = "localidade_instituicao"
INSTITUICAO_PADRAO_ID = os.environ.get("EVALYTICS_INSTITUICAO_ID", "ufc").strip() or "ufc"


def _caminho_preferencias() -> Path:
    """Retorna o arquivo local de preferências do usuário atual."""
    if os.name == "nt":
        pasta_configuracao = Path(os.environ.get("APPDATA") or Path.home()) / "Evalytics"
    else:
        pasta_configuracao = Path(
            os.environ.get("XDG_CONFIG_HOME") or (Path.home() / ".config")
        ) / "evalytics"
    return pasta_configuracao / "preferencias.json"


def _chave_localidade(instituicao_id: str | None) -> str:
    return (
        f"{CHAVE_LOCALIDADE_INSTITUICAO}:{instituicao_id}"
        if instituicao_id
        else CHAVE_LOCALIDADE_INSTITUICAO
    )


def obter_localidade_instituicao(instituicao_id: str | None = None) -> Optional[str]:
    """Carrega a localidade escolhida, se houver, sem depender da UI."""
    try:
        preferencias = json.loads(_caminho_preferencias().read_text(encoding="utf-8"))
        valor = preferencias.get(_chave_localidade(instituicao_id))
        if valor is None and instituicao_id == INSTITUICAO_PADRAO_ID:
            # Lê a configuração anterior, que usava uma chave única por dispositivo.
            valor = preferencias.get(CHAVE_LOCALIDADE_INSTITUICAO)
        return valor.strip() if isinstance(valor, str) and valor.strip() else None
    except (OSError, ValueError, AttributeError):
        return None


def salvar_localidade_instituicao(
    localidade: str,
    instituicao_id: str | None = None,
) -> bool:
    """Persiste a localidade em arquivo local, sem bloquear serviços da UI."""
    caminho = _caminho_preferencias()
    try:
        caminho.parent.mkdir(parents=True, exist_ok=True)
        try:
            preferencias = json.loads(caminho.read_text(encoding="utf-8"))
            if not isinstance(preferencias, dict):
                preferencias = {}
        except (OSError, ValueError):
            preferencias = {}
        preferencias[_chave_localidade(instituicao_id)] = localidade.strip()
        caminho.write_text(
            json.dumps(preferencias, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return True
    except OSError:
        logger.warning("Não foi possível salvar a localidade escolhida.", exc_info=True)
        return False

def obter_localizacao() -> str:
    """Descobre a localização aproximada do usuário (Cidade - Estado) via IP consumindo API REST pública."""
    
    global _localizacao_em_cache

    if _localizacao_em_cache is not None:
        return _localizacao_em_cache # Retorna imediatamente se já fez a busca antes com sucesso

    try:
        # Request HTTP usando biblioteca nativa do Python com Timeout de segurança
        with urllib.request.urlopen(URL_API_LOCALIZACAO, timeout=TIMEOUT_SEGUNDOS) as resposta:
            dados = json.loads(resposta.read().decode())

            if dados.get("status") == "success":
                cidade = dados.get("city", "")
                estado = dados.get("region", "")
                
                # Salva o resultado no Cache e devolve
                _localizacao_em_cache = f"{cidade} - {estado}"
                return _localizacao_em_cache

    except Exception:
        logger.warning("Não foi possível obter a localização via IP.", exc_info=True) # Falha silenciosa: a UI continuará rodando mesmo se a internet cair

    return LOCALIZACAO_INDISPONIVEL
