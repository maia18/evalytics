import flet as ft
from datetime import datetime
from typing import Callable

from components.core.constants.constants import (
    CARD,
    CARD_SECUNDARIO,
    BORDA,
    TEXTO_PRINCIPAL,
    TEXTO_SECUNDARIO,
    COR_PRIMARIA,
)
from components.core.constants.texts import (
    NOMES_EIXOS,
    TXTS_INICIO,
)
from components.core.router.rotas_cts import (
    ROTA_DASHBOARD_AVALIACOES,
    ROTA_FORMULARIO,
)
from components.layout.responsive.responsive import ResponsiveLayout
from database.services.cursos.firestore_courses import (
    obter_cursos_db,
    curso_esta_ativo,
)
from database.services.dashboard.dashboard_utils import obter_mapa_eixos, normalizar_nota
from utils.services.avaliacoes.avaliacoes_service import listar_avaliacoes
from utils.services.relatorio.relatorio_utils import obter_semestre


def _chave_data(data) -> float:
    """Gera uma chave de ordenação para datas Firestore, datetime ou ISO."""
    if hasattr(data, "timestamp"):
        try:
            return float(data.timestamp())
        except (TypeError, ValueError, OSError):
            pass
    if isinstance(data, str) and data.strip():
        try:
            valor = datetime.fromisoformat(data.strip().replace("Z", "+00:00"))
            return valor.timestamp()
        except (TypeError, ValueError, OSError):
            pass
    return 0.0


def _formatar_data(data) -> str:
    if hasattr(data, "strftime"):
        return data.strftime("%d/%m/%Y")
    if isinstance(data, str) and data.strip():
        try:
            valor = datetime.fromisoformat(data.strip().replace("Z", "+00:00"))
            return valor.strftime("%d/%m/%Y")
        except (TypeError, ValueError):
            return data[:10]
    return "Data não informada"


def _mes_da_data(data) -> tuple[int, int] | None:
    """Extrai ano e mês de valores datetime do Firestore ou texto ISO."""
    if hasattr(data, "year") and hasattr(data, "month"):
        try:
            return int(data.year), int(data.month)
        except (TypeError, ValueError):
            pass
    if isinstance(data, str) and data.strip():
        try:
            valor = datetime.fromisoformat(data.strip().replace("Z", "+00:00"))
            return valor.year, valor.month
        except (TypeError, ValueError):
            pass
    return None


def _criar_painel_tendencia(
    layout: ResponsiveLayout,
    avaliacoes: list[dict],
    altura_painel: int,
) -> ft.Container:
    """Exibe em colunas os resultados por eixo do mês mais recente com dados."""
    nomes_meses = (
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
    )
    mapa_eixos_atual = obter_mapa_eixos()
    dados_por_mes: dict[tuple[int, int], dict] = {}

    for avaliacao in avaliacoes:
        mes = _mes_da_data(avaliacao.get("data_avaliacao"))
        if mes is None:
            continue
        respostas = avaliacao.get("respostas", {})
        if not isinstance(respostas, dict):
            respostas = {}

        dados_mes = dados_por_mes.setdefault(
            mes,
            {
                "avaliacoes": 0,
                "respostas": 0,
                "eixos": {1: [], 2: [], 3: []},
            },
        )
        dados_mes["avaliacoes"] += 1
        dados_mes["respostas"] += len(respostas)

        # Prefere o eixo salvo junto à avaliação; avaliações antigas usam o catálogo atual.
        mapa_eixos_avaliacao = dict(mapa_eixos_atual)
        perguntas = avaliacao.get("perguntas", [])
        if isinstance(perguntas, list):
            for pergunta in perguntas:
                if not isinstance(pergunta, dict) or not pergunta.get("id"):
                    continue
                try:
                    mapa_eixos_avaliacao[str(pergunta["id"])] = int(pergunta.get("eixo"))
                except (TypeError, ValueError):
                    continue

        for indicador_id, resposta in respostas.items():
            nota = normalizar_nota(resposta)
            if nota is None:
                continue
            try:
                eixo_id = int(mapa_eixos_avaliacao.get(str(indicador_id)))
            except (TypeError, ValueError):
                continue
            if eixo_id in dados_mes["eixos"]:
                dados_mes["eixos"][eixo_id].append(nota)

    if dados_por_mes:
        ano, mes = max(dados_por_mes)
        dados_mais_recentes = dados_por_mes[(ano, mes)]
        cores_eixos = (COR_PRIMARIA, "#34D399", "#F87171")
        colunas = []
        detalhe_hover = ft.Text(
            size=10,
            weight=ft.FontWeight.W_600,
            color=layout.cores[TEXTO_SECUNDARIO],
        )

        for eixo_id, nome_eixo in NOMES_EIXOS.items():
            notas = dados_mais_recentes["eixos"].get(eixo_id, [])
            media = sum(notas) / len(notas) if notas else None
            altura_maxima_barra = max(80, altura_painel - 202)
            altura_barra = max(4, round(altura_maxima_barra * media / 5)) if media is not None else 3
            rotulo_media = f"{media:.1f} / 5,0" if media is not None else "Sem respostas"
            cor_eixo = cores_eixos[eixo_id - 1]
            barra = ft.Container(
                width=44,
                height=altura_barra,
                data=(media / 5) if media is not None else None,
                bgcolor=cor_eixo if media is not None else layout.cores[CARD_SECUNDARIO],
                border_radius=6,
                animate=ft.Animation(180, ft.AnimationCurve.EASE_OUT),
            )
            coluna = ft.Container(
                expand=True,
                padding=6,
                border_radius=10,
                border=ft.Border.all(1, "#00000000"),
                animate=ft.Animation(180, ft.AnimationCurve.EASE_OUT),
                animate_scale=ft.Animation(180, ft.AnimationCurve.EASE_OUT),
                on_hover=lambda e, nome=nome_eixo, valor=media, total=len(notas), cor=cor_eixo, barra_ref=barra, altura_ref=altura_barra: destacar_coluna(
                    e, nome, valor, total, cor, barra_ref, altura_ref
                ),
                content=ft.Column(
                    expand=True,
                    alignment=ft.MainAxisAlignment.START,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=7,
                    controls=[
                        ft.Text(
                            rotulo_media,
                            size=10,
                            weight=ft.FontWeight.W_600,
                            color=layout.cores[TEXTO_PRINCIPAL],
                        ),
                        ft.Container(
                            height=max(100, altura_painel - 190),
                            alignment=ft.Alignment.BOTTOM_CENTER,
                            content=barra,
                        ),
                        ft.Container(
                            height=28,
                            alignment=ft.Alignment.CENTER,
                            content=ft.Text(
                                nome_eixo,
                                size=10,
                                color=layout.cores[TEXTO_PRINCIPAL],
                                text_align=ft.TextAlign.CENTER,
                                max_lines=2,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                        ),
                    ],
                ),
            )
            colunas.append(coluna)

        def destacar_coluna(
            e,
            nome: str,
            media: float | None,
            total: int,
            cor: str,
            barra: ft.Container,
            altura_barra: int,
        ) -> None:
            ativa = bool(e.data)
            e.control.bgcolor = ft.Colors.with_opacity(0.10, cor) if ativa else None
            e.control.border = ft.Border.all(
                1,
                ft.Colors.with_opacity(0.30, cor) if ativa else "#00000000",
            )
            e.control.scale = 1.05 if ativa else 1.0
            barra.width = 50 if ativa else 44
            if media is not None:
                barra.height = altura_barra + 10 if ativa else altura_barra
            detalhe_hover.value = (
                f"{nome} · média {media:.1f}/5,0 · {total} respostas"
                if ativa and media is not None
                else f"{nome} · sem respostas válidas"
                if ativa
                else ""
            )
            layout.page.update()

        contexto = (
            f"{nomes_meses[mes - 1]} / {ano} · {dados_mais_recentes['avaliacoes']} avaliações · "
            f"{dados_mais_recentes['respostas']} respostas registradas"
        )
        conteudo_grafico: ft.Control = ft.Row(
            expand=True,
            spacing=14,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=colunas,
        )
        detalhe_grafico: ft.Control = detalhe_hover
    else:
        contexto = "Os resultados por eixo aparecerão após as primeiras avaliações."
        conteudo_grafico = ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            content=ft.Text(
                "Ainda não há dados para exibir.",
                size=12,
                color=layout.cores[TEXTO_SECUNDARIO],
                text_align=ft.TextAlign.CENTER,
            ),
        )
        detalhe_grafico = ft.Container(height=18)

    return ft.Container(
        height=altura_painel,
        bgcolor=layout.cores[CARD],
        padding=18,
        border_radius=12,
        border=ft.Border.all(1, layout.cores[BORDA]),
        content=ft.Column(
            spacing=8,
            controls=[
                ft.Column(
                    spacing=4,
                    controls=[
                        ft.Text("Desempenho do mês mais recente", size=16, weight=ft.FontWeight.W_700, color=layout.cores[TEXTO_PRINCIPAL]),
                        ft.Text(contexto, size=10, color=layout.cores[TEXTO_SECUNDARIO]),
                    ],
                ),
                ft.Container(height=max(180, altura_painel - 120), content=conteudo_grafico),
                detalhe_grafico,
            ],
        ),
    )


def _criar_indicador(
    layout: ResponsiveLayout,
    titulo: str,
    valor: str,
    icone: str,
    coluna: dict[str, int],
) -> ft.Container:
    cores = layout.cores
    return ft.Container(
        col=coluna,
        bgcolor=cores[CARD],
        padding=16,
        border_radius=12,
        border=ft.Border.all(1, cores[BORDA]),
        content=ft.Column(
            spacing=12,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(
                            titulo,
                            size=12,
                            color=cores[TEXTO_SECUNDARIO],
                        ),
                        ft.Icon(icone, size=18, color=COR_PRIMARIA),
                    ],
                ),
                ft.Text(
                    valor,
                    size=26,
                    weight=ft.FontWeight.W_700,
                    color=cores[TEXTO_PRINCIPAL],
                ),
            ],
        ),
    )


def _criar_painel_cursos(
    layout: ResponsiveLayout,
    avaliacoes: list[dict],
    cursos: list[dict],
    altura_painel: int,
) -> ft.Container:
    """Exibe avaliações e respostas agrupadas pelos cursos atuais."""
    por_curso: dict[str, dict] = {}

    for curso in cursos:
        nome = str(curso.get("nome") or "").strip()
        if nome:
            por_curso[nome.casefold()] = {
                "nome": nome,
                "avaliacoes": 0,
                "respostas": 0,
            }

    for avaliacao in avaliacoes:
        nome = str(avaliacao.get("curso_nome") or "Curso sem nome").strip()
        chave = nome.casefold()
        if chave not in por_curso:
            # Avaliações órfãs (curso removido do cadastro) não entram nos dados válidos.
            continue
        respostas = avaliacao.get("respostas", {})
        por_curso[chave]["avaliacoes"] += 1
        por_curso[chave]["respostas"] += len(respostas) if isinstance(respostas, dict) else 0

    dados = sorted(
        por_curso.values(),
        key=lambda item: (
            -item["avaliacoes"],
            -item["respostas"],
            item["nome"].casefold(),
        ),
    )
    maior_total = max((item["avaliacoes"] for item in dados), default=0)
    cores = layout.cores

    if dados:
        controles: list[ft.Control] = []
        for item in dados:
            proporcao = item["avaliacoes"] / maior_total if maior_total else 0
            controles.append(
                ft.Column(
                    spacing=6,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            spacing=8,
                            controls=[
                                ft.Text(
                                    item["nome"],
                                    size=12,
                                    weight=ft.FontWeight.W_600,
                                    color=cores[TEXTO_PRINCIPAL],
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                    expand=True,
                                ),
                                ft.Text(
                                    f"{item['avaliacoes']} avaliações",
                                    size=11,
                                    color=cores[TEXTO_SECUNDARIO],
                                ),
                            ],
                        ),
                        ft.ProgressBar(
                            value=proporcao,
                            color=COR_PRIMARIA,
                            bgcolor=cores[CARD_SECUNDARIO],
                            height=7,
                            border_radius=5,
                        ),
                        ft.Text(
                            f"{item['respostas']} respostas registradas",
                            size=10,
                            color=cores[TEXTO_SECUNDARIO],
                        ),
                    ],
                )
            )
    else:
        controles = [
            ft.Text(
                "Cadastre cursos e registre avaliações para ver a atividade por curso.",
                size=12,
                color=cores[TEXTO_SECUNDARIO],
            )
        ]

    lista_cursos = ft.Column(
        height=max(180, altura_painel - 100),
        spacing=14,
        scroll=ft.ScrollMode.AUTO,
        controls=controles,
    )

    return ft.Container(
        height=altura_painel,
        bgcolor=cores[CARD],
        padding=18,
        border_radius=12,
        border=ft.Border.all(1, cores[BORDA]),
        content=ft.Column(
            spacing=14,
            controls=[
                ft.Column(
                    spacing=4,
                    controls=[
                        ft.Text(
                            "Atividade por curso",
                            size=16,
                            weight=ft.FontWeight.W_700,
                            color=cores[TEXTO_PRINCIPAL],
                        ),
                        ft.Text(
                            f"{len(dados)} cursos · ordenados por avaliações e respostas.",
                            size=11,
                            color=cores[TEXTO_SECUNDARIO],
                        ),
                    ],
                ),
                lista_cursos,
            ],
        ),
    )


def _criar_secao_avaliacoes(
    layout: ResponsiveLayout,
    avaliacoes: list[dict],
    mudar_tela: Callable[[str], None],
) -> ft.Container:
    cores = layout.cores
    linhas = []

    for avaliacao in avaliacoes[:5]:
        respostas = avaliacao.get("respostas", {})
        if not isinstance(respostas, dict):
            respostas = {}
        data = avaliacao.get("data_avaliacao")
        semestre = avaliacao.get("semestre") or obter_semestre(data)
        nome_curso = str(avaliacao.get("curso_nome") or "Curso sem nome")
        descricao = " · ".join(
            parte
            for parte in (
                semestre or "Semestre não informado",
                _formatar_data(data),
                f"{len(respostas)} respostas",
            )
            if parte
        )
        linhas.append(
            ft.Container(
                padding=ft.Padding.symmetric(vertical=12, horizontal=4),
                ink=True,
                on_click=lambda e: mudar_tela(ROTA_DASHBOARD_AVALIACOES),
                border=ft.Border(
                    bottom=ft.BorderSide(1, cores[BORDA]),
                ),
                content=ft.Row(
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            width=36,
                            height=36,
                            border_radius=10,
                            bgcolor=ft.Colors.with_opacity(0.12, COR_PRIMARIA),
                            alignment=ft.Alignment.CENTER,
                            content=ft.Icon(
                                ft.Icons.ASSIGNMENT_OUTLINED,
                                size=18,
                                color=COR_PRIMARIA,
                            ),
                        ),
                        ft.Column(
                            expand=True,
                            spacing=3,
                            controls=[
                                ft.Text(
                                    nome_curso,
                                    size=13,
                                    weight=ft.FontWeight.W_600,
                                    color=cores[TEXTO_PRINCIPAL],
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                                ft.Text(
                                    descricao,
                                    size=11,
                                    color=cores[TEXTO_SECUNDARIO],
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                            ],
                        ),
                        ft.Icon(
                            ft.Icons.CHEVRON_RIGHT,
                            size=19,
                            color=cores[TEXTO_SECUNDARIO],
                        ),
                    ],
                ),
            )
        )

    if not linhas:
        linhas.append(
            ft.Container(
                padding=ft.Padding.symmetric(vertical=24, horizontal=8),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                    controls=[
                        ft.Text(
                            "Nenhuma avaliação registrada ainda.",
                            size=13,
                            weight=ft.FontWeight.W_600,
                            color=cores[TEXTO_PRINCIPAL],
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(
                            "Inicie uma avaliação para acompanhar os resultados nesta tela.",
                            size=11,
                            color=layout.cores[TEXTO_SECUNDARIO],
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.OutlinedButton(
                            "Iniciar primeira avaliação",
                            icon=ft.Icons.ADD_ROUNDED,
                            on_click=lambda e: mudar_tela("/formulario"),
                        ),
                    ],
                ),
            )
        )

    return ft.Container(
        bgcolor=cores[CARD],
        padding=20,
        border_radius=12,
        border=ft.Border.all(1, cores[BORDA]),
        content=ft.Column(
            spacing=4,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(
                            spacing=3,
                            controls=[
                                ft.Text(
                                    "Avaliações recentes",
                                    size=16,
                                    weight=ft.FontWeight.W_700,
                                    color=cores[TEXTO_PRINCIPAL],
                                ),
                                ft.Text(
                                    "Acompanhe os últimos registros da instituição.",
                                    size=11,
                                    color=cores[TEXTO_SECUNDARIO],
                                ),
                            ],
                        ),
                        ft.TextButton(
                            "Ver todas",
                            icon=ft.Icons.ARROW_FORWARD,
                            on_click=lambda e: mudar_tela(ROTA_DASHBOARD_AVALIACOES),
                        ),
                    ],
                ),
                *linhas,
            ],
        ),
    )


def ViewInicio(page: ft.Page, mudar_tela: Callable[[str], None]) -> ft.View:
    """Constrói a tela inicial com boas-vindas, indicadores e atividades recentes."""
    layout = ResponsiveLayout(
        page,
        TXTS_INICIO[0],
        TXTS_INICIO[1],
        mudar_tela=mudar_tela,
    )

    cursos = obter_cursos_db()
    cursos_ativos = sum(1 for curso in cursos if curso_esta_ativo(curso))
    avaliacoes = listar_avaliacoes()
    cursos_existentes = {
        str(curso.get("nome") or "").strip().casefold()
        for curso in cursos
        if str(curso.get("nome") or "").strip()
    }
    avaliacoes = [
        avaliacao
        for avaliacao in avaliacoes
        if str(avaliacao.get("curso_nome") or "").strip().casefold()
        in cursos_existentes
    ]
    total_respostas = sum(
        len(avaliacao.get("respostas", {}))
        for avaliacao in avaliacoes
        if isinstance(avaliacao.get("respostas", {}), dict)
    )
    # Mantém os painéis no tamanho visual original quando há espaço e reduz
    # somente o necessário em janelas baixas.
    altura_paineis = max(300, min(460, int(page.height or 768) - 240))
    avaliacoes.sort(
        key=lambda item: _chave_data(item.get("data_avaliacao")),
        reverse=True,
    )

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

    colunas_kpi = {"xs": 12, "sm": 6, "md": 4, "lg": 4}
    indicadores = ft.ResponsiveRow(
        spacing=16,
        run_spacing=12,
        controls=[
            _criar_indicador(
                layout,
                "Avaliações realizadas",
                str(len(avaliacoes)),
                ft.Icons.ASSIGNMENT_OUTLINED,
                colunas_kpi,
            ),
            _criar_indicador(
                layout,
                "Cursos ativos",
                str(cursos_ativos),
                ft.Icons.SCHOOL_OUTLINED,
                colunas_kpi,
            ),
            _criar_indicador(
                layout,
                "Respostas registradas",
                f"{total_respostas:,}".replace(",", "."),
                ft.Icons.FORMAT_LIST_BULLETED,
                colunas_kpi,
            ),
        ],
    )

    painel_tendencia = _criar_painel_tendencia(layout, avaliacoes, altura_paineis)
    painel_cursos = _criar_painel_cursos(layout, avaliacoes, cursos, altura_paineis)
    paineis_resumo = ft.ResponsiveRow(
        spacing=16,
        run_spacing=16,
        controls=[
            ft.Container(
                col={"xs": 12, "sm": 12, "md": 6, "lg": 6},
                content=painel_tendencia,
            ),
            ft.Container(
                col={"xs": 12, "sm": 12, "md": 6, "lg": 6},
                content=painel_cursos,
            ),
        ],
    )

    conteudo = ft.Column(
        expand=True,
        spacing=18,
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

    def ajustar_inicio_ao_redimensionar(e=None) -> None:
        ajustar_layout_original(e)
        altura = max(300, min(460, int(page.height or 768) - 240))
        painel_tendencia.height = altura
        painel_cursos.height = altura

        # Redimensiona a área do gráfico e suas barras, mantendo as três
        # colunas proporcionais ao espaço vertical disponível.
        controles_grafico = painel_tendencia.content.controls
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

        lista_cursos = painel_cursos.content.controls[1]
        lista_cursos.height = max(180, altura - 100)
        page.update()

    page.on_resize = ajustar_inicio_ao_redimensionar
    return view
