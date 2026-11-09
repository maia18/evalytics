import flet as ft
from typing import Callable, Optional
from components.core.constants.constants import (
    BORDA,
    COR_PRIMARIA,
    TEXTO_PRINCIPAL,
    SUCESSO,
    PERIGO,
)
from models.configuracoes.widgets.estado_indicadores import EstadoIndicadores
from utils.services.indicadores.indicadores_repository import (
    atualizar_criterios_indicador,
)

NUM_CRITERIOS = 5

def criar_modal_criterios(
    page: ft.Page,
    estado: EstadoIndicadores,
    cores: dict[str, str],
) -> tuple[ft.AlertDialog, list[ft.TextField], Callable]:
    """Gera um popup para gerenciar os critérios de avaliação."""

    campos_criterios = [
        ft.TextField(
            label=f"Critério {i + 1}",
            multiline=True,
            width=600,
            border_color=cores[BORDA],
        )
        for i in range(NUM_CRITERIOS)
    ]

    def salvar_criterios(e: ft.ControlEvent) -> None:
        indicador_id = estado.item_alvo.get("id")

        if not indicador_id:
            page.snack_bar = ft.SnackBar(
                ft.Text(
                    "Não foi possível identificar o indicador."
                ),
                bgcolor=cores[PERIGO],
            )
            page.snack_bar.open = True
            page.update()
            return

        novos_criterios = {
            str(i + 1): (
                campos_criterios[i].value or ""
            ).strip()
            for i in range(NUM_CRITERIOS)
        }

        sucesso = atualizar_criterios_indicador(
            indicador_id,
            novos_criterios,
        )

        if not sucesso:
            page.snack_bar = ft.SnackBar(
                ft.Text(
                    "Não foi possível atualizar os critérios."
                ),
                bgcolor=cores[PERIGO],
            )
            page.snack_bar.open = True
            page.update()
            return

        page.snack_bar = ft.SnackBar(
            ft.Text("Critérios atualizados com sucesso!"),
            bgcolor=cores[SUCESSO],
        )
        page.snack_bar.open = True

        modal.open = False
        page.update()

    modal = ft.AlertDialog(
        modal=True,
        title=ft.Text(
            "Editar Critérios",
            size=20,
            weight=ft.FontWeight.BOLD,
            color=cores[TEXTO_PRINCIPAL],
        ),
        content=ft.Column(
            width=600,
            height=450,
            scroll=ft.ScrollMode.AUTO,
            spacing=15,
            controls=[
                ft.Container(
                    padding=ft.Padding.only(top=8),
                    content=campos_criterios[0],
                ),
                *campos_criterios[1:],
            ],
        ),
        actions=[
            ft.TextButton(
                "Cancelar",
                on_click=lambda e: setattr(modal, "open", False),
            ),
            ft.ElevatedButton(
                "Salvar",
                on_click=salvar_criterios,
                bgcolor=cores[COR_PRIMARIA],
                color=ft.Colors.WHITE,
            ),
        ],
    )

    def abrir_modal_criterios(
        e: Optional[ft.ControlEvent],
        indicador_selecionado: dict,
    ) -> None:
        estado.definir_item_alvo(indicador_selecionado)

        criterios_atuais = indicador_selecionado.get(
            "criterios",
            {},
        )

        for i in range(NUM_CRITERIOS):
            valor_salvo = criterios_atuais.get(
                str(i + 1),
                criterios_atuais.get(i + 1, ""),
            )

            campos_criterios[i].value = valor_salvo

        if modal not in page.overlay:
            page.overlay.append(modal)

        modal.open = True
        page.update()

    return modal, campos_criterios, abrir_modal_criterios
