import os
import logging
import flet as ft
from pathlib import Path
from components.core.constants.constants import (
    COR_PRIMARIA,
    TEXTO_PRINCIPAL,
    TEXTO_SECUNDARIO,
    BORDA,
    CARD,
)

logger = logging.getLogger(__name__)

# ==========================================================
# CONFIGURAÇÕES
# ==========================================================

EXTENSOES_PERMITIDAS = {
    "png", "jpg", "jpeg", "webp",
    "pdf",
    "doc", "docx",
    "xls", "xlsx",
    "ppt", "pptx",
    "txt", "csv",
    "odt", "ods", "odp",
}

TAMANHO_MAXIMO_ARQUIVO = 10 * 1024 * 1024
QUANTIDADE_MAXIMA_ARQUIVOS = 20


def formatar_tamanho(tamanho: int) -> str:
    """Formata o tamanho do arquivo."""

    if tamanho < 1024:
        return f"{tamanho} B"

    if tamanho < 1024**2:
        return f"{tamanho / 1024:.1f} KB"

    return f"{tamanho / (1024**2):.1f} MB"


def criar_card_pergunta(
    page: ft.Page,
    indicador: dict,
    estado: dict,
    rodape: ft.Container,
    cores: dict[str, str],
) -> ft.Container:
    """Constrói o cartão do indicador e suas evidências."""

    # ==========================================================
    # DADOS DO INDICADOR
    # ==========================================================

    indicador_id = str(indicador.get("id", ""))
    titulo_ind = indicador.get("titulo", "Indicador")
    criterios = indicador.get("criterios", {})

    estado.setdefault("respostas", {})
    estado.setdefault("justificativas", {})
    estado.setdefault("anexos", {})
    
    # ==========================================================
    # DADOS DO INDICADOR E ESTADO COMPARTILHADO
    # ==========================================================

    indicador_id = indicador.get("id")

    if indicador_id is None:
        raise ValueError("O indicador precisa possuir um ID.")

    # Padroniza a chave para evitar divergências entre int e str.
    indicador_id = str(indicador_id)

    titulo_ind = indicador.get("titulo", "Indicador")
    criterios = indicador.get("criterios", {})

    estado.setdefault("respostas", {})
    estado.setdefault("justificativas", {})
    estado.setdefault("anexos", {})

    # Normaliza chaves antigas para string, se existirem.
    anexos_estado = estado["anexos"]

    if indicador_id not in anexos_estado:
        chave_antiga = next(
            (
                chave
                for chave in anexos_estado
                if str(chave) == indicador_id
            ),
            None,
        )

        anexos_estado[indicador_id] = (
            anexos_estado.pop(chave_antiga)
            if chave_antiga is not None
            else []
        )

    anexos = anexos_estado[indicador_id]

    justificativa_inicial = estado["justificativas"].get(
        indicador_id, ""
    )

    valor_inicial = str(
        estado["respostas"].get(indicador_id, "")
    )

    # ==========================================================
    # RESPOSTA
    # ==========================================================

    def ao_mudar_opcao(e: ft.ControlEvent) -> None:
        if indicador_id and e.control.value is not None:
            estado["respostas"][indicador_id] = int(
                e.control.value
            )

    opcoes_radio = []

    for chave, texto_criterio in sorted(
        criterios.items(),
        key=lambda item: str(item[0]),
    ):
        opcoes_radio.append(
            ft.Container(
                padding=ft.Padding.symmetric(vertical=0),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Radio(
                            value=str(chave),
                            active_color=cores[COR_PRIMARIA],
                        ),
                        ft.Container(
                            expand=True,
                            padding=ft.Padding.only(
                                top=3,
                                right=4,
                            ),
                            content=ft.Text(
                                f"Nível {chave}: {texto_criterio}",
                                color=cores[TEXTO_PRINCIPAL],
                                size=13,
                            ),
                        ),
                    ],
                ),
            )
        )

    grupo_radio = ft.RadioGroup(
        content=ft.Column(
            spacing=0,
            controls=opcoes_radio,
        ),
        value=valor_inicial,
        on_change=ao_mudar_opcao,
    )

    area_criterios = ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        spacing=0,
        controls=[grupo_radio],
    )

    # ==========================================================
    # LISTA DE ANEXOS
    # ==========================================================

    lista_anexos = ft.Column(
        spacing=4,
        controls=[],
    )

    mensagem_anexos = ft.Text(
        f"{len(anexos)} de {QUANTIDADE_MAXIMA_ARQUIVOS} arquivos anexados"
        if anexos
        else "",
        size=12,
        color=cores[TEXTO_PRINCIPAL],
        visible=bool(anexos),
    )

    def atualizar_lista_anexos(
        atualizar_pagina: bool = True,
    ) -> None:
        lista_anexos.controls.clear()

        for anexo in anexos:
            nome = anexo["nome"]
            tamanho = anexo["tamanho"]
            caminho = anexo["caminho"]

            linha = ft.Row(
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(
                        ft.Icons.ATTACH_FILE,
                        size=18,
                        color=cores[COR_PRIMARIA],
                    ),
                    ft.Column(
                        expand=True,
                        spacing=1,
                        controls=[
                            ft.Text(
                                nome,
                                size=12,
                                color=cores[TEXTO_PRINCIPAL],
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            ft.Text(
                                formatar_tamanho(tamanho),
                                size=10,
                                color="onSurfaceVariant",
                            ),
                        ],
                    ),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        icon_size=17,
                        tooltip="Remover anexo",
                        on_click=lambda e, p=caminho: remover_anexo(p),
                    ),
                ],
            )

            lista_anexos.controls.append(
                ft.Container(
                    padding=ft.Padding.symmetric(
                        horizontal=8,
                        vertical=4,
                    ),
                    border=ft.Border.all(
                        1,
                        cores[BORDA],
                    ),
                    border_radius=8,
                    content=linha,
                )
            )

        mensagem_anexos.value = (
            f"{len(anexos)} de {QUANTIDADE_MAXIMA_ARQUIVOS} "
            "arquivos anexados"
            if anexos
            else ""
        )
        mensagem_anexos.visible = bool(anexos)

        if atualizar_pagina:
            page.update()

    def remover_anexo(caminho: str) -> None:
        anexos[:] = [
            anexo
            for anexo in anexos
            if anexo["caminho"] != caminho
        ]

        atualizar_lista_anexos()

    # ==========================================================
    # FILE PICKER COMPARTILHADO
    # ==========================================================

    seletor_arquivos = getattr(
        page,
        "file_picker_evidencias",
        None,
    )

    if seletor_arquivos is None:
        logger.error(
            "FilePicker não registrado na inicialização da página."
        )
        mensagem_anexos.value = (
            "O seletor de arquivos não foi inicializado."
        )
        mensagem_anexos.visible = True

    async def abrir_seletor(e):
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
        
    botao_anexar_evidencias = ft.OutlinedButton(
        content=ft.Row(
            tight=True,
            spacing=8,
            controls=[
                ft.Icon(ft.Icons.ATTACH_FILE),
                ft.Text("Anexar evidências"),
            ],
        ),
        on_click=abrir_seletor,
        style=ft.ButtonStyle(
            color=cores[TEXTO_PRINCIPAL],
            padding=ft.Padding.symmetric(horizontal=10, vertical=0),
            side=ft.BorderSide(
                1,
                cores[BORDA],
            ),
        ),
    )

    # ==========================================================
    # JUSTIFICATIVA
    # ==========================================================

    campo_justificativa = ft.TextField(
        label="Justificativa",
        hint_text="Escreva um contexto para esta resposta (opcional).",
        value=justificativa_inicial,
        visible=True,
        multiline=True,
        min_lines=1,
        max_lines=2,
        border_color=cores[BORDA],
        text_size=13,
        content_padding=10,
        on_change=lambda e: estado["justificativas"].__setitem__(
            indicador_id,
            e.control.value,
        ),
    )
    acoes_evidencia_justificativa = ft.Row(
        spacing=8,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            botao_anexar_evidencias,
            ft.Container(
                expand=True,
                content=campo_justificativa,
            ),
        ],
    )

    # ==========================================================
    # CABEÇALHO
    # ==========================================================

    cabecalho_card = [
        ft.Text(
            titulo_ind,
            size=19,
            weight="bold",
            color=cores[TEXTO_PRINCIPAL],
        ),
    ]

    descricao_texto = indicador.get("descricao", "")

    if descricao_texto:
        cabecalho_card.append(
            ft.Text(
                descricao_texto,
                size=13,
                color="onSurfaceVariant",
                italic=True,
            )
        )

    cabecalho_card.append(
        ft.Divider(
            height=1,
            color=cores[BORDA],
        )
    )

    # Renderiza os anexos que já estavam no estado.
    atualizar_lista_anexos(atualizar_pagina=False)

    # ==========================================================
    # CARTÃO
    # ==========================================================

    return ft.Container(
        bgcolor=cores[CARD],
        padding=14,
        border_radius=12,
        border=ft.Border.all(
            1,
            cores[BORDA],
        ),
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=15,
            color=ft.Colors.BLACK12,
            offset=ft.Offset(0, 4),
        ),
        expand=True,
        content=ft.Column(
            spacing=4,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                *cabecalho_card,
                area_criterios,
                ft.Divider(
                    height=1,
                    color=cores[BORDA],
                ),
                ft.Column(
                    spacing=6,
                    controls=[
                        ft.Text(
                            "Complementos da resposta",
                            size=11,
                            color=cores[TEXTO_SECUNDARIO],
                            weight=ft.FontWeight.W_600,
                        ),
                        acoes_evidencia_justificativa,
                    ],
                ),
                mensagem_anexos,
                lista_anexos,
                ft.Container(
                    padding=ft.Padding.only(top=3),
                    content=rodape,
                ),
            ],
        ),
    )
