from typing import Callable

import flet as ft

from components.core.constants.constants import COR_PRIMARIA, SURFACE, TEXTO_PRINCIPAL, TEXTO_SECUNDARIO
from components.core.router.rotas_cts import ROTA_AVALIACOES, ROTA_CONTA, ROTA_DASHBOARD_VISAO_GERAL, ROTA_RELATORIOS
from components.core.theme.darkmode_toggle import toggle_dark_mode
from components.core.theme.theme_config import configurar_tema
from .account_shared import _exibir_dialogo, _fechar_dialogo


def abrir_sobre(page: ft.Page, cores: dict[str, str]):
    conteudo = ft.Column(
        tight=True,
        spacing=10,
        controls=[
            ft.Text("Evalytics", size=18, weight=ft.FontWeight.W_700, color=cores[TEXTO_PRINCIPAL]),
            ft.Text(
                "Sistema de avaliação institucional para organizar cursos e indicadores, acompanhar resultados e gerar relatórios em PDF e CSV.",
                size=13,
                color=ft.Colors.GREY_400,
            ),
        ],
    )
    _exibir_dialogo(page, "Sobre o Evalytics", conteudo, cores)


def abrir_ajuda(page: ft.Page, cores: dict[str, str], mudar_tela: Callable[[str], None]):
    conteudo = ft.Column(
        tight=True,
        spacing=12,
        controls=[
            ft.Text("Comece por uma avaliação, acompanhe os indicadores no dashboard e consulte os relatórios para analisar os resultados.", color=ft.Colors.GREY_400, size=13),
            ft.Text("Atalhos", color=cores[TEXTO_PRINCIPAL], weight=ft.FontWeight.W_600),
            ft.Row(
                wrap=True,
                controls=[
                    ft.TextButton("Avaliações", on_click=lambda e: mudar_tela(ROTA_AVALIACOES)),
                    ft.TextButton("Dashboard", on_click=lambda e: mudar_tela(ROTA_DASHBOARD_VISAO_GERAL)),
                    ft.TextButton("Relatórios", on_click=lambda e: mudar_tela(ROTA_RELATORIOS)),
                ],
            ),
            ft.Divider(),
            ft.Text("O contato de suporte da instituição não está configurado no aplicativo.", size=11, color=ft.Colors.GREY_500),
        ],
    )
    _exibir_dialogo(page, "Ajuda e suporte", conteudo, cores)


def abrir_configuracoes_conta(
    page: ft.Page,
    cores: dict[str, str],
    nome: str,
    email: str,
    abrir_perfil: Callable,
    mudar_tela: Callable[[str], None],
):
    """Mostra atalhos de configurações pessoais da conta, sem abrir as configurações institucionais."""
    dialogo = None
    rota = getattr(page, "rota_navegacao_atual", None) or page.route
    dicas_por_rota = {
        "/inicio": ("Início", "Use os atalhos para iniciar uma avaliação ou acessar cursos, dashboard e relatórios."),
        "/dashboard": ("Dashboard", "Abra a Visão Geral para conferir os indicadores ou Acompanhamento para consultar avaliações."),
        "/dashboard/visao-geral": ("Indicadores", "Selecione semestre, curso e departamento, depois aplique os filtros para atualizar os indicadores."),
        "/dashboard/avaliacoes": ("Acompanhamento", "Use os filtros para localizar avaliações e acompanhar seus registros."),
        "/avaliacoes": ("Avaliações", "Consulte as avaliações cadastradas ou inicie uma nova pelo menu lateral."),
        "/cursos": ("Cursos", "Pesquise pelo nome ou código; selecione departamento e status e aplique os filtros."),
        "/relatorios": ("Relatórios", "Escolha uma subtela na navegação de Relatórios para abrir o dashboard ou os dados para exportação."),
        "/dashboard/resultados": ("Resultados por eixo", "Selecione semestre, curso e eixo e aplique os filtros para atualizar a análise."),
        "/relatorios/dados": ("Dados e Exportação", "Defina os filtros antes de gerar o arquivo PDF ou CSV."),
        "/configuracoes": ("Configurações", "Escolha um eixo para consultar e editar os indicadores e seus critérios."),
        "/formulario": ("Avaliação", "Responda aos critérios de cada eixo; revise as respostas antes de finalizar."),
    }
    nome_tela, dica_tela = dicas_por_rota.get(
        rota,
        ("Evalytics", "Use o menu lateral para acessar avaliações, cursos, dashboard e relatórios."),
    )
    preferencias_pendentes = {
        "tema_escuro": getattr(page, "is_dark_mode", False),
        "densidade": getattr(page, "preferencia_densidade_visual", "standard"),
    }

    def ir_para_perfil(e):
        _fechar_dialogo(page, dialogo)
        page.run_task(abrir_perfil, None)

    async def aplicar_aparencia():
        # Deixa o evento de fechamento terminar antes de o Navigator remontar a view.
        await asyncio.sleep(0.1)
        rota_atual = getattr(page, "rota_navegacao_atual", None) or page.route
        modo_escuro_atual = getattr(page, "is_dark_mode", False)
        densidade_atual = getattr(page, "preferencia_densidade_visual", "standard")
        tema_mudou = preferencias_pendentes["tema_escuro"] != modo_escuro_atual
        densidade_mudou = preferencias_pendentes["densidade"] != densidade_atual
        page.preferencia_densidade_visual = preferencias_pendentes["densidade"]

        if tema_mudou:
            toggle_dark_mode(page, modo_escuro_atual, mudar_tela, rota_atual)
        elif densidade_mudou:
            configurar_tema(page, modo_escuro_atual)
            if rota_atual:
                mudar_tela(rota_atual)
            else:
                page.update()

    def alterar_aparencia(e):
        preferencias_pendentes["tema_escuro"] = bool(e.control.value)

    def voltar_configuracoes(e):
        _fechar_dialogo(page, dialogo)

    def aplicar_configuracoes(e):
        _fechar_dialogo(page, dialogo)
        modo_escuro_atual = getattr(page, "is_dark_mode", False)
        densidade_atual = getattr(page, "preferencia_densidade_visual", "standard")
        if (
            preferencias_pendentes["tema_escuro"] != modo_escuro_atual
            or preferencias_pendentes["densidade"] != densidade_atual
        ):
            page.run_task(aplicar_aparencia)

    preferencia_tema = ft.Switch(
        label="Tema escuro",
        value=getattr(page, "is_dark_mode", False),
        on_change=alterar_aparencia,
        active_color=COR_PRIMARIA,
    )
    texto_densidade = ft.Text(
        "Compacta" if preferencias_pendentes["densidade"] == "compact" else "Padrão",
        size=12,
        color=cores[TEXTO_SECUNDARIO],
    )

    def alterar_densidade(e):
        compacta = bool(e.control.value)
        preferencias_pendentes["densidade"] = "compact" if compacta else "standard"
        texto_densidade.value = "Compacta" if compacta else "Padrão"
        page.update()

    preferencia_densidade = ft.Switch(
        value=preferencias_pendentes["densidade"] == "compact",
        on_change=alterar_densidade,
        active_color=COR_PRIMARIA,
    )
    preferencia_idioma = ft.Dropdown(
        label="Idioma",
        value="pt-BR",
        options=[ft.dropdown.Option(key="pt-BR", text="Português (Brasil)")],
        disabled=True,
        border_radius=8,
        border_color=ft.Colors.GREY_600,
    )

    conteudo = ft.Column(
        tight=True,
        scroll=ft.ScrollMode.AUTO,
        spacing=14,
        controls=[
            ft.Text(
                "Gerencie seus dados pessoais e a senha usada para acessar o Evalytics.",
                size=13,
                color=cores[TEXTO_SECUNDARIO],
            ),
            ft.Container(
                width=420,
                padding=14,
                bgcolor=cores[SURFACE],
                border=ft.Border.all(1, ft.Colors.with_opacity(0.16, ft.Colors.GREY_400)),
                border_radius=10,
                content=ft.Column(
                    spacing=8,
                    controls=[
                        ft.Text("PERFIL", size=10, weight=ft.FontWeight.W_700, color=cores[TEXTO_SECUNDARIO]),
                        ft.Text(nome or "Nome não informado", size=13, color=cores[TEXTO_PRINCIPAL]),
                        ft.Text(email or "E-mail indisponível", size=12, color=cores[TEXTO_SECUNDARIO]),
                    ],
                ),
                on_click=ir_para_perfil,
                ink=True,
                tooltip="Abrir meu perfil",
            ),
            ft.Text(
                "A alteração do nome e da senha fica disponível na área do seu perfil.",
                size=12,
                color=cores[TEXTO_SECUNDARIO],
            ),
            ft.Divider(height=1),
            ft.Text("PREFERÊNCIAS", size=10, weight=ft.FontWeight.W_700, color=cores[TEXTO_SECUNDARIO]),
            ft.Container(
                padding=ft.Padding.all(12),
                bgcolor=cores[SURFACE],
                border=ft.Border.all(1, ft.Colors.with_opacity(0.16, ft.Colors.GREY_400)),
                border_radius=10,
                content=ft.Column(
                    spacing=12,
                    controls=[
                        preferencia_idioma,
                        ft.Text(
                            "Outros idiomas ainda não estão disponíveis.",
                            size=11,
                            color=cores[TEXTO_SECUNDARIO],
                        ),
                        ft.Divider(height=1),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Column(
                                    spacing=2,
                                    controls=[
                                        ft.Text("Tema escuro", color=cores[TEXTO_PRINCIPAL], size=13),
                                        ft.Text("Altera as cores da plataforma.", color=cores[TEXTO_SECUNDARIO], size=11),
                                    ],
                                ),
                                preferencia_tema,
                            ],
                        ),
                        ft.Text("EXIBIÇÃO", size=10, weight=ft.FontWeight.W_700, color=cores[TEXTO_SECUNDARIO]),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Column(
                                    spacing=2,
                                    controls=[
                                        ft.Text("Densidade da interface", color=cores[TEXTO_PRINCIPAL], size=13),
                                        ft.Text("Alternar entre padrão e compacta.", color=cores[TEXTO_SECUNDARIO], size=11),
                                    ],
                                ),
                                ft.Row(
                                    spacing=6,
                                    tight=True,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[texto_densidade, preferencia_densidade],
                                ),
                            ],
                        ),
                    ],
                ),
            ),
            ft.Container(
                padding=12,
                bgcolor=cores[SURFACE],
                border=ft.Border.all(1, ft.Colors.with_opacity(0.16, ft.Colors.GREY_400)),
                border_radius=10,
                content=ft.Row(
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Icon(ft.Icons.TIPS_AND_UPDATES_OUTLINED, size=18, color=COR_PRIMARIA),
                        ft.Column(
                            expand=True,
                            spacing=4,
                            controls=[
                                ft.Text(f"AJUDA RÁPIDA · {nome_tela.upper()}", size=10, weight=ft.FontWeight.W_700, color=cores[TEXTO_SECUNDARIO]),
                                ft.Text(dica_tela, size=12, color=cores[TEXTO_PRINCIPAL]),
                            ],
                        ),
                    ],
                ),
            ),
        ],
    )
    dialogo = ft.AlertDialog(
        modal=True,
        bgcolor=cores[SURFACE],
        shape=ft.RoundedRectangleBorder(radius=14),
        title=ft.Text("Configurações da conta", color=cores[TEXTO_PRINCIPAL], weight=ft.FontWeight.W_700),
        content=ft.Container(
            width=420,
            height=max(220, min(540, (page.height or 760) - 220)),
            content=conteudo,
        ),
        actions=[
            ft.TextButton("Voltar", on_click=voltar_configuracoes),
            ft.ElevatedButton(
                "Aplicar alterações",
                bgcolor=COR_PRIMARIA,
                color=ft.Colors.WHITE,
                on_click=aplicar_configuracoes,
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.overlay.append(dialogo)
    dialogo.open = True
    page.update()


