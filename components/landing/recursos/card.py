import flet as ft
from components.landing.palette import PAGE, BORDER, TEXT, MUTED

def criar_card_beneficio(
    titulo: str,
    descricao: str,
    scroll_key: str = None,
) -> ft.Container:
    """Cria um card minimalista da grade de benefícios."""

    return ft.Container(
        key=ft.ScrollKey(scroll_key) if scroll_key else None,
        bgcolor=PAGE,
        border=ft.Border.all(1, BORDER),
        border_radius=12,
        padding=ft.Padding.only(left=20, right=20, top=18, bottom=20),
        content=ft.Column(
            spacing=6,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.Text(
                    titulo,
                    size=14,
                    weight=ft.FontWeight.W_600,
                    color=TEXT,
                ),
                ft.Text(
                    descricao,
                    size=12,
                    color=MUTED,
                ),
            ],
        ),
    )

def criar_card_responsivo(
    titulo: str,
    descricao: str,
    scroll_key: str = None,
) -> ft.Container:
    """Encapsula o card em uma coluna de grade responsiva (1/3 no desktop, 1 no mobile)."""

    return ft.Container(
        col={
            "xs": 12,
            "sm": 12,
            "md": 4,
            "lg": 4,
            "xl": 4,
        },
        content=criar_card_beneficio(
            titulo=titulo,
            descricao=descricao,
            scroll_key=scroll_key,
        ),
    )
