import flet as ft
from typing import Callable, Optional
from components.landing.palette import (
    PAGE,
    SURFACE,
    SURFACE_ALT,
    BORDER,
    BORDER_STRONG,
    TEXT,
    MUTED,
    ROXO,
    ROXO_CLARO,
    ROSA,
    CIANO,
    VERDE,
    LARANJA,
    MAX_CONTENT_WIDTH,
)
from database.indicadores import INDICADORES

# Nomes oficiais dos 3 eixos do SINAES/MEC no Evalytics
NOMES_EIXOS = {
    1: "Eixo 1 — Organização Didático-Pedagógica",
    2: "Eixo 2 — Corpo Docente e Tutorial",
    3: "Eixo 3 — Infraestrutura",
}

CORES_EIXOS = {
    1: ROXO_CLARO,
    2: CIANO,
    3: VERDE,
}

CORES_CONCEITOS = {
    "1": ROSA,
    "2": LARANJA,
    "3": CIANO,
    "4": ROXO_CLARO,
    "5": VERDE,
}

ROTULOS_CONCEITOS = {
    "1": "Critério 1 — Não implantado / Insatisfatório",
    "2": "Critério 2 — Parcialmente implantado / Limitado",
    "3": "Critério 3 — Implantado / Adequado",
    "4": "Critério 4 — Muito bom / Evidências claras",
    "5": "Critério 5 — Excelente / Práticas inovadoras",
}

def ViewIndicadores(
    page: ft.Page,
    mudar_tela: Callable[[str], None],
) -> ft.View:
    """View pública dedicada para apresentação e consulta dos 58 Indicadores Institucionais nos 3 Eixos."""

    filtro_eixo_atual = 0  # 0 significa todos
    termo_busca_atual = ""

    # Container onde os cards serão renderizados dinamicamente
    lista_indicadores_coluna = ft.Column(
        spacing=16,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
    )

    def _badge_eixo(eixo_num: int) -> ft.Container:
        cor = CORES_EIXOS.get(eixo_num, ROXO_CLARO)
        nome = NOMES_EIXOS.get(eixo_num, f"Eixo {eixo_num}")
        return ft.Container(
            padding=ft.Padding.symmetric(horizontal=10, vertical=4),
            bgcolor=ft.Colors.with_opacity(0.12, cor),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.35, cor)),
            border_radius=14,
            content=ft.Text(
                nome,
                size=11,
                weight=ft.FontWeight.W_600,
                color=cor,
            ),
        )

    def _criar_card_indicador(item: dict, indice: int) -> ft.Container:
        eixo_num = item.get("eixo", 1)
        cor_eixo = CORES_EIXOS.get(eixo_num, ROXO_CLARO)
        titulo = item.get("titulo", "")
        descricao = item.get("descricao", "")
        criterios = item.get("criterios", {})

        detalhes_abertos = False

        criterios_coluna = ft.Column(
            spacing=8,
            visible=False,
            controls=[
                ft.Divider(height=1, color=BORDER),
                ft.Text(
                    "Critérios de Avaliação (Conceitos 1 a 5):",
                    size=12,
                    weight=ft.FontWeight.W_600,
                    color=TEXT,
                ),
            ],
        )

        for nivel in ["1", "2", "3", "4", "5"]:
            texto_criterio = criterios.get(nivel)
            if texto_criterio:
                cor_nivel = CORES_CONCEITOS.get(nivel, ROXO_CLARO)
                rotulo = ROTULOS_CONCEITOS.get(nivel, f"Critério {nivel}")
                criterios_coluna.controls.append(
                    ft.Container(
                        padding=ft.Padding.symmetric(horizontal=12, vertical=8),
                        bgcolor=ft.Colors.with_opacity(0.05, cor_nivel),
                        border=ft.Border(
                            left=ft.BorderSide(3, cor_nivel),
                        ),
                        border_radius=ft.BorderRadius.only(
                            top_right=6,
                            bottom_right=6,
                        ),
                        content=ft.Column(
                            spacing=3,
                            controls=[
                                ft.Text(
                                    rotulo,
                                    size=11,
                                    weight=ft.FontWeight.W_700,
                                    color=cor_nivel,
                                ),
                                ft.Text(
                                    texto_criterio,
                                    size=12,
                                    color=MUTED,
                                    selectable=True,
                                ),
                            ],
                        ),
                    )
                )

        btn_toggle = ft.TextButton(
            content=ft.Row(
                spacing=6,
                tight=True,
                controls=[
                    ft.Text(
                        "Ver os 5 critérios de pontuação",
                        size=12,
                        weight=ft.FontWeight.W_600,
                        color=cor_eixo,
                    ),
                    ft.Icon(
                        ft.Icons.KEYBOARD_ARROW_DOWN_ROUNDED,
                        size=18,
                        color=cor_eixo,
                    ),
                ],
            ),
            style=ft.ButtonStyle(
                overlay_color=ft.Colors.TRANSPARENT,
                padding=ft.Padding.symmetric(horizontal=0, vertical=4),
            ),
        )

        def alternar_detalhes(e):
            nonlocal detalhes_abertos
            detalhes_abertos = not detalhes_abertos
            criterios_coluna.visible = detalhes_abertos
            btn_toggle.content.controls[0].value = (
                "Ocultar critérios de pontuação" if detalhes_abertos else "Ver os 5 critérios de pontuação"
            )
            btn_toggle.content.controls[1].name = (
                ft.Icons.KEYBOARD_ARROW_UP_ROUNDED if detalhes_abertos else ft.Icons.KEYBOARD_ARROW_DOWN_ROUNDED
            )
            card_container.update()

        btn_toggle.on_click = alternar_detalhes

        card_container = ft.Container(
            bgcolor=SURFACE,
            border=ft.Border.all(1, BORDER),
            border_radius=12,
            padding=20,
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        wrap=True,
                        controls=[
                            _badge_eixo(eixo_num),
                            ft.Text(
                                f"Indicador #{indice}",
                                size=11,
                                color=MUTED,
                                font_family="monospace",
                            ),
                        ],
                    ),
                    ft.Text(
                        titulo,
                        size=16,
                        weight=ft.FontWeight.W_700,
                        color=TEXT,
                    ),
                    *(
                        [
                            ft.Text(
                                descricao,
                                size=12,
                                color=MUTED,
                            )
                        ]
                        if descricao
                        else []
                    ),
                    btn_toggle,
                    criterios_coluna,
                ],
            ),
        )

        return card_container

    def renderizar_indicadores():
        lista_indicadores_coluna.controls.clear()

        itens_filtrados = []
        for idx, item in enumerate(INDICADORES, start=1):
            # Filtro por Eixo (1, 2 ou 3)
            if filtro_eixo_atual > 0 and item.get("eixo") != filtro_eixo_atual:
                continue

            # Filtro por Busca textual
            if termo_busca_atual:
                termo = termo_busca_atual.lower()
                titulo = item.get("titulo", "").lower()
                criterios_str = " ".join(item.get("criterios", {}).values()).lower()
                if termo not in titulo and termo not in criterios_str:
                    continue

            itens_filtrados.append((idx, item))

        if not itens_filtrados:
            lista_indicadores_coluna.controls.append(
                ft.Container(
                    padding=40,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.SEARCH_OFF_ROUNDED, size=40, color=MUTED),
                            ft.Text(
                                "Nenhum indicador encontrado com os filtros aplicados.",
                                size=14,
                                color=MUTED,
                            ),
                        ],
                    ),
                )
            )
        else:
            for idx, item in itens_filtrados:
                lista_indicadores_coluna.controls.append(_criar_card_indicador(item, idx))

        texto_contador.value = f"Exibindo {len(itens_filtrados)} de {len(INDICADORES)} indicadores"
        page.update()

    # Barra de busca interativa
    campo_busca = ft.TextField(
        hint_text="Buscar por título ou palavra-chave nos 5 critérios...",
        hint_style=ft.TextStyle(color=MUTED, size=13),
        text_style=ft.TextStyle(color=TEXT, size=13),
        bgcolor=SURFACE_ALT,
        border_color=BORDER,
        focused_border_color=ROXO_CLARO,
        border_radius=10,
        dense=True,
        prefix_icon=ft.Icons.SEARCH_ROUNDED,
        cursor_color=ROXO_CLARO,
    )

    def on_busca_change(e):
        nonlocal termo_busca_atual
        termo_busca_atual = e.control.value or ""
        renderizar_indicadores()

    campo_busca.on_change = on_busca_change

    texto_contador = ft.Text(
        "",
        size=12,
        color=MUTED,
        font_family="monospace",
    )

    # Botões de filtro pelos 3 Eixos
    def _criar_chip_filtro(rotulo: str, eixo_id: int, cor_destaque: str):
        selecionado = filtro_eixo_atual == eixo_id
        return ft.OutlinedButton(
            rotulo,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.with_opacity(0.18, cor_destaque) if selecionado else ft.Colors.TRANSPARENT,
                color=cor_destaque if selecionado else MUTED,
                side=ft.BorderSide(
                    1.5 if selecionado else 1,
                    cor_destaque if selecionado else BORDER,
                ),
                shape=ft.RoundedRectangleBorder(radius=20),
                padding=ft.Padding.symmetric(horizontal=14, vertical=6),
                text_style=ft.TextStyle(size=12, weight=ft.FontWeight.W_600),
            ),
            on_click=lambda e: mudar_filtro_eixo(eixo_id),
        )

    chips_eixos_row = ft.Row(
        spacing=8,
        wrap=True,
    )

    def atualizar_chips_eixos():
        total_eixo1 = sum(1 for i in INDICADORES if i.get("eixo") == 1)
        total_eixo2 = sum(1 for i in INDICADORES if i.get("eixo") == 2)
        total_eixo3 = sum(1 for i in INDICADORES if i.get("eixo") == 3)

        chips_eixos_row.controls = [
            _criar_chip_filtro(f"Todos os Eixos ({len(INDICADORES)})", 0, ROXO_CLARO),
            _criar_chip_filtro(f"Eixo 1 (Didático-Pedagógica • {total_eixo1})", 1, ROXO_CLARO),
            _criar_chip_filtro(f"Eixo 2 (Corpo Docente • {total_eixo2})", 2, CIANO),
            _criar_chip_filtro(f"Eixo 3 (Infraestrutura • {total_eixo3})", 3, VERDE),
        ]

    def mudar_filtro_eixo(novo_eixo: int):
        nonlocal filtro_eixo_atual
        filtro_eixo_atual = novo_eixo
        atualizar_chips_eixos()
        renderizar_indicadores()

    atualizar_chips_eixos()

    # =========================================================
    # KPI CARDS DO TOPO (58 INDICADORES, 3 EIXOS, 5 CRITÉRIOS)
    # =========================================================
    def _kpi_card(valor: str, rotulo: str, cor: str) -> ft.Container:
        return ft.Container(
            col={"xs": 6, "sm": 6, "md": 3, "lg": 3},
            bgcolor=SURFACE,
            border=ft.Border.all(1, BORDER),
            border_radius=12,
            padding=16,
            content=ft.Column(
                spacing=4,
                controls=[
                    ft.Text(
                        valor,
                        size=22,
                        weight=ft.FontWeight.W_700,
                        color=cor,
                    ),
                    ft.Text(
                        rotulo,
                        size=12,
                        color=MUTED,
                    ),
                ],
            ),
        )

    kpis = ft.ResponsiveRow(
        columns=12,
        spacing=12,
        run_spacing=12,
        controls=[
            _kpi_card(f"{len(INDICADORES)}", "Indicadores Normativos", ROXO_CLARO),
            _kpi_card("3 Eixos", "Dimensões Avaliativas", CIANO),
            _kpi_card("5 Critérios", "Por Indicador (Conceitos 1 a 5)", VERDE),
            _kpi_card("100% SINAES", "Conformidade MEC", LARANJA),
        ],
    )

    # =========================================================
    # CABEÇALHO DA PÁGINA
    # =========================================================
    header_nav = ft.Container(
        bgcolor=PAGE,
        border=ft.Border(bottom=ft.BorderSide(1, BORDER)),
        padding=ft.Padding.symmetric(horizontal=24, vertical=12),
        alignment=ft.Alignment.CENTER,
        content=ft.Container(
            width=MAX_CONTENT_WIDTH,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.TextButton(
                        content=ft.Row(
                            spacing=6,
                            tight=True,
                            controls=[
                                ft.Icon(ft.Icons.ARROW_BACK_ROUNDED, size=16, color=ROXO_CLARO),
                                ft.Text("Voltar ao início", size=13, weight=ft.FontWeight.W_600, color=ROXO_CLARO),
                            ],
                        ),
                        on_click=lambda e: mudar_tela("/"),
                    ),
                    # Marca central
                    ft.Row(
                        spacing=0,
                        tight=True,
                        controls=[
                            ft.Text("evalytics", size=18, weight=ft.FontWeight.W_700, color=TEXT),
                            ft.Text("_", size=18, weight=ft.FontWeight.W_700, color=ROXO_CLARO),
                        ],
                    ),
                    # Botão entrar
                    ft.ElevatedButton(
                        "Entrar",
                        bgcolor=ROXO,
                        color="#ffffff",
                        height=36,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8),
                            padding=ft.Padding.symmetric(horizontal=16),
                            text_style=ft.TextStyle(size=12, weight=ft.FontWeight.W_600),
                        ),
                        on_click=lambda e: mudar_tela("/login"),
                    ),
                ],
            ),
        ),
    )

    # Render inicial
    renderizar_indicadores()

    # =========================================================
    # MONTAGEM DA VIEW
    # =========================================================
    return ft.View(
        route="/indicadores",
        bgcolor=PAGE,
        padding=0,
        spacing=0,
        scroll=ft.ScrollMode.AUTO,
        appbar=ft.AppBar(
            title=header_nav,
            toolbar_height=60,
            bgcolor=PAGE,
            elevation=0,
            automatically_imply_leading=False,
            title_spacing=0,
        ),
        controls=[
            ft.Container(
                alignment=ft.Alignment.CENTER,
                padding=ft.Padding.only(top=36, bottom=56, left=24, right=24),
                content=ft.Container(
                    width=MAX_CONTENT_WIDTH,
                    content=ft.Column(
                        spacing=24,
                        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                        controls=[
                            # Bloco de introdução
                            ft.Column(
                                spacing=8,
                                controls=[
                                    ft.Text(
                                        "avaliação institucional por dados",
                                        size=12,
                                        color=ROXO_CLARO,
                                        font_family="monospace",
                                        weight=ft.FontWeight.W_500,
                                    ),
                                    ft.Text(
                                        "Indicadores Institucionais",
                                        size=32,
                                        weight=ft.FontWeight.W_700,
                                        color=TEXT,
                                    ),
                                    ft.Text(
                                        "Explore os 58 indicadores distribuídos nos 3 eixos avaliativos oficiais do SINAES/MEC "
                                        "(Organização Didático-Pedagógica, Corpo Docente e Infraestrutura), cada um com 5 critérios "
                                        "objetivos de pontuação (Conceitos 1 a 5).",
                                        size=14,
                                        color=MUTED,
                                    ),
                                ],
                            ),

                            # Cards KPI
                            kpis,

                            # Barra de busca e filtros pelos 3 Eixos
                            ft.Column(
                                spacing=12,
                                controls=[
                                    campo_busca,
                                    chips_eixos_row,
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        controls=[texto_contador],
                                    ),
                                ],
                            ),

                            # Lista de Indicadores
                            lista_indicadores_coluna,

                            # CTA inferior
                            ft.Container(
                                margin=ft.Margin.only(top=32),
                                padding=32,
                                bgcolor=SURFACE,
                                border=ft.Border.all(1, BORDER),
                                border_radius=16,
                                alignment=ft.Alignment.CENTER,
                                content=ft.Column(
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=12,
                                    controls=[
                                        ft.Text(
                                            "Pronto para estruturar as avaliações da sua instituição?",
                                            size=20,
                                            weight=ft.FontWeight.W_700,
                                            color=TEXT,
                                            text_align=ft.TextAlign.CENTER,
                                        ),
                                        ft.Text(
                                            "Acesse a plataforma para associar esses indicadores a perguntas, cursos e relatórios em tempo real.",
                                            size=13,
                                            color=MUTED,
                                            text_align=ft.TextAlign.CENTER,
                                        ),
                                        ft.Container(height=4),
                                        ft.Row(
                                            alignment=ft.MainAxisAlignment.CENTER,
                                            spacing=12,
                                            wrap=True,
                                            controls=[
                                                ft.ElevatedButton(
                                                    "Acessar plataforma",
                                                    bgcolor=ROXO,
                                                    color="#ffffff",
                                                    height=38,
                                                    style=ft.ButtonStyle(
                                                        shape=ft.RoundedRectangleBorder(radius=8),
                                                        padding=ft.Padding.symmetric(horizontal=20),
                                                    ),
                                                    on_click=lambda e: mudar_tela("/login"),
                                                ),
                                                ft.OutlinedButton(
                                                    "Voltar à página inicial",
                                                    height=38,
                                                    style=ft.ButtonStyle(
                                                        color=TEXT,
                                                        side=ft.BorderSide(1, BORDER_STRONG),
                                                        shape=ft.RoundedRectangleBorder(radius=8),
                                                        padding=ft.Padding.symmetric(horizontal=18),
                                                    ),
                                                    on_click=lambda e: mudar_tela("/"),
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                            ),
                        ],
                    ),
                ),
            ),
        ],
    )
