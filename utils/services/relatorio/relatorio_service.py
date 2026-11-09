import logging
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
from database.services.institutions.institutions_service import obter_instituicao_id_atual
from database.services.memory_cache import obter_cache, salvar_cache
from database.services.cursos.firestore_courses import obter_cursos_db
from utils.services.indicadores.indicadores_repository import listar_indicadores
from utils.services.cursos.curso_utils import (
    chave_curso,
    criar_indice_cursos_atuais,
    normalizar_nome_curso,
    resolver_curso_avaliacao,
)
from utils.services.avaliacoes.avaliacoes_service import listar_avaliacoes

# Importação dos utilitários puros
from .relatorio_utils import obter_semestre

logger = logging.getLogger(__name__)
EIXO_PADRAO = 1
EIXOS_PADRAO = (1, 2, 3)
CACHE_RELATORIOS_TTL = 15.0

def _obter_mapa_eixos(propagar_erro: bool = False) -> dict[str, int]:
    """Cria um mapa relacionando o ID do indicador ao seu eixo."""
    try:
        indicadores = listar_indicadores(propagar_erro=propagar_erro)
        return {
            indicador["id"]: indicador.get("eixo", EIXO_PADRAO)
            for indicador in indicadores
            if indicador.get("id")
        }
    except Exception:
        logger.exception("Erro ao montar mapa de eixos.")
        if propagar_erro:
            raise
        return {}

def listar_semestres_disponiveis() -> list[str]:
    """Retorna os semestres encontrados nas avaliações reais no Firestore."""
    try:
        cursos = obter_cursos_db()
        indice_cursos = criar_indice_cursos_atuais(cursos)
        documentos = listar_avaliacoes(cursos)
        semestres = set()

        for dados in documentos:
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
    resumo = obter_resumo_eixos(semestre, curso_nome, eixo)
    return {
        eixo_id: dados["media"]
        for eixo_id, dados in resumo["eixos"].items()
    }


def obter_resumo_eixos(
    semestre: str | None = None,
    curso_nome: str | None = None,
    eixo: int | None = None,
) -> dict:
    """Retorna médias e contagens válidas no mesmo conjunto filtrado."""
    chave_cache = (
        f"resumo_eixos:{obter_instituicao_id_atual()}:"
        f"{semestre or ''}:{curso_nome or ''}:{eixo if eixo is not None else ''}"
    )
    encontrado, valor_cache = obter_cache(chave_cache)
    if encontrado:
        return deepcopy(valor_cache)

    try:
        # Os metadados vêm de coleções independentes. Consultá-los em paralelo
        # reduz o tempo de espera da primeira abertura (cache frio).
        with ThreadPoolExecutor(max_workers=2) as executor:
            tarefa_mapa = executor.submit(_obter_mapa_eixos)
            tarefa_cursos = executor.submit(obter_cursos_db)
            mapa_eixo = tarefa_mapa.result()
            cursos_cadastrados = tarefa_cursos.result()
        indice_cursos = criar_indice_cursos_atuais(cursos_cadastrados)
        avaliacoes = listar_avaliacoes(cursos_cadastrados)

        acumulador: dict[int, list[float]] = {eixo_id: [] for eixo_id in EIXOS_PADRAO}
        avaliacoes_com_respostas = 0

        for dados in avaliacoes:
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

            respostas_avaliacao = 0
            for indicador_id, nota in respostas.items():
                eixo_id = mapa_eixo.get(indicador_id)

                if eixo_id not in acumulador:
                    continue

                if eixo is not None and eixo_id != eixo:
                    continue

                try:
                    nota_numerica = float(nota)
                    if not 1 <= nota_numerica <= 5:
                        continue
                    acumulador[eixo_id].append(nota_numerica)
                    respostas_avaliacao += 1
                except (TypeError, ValueError):
                    continue

            if respostas_avaliacao:
                avaliacoes_com_respostas += 1

        total_respostas = sum(len(notas) for notas in acumulador.values())
        todas_notas = [nota for notas in acumulador.values() for nota in notas]
        resumo = {
            "avaliacoes": avaliacoes_com_respostas,
            "respostas": total_respostas,
            "media_geral": sum(todas_notas) / len(todas_notas) if todas_notas else None,
            "eixos": {
                eixo_id: {
                    "media": sum(notas) / len(notas) if notas else None,
                    "respostas": len(notas),
                }
                for eixo_id, notas in acumulador.items()
            },
        }
        salvar_cache(chave_cache, resumo, CACHE_RELATORIOS_TTL)
        return resumo

    except Exception:
        logger.exception("Erro ao calcular resumo dos eixos.")
        return {
            "avaliacoes": 0,
            "respostas": 0,
            "media_geral": None,
            "eixos": {
                eixo_id: {"media": None, "respostas": 0}
                for eixo_id in EIXOS_PADRAO
            },
        }

def listar_resultados_consolidados(
    semestre: str | None = None,
    eixo: int | None = None,
    curso_nome: str | None = None,
    propagar_erro: bool = False,
) -> list[dict]:
    """Retorna avaliações consolidadas por eixo."""
    chave_cache = (
        f"resultados:{obter_instituicao_id_atual()}:"
        f"{semestre or ''}:{eixo if eixo is not None else ''}:{curso_nome or ''}"
    )
    encontrado, valor_cache = obter_cache(chave_cache)
    if encontrado:
        return deepcopy(valor_cache)

    try:
        # Indicadores e catálogo não dependem um do outro; carregue juntos
        # para diminuir a latência da consulta inicial de relatórios.
        with ThreadPoolExecutor(max_workers=2) as executor:
            tarefa_mapa = executor.submit(_obter_mapa_eixos, propagar_erro)
            tarefa_cursos = executor.submit(obter_cursos_db, propagar_erro)
            mapa_eixo = tarefa_mapa.result()
            cursos_cadastrados = tarefa_cursos.result()
        nomes_cadastrados = [
            str(curso.get("nome", "")).strip()
            for curso in cursos_cadastrados
            if curso.get("nome") and str(curso.get("nome")).strip()
        ]
        indice_cursos = criar_indice_cursos_atuais(cursos_cadastrados)
        documentos = listar_avaliacoes(
            cursos_cadastrados, propagar_erro=propagar_erro
        )
        resultados: list[dict] = []

        for dados in documentos:
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
                "id": dados.get("id", ""),
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

        salvar_cache(chave_cache, resultados, CACHE_RELATORIOS_TTL)
        return resultados

    except Exception:
        logger.exception("Erro ao listar resultados consolidados.")
        if propagar_erro:
            raise
        return []

def listar_resultados_avaliacoes(propagar_erro: bool = False) -> list[dict]:
    """Mantém compatibilidade com chamadas antigas."""
    return listar_resultados_consolidados(propagar_erro=propagar_erro)
