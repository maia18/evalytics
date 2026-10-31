import asyncio
import flet as ft
from components.landing.palette import (
    SURFACE,
    BORDER,
    MUTED,
    ACCENT,
    CMD_TEXT,
)

def criar_painel_hero(page: ft.Page = None) -> ft.Container:
    """
    Cria a caixa de terminal/demonstração simulando o fluxo de comandos da plataforma.
    Inclui botão interativo para copiar o conteúdo da prévia.
    """

    texto_previa = (
        "$ evalytics login\n"
        "$ evalytics relatorio --curso [CURSO] --semestre [SEMESTRE]\n"
        "✓ [N] respostas consolidadas por eixo\n"
        "PDF e CSV prontos para exportar."
    )

    btn_copiar = ft.TextButton(
        content=ft.Text(
            "Copiar prévia",
            size=11,
            color=MUTED,
            font_family="monospace",
        ),
        style=ft.ButtonStyle(
            overlay_color=ft.Colors.TRANSPARENT,
            padding=ft.Padding.symmetric(horizontal=8, vertical=4),
        ),
    )

    async def copiar_texto(e):
        if page:
            await page.set_clipboard(texto_previa)
            btn_copiar.content.value = "✓ Prévia copiada"
            btn_copiar.content.color = ACCENT
            btn_copiar.update()

            await asyncio.sleep(2)
            btn_copiar.content.value = "Copiar prévia"
            btn_copiar.content.color = MUTED
            btn_copiar.update()

    btn_copiar.on_click = copiar_texto

    def _linha_cmd(comando: str) -> ft.Row:
        return ft.Row(
            spacing=4,
            tight=True,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    "$",
                    size=12,
                    color=MUTED,
                    font_family="monospace",
                ),
                ft.Text(
                    comando,
                    size=12,
                    color=CMD_TEXT,
                    font_family="monospace",
                ),
            ],
        )

    return ft.Container(
        width=480,
        bgcolor=SURFACE,
        border=ft.Border.all(1, BORDER),
        border_radius=10,
        padding=ft.Padding.only(left=22, right=22, top=16, bottom=18),
        content=ft.Column(
            spacing=6,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            controls=[
                # Cabeçalho do terminal com botão copiar
                ft.Row(
                    alignment=ft.MainAxisAlignment.END,
                    controls=[btn_copiar],
                ),

                # Linha 1: $ evalytics login
                _linha_cmd("evalytics login"),

                # Linha 2: $ evalytics relatorio --curso [CURSO] --semestre [SEMESTRE]
                _linha_cmd("evalytics relatorio --curso [CURSO] --semestre [SEMESTRE]"),

                # Linha 3: ✓ [N] respostas consolidadas por eixo
                ft.Text(
                    "✓ [N] respostas consolidadas por eixo",
                    size=12,
                    color=ACCENT,
                    font_family="monospace",
                ),

                # Linha 4: PDF e CSV prontos para exportar.
                ft.Text(
                    "PDF e CSV prontos para exportar.",
                    size=12,
                    color=MUTED,
                    font_family="monospace",
                ),
            ],
        ),
    )
