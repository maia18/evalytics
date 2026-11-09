import flet as ft
from typing import Callable
from components.core.constants.constants import (
    CARD,
    BORDA,
    SUCESSO,
    AVISO,
)
from utils.services.indicadores.indicadores_repository import (
    atualizar_status_indicador,
)

def criar_linha_indicador(
    page: ft.Page,
    item: dict,
    abrir_modal_criterios: Callable[..., None],
    abrir_modal_edicao: Callable[..., None],
    preparar_exclusao: Callable[[dict], None],
    cores: dict[str, str],
) -> ft.Container:
    """
    Renderiza um card individual (linha) para um indicador na lista.
        Possui área clicável para abrir critérios e botões de ação isolados (editar/excluir).
    """

    '''
    Lógica de formatação condicional: 
        Determina a cor da "etiqueta" com base no status salvo no banco.
    '''
    status_texto = ft.Text(
        item.get("status", "ATIVO"),
        size=12,
        color=ft.Colors.WHITE,
        weight=ft.FontWeight.BOLD,
    )
    badge_status = ft.Container(
        padding=5,
        border_radius=4,
        ink=True,
        content=status_texto,
    )
    cor_destaque_indicador = (
        "#B69CFF" if cores[CARD] == "#2A2A2A" else "#5B21B6"
    )

    def atualizar_visual_status(status: str) -> None:
        status_texto.value = status
        badge_status.bgcolor = cores[SUCESSO] if status == "ATIVO" else cores[AVISO]

    def alternar_status(e: ft.ControlEvent) -> None:
        status_atual = str(item.get("status", "ATIVO")).upper()
        novo_status = "INATIVO" if status_atual == "ATIVO" else "ATIVO"
        indicador_id = item.get("id")

        if not atualizar_status_indicador(indicador_id, novo_status):
            page.snack_bar = ft.SnackBar(
                ft.Text("Não foi possível atualizar o status do indicador."),
                bgcolor=cores[AVISO],
            )
            page.snack_bar.open = True
            page.update()
            return

        item["status"] = novo_status
        atualizar_visual_status(novo_status)
        page.snack_bar = ft.SnackBar(
            ft.Text(f"Indicador marcado como {novo_status.lower()}."),
            bgcolor=cores[SUCESSO],
        )
        page.snack_bar.open = True
        page.update()

    atualizar_visual_status(str(item.get("status", "ATIVO")).upper())
    badge_status.on_click = alternar_status

    return ft.Container(
        padding=15,
        bgcolor=cores[CARD],

        # Borda sutil e arredondada envolvendo toda a linha.
        # Alternativa mais curta do Flet para isso seria: border=ft.border.all(1, cores[BORDA])
        border=ft.Border(
            top=ft.BorderSide(1, cores[BORDA]),
            bottom=ft.BorderSide(1, cores[BORDA]),
            left=ft.BorderSide(1, cores[BORDA]),
            right=ft.BorderSide(1, cores[BORDA]),
        ),
        border_radius=8,

        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                
                # 1. BLOCO DO TÍTULO (Clicável)
                ft.Container(
                    expand=True, # Diz a este contêiner para ocupar todo o espaço horizontal disponível na Row empurrando a tag e os botões para a extremidade direita. 
                    
                    content=ft.Text(
                        item["titulo"],
                        size=15,
                        weight=ft.FontWeight.W_500,
                        color=cor_destaque_indicador,
                    ),
                    
                    # Ao clicar no título, abre o modal de critérios. 
                    on_click=lambda e, i=item: abrir_modal_criterios(e, i), 
                ),

                # 2. ETIQUETA DE STATUS (Badge)
                badge_status,

                # 3. BLOCO DE AÇÕES (Ícones de Edição e Exclusão)
                ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.EDIT,
                            icon_color=cor_destaque_indicador,
                            tooltip="Editar",
                            on_click=lambda e, i=item: abrir_modal_edicao(e, i),
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            icon_color=ft.Colors.RED_700,
                            tooltip="Excluir",
                            on_click=lambda e, i=item: preparar_exclusao(i),
                        ),
                    ],
                ),
            ],
        ),
    )
