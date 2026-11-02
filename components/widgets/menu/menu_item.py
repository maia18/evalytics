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
    conteudo = ft.Row(
        spacing=10,
        controls=[
            ft.Icon(
                icone,
                size=18, # Sutilmente menor que a versão colapsada (24) para balancear o design com o texto)
                color=("#B69CFF" if dark_mode else COR_PRIMARIA) if ativo else (ft.Colors.GREY_700 if not dark_mode else ft.Colors.GREY_300),
            ),
            ft.Text(
                texto,
                size=13,
                weight="w600" if ativo else "w500",
                color=("#B69CFF" if dark_mode else COR_PRIMARIA) if ativo else cor_texto,
            ),
        ], 
    )
    
    # Retorna o componente base injetando a linha (Row) recém-criada
    return criar_botao_menu_base(
        content=conteudo,
        rota=rota,
        dark_mode=dark_mode,
        mudar_tela=mudar_tela,
        expand=True,
        ativo=ativo,
    )
