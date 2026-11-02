import logging
from database.services.firebase_config import db
from database.services.cursos.firestore_courses import obter_cursos_db
from database.services.institutions.institutions_service import listar_documentos_da_instituicao
from utils.services.indicadores.indicadores_repository import listar_indicadores
from utils.services.cursos.curso_utils import (
    chave_curso,
    criar_indice_cursos_atuais,
    normalizar_nome_curso,
    resolver_curso_avaliacao,
)

# Importação dos utilitários puros
from .relatorio_utils import obter_semestre

logger = logging.getLogger(__name__)
COLECAO_AVALIACOES = "avaliacoes"

EIXO_PADRAO = 1
EIXOS_PADRAO = (1, 2, 3)

def _obter_mapa_eixos() -> dict[str, int]:
    """Cria um mapa relacionando o ID do indicador ao seu eixo."""
    try:
        indicadores = listar_indicadores()
        return {
            indicador["id"]: indicador.get("eixo", EIXO_PADRAO)
            for indicador in indicadores
            if indicador.get("id")
        }
    except Exception:
        logger.exception("Erro ao montar mapa de eixos.")
        return {}

def listar_semestres_disponiveis() -> list[str]:
    """Retorna os semestres encontrados nas avaliações reais no Firestore."""
    try:
        indice_cursos = criar_indice_cursos_atuais(obter_cursos_db())
        documentos = listar_documentos_da_instituicao(COLECAO_AVALIACOES)
        semestres = set()

        for documento in documentos:
            dados = documento.to_dict() or {}
            if not resolver_curso_avaliacao(dados, indice_cursos):
                continue
            data_avaliacao = dados.get("data_avaliacao", "")
            semestre = obter_semestre(data_avaliacao)

            if semestre:
                semestres.add(semestre)

        return sorted(semestres, reverse=True)

    except Exception:
        logger.exception("Erro ao listar semestres disponíveis.")
        return []

def calcular_medias_eixos(
    semestre: str | None = None,
    eixo: int | None = None,
    curso_nome: str | None = None,
) -> dict[int, float | None]:
    """Calcula as médias das avaliações por eixo, buscando diretamente no banco."""
    try:
        mapa_eixo = _obter_mapa_eixos()
        cursos_cadastrados = obter_cursos_db()
        indice_cursos = criar_indice_cursos_atuais(cursos_cadastrados)
        avaliacoes = listar_documentos_da_instituicao(COLECAO_AVALIACOES)

        acumulador: dict[int, list[float]] = {eixo_id: [] for eixo_id in EIXOS_PADRAO}

        for avaliacao in avaliacoes:
            dados = avaliacao.to_dict() or {}
            curso_atual = resolver_curso_avaliacao(dados, indice_cursos)
            if not curso_atual:
                continue
            data_avaliacao = dados.get("data_avaliacao", "")
            semestre_avaliacao = obter_semestre(data_avaliacao)

            if semestre and semestre_avaliacao != semestre:
                continue
            nome_curso = curso_atual.get("nome", "")
            if curso_nome and chave_curso(nome_curso) != chave_curso(curso_nome):
                continue

            respostas = dados.get("respostas", {})
            if not isinstance(respostas, dict):
                continue

            for indicador_id, nota in respostas.items():
                eixo_id = mapa_eixo.get(indicador_id)

                if eixo_id not in acumulador:
                    continue

                if eixo is not None and eixo_id != eixo:
                    continue

                try:
                    acumulador[eixo_id].append(float(nota))
                except (TypeError, ValueError):
                    continue

        return {
            eixo_id: (sum(notas) / len(notas) if notas else None)
            for eixo_id, notas in acumulador.items()
        }

    except Exception:
        logger.exception("Erro ao calcular médias dos eixos.")
        return {eixo_id: None for eixo_id in EIXOS_PADRAO}

def listar_resultados_consolidados(
    semestre: str | None = None,
    eixo: int | None = None,
    curso_nome: str | None = None,
) -> list[dict]:
    """Retorna avaliações consolidadas por eixo."""
    try:
        mapa_eixo = _obter_mapa_eixos()
        cursos_cadastrados = obter_cursos_db()
        nomes_cadastrados = [
            str(curso.get("nome", "")).strip()
            for curso in cursos_cadastrados
            if curso.get("nome") and str(curso.get("nome")).strip()
        ]
        indice_cursos = criar_indice_cursos_atuais(cursos_cadastrados)
        documentos = listar_documentos_da_instituicao(COLECAO_AVALIACOES)
        resultados: list[dict] = []

        for documento in documentos:
            dados = documento.to_dict() or {}
            curso_atual = resolver_curso_avaliacao(dados, indice_cursos)
            if not curso_atual:
                continue
            data_avaliacao = dados.get("data_avaliacao", "")
            semestre_avaliacao = obter_semestre(data_avaliacao)

            if semestre and semestre_avaliacao != semestre:
                continue
            nome_original = curso_atual.get("nome", "")
            if curso_nome and chave_curso(nome_original) != chave_curso(curso_nome):
                continue

            respostas = dados.get("respostas", {})
            if not isinstance(respostas, dict):
                respostas = {}

            acumulador: dict[int, list[float]] = {eixo_id: [] for eixo_id in EIXOS_PADRAO}

            for indicador_id, nota in respostas.items():
                eixo_id = mapa_eixo.get(indicador_id)
                if eixo_id not in acumulador:
                    continue
                try:
                    acumulador[eixo_id].append(float(nota))
                except (TypeError, ValueError):
                    continue

            if eixo is not None:
                if eixo not in acumulador or not acumulador[eixo]:
                    continue

            medias_eixos: dict[int, float] = {}
            for eixo_id in EIXOS_PADRAO:
                notas = acumulador[eixo_id]
                medias_eixos[eixo_id] = sum(notas) / len(notas) if notas else 0.0

            medias_respondidas = [
                medias_eixos[eixo_id]
                for eixo_id in EIXOS_PADRAO
                if acumulador[eixo_id]
            ]
            media_geral = sum(medias_respondidas) / len(medias_respondidas) if medias_respondidas else 0.0

            resultados.append({
                "id": documento.id,
                "curso_id": dados.get("curso_id", ""),
                "curso_nome": normalizar_nome_curso(
                    nome_original, nomes_cadastrados
                ),
                "data_avaliacao": data_avaliacao,
                "semestre": semestre_avaliacao,
                "eixos": {
                    1: medias_eixos[1],
                    2: medias_eixos[2],
                    3: medias_eixos[3],
                },
                "media_geral": media_geral,
            })

        return resultados

    except Exception:
        logger.exception("Erro ao listar resultados consolidados.")
        return []

def listar_resultados_avaliacoes() -> list[dict]:
    """Mantém compatibilidade com chamadas antigas."""
    return listar_resultados_consolidados()
