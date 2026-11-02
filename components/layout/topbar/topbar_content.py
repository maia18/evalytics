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

    local_atual = (
        getattr(page, "localidade_instituicao", None)
        or obter_localizacao()
    )
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

    texto_localidade = ft.Text(
        local_atual,
        size=10,
        weight="w500",
        color=cores[TEXTO_PRINCIPAL],
        max_lines=1,
        overflow=ft.TextOverflow.ELLIPSIS,
    )

    def fechar_dialogo_localidade(dialogo: ft.AlertDialog) -> None:
        dialogo.open = False
        if dialogo in page.overlay:
            page.overlay.remove(dialogo)
        page.update()

    async def salvar_localidade(valor: str, dialogo: ft.AlertDialog) -> None:
        localidade = valor.strip()
        if not localidade:
            return
        try:
            preferencias = ft.SharedPreferences()
            await preferencias.set("evalytics.localidade_instituicao", localidade)
        except Exception:
            # Mantém a seleção na sessão atual mesmo se o armazenamento local
            # estiver indisponível nesta plataforma.
            pass
        page.localidade_instituicao = localidade
        texto_localidade.value = localidade
        fechar_dialogo_localidade(dialogo)

    def abrir_seletor_localidade(e=None) -> None:
        campo_localidade = ft.TextField(
            label="Localidade da instituição",
            hint_text="Ex.: Fortaleza - CE",
            value=texto_localidade.value,
            autofocus=True,
            width=360,
            on_submit=lambda evento: page.run_task(
                salvar_localidade, campo_localidade.value or "", dialogo_localidade
            ),
        )
        dialogo_localidade = ft.AlertDialog(
            modal=True,
            title=ft.Text("Localidade da instituição"),
            content=ft.Column(
                tight=True,
                spacing=10,
                controls=[
                    ft.Text(
                        "Defina a localidade que será exibida no cabeçalho.",
                        size=12,
                        color=cores.get("texto_secundario", ft.Colors.GREY_500),
                    ),
                    campo_localidade,
                ],
            ),
            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=lambda evento: fechar_dialogo_localidade(dialogo_localidade),
                ),
                ft.ElevatedButton(
                    "Salvar",
                    on_click=lambda evento: page.run_task(
                        salvar_localidade,
                        campo_localidade.value or "",
                        dialogo_localidade,
                    ),
                    bgcolor=COR_PRIMARIA,
                    color=ft.Colors.WHITE,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(dialogo_localidade)
        dialogo_localidade.open = True
        page.update()

    async def carregar_localidade_salva() -> None:
        try:
            preferencias = ft.SharedPreferences()
            localidade_salva = await preferencias.get("evalytics.localidade_instituicao")
        except Exception:
            return
        if isinstance(localidade_salva, str) and localidade_salva.strip():
            page.localidade_instituicao = localidade_salva.strip()
            texto_localidade.value = localidade_salva.strip()
            page.update()

    page.run_task(carregar_localidade_salva)

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
                        width=150,
                        padding=4,
                        border_radius=8,
                        bgcolor=cores[SURFACE],
                        tooltip="Alterar localidade exibida",
                        on_click=abrir_seletor_localidade,
                        content=ft.Row(
                            spacing=3,
                            controls=[
                                ft.Icon(ft.Icons.LOCATION_ON_OUTLINED, size=14, color=COR_PRIMARIA),
                                texto_localidade,
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
