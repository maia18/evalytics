import logging
import os
from pathlib import Path

import flet as ft

from models.formulario.widgets.evidencias_config import (
    EXTENSOES_PERMITIDAS,
    QUANTIDADE_MAXIMA_ARQUIVOS,
    TAMANHO_MAXIMO_ARQUIVO,
)

logger = logging.getLogger(__name__)


async def selecionar_evidencias(
    page,
    indicador_id,
    anexos,
    mensagem_anexos,
    atualizar_lista_anexos,
):
    seletor_arquivos = getattr(
        page,
        "file_picker_evidencias",
        None,
    )

    if seletor_arquivos is None:
        logger.error("FilePicker não inicializado.")
        mensagem_anexos.value = (
            "O seletor de arquivos não está disponível."
        )
        mensagem_anexos.visible = True
        page.update()
        return

    logger.info(
        "Abrindo seletor para o indicador %s.",
        indicador_id,
    )

    try:
        arquivos = await seletor_arquivos.pick_files(
            allow_multiple=True,
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=sorted(EXTENSOES_PERMITIDAS),
            dialog_title="Selecionar evidências",
        )

        logger.info(
            "Indicador %s: %s arquivo(s) selecionado(s).",
            indicador_id,
            len(arquivos or []),
        )

        if not arquivos:
            return

        caminhos_existentes = {
            anexo["caminho"]
            for anexo in anexos
        }

        for arquivo in arquivos:
            nome = arquivo.name
            caminho = arquivo.path

            if not caminho:
                logger.warning(
                    "Arquivo sem caminho local: %s",
                    nome,
                )
                continue

            caminho = os.path.abspath(caminho)
            extensao = Path(nome).suffix.lower().lstrip(".")

            if extensao not in EXTENSOES_PERMITIDAS:
                continue

            if caminho in caminhos_existentes:
                continue

            if len(anexos) >= QUANTIDADE_MAXIMA_ARQUIVOS:
                mensagem_anexos.value = (
                    f"O limite é de "
                    f"{QUANTIDADE_MAXIMA_ARQUIVOS} arquivos."
                )
                break

            try:
                tamanho = os.path.getsize(caminho)
            except OSError:
                logger.exception(
                    "Não foi possível acessar %s.",
                    nome,
                )
                continue

            if tamanho <= 0:
                mensagem_anexos.value = f"{nome} está vazio."
                continue

            if tamanho > TAMANHO_MAXIMO_ARQUIVO:
                mensagem_anexos.value = (
                    f"{nome} excede o limite de 10 MB."
                )
                continue

            anexos.append(
                {
                    "nome": Path(caminho).name,
                    "caminho": caminho,
                    "tamanho": tamanho,
                    "extensao": extensao,
                }
            )

            caminhos_existentes.add(caminho)

        atualizar_lista_anexos()

    except Exception:
        logger.exception(
            "Falha ao selecionar evidências do indicador %s.",
            indicador_id,
        )
        mensagem_anexos.value = (
            "Não foi possível selecionar os arquivos."
        )
        mensagem_anexos.visible = True
        page.update()
    
