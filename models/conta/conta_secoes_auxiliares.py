import flet as ft

from components.core.constants.constants import BORDA, COR_PRIMARIA, TEXTO_PRINCIPAL, TEXTO_SECUNDARIO
from components.layout.topbar.core.account_menu import abrir_dialogo_alterar_senha
from models.conta.conta_utils import _card
def criar_secoes_auxiliares(page, layout, cores, campo_email, status_seguranca, notificacoes_ativas, contador_notificacoes_ativo):
    def atualizar_preferencias_notificacoes(e=None) -> None:
        page.notificacoes_ativas = bool(switch_notificacoes.value)
        page.contador_notificacoes_ativo = bool(switch_contador.value)
        topbar = getattr(page, "_topbar_notificacoes", None)
        if topbar is not None:
            topbar.aplicar_preferencias_notificacoes()
        page.update()

    switch_notificacoes = ft.Switch(
        value=notificacoes_ativas,
        active_color=COR_PRIMARIA,
        on_change=atualizar_preferencias_notificacoes,
    )
    switch_contador = ft.Switch(
        value=contador_notificacoes_ativo,
        active_color=COR_PRIMARIA,
        on_change=atualizar_preferencias_notificacoes,
    )
    seguranca = _card(
        layout,
        ft.Column(
            spacing=14,
            controls=[
                ft.Column(
                    spacing=4,
                    controls=[
                        ft.Text("Segurança da conta", size=15, weight=ft.FontWeight.W_700, color=cores[TEXTO_PRINCIPAL]),
                        ft.Text("Acompanhe a proteção dos dados de acesso.", size=11, color=cores[TEXTO_SECUNDARIO]),
                    ],
                ),
                ft.Container(
                    padding=12,
                    border=ft.Border.all(1, cores[BORDA]),
                    border_radius=8,
                    content=ft.Row(
                        spacing=9,
                        controls=[
                            ft.Icon(ft.Icons.MARK_EMAIL_READ_OUTLINED, size=18, color=cores[TEXTO_SECUNDARIO]),
                            ft.Text("Verificação do e-mail", size=12, color=cores[TEXTO_PRINCIPAL]),
                            ft.Container(expand=True),
                            status_seguranca,
                        ],
                    ),
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            spacing=3,
                            controls=[
                                ft.Text("Senha", size=12, color=cores[TEXTO_PRINCIPAL]),
                                ft.Text("Altere sua senha de acesso.", size=10, color=cores[TEXTO_SECUNDARIO]),
                            ],
                        ),
                        ft.OutlinedButton(
                            "Alterar senha",
                            icon=ft.Icons.LOCK_OUTLINE,
                            on_click=lambda e: abrir_dialogo_alterar_senha(page, cores, campo_email.value or ""),
                        ),
                    ],
                ),
            ],
        ),
    )
    notificacoes = _card(
        layout,
        ft.Column(
            spacing=14,
            controls=[
                ft.Column(
                    spacing=4,
                    controls=[
                        ft.Text("Notificações", size=15, weight=ft.FontWeight.W_700, color=cores[TEXTO_PRINCIPAL]),
                        ft.Text("Escolha quais avisos aparecem no aplicativo.", size=11, color=cores[TEXTO_SECUNDARIO]),
                    ],
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            spacing=2,
                            controls=[
                                ft.Text("Notificações no aplicativo", size=12, color=cores[TEXTO_PRINCIPAL]),
                                ft.Text("Mostrar o sino e o painel de notificações.", size=10, color=cores[TEXTO_SECUNDARIO]),
                            ],
                        ),
                        switch_notificacoes,
                    ],
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            spacing=2,
                            controls=[
                                ft.Text("Contador de não lidas", size=12, color=cores[TEXTO_PRINCIPAL]),
                                ft.Text("Exibir a quantidade pendente sobre o sino.", size=10, color=cores[TEXTO_SECUNDARIO]),
                            ],
                        ),
                        switch_contador,
                    ],
                ),
            ],
        ),
    )
    sobre_evalytics = _card(
        layout,
        ft.Column(
            spacing=10,
            controls=[
                ft.Row(
                    spacing=12,
                    controls=[
                        ft.Container(
                            width=42,
                            height=42,
                            border_radius=11,
                            bgcolor="#302747" if layout.controller.dark_mode else "#EEE9FB",
                            alignment=ft.Alignment.CENTER,
                            content=ft.Icon(
                                ft.Icons.INFO_OUTLINE,
                                size=21,
                                color="#B69CFF" if layout.controller.dark_mode else COR_PRIMARIA,
                            ),
                        ),
                        ft.Column(
                            spacing=3,
                            controls=[
                                ft.Text("Sobre", size=16, weight=ft.FontWeight.W_700, color=cores[TEXTO_PRINCIPAL]),
                                ft.Text("solução inteligente para gestão & execução de autoavaliações institucionais", size=11, color=cores[TEXTO_SECUNDARIO]),
                            ],
                        ),
                    ],
                ),
                ft.Divider(height=1, color=cores[BORDA]),
                ft.Text(
                    "O Evalytics organiza avaliações institucionais, acompanha indicadores por curso e eixo e reúne resultados para consulta e exportação em PDF ou CSV.",
                    size=13,
                    color=cores[TEXTO_PRINCIPAL],
                ),
            ],
        ),
    )

    return {'Segurança': seguranca, 'Notificações': notificacoes, 'Sobre o Evalytics': sobre_evalytics}
