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
    VERDE,
    CIANO,
    ROSA,
    LARANJA,
)

def abrir_modal_simulacao(page: ft.Page, mudar_tela: Optional[Callable[[str], None]] = None) -> None:
    """Abre um modal interativo para o usuário simular o preenchimento de uma avaliação institucional."""

    nota_selecionada = {"valor": 4}

    # Opções de resposta com escala de 1 a 5 critérios
    opcoes_escala = [
        ("1", "1 — Crítico / Não atende aos critérios", ROSA),
        ("2", "2 — Insuficiente / Atende com restrições", LARANJA),
        ("3", "3 — Adequado / Atende satisfatoriamente", CIANO),
        ("4", "4 — Muito Bom / Supera expectativas", ROXO_CLARO),
        ("5", "5 — Excelente / Práticas inovadoras", VERDE),
    ]

    cores_por_nota = {val: cor for val, _, cor in opcoes_escala}

    container_opcoes = ft.Column(spacing=6)

    def _renderizar_opcoes():
        container_opcoes.controls.clear()
        for valor_str, rotulo, cor in opcoes_escala:
            valor_int = int(valor_str)
            selecionado = nota_selecionada["valor"] == valor_int

            def _criar_click(val):
                def _handle(e):
                    nota_selecionada["valor"] = val
                    _renderizar_opcoes()
                    page.update()
                return _handle

            botao_opcao = ft.Container(
                bgcolor=ft.Colors.with_opacity(0.12, cor) if selecionado else SURFACE_ALT,
                border=ft.Border.all(
                    1.5 if selecionado else 1,
                    cor if selecionado else BORDER,
                ),
                border_radius=8,
                padding=ft.Padding.symmetric(horizontal=12, vertical=10),
                on_click=_criar_click(valor_int),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Row(
                            spacing=10,
                            tight=True,
                            controls=[
                                ft.Container(
                                    width=20,
                                    height=20,
                                    border_radius=10,
                                    border=ft.Border.all(1.5, cor if selecionado else MUTED),
                                    bgcolor=cor if selecionado else ft.Colors.TRANSPARENT,
                                    alignment=ft.Alignment.CENTER,
                                    content=ft.Icon(
                                        ft.Icons.CHECK_ROUNDED,
                                        size=14,
                                        color="#ffffff",
                                        visible=selecionado,
                                    ),
                                ),
                                ft.Text(
                                    rotulo,
                                    size=12,
                                    weight=ft.FontWeight.W_600 if selecionado else ft.FontWeight.W_400,
                                    color=TEXT if selecionado else MUTED,
                                ),
                            ],
                        ),
                        ft.Text(
                            f"Critério {valor_int}/5",
                            size=11,
                            color=cor if selecionado else MUTED,
                            font_family="monospace",
                            weight=ft.FontWeight.BOLD,
                        ),
                    ],
                ),
            )
            container_opcoes.controls.append(botao_opcao)

    _renderizar_opcoes()

    campo_comentario = ft.TextField(
        hint_text="Escreva um comentário qualitativo ou sugestão de melhoria (opcional)...",
        hint_style=ft.TextStyle(color=MUTED, size=12),
        text_style=ft.TextStyle(color=TEXT, size=12),
        bgcolor=SURFACE_ALT,
        border_color=BORDER,
        focused_border_color=ROXO_CLARO,
        border_radius=8,
        min_lines=2,
        max_lines=3,
        multiline=True,
        cursor_color=ROXO_CLARO,
    )

    def fechar_dialog(e=None):
        dialog.open = False
        page.update()

    # Conteúdo dinâmico (troca para tela de sucesso ao submeter)
    conteudo_modal = ft.Column(
        spacing=16,
        tight=True,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
    )

    def submeter_simulacao(e):
        nota = nota_selecionada["valor"]
        cor_nota = cores_por_nota.get(str(nota), ROXO_CLARO)

        # Transição para o estado de Sucesso
        conteudo_modal.controls.clear()
        conteudo_modal.controls.extend([
            ft.Container(
                alignment=ft.Alignment.CENTER,
                padding=ft.Padding.symmetric(vertical=10),
                content=ft.Column(
                    spacing=12,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            width=64,
                            height=64,
                            border_radius=32,
                            bgcolor=ft.Colors.with_opacity(0.12, VERDE),
                            alignment=ft.Alignment.CENTER,
                            content=ft.Icon(
                                ft.Icons.CHECK_CIRCLE_ROUNDED,
                                size=42,
                                color=VERDE,
                            ),
                        ),
                        ft.Text(
                            "Simulação concluída com sucesso!",
                            size=18,
                            weight=ft.FontWeight.W_700,
                            color=TEXT,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(
                            padding=ft.Padding.symmetric(horizontal=14, vertical=10),
                            bgcolor=SURFACE_ALT,
                            border=ft.Border.all(1, BORDER),
                            border_radius=10,
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                                controls=[
                                    ft.Column(
                                        spacing=2,
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        controls=[
                                            ft.Text("Critério", size=10, color=MUTED),
                                            ft.Text(f"{nota}.0 / 5.0", size=16, weight=ft.FontWeight.W_700, color=cor_nota),
                                        ],
                                    ),
                                    ft.Container(width=1, height=24, bgcolor=BORDER),
                                    ft.Column(
                                        spacing=2,
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        controls=[
                                            ft.Text("Eixo Avaliativo", size=10, color=MUTED),
                                            ft.Text("Eixo 1 — Didático-Pedagógica", size=12, weight=ft.FontWeight.W_600, color=TEXT),
                                        ],
                                    ),
                                    ft.Container(width=1, height=24, bgcolor=BORDER),
                                    ft.Column(
                                        spacing=2,
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        controls=[
                                            ft.Text("Privacidade", size=10, color=MUTED),
                                            ft.Text("100% Anônimo", size=12, weight=ft.FontWeight.W_600, color=CIANO),
                                        ],
                                    ),
                                ],
                            ),
                        ),
                        ft.Text(
                            "No Evalytics, cada resposta é processada em tempo real e alimenta os relatórios dos 3 eixos institucionais "
                            "sem expor a identidade de quem respondeu.",
                            size=12,
                            color=MUTED,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(height=6),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=10,
                            wrap=True,
                            controls=[
                                ft.OutlinedButton(
                                    "Fechar simulação",
                                    height=38,
                                    style=ft.ButtonStyle(
                                        color=TEXT,
                                        side=ft.BorderSide(1, BORDER_STRONG),
                                        shape=ft.RoundedRectangleBorder(radius=8),
                                    ),
                                    on_click=fechar_dialog,
                                ),
                                ft.ElevatedButton(
                                    "Acessar plataforma",
                                    bgcolor=ROXO,
                                    color="#ffffff",
                                    height=38,
                                    style=ft.ButtonStyle(
                                        shape=ft.RoundedRectangleBorder(radius=8),
                                    ),
                                    on_click=lambda ev: (fechar_dialog(), mudar_tela("/login") if mudar_tela else None),
                                ),
                            ],
                        ),
                    ],
                ),
            )
        ])
        page.update()

    # Monta a tela de preenchimento inicial
    conteudo_modal.controls.extend([
        # Pergunta simulada
        ft.Container(
            padding=14,
            bgcolor=SURFACE_ALT,
            border=ft.Border.all(1, BORDER),
            border_radius=10,
            content=ft.Column(
                spacing=6,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Container(
                                padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                                bgcolor=ft.Colors.with_opacity(0.12, ROXO_CLARO),
                                border_radius=10,
                                content=ft.Text(
                                    "EIXO 1 • ORGANIZAÇÃO DIDÁTICO-PEDAGÓGICA",
                                    size=10,
                                    weight=ft.FontWeight.W_700,
                                    color=ROXO_CLARO,
                                    font_family="monospace",
                                ),
                            ),
                            ft.Text("Questão 01 de 01", size=10, color=MUTED, font_family="monospace"),
                        ],
                    ),
                    ft.Text(
                        "Em que medida os objetivos e a estrutura do curso atendem às demandas de formação profissional e do mercado de trabalho?",
                        size=13,
                        weight=ft.FontWeight.W_600,
                        color=TEXT,
                    ),
                ],
            ),
        ),

        # Escala de Opções (1 a 5)
        ft.Column(
            spacing=4,
            controls=[
                ft.Text("Selecione o critério correspondente:", size=11, weight=ft.FontWeight.W_600, color=MUTED),
                container_opcoes,
            ],
        ),

        # Campo de observações
        campo_comentario,

        # Botão de envio
        ft.Row(
            alignment=ft.MainAxisAlignment.END,
            spacing=10,
            controls=[
                ft.TextButton(
                    "Cancelar",
                    style=ft.ButtonStyle(color=MUTED),
                    on_click=fechar_dialog,
                ),
                ft.ElevatedButton(
                    "Enviar Resposta Simulada",
                    bgcolor=ROXO,
                    color="#ffffff",
                    height=38,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.Padding.symmetric(horizontal=16),
                        text_style=ft.TextStyle(size=12, weight=ft.FontWeight.W_600),
                    ),
                    on_click=submeter_simulacao,
                ),
            ],
        ),
    ])

    dialog = ft.AlertDialog(
        modal=True,
        bgcolor=SURFACE,
        title_padding=ft.Padding.only(left=22, right=16, top=18, bottom=0),
        content_padding=ft.Padding.only(left=22, right=22, top=14, bottom=18),
        shape=ft.RoundedRectangleBorder(radius=14),
        title=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    spacing=8,
                    tight=True,
                    controls=[
                        ft.Icon(ft.Icons.RULE_ROUNDED, size=20, color=ROXO_CLARO),
                        ft.Text(
                            "Simulação de Avaliação",
                            size=16,
                            weight=ft.FontWeight.W_700,
                            color=TEXT,
                        ),
                    ],
                ),
                ft.IconButton(
                    icon=ft.Icons.CLOSE_ROUNDED,
                    icon_color=MUTED,
                    icon_size=20,
                    on_click=fechar_dialog,
                ),
            ],
        ),
        content=ft.Container(
            width=500,
            content=conteudo_modal,
        ),
    )

    page.overlay.append(dialog)
    dialog.open = True
    page.update()
