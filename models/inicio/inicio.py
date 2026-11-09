import asyncio
import logging
import flet as ft
from typing import Callable

from components.core.constants.constants import TEXTO_PRINCIPAL, TEXTO_SECUNDARIO
from components.core.constants.texts import TXTS_INICIO
from components.layout.responsive.responsive import ResponsiveLayout
from database.services.cursos.firestore_courses import (
    curso_esta_ativo,
)
from database.services.dashboard.dashboard_utils import normalizar_nota
from utils.services.avaliacoes.avaliacoes_service import carregar_cursos_e_avaliacoes

from models.inicio.inicio_widgets import (
    _chave_data,
    _formatar_data,
    _mes_da_data,
    _criar_painel_tendencia,
    _criar_indicador,
    _criar_painel_cursos,
    _criar_secao_avaliacoes,
)

logger = logging.getLogger(__name__)


def ViewInicio(page: ft.Page, mudar_tela: Callable[[str], None]) -> ft.View:
    """Constrói a tela inicial com boas-vindas, indicadores e atividades recentes."""
    layout = ResponsiveLayout(
        page,
        TXTS_INICIO[0],
        TXTS_INICIO[1],
        mudar_tela=mudar_tela,
    )

    cursos: list[dict] = []
    avaliacoes: list[dict] = []
    # Reserva espaço para o cabeçalho e a faixa de cards, ajustando os painéis
    # à altura da janela para evitar rolagem desnecessária em tela cheia.
    altura_paineis = max(300, min(460, int((page.height or 768) * 0.56)))
    descricao_boas_vindas = "Acompanhe avaliações e atividade dos cursos."

    cabecalho_conteudo = ft.Column(
        spacing=4,
        controls=[
            ft.Text(
                "Visão geral",
                weight=ft.FontWeight.W_700,
                size=24,
                color=layout.cores[TEXTO_PRINCIPAL],
            ),
            ft.Text(
                descricao_boas_vindas,
                size=12,
                color=layout.cores[TEXTO_SECUNDARIO],
            ),
        ],
    )

    colunas_kpi = {"xs": 12, "sm": 6, "md": 3, "lg": 3}
    indicadores = ft.ResponsiveRow(
        spacing=12,
        run_spacing=12,
        controls=[
            _criar_indicador(
                layout,
                "Média geral",
                "—",
                ft.Icons.STAR_OUTLINE,
                colunas_kpi,
                "Média das respostas válidas",
            ),
            _criar_indicador(
                layout,
                "Respostas por avaliação",
                "—",
                ft.Icons.FORMAT_LIST_BULLETED,
                colunas_kpi,
                "Média de respostas em cada registro",
            ),
            _criar_indicador(
                layout,
                "Cobertura dos cursos",
                "—",
                ft.Icons.SCHOOL_OUTLINED,
                colunas_kpi,
                "Carregando dados",
            ),
            _criar_indicador(
                layout,
                "Última avaliação",
                "—",
                ft.Icons.EVENT_AVAILABLE_OUTLINED,
                colunas_kpi,
                "Carregando dados",
            ),
        ],
    )

    painel_tendencia = _criar_painel_tendencia(layout, avaliacoes, altura_paineis)
    painel_cursos = _criar_painel_cursos(layout, avaliacoes, cursos, altura_paineis)
    referencias_paineis = {"tendencia": painel_tendencia, "cursos": painel_cursos}
    paineis_resumo = ft.ResponsiveRow(
        spacing=16,
        run_spacing=16,
        controls=[
            ft.Container(
                col={"xs": 12, "sm": 12, "md": 6, "lg": 6},
                content=referencias_paineis["tendencia"],
            ),
            ft.Container(
                col={"xs": 12, "sm": 12, "md": 6, "lg": 6},
                content=referencias_paineis["cursos"],
            ),
        ],
    )

    conteudo = ft.Column(
        expand=True,
        spacing=8,
        scroll=ft.ScrollMode.AUTO,
        controls=[
            cabecalho_conteudo,
            indicadores,
            paineis_resumo,
        ],
    )

    layout.add_content(conteudo)
    view = layout.criar_view("/inicio")
    ajustar_layout_original = layout.controller.ajustar_responsividade

    async def carregar_dados_inicio() -> None:
        try:
            cursos_carregados, avaliacoes_carregadas = await asyncio.to_thread(
                carregar_cursos_e_avaliacoes
            )
        except Exception:
            logger.exception("Falha ao carregar os dados da tela inicial.")
            return

        cursos_existentes = {
            str(curso.get("nome") or "").strip().casefold()
            for curso in cursos_carregados
            if str(curso.get("nome") or "").strip()
        }
        avaliacoes_carregadas = [
            avaliacao
            for avaliacao in avaliacoes_carregadas
            if str(avaliacao.get("curso_nome") or "").strip().casefold()
            in cursos_existentes
        ]
        avaliacoes_carregadas.sort(
            key=lambda item: _chave_data(item.get("data_avaliacao")),
            reverse=True,
        )

        total_respostas = 0
        notas_validas: list[float] = []
        for avaliacao in avaliacoes_carregadas:
            respostas = avaliacao.get("respostas", {})
            if not isinstance(respostas, dict):
                continue
            total_respostas += len(respostas)
            notas_validas.extend(
                nota
                for resposta in respostas.values()
                if (nota := normalizar_nota(resposta)) is not None
            )

        cursos_ativos_nomes = {
            str(curso.get("nome") or "").strip().casefold()
            for curso in cursos_carregados
            if curso_esta_ativo(curso) and str(curso.get("nome") or "").strip()
        }
        cursos_ativos_avaliados = {
            str(avaliacao.get("curso_nome") or "").strip().casefold()
            for avaliacao in avaliacoes_carregadas
            if str(avaliacao.get("curso_nome") or "").strip().casefold()
            in cursos_ativos_nomes
        }
        cobertura_cursos = (
            f"{round(len(cursos_ativos_avaliados) / len(cursos_ativos_nomes) * 100)}%"
            if cursos_ativos_nomes
            else "—"
        )
        cobertura_contexto = (
            f"{len(cursos_ativos_avaliados)} de {len(cursos_ativos_nomes)} cursos ativos"
            if cursos_ativos_nomes
            else "Nenhum curso ativo cadastrado"
        )
        media_geral = (
            f"{sum(notas_validas) / len(notas_validas):.1f} / 5.0"
            if notas_validas
            else "—"
        )
        respostas_por_avaliacao = (
            f"{total_respostas / len(avaliacoes_carregadas):.1f}"
            if avaliacoes_carregadas
            else "—"
        ).replace(".", ",")
        ultima_avaliacao = avaliacoes_carregadas[0] if avaliacoes_carregadas else None
        ultima_data = (
            _formatar_data(ultima_avaliacao.get("data_avaliacao"))
            if ultima_avaliacao
            else "—"
        )
        ultima_data_contexto = (
            str(ultima_avaliacao.get("curso_nome") or "Curso não informado")
            if ultima_avaliacao
            else "Nenhuma avaliação registrada"
        )
        indicadores.controls = [
            _criar_indicador(layout, "Média geral", media_geral, ft.Icons.STAR_OUTLINE, colunas_kpi, "Média das respostas válidas"),
            _criar_indicador(layout, "Respostas por avaliação", respostas_por_avaliacao, ft.Icons.FORMAT_LIST_BULLETED, colunas_kpi, "Média de respostas em cada registro"),
            _criar_indicador(layout, "Cobertura dos cursos", cobertura_cursos, ft.Icons.SCHOOL_OUTLINED, colunas_kpi, cobertura_contexto),
            _criar_indicador(layout, "Última avaliação", ultima_data, ft.Icons.EVENT_AVAILABLE_OUTLINED, colunas_kpi, ultima_data_contexto),
        ]
        referencias_paineis["tendencia"] = _criar_painel_tendencia(
            layout, avaliacoes_carregadas, altura_paineis
        )
        referencias_paineis["cursos"] = _criar_painel_cursos(
            layout, avaliacoes_carregadas, cursos_carregados, altura_paineis
        )
        paineis_resumo.controls[0].content = referencias_paineis["tendencia"]
        paineis_resumo.controls[1].content = referencias_paineis["cursos"]
        page.update()

    def ajustar_inicio_ao_redimensionar(e=None) -> None:
        ajustar_layout_original(e)
        altura = max(300, min(460, int((page.height or 768) * 0.56)))
        painel_tendencia_atual = referencias_paineis["tendencia"]
        painel_cursos_atual = referencias_paineis["cursos"]
        painel_tendencia_atual.height = altura
        painel_cursos_atual.height = altura

        # Redimensiona a área do gráfico e suas barras, mantendo as três
        # colunas proporcionais ao espaço vertical disponível.
        controles_grafico = painel_tendencia_atual.content.controls
        area_grafico = controles_grafico[1]
        area_grafico.height = max(180, altura - 120)
        grafico = area_grafico.content
        if isinstance(grafico, ft.Row):
            altura_maxima_barra = max(80, altura - 202)
            for coluna in grafico.controls:
                area_barra = coluna.content.controls[1]
                area_barra.height = max(100, altura - 190)
                barra = area_barra.content
                proporcao = barra.data
                if proporcao is not None:
                    barra.height = max(4, round(altura_maxima_barra * proporcao))

        lista_cursos = painel_cursos_atual.content.controls[1]
        lista_cursos.height = max(180, altura - 100)
        page.update()

    page.on_resize = ajustar_inicio_ao_redimensionar
    page.run_task(carregar_dados_inicio)
    return view
