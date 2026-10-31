import flet as ft
from typing import Callable, Optional
from components.landing.palette import (
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

    etapa_atual = {"valor": 0}
    respostas = [4, 4, 4]
    perguntas = [
        (
            "Organização Didático-Pedagógica",
            "Em que medida os objetivos e a estrutura do curso atendem às demandas de formação profissional?",
        ),
        (
            "Corpo Docente e Tutorial",
            "Como você avalia o acompanhamento e a contribuição dos docentes para a sua aprendizagem?",
        ),
        (
            "Infraestrutura",
            "Como você avalia os espaços, equipamentos e recursos disponíveis para as atividades do curso?",
        ),
    ]

    # Escala ilustrativa de 1 a 5. A prévia não envia nem salva respostas.
    opcoes_escala = [
        ("1", "1 — Crítico / Não atende aos critérios", ROSA),
        ("2", "2 — Insuficiente / Atende com restrições", LARANJA),
        ("3", "3 — Adequado / Atende satisfatoriamente", CIANO),
        ("4", "4 — Muito Bom / Supera expectativas", ROXO_CLARO),
        ("5", "5 — Excelente / Práticas inovadoras", VERDE),
    ]

    cores_por_nota = {int(val): cor for val, _, cor in opcoes_escala}

    container_opcoes = ft.Column(spacing=6)
    texto_eixo = ft.Text(size=10, weight=ft.FontWeight.W_700, color=ROXO_CLARO, font_family="monospace")
    texto_pergunta = ft.Text(size=13, weight=ft.FontWeight.W_600, color=TEXT)
    texto_progresso = ft.Text(size=10, color=MUTED, font_family="monospace")
    barra_progresso = ft.ProgressBar(value=1 / len(perguntas), color=ROXO_CLARO, bgcolor=BORDER, height=4)

    def _atualizar_pergunta():
        indice = etapa_atual["valor"]
        eixo, pergunta = perguntas[indice]
        texto_eixo.value = f"EIXO {indice + 1} • {eixo.upper()}"
        texto_pergunta.value = pergunta
        texto_progresso.value = f"QUESTÃO {indice + 1} DE {len(perguntas)}"
        barra_progresso.value = (indice + 1) / len(perguntas)
        _renderizar_opcoes()

    def _renderizar_opcoes():
        container_opcoes.controls.clear()
        for valor_str, rotulo, cor in opcoes_escala:
            valor_int = int(valor_str)
            selecionado = respostas[etapa_atual["valor"]] == valor_int

            def _criar_click(val):
                def _handle(e):
                    respostas[etapa_atual["valor"]] = val
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
                            f"Nota {valor_int}/5",
                            size=11,
                            color=cor if selecionado else MUTED,
                            font_family="monospace",
                            weight=ft.FontWeight.BOLD,
                        ),
                    ],
                ),
            )
            container_opcoes.controls.append(botao_opcao)

    _atualizar_pergunta()

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
        media = sum(respostas) / len(respostas)

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
                            padding=ft.Padding.symmetric(horizontal=14, vertical=12),
                            bgcolor=SURFACE_ALT,
                            border=ft.Border.all(1, BORDER),
                            border_radius=10,
                            content=ft.Column(
                                spacing=10,
                                controls=[
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                                        controls=[
                                            ft.Column(
                                                spacing=2,
                                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                controls=[
                                                    ft.Text("Média simulada", size=10, color=MUTED),
                                                    ft.Text(
                                                        f"{media:.1f} / 5.0",
                                                        size=16,
                                                        weight=ft.FontWeight.W_700,
                                                        color=ROXO_CLARO,
                                                    ),
                                                ],
                                            ),
                                            ft.Column(
                                                spacing=2,
                                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                controls=[
                                                    ft.Text("Eixos percorridos", size=10, color=MUTED),
                                                    ft.Text(
                                                        f"{len(perguntas)} eixos",
                                                        size=12,
                                                        weight=ft.FontWeight.W_600,
                                                        color=TEXT,
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                    ft.Divider(height=1, color=BORDER),
                                    *[
                                        ft.Row(
                                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                            controls=[
                                                ft.Text(eixo, size=11, color=MUTED),
                                                ft.Text(
                                                    f"{respostas[indice]} / 5",
                                                    size=11,
                                                    color=cores_por_nota[respostas[indice]],
                                                    weight=ft.FontWeight.W_700,
                                                ),
                                            ],
                                        )
                                        for indice, (eixo, _) in enumerate(perguntas)
                                    ],
                                ],
                            ),
                        ),
                        ft.Text(
                            "Esta prévia é ilustrativa. As respostas acima foram calculadas nesta tela e não foram enviadas nem salvas.",
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
        # Prévia ilustrativa, percorrida como um fluxo de avaliação.
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
                                    content=texto_eixo,
                                ),
                                texto_progresso,
                            ],
                        ),
                        barra_progresso,
                        texto_pergunta,
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

        ft.Text(
            "Conteúdo demonstrativo. Nenhuma resposta será transmitida ou registrada.",
            size=10,
            color=MUTED,
            italic=True,
        ),

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
                    "Próxima pergunta",
                    bgcolor=ROXO,
                    color="#ffffff",
                    height=38,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.Padding.symmetric(horizontal=16),
                        text_style=ft.TextStyle(size=12, weight=ft.FontWeight.W_600),
                    ),
                    on_click=lambda e: _avancar_ou_concluir(e),
                ),
            ],
        ),
    ])

    def _avancar_ou_concluir(e):
        if etapa_atual["valor"] < len(perguntas) - 1:
            etapa_atual["valor"] += 1
            _atualizar_pergunta()
            btn_enviar.content = (
                "Próxima pergunta"
                if etapa_atual["valor"] < len(perguntas) - 1
                else "Finalizar"
            )
            btn_voltar.visible = etapa_atual["valor"] > 0
            page.update()
            return
        submeter_simulacao(e)

    def _voltar_pergunta(e):
        if etapa_atual["valor"] > 0:
            etapa_atual["valor"] -= 1
            _atualizar_pergunta()
            btn_enviar.content = "Próxima pergunta"
            btn_voltar.visible = etapa_atual["valor"] > 0
            page.update()

    # Referências usadas para atualizar a navegação entre perguntas.
    botoes_fluxo = conteudo_modal.controls[-1].controls
    btn_voltar = ft.TextButton(
        "Voltar",
        visible=False,
        style=ft.ButtonStyle(color=MUTED),
        on_click=_voltar_pergunta,
    )
    btn_enviar = botoes_fluxo[-1]
    btn_enviar.content = "Próxima pergunta"
    botoes_fluxo.insert(1, btn_voltar)

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
