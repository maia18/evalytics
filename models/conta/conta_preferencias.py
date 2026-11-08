import flet as ft

from components.core.constants.constants import BORDA, COR_PRIMARIA, TEXTO_PRINCIPAL, TEXTO_SECUNDARIO
from components.core.router.rotas_cts import ROTA_CONTA
from components.core.theme.darkmode_toggle import toggle_dark_mode
from components.core.theme.theme_config import configurar_tema
from models.conta.conta_utils import _card
def criar_secao_preferencias(page, layout, cores, mudar_tela):
    tema_atual = bool(getattr(page, "is_dark_mode", False))
    densidade_atual = getattr(page, "preferencia_densidade_visual", "standard")
    preferencias_pendentes = {"tema": tema_atual, "densidade": densidade_atual}
    def aplicar_preferencias(e) -> None:
        tema_mudou = preferencias_pendentes["tema"] != bool(getattr(page, "is_dark_mode", False))
        densidade_atualizada = getattr(page, "preferencia_densidade_visual", "standard")
        densidade_mudou = preferencias_pendentes["densidade"] != densidade_atualizada
        if not tema_mudou and not densidade_mudou:
            aviso = ft.SnackBar(content=ft.Text("As preferências já estão aplicadas."))
            page.overlay.append(aviso)
            aviso.open = True
            page.update()
            return

        page.preferencia_densidade_visual = preferencias_pendentes["densidade"]
        if tema_mudou:
            toggle_dark_mode(page, bool(getattr(page, "is_dark_mode", False)), mudar_tela, ROTA_CONTA)
        else:
            configurar_tema(page, bool(getattr(page, "is_dark_mode", False)))
            mudar_tela(ROTA_CONTA)

    preferencias = _card(
        layout,
        ft.Column(
            spacing=14,
            controls=[
                ft.Column(
                    spacing=3,
                    controls=[
                        ft.Text("Preferências", size=16, weight=ft.FontWeight.W_700, color=cores[TEXTO_PRINCIPAL]),
                        ft.Text("Ajuste a aparência da sua interface.", size=11, color=cores[TEXTO_SECUNDARIO]),
                    ],
                ),
                ft.Divider(height=1),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            spacing=2,
                            controls=[
                                ft.Text("Tema escuro", size=12, color=cores[TEXTO_PRINCIPAL]),
                                ft.Text("Alterna entre os temas claro e escuro.", size=10, color=cores[TEXTO_SECUNDARIO]),
                            ],
                        ),
                        ft.Switch(
                            value=tema_atual,
                            active_color=COR_PRIMARIA,
                            on_change=lambda e: preferencias_pendentes.update(tema=bool(e.control.value)),
                        ),
                    ],
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            spacing=2,
                            controls=[
                                ft.Text("Densidade compacta", size=12, color=cores[TEXTO_PRINCIPAL]),
                                ft.Text("Reduz espaçamentos da interface.", size=10, color=cores[TEXTO_SECUNDARIO]),
                            ],
                        ),
                        ft.Switch(
                            value=densidade_atual == "compact",
                            active_color=COR_PRIMARIA,
                            on_change=lambda e: preferencias_pendentes.update(
                                densidade="compact" if e.control.value else "standard"
                            ),
                        ),
                    ],
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            spacing=2,
                            controls=[
                                ft.Text("Idioma", size=12, color=cores[TEXTO_PRINCIPAL]),
                                ft.Text("Português (Brasil)", size=10, color=cores[TEXTO_SECUNDARIO]),
                            ],
                        ),
                        ft.Icon(ft.Icons.LANGUAGE, size=18, color=cores[TEXTO_SECUNDARIO]),
                    ],
                ),
                ft.Divider(height=1, color=cores[BORDA]),
                ft.Row(
                    expand=True,
                    alignment=ft.MainAxisAlignment.END,
                    controls=[
                        ft.ElevatedButton(
                            "Aplicar alterações",
                            icon=ft.Icons.CHECK,
                            bgcolor=COR_PRIMARIA,
                            color=ft.Colors.WHITE,
                            on_click=aplicar_preferencias,
                        ),
                    ],
                ),
            ],
        )
    )

    return preferencias
