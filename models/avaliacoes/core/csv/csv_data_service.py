import logging

from database.services.firebase_config import db
from database.services.institutions.institutions_service import listar_documentos_da_instituicao
from database.services.cursos.firestore_courses import obter_cursos_db
from utils.services.indicadores.indicadores_repository import listar_indicadores
from utils.services.cursos.curso_utils import (
    criar_indice_cursos_atuais,
    resolver_curso_avaliacao,
)

logger = logging.getLogger(__name__)
COLECAO_AVALIACOES = "avaliacoes"

NOMES_EIXOS = {
    1: "Organização Didático-Pedagógica",
    2: "Corpo Docente e Tutorial",
    3: "Infraestrutura",
}

CABECALHO_CSV = [
    "ID_Avaliacao",
    "Data_Avaliacao",
    "ID_Curso",
    "Curso",
    "Eixo",
    "ID_Indicador",
    "Pergunta",
    "Descricao",
    "Nota",
    "Resposta_Selecionada",
    "Status_Resposta",
    "Justificativa",
    "Evidencias",
    "Alternativas",
    "Fonte_Perguntas",
]


def formatar_data(data) -> str:
    """Converte timestamps do Firestore para o formato brasileiro."""
    if not data:
        return ""
    if hasattr(data, "strftime"):
        return data.strftime("%d/%m/%Y %H:%M")
    return str(data)


def obter_mapa_indicadores() -> dict[str, dict]:
    """Carrega o catálogo para avaliações antigas sem cópia histórica."""
    try:
        indicadores = listar_indicadores()
        return {
            str(indicador.get("id")): indicador
            for indicador in indicadores
            if indicador.get("id")
        }
    except Exception:
        logger.exception("Erro ao carregar indicadores para exportação CSV.")
        return {}


def _obter_por_id(mapa: dict, identificador) -> dict | list | str | None:
    chave = str(identificador)
    for chave_mapa, valor in mapa.items():
        if str(chave_mapa) == chave:
            return valor
    return None


def _normalizar_nivel(valor) -> str:
    if valor is None or str(valor).strip() == "":
        return ""
    try:
        numero = float(valor)
        return str(int(numero)) if numero.is_integer() else str(numero)
    except (TypeError, ValueError):
        return str(valor).strip()


def _formatar_nota(valor) -> str:
    if valor is None or str(valor).strip() == "":
        return ""
    try:
        return f"{float(valor):.1f}".replace(".", ",")
    except (TypeError, ValueError):
        return str(valor)


def _formatar_alternativas(criterios) -> str:
    if not isinstance(criterios, dict):
        return ""
    return "\n".join(
        f"Nível {nivel}: {texto}"
        for nivel, texto in sorted(criterios.items(), key=lambda item: str(item[0]))
        if texto is not None and str(texto).strip()
    )


def _formatar_evidencias(evidencias) -> str:
    if not isinstance(evidencias, list):
        return ""
    return "\n".join(
        " — ".join(
            parte for parte in (str(anexo.get("nome", "")).strip(), str(anexo.get("url", "")).strip())
            if parte
        )
        for anexo in evidencias
        if isinstance(anexo, dict)
    )


def _linha_csv(
    avaliacao_id: str,
    dados_avaliacao: dict,
    pergunta: dict,
    indicador_id: str,
    respostas: dict,
    justificativas: dict,
    evidencias: dict,
    nome_curso: str,
    fonte_perguntas: str,
    mapa_indicadores: dict[str, dict],
) -> list[str]:
    indicador_id = str(indicador_id)
    indicador_catalogo = mapa_indicadores.get(indicador_id, {})

    chave_resposta = next(
        (chave for chave in respostas if str(chave) == indicador_id), None
    )
    nota = respostas.get(chave_resposta) if chave_resposta is not None else None
    nivel = _normalizar_nivel(nota)

    criterios = pergunta.get("criterios") or indicador_catalogo.get("criterios", {})
    resposta_selecionada = ""
    if nivel and isinstance(criterios, dict):
        resposta_selecionada = str(
            criterios.get(nivel)
            or criterios.get(nota)
            or ""
        )

    justificativa = _obter_por_id(justificativas, indicador_id) if isinstance(justificativas, dict) else None
    anexos = _obter_por_id(evidencias, indicador_id) if isinstance(evidencias, dict) else None

    try:
        eixo_id = int(pergunta.get("eixo", indicador_catalogo.get("eixo")))
    except (TypeError, ValueError):
        eixo_id = None

    eixo = NOMES_EIXOS.get(
        eixo_id,
        f"Eixo {eixo_id}" if eixo_id is not None else "Não informado",
    )
    titulo = pergunta.get("titulo") or indicador_catalogo.get("titulo") or "Pergunta não recuperada"
    descricao = pergunta.get("descricao") or indicador_catalogo.get("descricao") or ""

    return [
        avaliacao_id,
        formatar_data(dados_avaliacao.get("data_avaliacao")),
        str(dados_avaliacao.get("curso_id", "")),
        nome_curso,
        eixo,
        indicador_id,
        str(titulo),
        str(descricao),
        _formatar_nota(nota),
        resposta_selecionada,
        "Respondida" if nivel else "Sem resposta",
        str(justificativa or ""),
        _formatar_evidencias(anexos),
        _formatar_alternativas(criterios),
        fonte_perguntas,
    ]


def preparar_dados_csv(resultados: list[dict]) -> list[list[str]]:
    """Exporta cada pergunta da avaliação, com resposta, justificativa e evidências."""
    dados = [CABECALHO_CSV]
    if not resultados:
        return dados

    ids_avaliacoes = [
        str(resultado.get("id"))
        for resultado in resultados
        if resultado.get("id")
    ]
    if not ids_avaliacoes:
        return dados

    mapa_indicadores = obter_mapa_indicadores()
    cursos_cadastrados = obter_cursos_db()
    indice_cursos = criar_indice_cursos_atuais(cursos_cadastrados)

    try:
        ids_selecionados = set(ids_avaliacoes)
        documentos = {
            documento.id: (documento.to_dict() or {})
            for documento in listar_documentos_da_instituicao(COLECAO_AVALIACOES)
            if documento.id in ids_selecionados
        }

        for avaliacao_id in ids_avaliacoes:
            dados_avaliacao = documentos.get(avaliacao_id)
            if dados_avaliacao is None:
                continue
            curso_atual = resolver_curso_avaliacao(dados_avaliacao, indice_cursos)
            if not curso_atual:
                continue

            respostas = dados_avaliacao.get("respostas", {})
            if not isinstance(respostas, dict):
                respostas = {}
            justificativas = (
                dados_avaliacao.get("justificativas")
                or dados_avaliacao.get("comentarios")
                or {}
            )
            evidencias = dados_avaliacao.get("evidencias", {}) or {}

            perguntas = dados_avaliacao.get("perguntas")
            possui_snapshot = isinstance(perguntas, list) and bool(perguntas)
            if not possui_snapshot:
                perguntas = [
                    {
                        "id": identificador,
                        "titulo": indicador.get("titulo", "Pergunta não recuperada"),
                        "descricao": indicador.get("descricao", ""),
                        "eixo": indicador.get("eixo"),
                        "criterios": indicador.get("criterios", {}),
                    }
                    for identificador, indicador in mapa_indicadores.items()
                    if indicador.get("status", "ATIVO") == "ATIVO"
                ]

            perguntas_por_id = {
                str(pergunta.get("id")): pergunta
                for pergunta in perguntas
                if pergunta.get("id") is not None
            }
            perguntas_ordenadas = sorted(
                perguntas_por_id.values(),
                key=lambda pergunta: (
                    int(pergunta.get("eixo", 0) or 0),
                    str(pergunta.get("titulo", "")).casefold(),
                ),
            )
            fonte_perguntas = (
                "Cópia histórica da avaliação"
                if possui_snapshot
                else "Catálogo atual (avaliação antiga sem cópia histórica)"
            )

            nome_curso = curso_atual.get("nome", "")

            for pergunta in perguntas_ordenadas:
                indicador_id = str(pergunta.get("id", ""))
                dados.append(
                    _linha_csv(
                        avaliacao_id,
                        dados_avaliacao,
                        pergunta,
                        indicador_id,
                        respostas,
                        justificativas,
                        evidencias,
                        nome_curso,
                        fonte_perguntas,
                        mapa_indicadores,
                    )
                )

            respostas_sem_pergunta = [
                indicador_id
                for indicador_id in respostas
                if str(indicador_id) not in perguntas_por_id
            ]
            for indicador_id in respostas_sem_pergunta:
                indicador_id = str(indicador_id)
                dados.append(
                    _linha_csv(
                        avaliacao_id,
                        dados_avaliacao,
                        {"id": indicador_id, "titulo": "Pergunta não recuperada"},
                        indicador_id,
                        respostas,
                        justificativas,
                        evidencias,
                        nome_curso,
                        "Resposta preservada; pergunta não localizada",
                        mapa_indicadores,
                    )
                )

    except Exception:
        logger.exception("Erro ao preparar dados reais para exportação CSV.")
        raise

    return dados
