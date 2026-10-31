import asyncio
import flet as ft
from components.landing.palette import (
    SURFACE,
    BORDER,
    MUTED,
    ROXO_CLARO,
    VERDE,
    ROSA,
    LARANJA,
    CMD_TEXT,
)

def criar_painel_hero(page: ft.Page = None) -> ft.Container:
    """
    Cria a caixa de terminal/demonstração simulando o fluxo de comandos da plataforma.
    Inclui botões coloridos de janela de terminal e botão interativo para copiar o código.
    """

    texto_previa = (
        "$ evalytics login\n"
        "$ evalytics relatorio --curso [CURSO] --semestre [SEMESTRE]\n"
        "✓ [N] respostas consolidadas por eixo\n"
        "PDF e CSV prontos para exportar."
    )

    btn_copiar = ft.TextButton(
        content=ft.Row(
            spacing=4,
            tight=True,
            controls=[
                ft.Icon(ft.Icons.COPY_ROUNDED, size=12, color=MUTED),
                ft.Text(
                    "Copiar prévia",
                    size=11,
                    color=MUTED,
                    font_family="monospace",
                ),
            ],
        ),
        style=ft.ButtonStyle(
            overlay_color=ft.Colors.TRANSPARENT,
            padding=ft.Padding.symmetric(horizontal=8, vertical=4),
        ),
    )

    async def copiar_texto(e):
        if page:
            try:
                if hasattr(page, "clipboard"):
                    await page.clipboard.set(texto_previa)
                elif hasattr(page, "set_clipboard"):
                    await page.set_clipboard(texto_previa)
            except Exception:
                pass

            btn_copiar.content.controls[0].name = ft.Icons.CHECK_ROUNDED
            btn_copiar.content.controls[0].color = VERDE
            btn_copiar.content.controls[1].value = "Prévia copiada"
            btn_copiar.content.controls[1].color = VERDE
            page.update()

            await asyncio.sleep(2)
            btn_copiar.content.controls[0].name = ft.Icons.COPY_ROUNDED
            btn_copiar.content.controls[0].color = MUTED
            btn_copiar.content.controls[1].value = "Copiar prévia"
            btn_copiar.content.controls[1].color = MUTED
            page.update()

    btn_copiar.on_click = copiar_texto

    def _linha_cmd(comando: str) -> ft.Row:
        return ft.Row(
            spacing=6,
            tight=True,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    "$",
                    size=12,
                    color=ROXO_CLARO,
                    font_family="monospace",
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    comando,
                    size=12,
                    color=CMD_TEXT,
                    font_family="monospace",
                ),
            ],
        )

    # Bolinhas decorativas do terminal
    pontos_janela = ft.Row(
        spacing=6,
        tight=True,
        controls=[
            ft.Container(width=10, height=10, border_radius=5, bgcolor=ROSA),
            ft.Container(width=10, height=10, border_radius=5, bgcolor=LARANJA),
            ft.Container(width=10, height=10, border_radius=5, bgcolor=VERDE),
        ],
    )

    return ft.Container(
        width=500,
        bgcolor=SURFACE,
        border=ft.Border.all(1, BORDER),
        border_radius=12,
        padding=ft.Padding.only(left=20, right=20, top=14, bottom=18),
        content=ft.Column(
            spacing=8,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            controls=[
                # Barra superior do terminal
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        pontos_janela,
                        btn_copiar,
                    ],
                ),

                ft.Divider(height=1, color=BORDER),

                # Linha 1: $ evalytics login
                _linha_cmd("evalytics login"),

                # Linha 2: $ evalytics relatorio --curso [CURSO] --semestre [SEMESTRE]
                _linha_cmd("evalytics relatorio --curso [CURSO] --semestre [SEMESTRE]"),

                # Linha 3: ✓ [N] respostas consolidadas por eixo
                ft.Text(
                    "✓ [N] respostas consolidadas por eixo",
                    size=12,
                    color=VERDE,
                    font_family="monospace",
                    weight=ft.FontWeight.W_600,
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
