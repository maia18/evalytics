import flet as ft
from typing import Callable
from components.core.constants.constants import (
    TEXTO_PRINCIPAL, 
    SURFACE, 
    COR_PRIMARIA,
)
from utils.services.location.location_service import obter_localizacao
from .core.notifications.topbar_notifications import criar_componentes_notificacoes
from .core.account_menu import criar_menu_conta

def criar_topbar_content(
    page: ft.Page,
    titulo: str,
    subtitulo: str,
    dark_mode: bool,
    cores: dict[str, str],
    menu_button: ft.IconButton,
    atualizar_tema: Callable[[], None],
    mudar_tela: Callable[[str], None] | None = None,
    notificacoes_pendentes: int = 0,
) -> ft.ResponsiveRow:
    """Constrói a faixa de navegação superior (Cabeçalho da Página)."""

    local_atual = obter_localizacao()
    tela_muito_estreita = page.width is not None and page.width < 400
    titulo_exibido = titulo.split()[0] if tela_muito_estreita else titulo

    '''
    Extrai múltiplos componentes interligados relacionados a notificações.
        O "painel_notificacoes" é solto (não fica dentro da Row da Topbar), pois ele será colocado no `page.overlay` global.
    '''
    area_notificacoes, painel_notificacoes, badge_notificacoes, atualizar_lista = criar_componentes_notificacoes(page, cores)
    badge_notificacoes.visible = (
        badge_notificacoes.visible
        and getattr(page, "contador_notificacoes_ativo", True)
    )
    menu_conta = (
        criar_menu_conta(page, cores, mudar_tela)
        if mudar_tela
        else ft.CircleAvatar(
            radius=14,
            bgcolor=COR_PRIMARIA,
            color=ft.Colors.WHITE,
            content=ft.Text("U", size=10, weight=ft.FontWeight.W_600),
        )
    )
    notificacoes_visiveis = ft.Container(
        visible=getattr(page, "notificacoes_ativas", True),
        content=area_notificacoes,
    )

    conteudo = ft.ResponsiveRow(
        spacing=8,
        run_spacing=4,
        controls=[
            ft.Container(
                col={"xs": 12, "sm": 6, "md": 6, "lg": 6, "xl": 6, "xxl": 6},
                content=ft.Row(
                    spacing=6,
                    controls=[
                        menu_button,
                        ft.Column(
                            expand=1,
                            spacing=0,
                            controls=[
                                ft.Text(
                                    titulo_exibido,
                                    size=16,
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                    weight="bold",
                                    color=cores[TEXTO_PRINCIPAL],
                                ),
                                ft.Text(
                                    subtitulo,
                                    size=10,
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                    color=ft.Colors.GREY,
                                    visible=not tela_muito_estreita,
                                ),
                            ],
                        ),
                    ],
                ),
            ),
            # Em telas pequenas as ações passam para outra linha e quebram
            # naturalmente, em vez de comprimir os rótulos horizontalmente.
            ft.Container(
                col={"xs": 12, "sm": 6, "md": 6, "lg": 6, "xl": 6, "xxl": 6},
                content=ft.Row(
                    wrap=True,
                    alignment=ft.MainAxisAlignment.END,
                    spacing=4,
                    run_spacing=4,
                    controls=[
                    # Chip/Badge informativo da Localização Atual
                    ft.Container(
                        width=100,
                        padding=4,
                        border_radius=8,
                        bgcolor=cores[SURFACE],
                        content=ft.Row(
                            spacing=3,
                            controls=[
                                ft.Icon(ft.Icons.LOCATION_ON_OUTLINED, size=14, color=COR_PRIMARIA),
                                ft.Text(local_atual, size=10, weight="w500", color=cores[TEXTO_PRINCIPAL]),
                            ],
                        ),
                    ),
                    
                    # Ícone do sininho de notificações
                    notificacoes_visiveis,
                    menu_conta,
                    ],
                ),
            ),
        ],
    )
    
    '''
    MONKEY PATCHING (Atenção):
        O Python permite injetar atributos dinamicamente em objetos existentes.
            Estamos grudando referências do painel e do atualizador diretamente na instância  visual da `Row` (conteudo). 
            Isso permite que o `ResponsiveLayout` encontre o  `painel_notificacoes` para injetá-lo no `page.overlay` posteriormente.
    '''
    conteudo.badge_notificacoes = badge_notificacoes
    conteudo.painel_notificacoes = painel_notificacoes
    conteudo.atualizar_lista_notificacoes = atualizar_lista
    conteudo.area_notificacoes = notificacoes_visiveis

    return conteudo
