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

async def exportar_csv(page: ft.Page, resultados: Optional[list[dict]] = None) -> None:
    """Exporta as respostas reais das avaliações atualmente selecionadas pelos filtros."""
    
    if resultados is None:
        resultados = []

    if not resultados:
        mostrar_feedback(page, "Não existem dados para exportar.", sucesso=False)
        return

    nome_arquivo = Path(gerar_nome_arquivo()).name

    try:
        dados_exportacao = preparar_dados_csv(resultados)

        if len(dados_exportacao) <= 1:
            mostrar_feedback(page, "Não existem respostas para exportar.", sucesso=False)
            return

        buffer = io.StringIO(newline="")
        escritor = csv.writer(buffer, delimiter=";")
        escritor.writerows(dados_exportacao)
        conteudo_csv = buffer.getvalue().encode("utf-8-sig")

        seletor_arquivos = getattr(page, "file_picker_evidencias", None)
        if seletor_arquivos is None:
            mostrar_feedback(
                page,
                "O seletor para salvar arquivos não está disponível.",
                sucesso=False,
            )
            return

        caminho_salvo = await seletor_arquivos.save_file(
            dialog_title="Salvar exportação CSV",
            file_name=nome_arquivo,
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["csv"],
            src_bytes=conteudo_csv,
        )

        if not caminho_salvo:
            return

        mostrar_feedback(
            page, 
            f"Arquivo CSV exportado com sucesso: {caminho_salvo}", 
            sucesso=True
        )

    except Exception as erro:
        logger.exception("Erro ao exportar CSV.")
        mostrar_feedback(page, f"Erro ao exportar: {erro}", sucesso=False)
