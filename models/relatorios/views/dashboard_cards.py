import flet as ft

LIMIAR_DESEMPENHO_BOM = 3.5
LIMIAR_DESEMPENHO_ALERTA = 2.5

NOMES_EIXOS: dict[int, str] = {
    1: "Organização Didático-Pedagógica",
    2: "Corpo Docente e Tutorial",
    3: "Infraestrutura",
}

def obter_cor_desempenho(nota: float) -> str:
    """Retorna a cor associada ao limiar de desempenho da nota."""
    if nota >= LIMIAR_DESEMPENHO_BOM:
        return ft.Colors.GREEN
    if nota >= LIMIAR_DESEMPENHO_ALERTA:
        return ft.Colors.ORANGE
    return ft.Colors.RED

def criar_card_eixo(
    eixo_id: int, nota: float | None, respostas: int = 0
) -> ft.Card:
    """Constrói o card visual exibindo o desempenho de um eixo específico."""
    
    # ------------------------------------------------------
    # ESTADO SEM DADOS
    # ------------------------------------------------------
    if nota is None:
        return ft.Card(
            elevation=2,
            content=ft.Container(
                padding=20,
                content=ft.Column(
                    spacing=10,
                    controls=[
                        ft.Text(
                            NOMES_EIXOS.get(eixo_id, f"Eixo {eixo_id}"),
                            weight="bold",
                            size=16,
                        ),
                        ft.Text(
                            "Sem dados disponíveis",
                            size=14,
                            color=ft.Colors.GREY_600,
                        ),
                        ft.Text("0 respostas válidas", size=12, color=ft.Colors.GREY_500),
                    ],
                ),
            ),
        )

    # ------------------------------------------------------
    # ESTADO COM DADOS
    # ------------------------------------------------------
    cor_barra = obter_cor_desempenho(nota)

    return ft.Card(
        elevation=2,
        content=ft.Container(
            padding=20,
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Text(
                        NOMES_EIXOS.get(eixo_id, f"Eixo {eixo_id}"),
                        weight="bold",
                        size=16,
                    ),
                    ft.Row(
                        [
                            ft.Text("Desempenho", size=12, color=ft.Colors.GREY),
                            ft.Text(
                                f"{nota:.1f} / 5.0",
                                weight="bold",
                                size=14,
                                color=cor_barra,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.ProgressBar(
                        value=nota / 5,
                        color=cor_barra,
                        height=10,
                        border_radius=5,
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("1,0", size=10, color=ft.Colors.GREY_500),
                            ft.Text(f"{respostas} respostas válidas", size=11, color=ft.Colors.GREY_500),
                            ft.Text("5,0", size=10, color=ft.Colors.GREY_500),
                        ],
                    ),
                ],
            ),
        ),
    )
