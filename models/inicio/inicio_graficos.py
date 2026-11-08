import flet as ft
from datetime import datetime

from components.core.constants.constants import (
    CARD,
    CARD_SECUNDARIO,
    BORDA,
    TEXTO_PRINCIPAL,
    TEXTO_SECUNDARIO,
    COR_PRIMARIA,
)
from components.core.constants.texts import NOMES_EIXOS
from components.layout.responsive.responsive import ResponsiveLayout
from database.services.dashboard.dashboard_utils import obter_mapa_eixos, normalizar_nota


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
    # A primeira renderização usa lista vazia como placeholder. Evita uma
    # consulta ao catálogo no caminho síncrono da abertura da tela.
    mapa_eixos_atual = obter_mapa_eixos() if avaliacoes else {}
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


