import json
from pathlib import Path

import flet as ft

from components.core.constants.constants import (
    BORDA,
    CARD,
    COR_PRIMARIA,
    TEXTO_PRINCIPAL,
    TEXTO_SECUNDARIO,
)


def _ler_desenvolvedores() -> list[dict]:
    caminho = (
        Path(__file__).resolve().parents[2]
        / "components"
        / "landing"
        / "data"
        / "desenvolvedores.json"
    )
    try:
        with caminho.open("r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
        return [pessoa for pessoa in dados if pessoa.get("ativo", True)]
    except (OSError, json.JSONDecodeError, TypeError):
        return []


def criar_secao_sobre(page, layout, cores, altura=None):
    """Tela Sobre com conteúdo objetivo nas abas horizontais."""
    modo_escuro = layout.controller.dark_mode
    abas = ("Visão geral", "Recursos", "Desenvolvedores")
    aba_ativa = {"nome": getattr(page, "_sobre_aba_ativa", abas[0])}
    if aba_ativa["nome"] not in abas:
        aba_ativa["nome"] = abas[0]

    botoes_abas: dict[str, ft.Container] = {}
    conteudo = ft.Column(expand=bool(altura), spacing=12)

    def linha_info(titulo: str, descricao: str, icone=None, acao=None) -> ft.Control:
        controles = []
        if icone is not None:
            controles.append(ft.Icon(icone, size=17, color=COR_PRIMARIA))
        controles.append(
            ft.Column(
                expand=True,
                spacing=2,
                controls=[
                    ft.Text(
                        titulo,
                        size=12,
                        weight=ft.FontWeight.W_600,
                        color=cores[TEXTO_PRINCIPAL],
                    ),
                    ft.Text(
                        descricao,
                        size=10,
                        color=cores[TEXTO_SECUNDARIO],
                    ),
                ],
            )
        )
        if acao is not None:
            controles.append(acao)

        return ft.Container(
            padding=ft.Padding.symmetric(horizontal=8, vertical=9),
            border=ft.Border(bottom=ft.BorderSide(1, cores[BORDA])),
            content=ft.Row(
                spacing=11,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=controles,
            ),
        )

    recursos = (
        (
            "Avaliações institucionais",
            "Organize avaliações por curso, semestre e eixo.",
            ft.Icons.RATE_REVIEW_OUTLINED,
        ),
        (
            "Indicadores",
            "Acompanhe respostas e médias por curso e eixo.",
            ft.Icons.INSERT_CHART_OUTLINED,
        ),
        (
            "Gestão de cursos",
            "Mantenha cursos, departamentos e status organizados.",
            ft.Icons.SCHOOL_OUTLINED,
        ),
        (
            "Relatórios",
            "Consulte resultados e exporte arquivos em PDF ou CSV.",
            ft.Icons.DOWNLOAD_OUTLINED,
        ),
    )
    repositorio_evalytics = "https://github.com/maia18/evalytics"

    def cartao_etapa(numero: str, titulo: str, descricao: str) -> ft.Control:
        return ft.Container(
            col={"xs": 12, "sm": 4},
            height=120,
            padding=12,
            border=ft.Border.all(1, cores[BORDA]),
            border_radius=10,
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.CircleAvatar(
                        radius=14,
                        bgcolor="#302747" if modo_escuro else "#EEE9FB",
                        content=ft.Text(
                            numero,
                            size=11,
                            weight=ft.FontWeight.W_700,
                            color="#B69CFF" if modo_escuro else COR_PRIMARIA,
                        ),
                    ),
                    ft.Text(
                        titulo,
                        size=12,
                        weight=ft.FontWeight.W_600,
                        color=cores[TEXTO_PRINCIPAL],
                    ),
                    ft.Text(
                        descricao,
                        size=10,
                        color=cores[TEXTO_SECUNDARIO],
                    ),
                ],
            ),
        )

    def linha_desenvolvedor(pessoa: dict) -> ft.Control:
        nome = str(pessoa.get("nome") or "Nome não informado")
        funcao = str(pessoa.get("funcao") or "Colaborador")
        github = str(pessoa.get("github") or "")
        iniciais = "".join(parte[0] for parte in nome.split()[:2] if parte)
        botao_github = (
            ft.TextButton(
                "GitHub",
                icon=ft.Icons.OPEN_IN_NEW,
                on_click=lambda e, url=github: page.launch_url(url)
                if url.startswith("https://")
                else None,
            )
            if github
            else None
        )
        return ft.Container(
            padding=ft.Padding.symmetric(horizontal=8, vertical=9),
            border=ft.Border(bottom=ft.BorderSide(1, cores[BORDA])),
            content=ft.Row(
                spacing=11,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.CircleAvatar(
                        radius=17,
                        bgcolor="#302747" if modo_escuro else "#EEE9FB",
                        content=ft.Text(
                            iniciais,
                            size=11,
                            weight=ft.FontWeight.W_700,
                            color="#B69CFF" if modo_escuro else COR_PRIMARIA,
                        ),
                    ),
                    ft.Column(
                        expand=True,
                        spacing=2,
                        controls=[
                            ft.Text(
                                nome,
                                size=12,
                                weight=ft.FontWeight.W_600,
                                color=cores[TEXTO_PRINCIPAL],
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            ft.Text(funcao, size=10, color=cores[TEXTO_SECUNDARIO]),
                        ],
                    ),
                    *([botao_github] if botao_github else []),
                ],
            ),
        )

    desenvolvedores = _ler_desenvolvedores()

    def criar_conteudo(aba: str) -> list[ft.Control]:
        if aba == "Recursos":
            return [
                linha_info(titulo, descricao, icone)
                for titulo, descricao, icone in recursos
            ]
        if aba == "Desenvolvedores":
            if not desenvolvedores:
                return [
                    ft.Text(
                        "A equipe ainda não foi cadastrada.",
                        size=11,
                        color=cores[TEXTO_SECUNDARIO],
                    )
                ]
            return [linha_desenvolvedor(pessoa) for pessoa in desenvolvedores]
        return [
            ft.Text(
                "Da avaliação institucional à análise dos resultados",
                size=17,
                weight=ft.FontWeight.W_700,
                color=cores[TEXTO_PRINCIPAL],
            ),
            ft.Text(
                "O Evalytics organiza informações de avaliação para apoiar a leitura dos resultados acadêmicos.",
                size=11,
                color=cores[TEXTO_SECUNDARIO],
            ),
            ft.Text(
                "Fluxo de uso",
                size=13,
                weight=ft.FontWeight.W_600,
                color=cores[TEXTO_PRINCIPAL],
            ),
            ft.ResponsiveRow(
                spacing=10,
                run_spacing=10,
                controls=[
                    cartao_etapa(
                        "1",
                        "Organize",
                        "Selecione o curso e o semestre da avaliação.",
                    ),
                    cartao_etapa(
                        "2",
                        "Registre",
                        "Responda aos indicadores organizados por eixo.",
                    ),
                    cartao_etapa(
                        "3",
                        "Acompanhe",
                        "Consulte os resultados consolidados e exporte relatórios.",
                    ),
                ],
            ),
            linha_info(
                "Repositório do Evalytics",
                "Acesse o código-fonte e acompanhe o desenvolvimento do projeto.",
                ft.Icons.CODE,
                ft.TextButton(
                    "Abrir GitHub",
                    icon=ft.Icons.OPEN_IN_NEW,
                    on_click=lambda e: page.launch_url(repositorio_evalytics),
                ),
            ),
        ]

    def selecionar_aba(nome: str, atualizar: bool = True) -> None:
        aba_ativa["nome"] = nome
        page._sobre_aba_ativa = nome
        conteudo.controls = criar_conteudo(nome)
        cor_ativa = "#B69CFF" if modo_escuro else COR_PRIMARIA
        for rotulo, botao in botoes_abas.items():
            ativo = rotulo == nome
            botao.border = ft.Border(
                bottom=ft.BorderSide(2, COR_PRIMARIA if ativo else "#00000000")
            )
            botao.content.color = cor_ativa if ativo else cores[TEXTO_SECUNDARIO]
            botao.content.weight = (
                ft.FontWeight.W_600 if ativo else ft.FontWeight.W_500
            )
        if atualizar:
            page.update()

    for nome in abas:
        botao = ft.Container(
            padding=ft.Padding.symmetric(horizontal=10, vertical=9),
            border=ft.Border(bottom=ft.BorderSide(2, "#00000000")),
            ink=True,
            on_click=lambda e, aba=nome: selecionar_aba(aba),
            content=ft.Text(
                nome,
                size=12,
                color=cores[TEXTO_SECUNDARIO],
            ),
        )
        botoes_abas[nome] = botao

    conteudo.controls = criar_conteudo(aba_ativa["nome"])
    selecionar_aba(aba_ativa["nome"], atualizar=False)

    return ft.Container(
        height=altura,
        expand=False,
        padding=ft.Padding.symmetric(horizontal=20, vertical=16),
        border=ft.Border.all(1, cores[BORDA]),
        border_radius=12,
        bgcolor=cores[CARD],
        content=ft.Column(
            expand=bool(altura),
            spacing=12,
            controls=[
                ft.Row(spacing=8, controls=list(botoes_abas.values())),
                ft.Divider(height=1, color=cores[BORDA]),
                conteudo,
            ],
        ),
    )
