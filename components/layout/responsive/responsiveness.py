import flet as ft
from typing import Callable, Optional
from components.layout.responsive.layout.layout_breakpoints import obter_categoria_layout
from components.layout.sidebar.sidebar_factory import criar_sidebar_desktop
from components.core.constants.constants import (
    LARGURA_SIDEBAR_EXPANDIDA,
    LARGURA_SIDEBAR_COLAPSADA,
)

def ajustar_responsividade(
    page: ft.Page,
    sidebar_desktop: ft.Control,
    topbar: ft.Control,
    fechar_sidebar: Callable[[], None],
    dark_mode: bool,
    mudar_tela: Optional[Callable[[str], None]],
) -> None:
    """Ajusta o layout da interface conforme a largura da janela."""
    
    # Consulta a categoria atual usando a função isolada
    categoria = obter_categoria_layout(page.width)

    if sidebar_desktop.data == categoria:
        return  # Nenhuma mudança de categoria: evita reconstrução desnecessária

    sidebar_desktop.data = categoria  # Cacheia a categoria atual no próprio controle

    if categoria == "mobile":
        sidebar_desktop.visible = False  # Oculta a sidebar de desktop
        sidebar_desktop.width = 0        # Remove seu preenchimento de largura
        topbar.menu_button.visible = True  # Habilita o botão 'hamburguer' mobile
    else:
        sidebar_desktop.visible = True     # Traz a sidebar de desktop de volta à vista
        topbar.menu_button.visible = False  # Esconde o botão de menu mobile
        fechar_sidebar()  # Força o fechamento da versão mobile, caso estivesse aberta

        # Ajuste adaptativo extra: menu diminui para modo ícone em telas médias
        preferencia_recolhida = getattr(page, "sidebar_recolhida", None)
        sidebar_recolhida = (
            bool(preferencia_recolhida)
            if preferencia_recolhida is not None
            else categoria == "compacta"
        )
        if hasattr(sidebar_desktop, "definir_recolhida"):
            sidebar_desktop.definir_recolhida(sidebar_recolhida, atualizar=False)
        else:
            sidebar_desktop.width = (
                LARGURA_SIDEBAR_COLAPSADA
                if sidebar_recolhida
                else LARGURA_SIDEBAR_EXPANDIDA
            )
            sidebar_desktop.content = criar_sidebar_desktop(
                page=page,
                dark_mode=dark_mode,
                mudar_tela=mudar_tela,
                collapsed=sidebar_recolhida,
            ).content

    page.update()  # Atualiza a interface com os novos tamanhos
