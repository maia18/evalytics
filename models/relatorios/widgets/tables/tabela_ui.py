import flet as ft
from datetime import date, datetime

NOMES_EIXOS = {
    1: "Organização Didático-Pedagógica",
    2: "Corpo Docente e Tutorial",
    3: "Infraestrutura",
}

def formatar_nota(nota: float) -> str:
    """Formata notas flutuantes para exibição."""
    return f"{nota:.1f}"

def formatar_data(data_iso) -> str:
    """Converte timestamps do Firestore ou datas ISO para DD/MM/AAAA."""
    if data_iso is None or data_iso == "":
        return "-"

    if isinstance(data_iso, (datetime, date)):
        return data_iso.strftime("%d/%m/%Y")

    if hasattr(data_iso, "strftime"):
        try:
            return data_iso.strftime("%d/%m/%Y")
        except (TypeError, ValueError):
            pass

    try:
        texto = str(data_iso).strip()
        data = texto[:10]
        ano, mes, dia = data.split("-")
        return f"{dia}/{mes}/{ano}"
    except (ValueError, AttributeError, TypeError):
        return str(data_iso)

def criar_linha_resultado(
    item: dict,
    *,
    cabecalho: bool = False,
    cor_cabecalho: str | None = None,
) -> ft.Container:
    """Gera uma linha responsiva da tabela de resultados consolidados."""
    eixos = item.get("eixos", {})
    if cabecalho:
        dados = [
            ("Curso", 6, False, True),
            ("Data", 2, False, True),
            ("Eixo 1", 1, True, True),
            ("Eixo 2", 1, True, True),
            ("Eixo 3", 1, True, True),
            ("Média Geral", 2, True, True),
        ]
    else:
        dados = [
            (str(item.get("curso_nome", "Curso não informado")), 6, False, False),
            (formatar_data(item.get("data_avaliacao", "")), 2, False, False),
            (formatar_nota(eixos.get(1, 0.0)), 1, True, False),
            (formatar_nota(eixos.get(2, 0.0)), 1, True, False),
            (formatar_nota(eixos.get(3, 0.0)), 1, True, False),
            (formatar_nota(item.get("media_geral", 0.0)), 2, True, True),
        ]

    return ft.Container(
        bgcolor=cor_cabecalho if cabecalho else None,
        content=ft.Row(
            expand=True,
            spacing=0,
            controls=[
                ft.Container(
                    expand=proporcao,
                    padding=ft.Padding.symmetric(horizontal=14, vertical=14),
                    alignment=(
                        ft.Alignment.CENTER_RIGHT
                        if numerica
                        else ft.Alignment.CENTER_LEFT
                    ),
                    content=ft.Text(
                        texto,
                        size=12 if cabecalho else 11,
                        weight=ft.FontWeight.BOLD if negrito else None,
                        color=ft.Colors.ON_SURFACE,
                        text_align=(
                            ft.TextAlign.RIGHT if numerica else ft.TextAlign.LEFT
                        ),
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                )
                for texto, proporcao, numerica, negrito in dados
            ],
        ),
    )

def criar_estado_vazio() -> ft.Control:
    """Retorna o estado visual quando não há resultados."""
    return ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=12,
        controls=[
            ft.Container(height=10),
            ft.Icon(ft.Icons.INSERT_CHART_OUTLINED, size=48, color=ft.Colors.GREY_500),
            ft.Text("Nenhuma avaliação encontrada.", size=16, weight="bold", color=ft.Colors.ON_SURFACE),
            ft.Text(
                "Não existem avaliações correspondentes aos filtros selecionados.",
                size=13,
                color=ft.Colors.GREY_600,
                text_align=ft.TextAlign.CENTER,
            ),
        ],
    )

def criar_estrutura_tabela(page: ft.Page, resultados: list[dict]) -> ft.Control:
    """Constrói a DataTable completa ou o estado vazio dependendo dos resultados."""
    if not resultados:
        return criar_estado_vazio()

    linhas: list[ft.Control] = [
        criar_linha_resultado(
            {},
            cabecalho=True,
            cor_cabecalho=(
                ft.Colors.BLUE_GREY_900
                if page.theme_mode == ft.ThemeMode.DARK
                else ft.Colors.BLUE_50
            ),
        )
    ]
    for indice, item in enumerate(resultados):
        linhas.append(criar_linha_resultado(item))
        if indice < len(resultados) - 1:
            linhas.append(ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT))

    return ft.Column(
        expand=True,
        spacing=0,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        controls=linhas,
    )
