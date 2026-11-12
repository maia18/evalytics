import asyncio
import logging
import tempfile
from pathlib import Path
import flet as ft
from typing import Optional
from datetime import datetime
from database.services.institutions.institutions_service import (
    obter_documentos_da_instituicao_por_ids,
)
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
COLECAO_AVALIACOES = "avaliacoes"


def _gerar_conteudo_pdf(
    medias_validas: dict[int, float],
    nomes_eixos: dict[int, str],
    semestre: str,
    quantidade_avaliacoes: int,
    texto_cursos: str,
    resultados: list[dict],
    eixo_selecionado: int | None,
    nome_arquivo: str,
) -> bytes:
    """Executa consultas e renderização fora do loop da interface."""
    avaliacoes_detalhadas = carregar_avaliacoes_detalhadas(
        resultados, eixo_selecionado=eixo_selecionado
    )
    with tempfile.TemporaryDirectory(prefix="evalytics_pdf_") as diretorio_temp:
        caminho_imagem_temp = Path(diretorio_temp) / "radar_temp.png"
        caminho_pdf_temp = Path(diretorio_temp) / nome_arquivo
        salvar_grafico_radar(medias_validas, nomes_eixos, str(caminho_imagem_temp))
        construir_documento_pdf(
            caminho_arquivo=str(caminho_pdf_temp),
            medias_validas=medias_validas,
            nomes_eixos=nomes_eixos,
            semestre=semestre,
            quantidade_avaliacoes=quantidade_avaliacoes,
            texto_cursos=texto_cursos,
            caminho_imagem_radar=str(caminho_imagem_temp),
            avaliacoes_detalhadas=avaliacoes_detalhadas,
        )
        return caminho_pdf_temp.read_bytes()


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
    for documento in obter_documentos_da_instituicao_por_ids(
        COLECAO_AVALIACOES, ids
    ):
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

async def gerar_pdf_completo(
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
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"relatorio_evalytics_{timestamp}.pdf"

        seletor_arquivos = getattr(page, "file_picker_evidencias", None)
        if seletor_arquivos is None:
            mostrar_feedback(
                page,
                "O seletor para salvar arquivos não está disponível.",
                sucesso=False,
            )
            return None

        # Abre o diálogo antes das consultas ao Firestore e da renderização do PDF.
        caminho_salvo = await seletor_arquivos.save_file(
            dialog_title="Salvar relatório PDF",
            file_name=nome_arquivo,
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["pdf"],
        )

        if not caminho_salvo:
            return None

        conteudo_pdf = await asyncio.to_thread(
            _gerar_conteudo_pdf,
            medias_validas,
            nomes_eixos,
            semestre,
            quantidade_avaliacoes,
            texto_cursos,
            resultados or [],
            eixo_selecionado,
            nome_arquivo,
        )
        await asyncio.to_thread(Path(caminho_salvo).write_bytes, conteudo_pdf)

        # ==================================================
        # FEEDBACK
        # ==================================================
        mostrar_feedback(page, f"PDF salvo com sucesso: {caminho_salvo}", sucesso=True)
        return caminho_salvo

    except Exception:
        logger.exception("Erro ao gerar o documento PDF.")
        mostrar_feedback(page, "Erro ao gerar o documento PDF.", sucesso=False)
        return None
