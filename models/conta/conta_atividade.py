import asyncio

import flet as ft

from components.core.constants.constants import BORDA, COR_PRIMARIA, TEXTO_PRINCIPAL, TEXTO_SECUNDARIO
from components.core.router.rotas_cts import ROTA_AVALIACOES
from database.services.cursos.firestore_courses import obter_cursos_db
from models.conta.conta_utils import _card, _data_formatada, _data_ordenacao
from utils.services.avaliacoes.avaliacoes_service import listar_avaliacoes
def criar_secao_atividade(page, layout, cores, mudar_tela):
    lista_atividade = ft.Column(
        height=280,
        spacing=0,
        scroll=ft.ScrollMode.AUTO,
        controls=[
            ft.Row(
                spacing=10,
                controls=[
                    ft.ProgressRing(width=17, height=17, stroke_width=2),
                    ft.Text("Carregando atividade recente...", size=12, color=cores[TEXTO_SECUNDARIO]),
                ],
            )
        ],
    )

    def linha_atividade(avaliacao: dict) -> ft.Control:
        respostas = avaliacao.get("respostas", {})
        total_respostas = len(respostas) if isinstance(respostas, dict) else 0
        return ft.Container(
            padding=ft.Padding.symmetric(vertical=10, horizontal=2),
            border=ft.Border(bottom=ft.BorderSide(1, cores[BORDA])),
            ink=True,
            on_click=lambda e: mudar_tela(ROTA_AVALIACOES),
            content=ft.Row(
                spacing=10,
                controls=[
                    ft.Icon(ft.Icons.ASSIGNMENT_OUTLINED, size=18, color=COR_PRIMARIA),
                    ft.Column(
                        expand=True,
                        spacing=3,
                        controls=[
                            ft.Text(
                                str(avaliacao.get("curso_nome") or "Curso sem identificação"),
                                size=12,
                                weight=ft.FontWeight.W_600,
                                color=cores[TEXTO_PRINCIPAL],
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            ft.Text(
                                f"{_data_formatada(avaliacao.get('data_avaliacao'))} · {total_respostas} respostas",
                                size=10,
                                color=cores[TEXTO_SECUNDARIO],
                            ),
                        ],
                    ),
                    ft.Icon(ft.Icons.CHEVRON_RIGHT, size=18, color=cores[TEXTO_SECUNDARIO]),
                ],
            ),
        )

    async def carregar_atividade() -> None:
        try:
            avaliacoes, cursos = await asyncio.gather(
                asyncio.to_thread(listar_avaliacoes),
                asyncio.to_thread(obter_cursos_db),
            )
            cursos_validos = {
                str(curso.get("nome") or "").strip().casefold()
                for curso in cursos
                if str(curso.get("nome") or "").strip()
            }
            avaliacoes_validas = [
                avaliacao
                for avaliacao in avaliacoes
                if str(avaliacao.get("curso_nome") or "").strip().casefold() in cursos_validos
            ]
            avaliacoes_validas.sort(
                key=lambda item: _data_ordenacao(item.get("data_avaliacao")),
                reverse=True,
            )
            recentes = avaliacoes_validas[:8]
            lista_atividade.controls = (
                [linha_atividade(item) for item in recentes]
                if recentes
                else [
                    ft.Container(
                        padding=ft.Padding.symmetric(vertical=18),
                        content=ft.Text("Nenhuma atividade recente encontrada.", size=12, color=cores[TEXTO_SECUNDARIO]),
                    )
                ]
            )
        except Exception:
            lista_atividade.controls = [
                ft.Text("Não foi possível carregar a atividade agora.", size=12, color=ft.Colors.RED_400)
            ]
        page.update()

    cartao_atividade = _card(
        layout,
        ft.Column(
            spacing=8,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            spacing=3,
                            controls=[
                                ft.Text("Atividade recente", size=16, weight=ft.FontWeight.W_700, color=cores[TEXTO_PRINCIPAL]),
                                ft.Text("Últimas avaliações registradas na instituição.", size=11, color=cores[TEXTO_SECUNDARIO]),
                            ],
                        ),
                        ft.TextButton(
                            "Ver todas",
                            icon=ft.Icons.ARROW_FORWARD,
                            on_click=lambda e: mudar_tela(ROTA_AVALIACOES),
                        ),
                    ],
                ),
                lista_atividade,
            ],
        )
    )

    return cartao_atividade, carregar_atividade
