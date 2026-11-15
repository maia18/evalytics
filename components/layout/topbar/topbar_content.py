import flet as ft
from typing import Callable
from components.core.constants.constants import (
    TEXTO_PRINCIPAL, 
    SURFACE, 
    COR_PRIMARIA,
)
from database.services.institutions.institutions_service import (
    obter_instituicao,
)
from database.services.cursos.firestore_courses import obter_cursos_db
from components.core.auth.auth_state import auth_state
from utils.services.cursos.curso_utils import listar_cursos_associados_ao_coordenador
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
    sigla_instituicao = str(
        instituicao.get("sigla") or instituicao.get("nome") or "Instituição"
    )
    usuario = auth_state.usuario or {}
    cursos_coordenados = listar_cursos_associados_ao_coordenador(
        obter_cursos_db(), str(usuario.get("email") or "")
    )
    curso_id_ativo = str(usuario.get("curso_id_ativo") or "")
    curso_ativo = next(
        (curso for curso in cursos_coordenados if str(curso.get("id")) == curso_id_ativo),
        None,
    )
    if curso_ativo:
        rotulo_contexto = str(curso_ativo.get("nome") or "Curso coordenado")
    elif len(cursos_coordenados) == 1:
        rotulo_contexto = str(cursos_coordenados[0].get("nome") or "Curso coordenado")
    elif cursos_coordenados and curso_id_ativo == "*":
        rotulo_contexto = "Todos os cursos"
    elif cursos_coordenados:
        rotulo_contexto = "Meus cursos"
    else:
        rotulo_contexto = sigla_instituicao
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
    texto_contexto = ft.Text(
        rotulo_contexto,
        size=10,
        weight="w500",
        color=cores[TEXTO_PRINCIPAL],
        max_lines=1,
        overflow=ft.TextOverflow.ELLIPSIS,
    )

    def abrir_seletor_curso(e=None) -> None:
        if len(cursos_coordenados) < 2:
            return
        opcoes_curso = [
            ft.dropdown.Option(key="*", text="Todos os meus cursos")
        ] + [
            ft.dropdown.Option(
                key=str(curso.get("id")),
                text=str(curso.get("nome") or "Curso sem nome"),
            )
            for curso in cursos_coordenados
            if curso.get("id")
        ]
        ids_cursos_coordenados = {
            str(curso.get("id")) for curso in cursos_coordenados if curso.get("id")
        }
        valor_seletor = (
            curso_id_ativo
            if curso_id_ativo == "*" or curso_id_ativo in ids_cursos_coordenados
            else "*"
        )
        seletor_curso = ft.Dropdown(
            label="Curso sob coordenação",
            width=360,
            value=valor_seletor,
            options=opcoes_curso,
        )
        dialogo_curso = ft.AlertDialog(
            modal=True,
            title=ft.Text("Escopo da coordenação"),
            content=ft.Column(
                tight=True,
                spacing=10,
                controls=[
                    ft.Text("As análises serão limitadas ao curso selecionado."),
                    seletor_curso,
                ],
            ),
            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=lambda evento: page.pop_dialog(),
                ),
                ft.ElevatedButton(
                    "Aplicar",
                    bgcolor=COR_PRIMARIA,
                    color=ft.Colors.WHITE,
                    on_click=lambda evento: aplicar_escopo_curso(
                        seletor_curso.value or "*"
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dialogo_curso)

    def aplicar_escopo_curso(curso_id: str) -> None:
        if curso_id != "*" and not any(
            str(curso.get("id")) == curso_id for curso in cursos_coordenados
        ):
            return
        usuario["curso_id_ativo"] = curso_id
        rota_atual = getattr(page, "rota_navegacao_atual", None) or page.route
        if mudar_tela and rota_atual:
            mudar_tela(rota_atual)
        else:
            page.update()

    selo_contexto = ft.Container(
        width=max(84, min(190, round(len(rotulo_contexto) * 5.2 + 32))),
        padding=4,
        border_radius=8,
        bgcolor=cores[SURFACE],
        tooltip=(
            "Selecionar curso sob coordenação"
            if len(cursos_coordenados) > 1
            else "Curso sob coordenação"
            if cursos_coordenados
            else "Instituição"
        ),
        on_click=abrir_seletor_curso if len(cursos_coordenados) > 1 else None,
        ink=len(cursos_coordenados) > 1,
        content=ft.Row(
            spacing=3,
            controls=[
                ft.Icon(
                    ft.Icons.SCHOOL_OUTLINED
                    if cursos_coordenados
                    else ft.Icons.ACCOUNT_BALANCE_OUTLINED,
                    size=14,
                    color=COR_PRIMARIA,
                ),
                texto_contexto,
                *([ft.Icon(ft.Icons.ARROW_DROP_DOWN, size=14, color=cores[TEXTO_PRINCIPAL])]
                  if len(cursos_coordenados) > 1 else []),
            ],
        ),
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
                    # Escopo ativo da coordenação ou instituição atual.
                    selo_contexto,
                    
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
