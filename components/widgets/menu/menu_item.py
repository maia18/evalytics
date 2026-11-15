import flet as ft
from typing import Callable, Optional
from components.core.constants.constants import COR_PRIMARIA
from components.widgets.menu.menu_button_base import criar_botao_menu_base

def criar_item_menu(
    icone: str,
    texto: str,
    rota: str,
    dark_mode: bool,
    cor_texto: str,
    mudar_tela: Optional[Callable[[str], None]],
    ativo: bool = False,
) -> ft.Container:
    """Cria o botão de navegação tradicional: ícone à esquerda alinhado a um texto."""
    
    # Prepara o bloco visual: organiza ícone e texto lado a lado (Row)
    cor_ativo = "#B69CFF" if dark_mode else COR_PRIMARIA
    cor_icone = (
        cor_ativo
        if ativo
        else ft.Colors.GREY_700 if not dark_mode else ft.Colors.GREY_300
    )
    cor_texto_base = cor_ativo if ativo else cor_texto
    icone_menu = ft.Icon(
        icone,
        size=18,
        color=cor_icone,
    )
    texto_menu = ft.Text(
        texto,
        size=13,
        weight="w600" if ativo else "w500",
        color=cor_texto_base,
    )
    conteudo = ft.Row(
        spacing=10,
        controls=[
            icone_menu,
            texto_menu,
        ], 
    )
    
    # Retorna o componente base injetando a linha (Row) recém-criada
    botao = criar_botao_menu_base(
        content=conteudo,
        rota=rota,
        dark_mode=dark_mode,
        mudar_tela=mudar_tela,
        expand=True,
        ativo=ativo,
    )

    def animar_hover(e: ft.ControlEvent) -> None:
        sobre = e.data == "true"
        icone_menu.color = cor_ativo if sobre or ativo else cor_icone
        texto_menu.color = cor_ativo if sobre or ativo else cor_texto
        texto_menu.weight = "w600" if sobre or ativo else "w500"
        e.page.update()

    botao.content.on_hover = animar_hover
    return botao
