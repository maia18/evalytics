import os
import logging
import flet as ft
from typing import Optional
from datetime import datetime
from database.services.firebase_config import db
from database.services.institutions.institutions_service import listar_documentos_da_instituicao
from database.services.cursos.firestore_courses import obter_cursos_db
from models.avaliacoes.core.feedback import mostrar_feedback
from models.relatorios.core.grafico_radar import salvar_grafico_radar
from utils.services.indicadores.indicadores_repository import listar_indicadores
from utils.services.cursos.curso_utils import (
    criar_indice_cursos_atuais,
    normalizar_nome_curso,
    resolver_curso_avaliacao,
)
from .pdf_builder import construir_documento_pdf

logger = logging.getLogger(__name__)
CAMINHO_IMAGEM_TEMP = "radar_temp.png"
COLECAO_AVALIACOES = "avaliacoes"


def carregar_avaliacoes_detalhadas(
    resultados: list[dict],
    eixo_selecionado: int | None = None,
) -> list[dict]:
    """Carrega respostas e perguntas completas das avaliações filtradas."""
    ids = {str(item.get("id")) for item in resultados if item.get("id")}
    if not ids:
        return []

    indicadores_atuais = listar_indicadores()
    cursos_cadastrados = obter_cursos_db()
    nomes_cadastrados = [
        str(curso.get("nome", "")).strip()
        for curso in cursos_cadastrados
        if curso.get("nome") and str(curso.get("nome")).strip()
    ]
    indice_cursos = criar_indice_cursos_atuais(cursos_cadastrados)
    avaliacoes = []
    for documento in listar_documentos_da_instituicao(COLECAO_AVALIACOES):
        if documento.id not in ids:
            continue

        dados = documento.to_dict() or {}
        curso_atual = resolver_curso_avaliacao(dados, indice_cursos)
        if not curso_atual:
            continue
        perguntas = dados.get("perguntas")
        perguntas_historicas = isinstance(perguntas, list) and bool(perguntas)
        # Avaliações antigas não têm snapshot: usa o catálogo atual como fallback.
        if not isinstance(perguntas, list) or not perguntas:
            perguntas = [
                {
                    "id": str(indicador.get("id", "")),
                    "titulo": indicador.get("titulo", "Pergunta sem título"),
                    "descricao": indicador.get("descricao", ""),
                    "eixo": indicador.get("eixo"),
                    "criterios": indicador.get("criterios", {}),
                }
                for indicador in indicadores_atuais
                if indicador.get("status", "ATIVO") == "ATIVO"
            ]

        perguntas = [
            pergunta for pergunta in perguntas
            if eixo_selecionado is None
            or str(pergunta.get("eixo")) == str(eixo_selecionado)
        ]
        perguntas.sort(
            key=lambda pergunta: (
                int(pergunta.get("eixo", 0) or 0),
                str(pergunta.get("titulo", "")).casefold(),
            )
        )

        avaliacoes.append({
            "id": documento.id,
            "curso_nome": normalizar_nome_curso(
                curso_atual.get("nome"),
                nomes_cadastrados,
            ),
            "data_avaliacao": dados.get("data_avaliacao"),
            "respostas": dados.get("respostas", {}) or {},
            "justificativas": dados.get("justificativas", dados.get("comentarios", {})) or {},
            "evidencias": dados.get("evidencias", {}) or {},
            "perguntas": perguntas,
            "perguntas_historicas": perguntas_historicas,
        })

    return avaliacoes

def gerar_pdf_completo(
    page: ft.Page,
    medias: dict[int, float | None],
    nomes_eixos: dict[int, str],
    semestre: str = "Todos",
    quantidade_avaliacoes: int = 0,
    cursos: list[str] | None = None,
    resultados: list[dict] | None = None,
    eixo_selecionado: int | None = None,
) -> Optional[str]:
    """Orquestra a validação, estruturação, geração visual do PDF e os alertas na UI."""

    try:
        # ==================================================
        # VALIDAÇÃO DAS MÉDIAS
        # ==================================================
        medias_validas: dict[int, float] = {}

        for eixo_id, nota in medias.items():
            if nota is None:
                continue
            try:
                medias_validas[eixo_id] = float(nota)
            except (TypeError, ValueError):
                continue

        if not medias_validas:
            mostrar_feedback(page, "Não existem dados para gerar o relatório PDF.", sucesso=False)
            return None

        # ==================================================
        # NORMALIZAÇÃO DOS CURSOS
        # ==================================================
        cursos_normalizados = {
            normalizar_nome_curso(curso)
            for curso in (cursos or [])
            if curso and str(curso).strip()
        }

        cursos_validos = sorted(cursos_normalizados)
        texto_cursos = ", ".join(cursos_validos) if cursos_validos else "Todos os cursos"

        # ==================================================
        # GERAÇÃO DO ARQUIVO PDF E GRÁFICO AUXILIAR
        # ==================================================
        salvar_grafico_radar(medias_validas, nomes_eixos, CAMINHO_IMAGEM_TEMP)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"relatorio_evalytics_{timestamp}.pdf"
        avaliacoes_detalhadas = carregar_avaliacoes_detalhadas(
            resultados or [], eixo_selecionado=eixo_selecionado
        )

        # Delega a tarefa de desenho do documento ao pdf_builder
        construir_documento_pdf(
            caminho_arquivo=nome_arquivo,
            medias_validas=medias_validas,
            nomes_eixos=nomes_eixos,
            semestre=semestre,
            quantidade_avaliacoes=quantidade_avaliacoes,
            texto_cursos=texto_cursos,
            caminho_imagem_radar=CAMINHO_IMAGEM_TEMP,
            avaliacoes_detalhadas=avaliacoes_detalhadas,
        )

        # ==================================================
        # LIMPEZA E FEEDBACK
        # ==================================================
        if os.path.exists(CAMINHO_IMAGEM_TEMP):
            os.remove(CAMINHO_IMAGEM_TEMP)

        mostrar_feedback(page, f"PDF gerado com sucesso: {nome_arquivo}", sucesso=True)
        return nome_arquivo

    except Exception:
        if os.path.exists(CAMINHO_IMAGEM_TEMP):
            os.remove(CAMINHO_IMAGEM_TEMP)

        logger.exception("Erro ao gerar o documento PDF.")
        mostrar_feedback(page, "Erro ao gerar o documento PDF.", sucesso=False)
        return None
