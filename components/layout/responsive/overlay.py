import flet as ft
from typing import Callable
from components.core.constants.constants import OVERLAY_MODAL

# Cria uma camada de sobreposição (overlay) escura para destacar a sidebar mobile
def criar_overlay(fechar_sidebar_callback: Callable[[], None]) -> ft.GestureDetector:
    return ft.GestureDetector(
        visible=False,  # Inicia invisível até que a sidebar seja aberta
        expand=True,    # Ocupa 100% da tela disponível
        mouse_cursor=ft.MouseCursor.BASIC,
        on_tap=lambda e: fechar_sidebar_callback(),  # Fecha a sidebar mobile ao clicar fora dela
        content=ft.Container(
            expand=True,
            bgcolor=OVERLAY_MODAL,  # Camada de fundo sobre o conteúdo atrás da sidebar.
        ),
    )
