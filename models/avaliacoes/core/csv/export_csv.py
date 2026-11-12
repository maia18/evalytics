import asyncio
import csv
import io
import logging
from pathlib import Path
import flet as ft
from typing import Optional
from models.avaliacoes.core.feedback import mostrar_feedback
from models.avaliacoes.core.filename_generator import gerar_nome_arquivo
from .csv_data_service import preparar_dados_csv

logger = logging.getLogger(__name__)


def _montar_conteudo_csv(resultados: list[dict]) -> bytes:
    dados_exportacao = preparar_dados_csv(resultados)
    if len(dados_exportacao) <= 1:
        return b""
    buffer = io.StringIO(newline="")
    csv.writer(buffer, delimiter=";").writerows(dados_exportacao)
    return buffer.getvalue().encode("utf-8-sig")

async def exportar_csv(page: ft.Page, resultados: Optional[list[dict]] = None) -> None:
    """Exporta as respostas reais das avaliações atualmente selecionadas pelos filtros."""
    
    if resultados is None:
        resultados = []

    if not resultados:
        mostrar_feedback(page, "Não existem dados para exportar.", sucesso=False)
        return

    nome_arquivo = Path(gerar_nome_arquivo()).name

    try:
        seletor_arquivos = getattr(page, "file_picker_evidencias", None)
        if seletor_arquivos is None:
            mostrar_feedback(
                page,
                "O seletor para salvar arquivos não está disponível.",
                sucesso=False,
            )
            return

        # Mostra o seletor imediatamente; consultas e montagem ficam em worker.
        caminho_salvo = await seletor_arquivos.save_file(
            dialog_title="Salvar exportação CSV",
            file_name=nome_arquivo,
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["csv"],
        )

        if not caminho_salvo:
            return

        conteudo_csv = await asyncio.to_thread(_montar_conteudo_csv, resultados)
        if not conteudo_csv:
            mostrar_feedback(page, "Não existem respostas para exportar.", sucesso=False)
            return
        await asyncio.to_thread(Path(caminho_salvo).write_bytes, conteudo_csv)

        mostrar_feedback(
            page, 
            f"Arquivo CSV exportado com sucesso: {caminho_salvo}", 
            sucesso=True
        )

    except Exception as erro:
        logger.exception("Erro ao exportar CSV.")
        mostrar_feedback(page, f"Erro ao exportar: {erro}", sucesso=False)
