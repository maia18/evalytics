import flet as ft
import json
from typing import Callable
from pathlib import Path

from components.landing.header.logo import criar_logo
from components.landing.palette import (
    PAGE,
    SURFACE,
    BORDER,
    TEXT,
    MUTED,
    ROXO,
    ROXO_CLARO,
    TEXT_BRIGHT,
    MAX_CONTENT_WIDTH,
)


def ViewDesenvolvedores(
    page: ft.Page,
    mudar_tela: Callable[[str], None],
) -> ft.View:
    """Página pública de apresentação da equipe do Evalytics."""
    arquivo_desenvolvedores = Path(__file__).with_name("data") / "desenvolvedores.json"
    try:
        with arquivo_desenvolvedores.open("r", encoding="utf-8") as arquivo:
            dados_desenvolvedores = json.load(arquivo)
    except (OSError, json.JSONDecodeError):
        dados_desenvolvedores = []

    if not isinstance(dados_desenvolvedores, list):
        dados_desenvolvedores = []
    desenvolvedores = sorted(
        (
            pessoa
            for pessoa in dados_desenvolvedores
            if isinstance(pessoa, dict) and pessoa.get("ativo", True)
        ),
        key=lambda pessoa: pessoa.get("ordem", 999),
    )

    def criar_card_desenvolvedor(pessoa: dict) -> ft.Container:
        nome = str(pessoa.get("nome", "")).strip()
        funcao = str(pessoa.get("funcao", "")).strip()
        github = str(pessoa.get("github", "")).strip()
        iniciais = "".join(parte[0] for parte in nome.split()[:2]).upper() or "?"
        detalhes = [
            ft.Text(nome.title(), size=16, weight=ft.FontWeight.W_600, color=TEXT),
            ft.Container(
                padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                bgcolor=ft.Colors.with_opacity(0.12, ROXO_CLARO),
                border_radius=14,
                content=ft.Text(funcao, size=11, weight=ft.FontWeight.W_600, color=ROXO_CLARO),
            ),
        ]
        if github.startswith("https://github.com/"):
            detalhes.append(
                ft.TextButton(
                    "Ver perfil no GitHub",
                    icon=ft.Icons.OPEN_IN_NEW,
                    on_click=lambda e, url=github: page.launch_url(url),
                    style=ft.ButtonStyle(color=MUTED),
                )
            )
        return ft.Container(
            col={"xs": 12, "sm": 12, "md": 6, "lg": 6},
            padding=22,
            bgcolor=SURFACE,
            border=ft.Border.all(1, BORDER),
            border_radius=14,
            content=ft.Row(
                spacing=16,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.CircleAvatar(
                        radius=26,
                        bgcolor=ft.Colors.with_opacity(0.16, ROXO_CLARO),
                        content=ft.Text(iniciais, size=15, weight=ft.FontWeight.W_700, color=ROXO_CLARO),
                    ),
                    ft.Column(
                        expand=True,
                        spacing=5,
                        controls=detalhes,
                    ),
                ],
            ),
        )

    lista_equipe = ft.ResponsiveRow(
        columns=12,
        spacing=16,
        run_spacing=16,
        controls=[criar_card_desenvolvedor(pessoa) for pessoa in desenvolvedores],
    )
    if not desenvolvedores:
        lista_equipe.controls.append(
            ft.Container(
                col=12,
                padding=24,
                bgcolor=SURFACE,
                border=ft.Border.all(1, BORDER),
                border_radius=14,
                alignment=ft.Alignment.CENTER,
                content=ft.Text(
                    "As informações da equipe estarão disponíveis aqui em breve.",
                    color=MUTED,
                    size=13,
                    text_align=ft.TextAlign.CENTER,
                ),
            )
        )

    header = ft.Container(
        bgcolor=PAGE,
        border=ft.Border(bottom=ft.BorderSide(1, BORDER)),
        padding=ft.Padding.symmetric(horizontal=24, vertical=10),
        alignment=ft.Alignment.CENTER,
        content=ft.Container(
            width=MAX_CONTENT_WIDTH,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    criar_logo(ir_para_inicio=lambda e: mudar_tela("/")),
                    ft.Row(
                        spacing=10,
                        controls=[
                            ft.TextButton(
                                "Início",
                                icon=ft.Icons.ARROW_BACK,
                                on_click=lambda e: mudar_tela("/"),
                                style=ft.ButtonStyle(color=MUTED),
                            ),
                            ft.ElevatedButton(
                                "Acessar plataforma",
                                bgcolor=ROXO,
                                color=TEXT_BRIGHT,
                                height=38,
                                on_click=lambda e: mudar_tela("/login"),
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                    padding=ft.Padding.symmetric(horizontal=18),
                                ),
                            ),
                        ],
                    ),
                ],
            ),
        ),
    )

    conteudo = ft.Container(
        alignment=ft.Alignment.CENTER,
        padding=ft.Padding.symmetric(horizontal=24, vertical=64),
        content=ft.Container(
            width=760,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=24,
                controls=[
                    ft.Container(
                        padding=ft.Padding.symmetric(horizontal=12, vertical=5),
                        bgcolor=ft.Colors.with_opacity(0.10, ROXO_CLARO),
                        border=ft.Border.all(1, ft.Colors.with_opacity(0.32, ROXO_CLARO)),
                        border_radius=18,
                        content=ft.Text(
                            "EQUIPE DE DESENVOLVIMENTO",
                            size=10,
                            weight=ft.FontWeight.W_700,
                            color=ROXO_CLARO,
                            font_family="monospace",
                        ),
                    ),
                    ft.Text(
                        "Quem constrói o Evalytics",
                        size=34,
                        weight=ft.FontWeight.W_700,
                        color=TEXT,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(
                        width=620,
                        content=ft.Text(
                            "Conheça as pessoas que desenvolvem a plataforma e explore seus perfis profissionais.",
                            size=14,
                            color=MUTED,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ),
                    lista_equipe,
                ],
            ),
        ),
    )

    return ft.View(
        route="/desenvolvedores",
        bgcolor=PAGE,
        padding=0,
        spacing=0,
        scroll=ft.ScrollMode.AUTO,
        controls=[header, conteudo],
    )
