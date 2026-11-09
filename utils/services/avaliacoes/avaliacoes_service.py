import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from datetime import datetime
from threading import Lock
import requests

from database.services.firebase_config import db
from database.services.institutions.institutions_service import (
    documento_pertence_a_instituicao,
    listar_documentos_da_instituicao,
    obter_instituicao_id_atual,
)
from database.services.cursos.firestore_courses import obter_cursos_db
from database.services.memory_cache import invalidar_cache, obter_cache, salvar_cache
from utils.services.cursos.curso_utils import (
    criar_indice_cursos_atuais,
    resolver_curso_avaliacao,
)

logger = logging.getLogger(__name__)

TIMEOUT_UPLOAD = 120
TAMANHO_MAXIMO_ARQUIVO = 10 * 1024 * 1024
QUANTIDADE_MAXIMA_ARQUIVOS_POR_INDICADOR = 20

EXTENSOES_PERMITIDAS = {
    "png", "jpg", "jpeg", "webp",
    "pdf",
    "doc", "docx",
    "xls", "xlsx",
    "ppt", "pptx",
    "txt", "csv",
    "odt", "ods", "odp",
}

COLECAO_AVALIACOES = "avaliacoes"
CACHE_CURSOS_AVALIACOES_TTL = 15.0
CACHE_AVALIACOES_TTL = 15.0
_lock_carregamento_cursos_avaliacoes = Lock()


def enviar_ficheiro_dreamhost(caminho_local: str, nome_arquivo: str) -> str:
    """
    Envia um ficheiro local para o script PHP alojado no DreamHost
    e retorna a URL pública gerada.
    """
    url_servidor = "https://evalytics.com.br/upload.php"
    
    try:
        with open(caminho_local, "rb") as f:
            files = {"file": (nome_arquivo, f)}
            resposta = requests.post(url_servidor, files=files, timeout=TIMEOUT_UPLOAD)
            
            if resposta.ok:
                dados = resposta.json()
                if dados.get("success"):
                    return dados.get("file_url")
            
            logger.error("Erro no upload para o DreamHost: %s", resposta.text)
            return None
            
    except Exception:
        logger.exception("Falha de comunicação ao enviar ficheiro para o DreamHost.")
        return None


def _preparar_anexos(anexos: dict | None) -> list[dict]:
    """
    Valida os anexos e retorna uma lista com os caminhos e metadados validados.
    """
    arquivos_validados = []
    anexos = anexos or {}

    for indicador_id, lista_anexos in anexos.items():
        indicador_id = str(indicador_id)

        if not isinstance(lista_anexos, list):
            raise ValueError(f"Lista de anexos inválida para o indicador {indicador_id}.")

        if len(lista_anexos) > QUANTIDADE_MAXIMA_ARQUIVOS_POR_INDICADOR:
            raise ValueError(
                f"O indicador {indicador_id} excede o limite "
                f"de {QUANTIDADE_MAXIMA_ARQUIVOS_POR_INDICADOR} arquivos."
            )

        for anexo in lista_anexos:
            caminho_original = anexo.get("caminho")
            nome_original = anexo.get("nome")

            if not caminho_original or not nome_original:
                raise ValueError("Um anexo não possui nome ou caminho válido.")

            caminho = str(Path(caminho_original).resolve())
            nome = Path(nome_original).name
            extensao = Path(nome).suffix.lower().lstrip(".")

            if extensao not in EXTENSOES_PERMITIDAS:
                raise ValueError(f"Formato não permitido: {nome}.")

            if not os.path.isfile(caminho):
                raise FileNotFoundError(f"O arquivo não foi encontrado: {nome}.")

            tamanho = os.path.getsize(caminho)

            if tamanho <= 0:
                raise ValueError(f"O arquivo '{nome}' está vazio.")

            if tamanho > TAMANHO_MAXIMO_ARQUIVO:
                raise ValueError(f"O arquivo '{nome}' excede o limite de 10 MB.")

            arquivos_validados.append({
                "caminho": caminho,
                "nome": nome,
                "indicador_id": indicador_id,
            })

    return arquivos_validados


def salvar_avaliacao(
    curso_id: str,
    curso_nome: str,
    respostas: dict,
    justificativas: dict | None = None,
    anexos: dict | None = None,
    indicadores: list[dict] | None = None,
) -> bool:
    """
    Salva a avaliação institucional diretamente no Firestore
    e faz o upload das evidências para o servidor DreamHost via PHP.
    """
    try:
        # 1. Valida os arquivos locais antes de qualquer operação
        arquivos = _preparar_anexos(anexos)
        evidencias_urls = {}

        # 2. Faz o upload dos arquivos para a DreamHost usando a nova função
        for arquivo in arquivos:
            url_publica = enviar_ficheiro_dreamhost(arquivo["caminho"], arquivo["nome"])
            
            if not url_publica:
                raise Exception(f"Não foi possível enviar o arquivo {arquivo['nome']} para o DreamHost.")

            indicador_id = arquivo["indicador_id"]
            if indicador_id not in evidencias_urls:
                evidencias_urls[indicador_id] = []
                
            evidencias_urls[indicador_id].append({
                "nome": arquivo["nome"],
                "url": url_publica
            })

        # 3. Prepara o dicionário de dados da avaliação
        dados_avaliacao = {
            "curso_id": curso_id,
            "curso_nome": curso_nome,
            "instituicao_id": obter_instituicao_id_atual(),
            "data_avaliacao": datetime.now(),
            "respostas": respostas,
            "justificativas": justificativas or {},
            "evidencias": evidencias_urls,
            # Preserva as perguntas e alternativas exibidas nesta avaliação,
            # mesmo que o catálogo seja alterado futuramente.
            "perguntas": [
                {
                    "id": str(indicador.get("id", "")),
                    "titulo": indicador.get("titulo", ""),
                    "descricao": indicador.get("descricao", ""),
                    "eixo": indicador.get("eixo"),
                    "criterios": indicador.get("criterios", {}),
                }
                for indicador in (indicadores or [])
            ],
        }

        # 4. Salva diretamente no Firestore
        db.collection(COLECAO_AVALIACOES).add(dados_avaliacao)
        invalidar_cache("cursos_avaliacoes:")
        invalidar_cache(f"avaliacoes:{obter_instituicao_id_atual()}")
        invalidar_cache("respostas_tabela:")
        invalidar_cache("dashboard:")
        invalidar_cache("resultados:")
        invalidar_cache("resumo_eixos:")

        logger.info(
            "Avaliação do curso '%s' salva com sucesso no Firestore. "
            "Arquivos enviados para o DreamHost: %s.",
            curso_nome,
            len(arquivos),
        )
        return True

    except Exception:
        logger.exception("Erro ao salvar a avaliação do curso '%s' no Firebase/DreamHost.", curso_nome)
        return False


def listar_avaliacoes(
    cursos_cadastrados: list[dict] | None = None,
    propagar_erro: bool = False,
) -> list[dict]:
    """Lista apenas avaliações vinculadas a cursos ainda cadastrados."""
    instituicao_id = obter_instituicao_id_atual()
    chave_cache = f"avaliacoes:{instituicao_id}"
    encontrado, valor = obter_cache(chave_cache)
    if encontrado:
        return [dict(avaliacao) for avaliacao in valor]

    try:
        cursos = cursos_cadastrados if cursos_cadastrados is not None else obter_cursos_db()
        indice_cursos = criar_indice_cursos_atuais(cursos)
        docs = listar_documentos_da_instituicao(COLECAO_AVALIACOES)
        lista = []
        
        for doc in docs:
            dados = doc.to_dict() or {}
            if not documento_pertence_a_instituicao(dados):
                continue
            curso_atual = resolver_curso_avaliacao(dados, indice_cursos)
            if not curso_atual:
                continue
            dados["curso_nome"] = curso_atual.get("nome", "")
            dados["id"] = doc.id
            lista.append(dados)

        salvar_cache(
            chave_cache,
            tuple(dict(avaliacao) for avaliacao in lista),
            CACHE_AVALIACOES_TTL,
        )
        return lista

    except Exception:
        logger.exception("Erro ao consultar avaliações no Firestore.")
        if propagar_erro:
            raise
        return []


def carregar_cursos_e_avaliacoes() -> tuple[list[dict], list[dict]]:
    """Carrega cursos e avaliações válidas em paralelo para telas de entrada."""
    instituicao_id = obter_instituicao_id_atual()
    chave_pacote = f"cursos_avaliacoes:{instituicao_id}"
    encontrado_pacote, pacote = obter_cache(chave_pacote)
    if encontrado_pacote:
        cursos_cache, avaliacoes_cache = pacote
        return (
            [dict(item) for item in cursos_cache],
            [dict(item) for item in avaliacoes_cache],
        )

    # Navegações iniciais podem solicitar o mesmo conjunto ao mesmo tempo.
    # A segunda chamada aguarda no worker e reutiliza o cache que a primeira gravar.
    with _lock_carregamento_cursos_avaliacoes:
        encontrado_pacote, pacote = obter_cache(chave_pacote)
        if encontrado_pacote:
            cursos_cache, avaliacoes_cache = pacote
            return (
                [dict(item) for item in cursos_cache],
                [dict(item) for item in avaliacoes_cache],
            )

        cursos, avaliacoes = _buscar_cursos_e_avaliacoes(instituicao_id)
        salvar_cache(
            chave_pacote,
            (
                tuple(dict(item) for item in cursos),
                tuple(dict(item) for item in avaliacoes),
            ),
            CACHE_CURSOS_AVALIACOES_TTL,
        )
        return cursos, avaliacoes


def _buscar_cursos_e_avaliacoes(
    instituicao_id: str,
) -> tuple[list[dict], list[dict]]:
    """Obtém cursos e avaliações sem bloquear a thread da interface."""
    chave_cache = f"avaliacoes:{instituicao_id}"
    encontrado, valor = obter_cache(chave_cache)

    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            futuro_cursos = executor.submit(obter_cursos_db)
            futuro_documentos = None
            if not encontrado:
                futuro_documentos = executor.submit(
                    lambda: list(
                        listar_documentos_da_instituicao(
                            COLECAO_AVALIACOES, instituicao_id
                        )
                    )
                )

            cursos = futuro_cursos.result()
            if encontrado:
                avaliacoes = [dict(item) for item in valor]
            else:
                docs = futuro_documentos.result()
                indice_cursos = criar_indice_cursos_atuais(cursos)
                avaliacoes = []
                for doc in docs:
                    dados = doc.to_dict() or {}
                    if not documento_pertence_a_instituicao(dados, instituicao_id):
                        continue
                    curso_atual = resolver_curso_avaliacao(dados, indice_cursos)
                    if not curso_atual:
                        continue
                    dados["curso_nome"] = curso_atual.get("nome", "")
                    dados["id"] = doc.id
                    avaliacoes.append(dados)

                salvar_cache(
                    chave_cache,
                    tuple(dict(item) for item in avaliacoes),
                    CACHE_AVALIACOES_TTL,
                )
            return cursos, avaliacoes
    except Exception:
        logger.exception("Falha ao carregar cursos e avaliações em paralelo.")
        return [], []
