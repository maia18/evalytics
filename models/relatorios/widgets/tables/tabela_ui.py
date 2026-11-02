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

def criar_linha_resultado(item: dict) -> ft.DataRow:
    """Gera uma DataRow para um item de resultado específico."""
    eixos = item.get("eixos", {})
    curso_nome = item.get("curso_nome", "Curso não informado")
    data_avaliacao = formatar_data(item.get("data_avaliacao", ""))

    eixo_1 = eixos.get(1, 0.0)
    eixo_2 = eixos.get(2, 0.0)
    eixo_3 = eixos.get(3, 0.0)
    media_geral = item.get("media_geral", 0.0)

    return ft.DataRow(
        cells=[
            ft.DataCell(ft.Text(curso_nome, color=ft.Colors.ON_SURFACE)),
            ft.DataCell(ft.Text(data_avaliacao, color=ft.Colors.ON_SURFACE)),
            ft.DataCell(ft.Text(formatar_nota(eixo_1), color=ft.Colors.ON_SURFACE)),
            ft.DataCell(ft.Text(formatar_nota(eixo_2), color=ft.Colors.ON_SURFACE)),
            ft.DataCell(ft.Text(formatar_nota(eixo_3), color=ft.Colors.ON_SURFACE)),
            ft.DataCell(ft.Text(formatar_nota(media_geral), weight="bold", color=ft.Colors.ON_SURFACE)),
        ]
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

    linhas = [criar_linha_resultado(item) for item in resultados]

    return ft.DataTable(
        # Usa melhor a largura do painel; em telas estreitas, o contêiner externo
        # permite rolagem horizontal sem comprimir as colunas.
        column_spacing=112,
        horizontal_margin=24,
        heading_row_color=(
            ft.Colors.BLUE_GREY_900 if page.theme_mode == ft.ThemeMode.DARK else ft.Colors.BLUE_50
        ),
        columns=[
            ft.DataColumn(ft.Text("Curso", weight="bold", color=ft.Colors.ON_SURFACE)),
            ft.DataColumn(ft.Text("Data", weight="bold", color=ft.Colors.ON_SURFACE)),
            ft.DataColumn(ft.Text("Eixo 1", weight="bold", color=ft.Colors.ON_SURFACE)),
            ft.DataColumn(ft.Text("Eixo 2", weight="bold", color=ft.Colors.ON_SURFACE)),
            ft.DataColumn(ft.Text("Eixo 3", weight="bold", color=ft.Colors.ON_SURFACE)),
            ft.DataColumn(ft.Text("Média Geral", weight="bold", color=ft.Colors.ON_SURFACE)),
        ],
        rows=linhas,
    )
