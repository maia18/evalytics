import flet as ft
from typing import Callable
from components.core.constants.constants import (
    TEXTO_PRINCIPAL, 
    SURFACE, 
    COR_PRIMARIA,
)
from utils.services.location.location_service import (
    obter_localidade_instituicao,
    salvar_localidade_instituicao,
)
from database.services.institutions.institutions_service import (
    listar_campi_instituicao,
    obter_instituicao,
)
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

    instituicao = obter_instituicao()
    instituicao_id = str(instituicao.get("id") or "")
    sigla_instituicao = str(instituicao.get("sigla") or instituicao.get("nome") or "Instituição")
    campi = listar_campi_instituicao()
    catalogo_campi: dict[str, tuple[str, str, str]] = {}
    for campus in campi:
        campus_id = str(campus.get("id") or "").strip()
        nome = str(campus.get("nome") or "").strip()
        if not campus_id or not nome:
            continue
        municipio = str(campus.get("municipio") or "").strip()
        uf = str(campus.get("uf") or "").strip()
        local = " · ".join(parte for parte in (municipio, uf) if parte)
        rotulo_opcao = f"{nome} — {local}" if local else nome
        nome_curto = nome.removeprefix("Campus do ").removeprefix("Campus de ")
        catalogo_campi[campus_id] = (rotulo_opcao, f"{sigla_instituicao} · {nome_curto}", nome)

    localidade_salva = (
        getattr(page, "localidade_instituicao", None)
        or obter_localidade_instituicao(instituicao_id)
    )
    local_atual = localidade_salva if localidade_salva in catalogo_campi else None
    if local_atual is None and localidade_salva:
        local_atual = next(
            (campus_id for campus_id, (_, _, nome) in catalogo_campi.items()
             if nome.casefold() == localidade_salva.casefold()),
            None,
        )
    page.localidade_instituicao = local_atual
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
        catalogo_campi[local_atual][1] if local_atual else sigla_instituicao,
        size=10,
        weight="w500",
        color=cores[TEXTO_PRINCIPAL],
        max_lines=1,
        overflow=ft.TextOverflow.ELLIPSIS,
    )

    def largura_selo_localidade(texto: str) -> int:
        # Ajusta o chip ao rótulo, mantendo os nomes longos de campus legíveis.
        return max(84, min(154, round(len(texto) * 5.2 + 32)))

    selo_localidade = ft.Container(
        width=largura_selo_localidade(texto_localidade.value),
        padding=4,
        border_radius=8,
        bgcolor=cores[SURFACE],
        tooltip="Alterar campus",
        on_click=lambda e: abrir_seletor_localidade(e),
        content=ft.Row(
            spacing=3,
            controls=[
                ft.Icon(ft.Icons.LOCATION_ON_OUTLINED, size=14, color=COR_PRIMARIA),
                texto_localidade,
            ],
        ),
    )

    def fechar_dialogo_localidade(dialogo: ft.AlertDialog) -> None:
        if dialogo.open:
            page.pop_dialog()

    def salvar_localidade(valor: str, dialogo: ft.AlertDialog) -> None:
        localidade = valor.strip()
        if not localidade:
            return
        salvar_localidade_instituicao(localidade, instituicao_id)
        page.localidade_instituicao = localidade
        texto_localidade.value = catalogo_campi[localidade][1]
        selo_localidade.width = largura_selo_localidade(texto_localidade.value)
        fechar_dialogo_localidade(dialogo)

    def abrir_seletor_localidade(e=None) -> None:
        campo_localidade = ft.Dropdown(
            label="Campus da instituição",
            width=360,
            value=getattr(page, "localidade_instituicao", local_atual),
            options=[
                ft.dropdown.Option(key=campus_id, text=opcao[0])
                for campus_id, opcao in catalogo_campi.items()
            ],
            disabled=not catalogo_campi,
        )
        dialogo_localidade = ft.AlertDialog(
            modal=True,
            title=ft.Text("Campus da instituição"),
            content=ft.Column(
                tight=True,
                spacing=10,
                controls=[
                    campo_localidade,
                    *([] if catalogo_campi else [ft.Text("O cadastro de campi desta instituição ainda não foi configurado.")]),
                ],
            ),
            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=lambda evento: fechar_dialogo_localidade(dialogo_localidade),
                ),
                ft.ElevatedButton(
                    "Salvar",
                    disabled=not catalogo_campi,
                    on_click=lambda evento: salvar_localidade(
                        campo_localidade.value or "", dialogo_localidade
                    ),
                    bgcolor=COR_PRIMARIA,
                    color=ft.Colors.WHITE,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dialogo_localidade)

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
                    # Chip/Badge informativo do campus atual.
                    selo_localidade,
                    
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
