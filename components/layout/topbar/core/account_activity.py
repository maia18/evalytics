import asyncio
from datetime import date, datetime
from typing import Callable

import flet as ft

from components.core.constants.constants import COR_PRIMARIA, SURFACE, TEXTO_PRINCIPAL, TEXTO_SECUNDARIO
from components.core.router.rotas_cts import ROTA_AVALIACOES
from utils.services.avaliacoes.avaliacoes_service import listar_avaliacoes
from .account_shared import _exibir_dialogo
def _chave_data_atividade(valor) -> float:
    try:
        if isinstance(valor, datetime):
            return valor.timestamp()
        if isinstance(valor, date):
            return datetime.combine(valor, datetime.min.time()).timestamp()
        if isinstance(valor, str):
            data = datetime.fromisoformat(valor.replace("Z", "+00:00"))
            return data.timestamp()
    except (OverflowError, OSError, TypeError, ValueError):
        pass
    return 0.0


def _formatar_data_atividade(valor) -> str:
    try:
        if isinstance(valor, datetime):
            return valor.strftime("%d/%m/%Y")
        if isinstance(valor, date):
            return valor.strftime("%d/%m/%Y")
        if isinstance(valor, str):
            return datetime.fromisoformat(valor.replace("Z", "+00:00")).strftime("%d/%m/%Y")
    except (OverflowError, OSError, TypeError, ValueError):
        pass
    return "Data indisponível"


async def abrir_atividade_recente(
    page: ft.Page,
    cores: dict[str, str],
    mudar_tela: Callable[[str], None],
):
    lista_atividades = ft.Column(height=340, spacing=8, scroll=ft.ScrollMode.AUTO)
    conteudo = ft.Column(
        tight=True,
        spacing=12,
        controls=[
            ft.Text("Avaliações institucionais mais recentes.", size=12, color=cores[TEXTO_SECUNDARIO]),
            lista_atividades,
            ft.TextButton(
                "Ver todas as avaliações",
                icon=ft.Icons.ARROW_FORWARD,
                on_click=lambda e: mudar_tela(ROTA_AVALIACOES),
            ),
        ],
    )
    lista_atividades.controls.append(
        ft.Row(
            spacing=10,
            controls=[
                ft.ProgressRing(width=18, height=18, stroke_width=2),
                ft.Text("Carregando avaliações...", size=12, color=cores[TEXTO_SECUNDARIO]),
            ],
        )
    )
    _exibir_dialogo(page, "Atividade recente", conteudo, cores)

    avaliacoes = await asyncio.to_thread(listar_avaliacoes)
    recentes = sorted(
        avaliacoes,
        key=lambda item: _chave_data_atividade(item.get("data_avaliacao")),
        reverse=True,
    )[:5]

    lista_atividades.controls.clear()
    if not recentes:
        lista_atividades.controls.append(
            ft.Container(
                padding=16,
                border=ft.Border.all(1, ft.Colors.with_opacity(0.16, ft.Colors.GREY_400)),
                border_radius=10,
                content=ft.Text("Nenhuma avaliação encontrada.", size=12, color=cores[TEXTO_SECUNDARIO]),
            )
        )
    else:
        for avaliacao in recentes:
            curso = avaliacao.get("curso_nome") or "Curso sem identificação"
            data = _formatar_data_atividade(avaliacao.get("data_avaliacao"))
            lista_atividades.controls.append(
                ft.Container(
                    padding=12,
                    bgcolor=cores[SURFACE],
                    border=ft.Border.all(1, ft.Colors.with_opacity(0.16, ft.Colors.GREY_400)),
                    border_radius=10,
                    content=ft.Row(
                        spacing=10,
                        controls=[
                            ft.Container(
                                width=34,
                                height=34,
                                border_radius=9,
                                bgcolor=ft.Colors.with_opacity(0.12, COR_PRIMARIA),
                                alignment=ft.Alignment.CENTER,
                                content=ft.Icon(ft.Icons.ASSIGNMENT_OUTLINED, size=18, color=COR_PRIMARIA),
                            ),
                            ft.Column(
                                expand=True,
                                spacing=3,
                                controls=[
                                    ft.Text(
                                        curso,
                                        size=12,
                                        weight=ft.FontWeight.W_600,
                                        color=cores[TEXTO_PRINCIPAL],
                                        max_lines=1,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                    ),
                                    ft.Text(data, size=10, color=cores[TEXTO_SECUNDARIO]),
                                ],
                            ),
                        ],
                    ),
                )
            )
    page.update()


