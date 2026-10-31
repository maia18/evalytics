import flet as ft
from typing import Callable
from components.layout.topbar.topbar import TopBar

def criar_topbar(
    page: ft.Page,
    titulo: str,
    subtitulo: str,
    dark_mode: bool,
    
    # Recebe os callbacks (funções) para gerenciar o estado global: abrir o menu e trocar o tema
    toggle_sidebar: Callable[[], None],
    atualizar_tema: Callable[[], None],
    mudar_tela: Callable[[str], None] | None = None,
) -> TopBar:
    """Padrão Factory: instancia o objeto TopBar repassando as dependências de forma limpa."""
    
    # Retorna uma nova instância da classe TopBar preenchida com as variáveis passadas[cite: 28]. Ao encapsular essa chamada, se no futuro o construtor da TopBar mudar, você precisará alterar apenas este arquivo, e não todas as telas que a utilizam.
    return TopBar(
        page=page,
        titulo_pagina=titulo,
        subtitulo=subtitulo,
        dark_mode=dark_mode,
        toggle_sidebar=toggle_sidebar,
        atualizar_tema=atualizar_tema,
        mudar_tela=mudar_tela,
    )
