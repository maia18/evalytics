import flet as ft
from typing import Callable
from components.core.constants.constants import FUNDO

def montar_view(
    route: str,
    cores: dict[str, str],
    sidebar_desktop: ft.Control,
    topbar: ft.Control,
    conteudo_principal: ft.Control,
    overlay: ft.Control,
    sidebar_mobile: ft.Control,
    ajustar_responsividade: Callable[..., None],
    page: ft.Page,
) -> ft.View:
    """Estrutura fisicamente a página final, definindo camadas (z-index) e eixos."""
    
    page.on_resize = ajustar_responsividade  # Vincula o resize nativo à função de ajuste
    ajustar_responsividade()  # Aplica a formatação inicial
    espacamento_conteudo = 10 if getattr(page, "preferencia_densidade_visual", "standard") == "compact" else 16
    return ft.View(
        route=route,
        padding=0,  # Remove espaçamento padrão ao redor da janela
        bgcolor=cores[FUNDO],  # Fundo global de acordo com a constante e o tema
        controls=[
            ft.Stack(  # Permite que sidebar_mobile e overlay "voem" sobre o conteúdo principal
                expand=True,
                controls=[
                    ft.Row(
                        expand=True,
                        spacing=0,
                        vertical_alignment=ft.CrossAxisAlignment.STRETCH,
                        controls=[
                            sidebar_desktop,

                            ft.Column(
                                expand=True,
                                spacing=0,
                                controls=[
                                    topbar,

                                    ft.Container(
                                        expand=True,
                                        padding=espacamento_conteudo,
                                        content=conteudo_principal,
                                    ),
                                ],
                            ),
                        ],
                    ),
                    
                    overlay,          # Camada oculta ativada ao abrir o menu mobile
                    sidebar_mobile,   # Menu fora de tela inicialmente
                ],
            )
        ],
    )
