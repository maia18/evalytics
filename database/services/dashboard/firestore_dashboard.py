import logging
from copy import deepcopy

from database.services.cursos.firestore_courses import obter_cursos_db
from database.services.institutions.institutions_service import obter_instituicao_id_atual
from database.services.memory_cache import obter_cache, salvar_cache
from utils.services.cursos.curso_utils import (
    chave_curso,
    chave_departamento,
    criar_indice_cursos_atuais,
    listar_departamentos_unicos,
    listar_nomes_cursos_filtraveis,
    resolver_curso_avaliacao,
)
from utils.services.avaliacoes.avaliacoes_service import listar_avaliacoes
from utils.services.relatorio.relatorio_utils import obter_semestre
from .dashboard_utils import obter_mapa_eixos, normalizar_nota

logger = logging.getLogger(__name__)

EIXOS_PADRAO = (1, 2, 3)


def obter_dados_dashboard(
    semestre: str | None = None,
    curso_nome: str | None = None,
    departamento: str | None = None,
) -> dict:
    """Agrega KPIs, eixos e cursos das avaliações, com filtros opcionais."""
    chave_cache = (
        f"dashboard:{obter_instituicao_id_atual()}:"
        f"{semestre or ''}:{curso_nome or ''}:{departamento or ''}"
    )
    encontrado, valor_cache = obter_cache(chave_cache)
    if encontrado:
        return deepcopy(valor_cache)

    resultado_vazio = {
        "avaliacoes": 0,
        "respostas": 0,
        "cursos": 0,
        "media_geral": None,
        "respostas_validas": 0,
        "medias_eixos": {},
        "respostas_por_eixo": {},
        "dados_por_curso": [],
        "evolucao_semestres": [],
        "semestres_disponiveis": [],
        "cursos_disponiveis": [],
        "departamentos_disponiveis": [],
    }

    try:
        mapa_eixos = obter_mapa_eixos()
        cursos_cadastrados = obter_cursos_db()
        indice_cursos = criar_indice_cursos_atuais(cursos_cadastrados)

        registros = []
        semestres_disponiveis = set()

        for dados in listar_avaliacoes(cursos_cadastrados):
            semestre_avaliacao = dados.get("semestre") or obter_semestre(
                dados.get("data_avaliacao")
            )
            curso_atual = resolver_curso_avaliacao(dados, indice_cursos)
            if not curso_atual:
                continue
            nome_curso = str(curso_atual.get("nome", "")).strip()
            if not nome_curso:
                continue
            respostas = dados.get("respostas", {})
            if not isinstance(respostas, dict):
                respostas = {}

            if semestre_avaliacao:
                semestres_disponiveis.add(semestre_avaliacao)
            registros.append(
                {
                    "semestre": semestre_avaliacao,
                    "curso": nome_curso,
                    "departamento": str(
                        curso_atual.get("departamento", "")
                    ).strip(),
                    "respostas": respostas,
                }
            )

        registros_filtrados = [
            registro
            for registro in registros
            if (not semestre or registro["semestre"] == semestre)
            and (
                not curso_nome
                or chave_curso(registro["curso"]) == chave_curso(curso_nome)
            )
            and (
                not departamento
                or chave_departamento(registro["departamento"])
                == chave_departamento(departamento)
            )
        ]

        notas_por_semestre: dict[str, list[float]] = {}
        for registro in registros:
            if curso_nome and chave_curso(registro["curso"]) != chave_curso(curso_nome):
                continue
            if departamento and chave_departamento(
                registro["departamento"]
            ) != chave_departamento(departamento):
                continue
            semestre_registro = registro["semestre"]
            if not semestre_registro:
                continue
            notas_semestre = notas_por_semestre.setdefault(semestre_registro, [])
            for valor in registro["respostas"].values():
                nota = normalizar_nota(valor)
                if nota is not None:
                    notas_semestre.append(nota)

        notas_gerais: list[float] = []
        notas_por_eixo: dict[int, list[float]] = {
            eixo: [] for eixo in EIXOS_PADRAO
        }
        estatisticas_cursos: dict[str, dict] = {}
        quantidade_respostas = 0

        for registro in registros_filtrados:
            nome_curso = registro["curso"]
            respostas = registro["respostas"]
            quantidade_respostas += len(respostas)

            curso = estatisticas_cursos.setdefault(
                nome_curso,
                {
                    "curso": nome_curso,
                    "avaliacoes": 0,
                    "respostas": 0,
                    "notas": [],
                },
            )
            curso["avaliacoes"] += 1
            curso["respostas"] += len(respostas)

            for indicador_id, valor in respostas.items():
                nota = normalizar_nota(valor)
                if nota is None:
                    continue

                notas_gerais.append(nota)
                curso["notas"].append(nota)
                eixo_id = mapa_eixos.get(str(indicador_id))
                if eixo_id in notas_por_eixo:
                    notas_por_eixo[eixo_id].append(nota)

        # A visão por curso acompanha o catálogo atual, inclusive cursos novos
        # que ainda não receberam avaliações. Avaliações de cursos removidos
        # já foram excluídas ao resolver cada registro pelo catálogo.
        for curso_cadastrado in cursos_cadastrados:
            nome_cadastrado = str(curso_cadastrado.get("nome", "")).strip()
            if not nome_cadastrado:
                continue
            if curso_nome and chave_curso(nome_cadastrado) != chave_curso(curso_nome):
                continue
            if departamento and chave_departamento(
                curso_cadastrado.get("departamento")
            ) != chave_departamento(departamento):
                continue
            estatisticas_cursos.setdefault(
                nome_cadastrado,
                {
                    "curso": nome_cadastrado,
                    "avaliacoes": 0,
                    "respostas": 0,
                    "notas": [],
                },
            )

        medias_eixos = {
            eixo_id: round(sum(notas) / len(notas), 2)
            for eixo_id, notas in notas_por_eixo.items()
            if notas
        }
        respostas_por_eixo = {
            eixo_id: len(notas)
            for eixo_id, notas in notas_por_eixo.items()
        }
        dados_por_curso = [
            {
                "curso": nome,
                "avaliacoes": dados["avaliacoes"],
                "respostas": dados["respostas"],
                "media_geral": (
                    round(sum(dados["notas"]) / len(dados["notas"]), 2)
                    if dados["notas"]
                    else None
                ),
            }
            for nome, dados in sorted(
                estatisticas_cursos.items(), key=lambda item: item[0].casefold()
            )
        ]

        resultado = {
            "avaliacoes": len(registros_filtrados),
            "respostas": quantidade_respostas,
            "cursos": sum(
                1 for dados in estatisticas_cursos.values() if dados["avaliacoes"]
            ),
            "media_geral": (
                round(sum(notas_gerais) / len(notas_gerais), 2)
                if notas_gerais
                else None
            ),
            "respostas_validas": len(notas_gerais),
            "medias_eixos": medias_eixos,
            "respostas_por_eixo": respostas_por_eixo,
            "dados_por_curso": dados_por_curso,
            "evolucao_semestres": [
                {
                    "semestre": semestre_item,
                    "media_geral": round(sum(notas) / len(notas), 2),
                    "respostas_validas": len(notas),
                }
                for semestre_item, notas in sorted(notas_por_semestre.items())
                if notas
            ],
            "semestres_disponiveis": sorted(
                semestres_disponiveis, reverse=True
            ),
            # Os filtros exibem apenas cursos atualmente cadastrados.
            "cursos_disponiveis": listar_nomes_cursos_filtraveis(
                [], cursos_cadastrados
            ),
            "departamentos_disponiveis": listar_departamentos_unicos(
                cursos_cadastrados
            ),
        }
        salvar_cache(chave_cache, resultado, 5.0)
        return resultado

    except Exception:
        logger.exception("Erro ao calcular dados do Dashboard.")
        return resultado_vazio
