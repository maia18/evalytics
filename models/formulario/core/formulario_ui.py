import flet as ft
from typing import Callable
from components.core.constants.constants import (
    TEXTO_PRINCIPAL,
    TEXTO_SECUNDARIO,
    COR_PRIMARIA,
    BORDA,
    AVISO,
    CARD,
)

def criar_dropdown_cursos(cursos: list[dict], cores: dict) -> ft.Dropdown:
    """Cria o menu suspenso com a lista de cursos cadastrados."""
    
    return ft.Dropdown(
        label="Curso",
        hint_text="Escolha um curso",
        options=[
            ft.DropdownOption(
                key=curso["id"],
                text=curso.get("nome", "Curso sem nome"),
            )
            for curso in cursos
            if curso.get("id")
        ],
        width=500,
        color=cores[TEXTO_PRINCIPAL],
        border_color=cores[BORDA],
        label_style=ft.TextStyle(color=cores[TEXTO_SECUNDARIO]),
        hint_style=ft.TextStyle(color=cores[TEXTO_SECUNDARIO]),
    )

def criar_card_selecao_curso(
    dropdown_curso: ft.Dropdown, 
    cores: dict, 
    dark_mode: bool, 
    on_iniciar_click: Callable
) -> ft.Container:
    """Constrói o card inicial para seleção de curso antes de iniciar a avaliação."""
    
    return ft.Container(
        expand=True,
        padding=30,
        bgcolor=cores[CARD],
        border_radius=12,
        border=ft.Border.all(1, cores[BORDA]),
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=15,
            color="#00000033" if not dark_mode else "#00000066",
            offset=ft.Offset(0, 4),
        ),
        content=ft.Column(
            spacing=20,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.SCHOOL_OUTLINED, size=60, color=cores[COR_PRIMARIA]),
                ft.Text("Iniciar Avaliação", size=24, weight="bold", color=cores[TEXTO_PRINCIPAL]),
                ft.Container(height=5),
                dropdown_curso,
                ft.ElevatedButton(
                    "Abrir avaliação",
                    icon=ft.Icons.ARROW_FORWARD,
                    on_click=on_iniciar_click,
                ),
            ],
        ),
    )

def criar_estado_sem_cursos(cores: dict, on_cursos_click: Callable) -> ft.Container:
    """Constrói a tela de aviso caso não existam cursos cadastrados no banco."""
    
    return ft.Container(
        padding=30,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
            controls=[
                ft.Icon(ft.Icons.INFO_OUTLINE, size=50, color=cores[AVISO]),
                ft.Text("Nenhum curso cadastrado", size=22, weight="bold", color=cores[TEXTO_PRINCIPAL]),
                ft.Text(
                    "Cadastre pelo menos um curso antes de iniciar uma avaliação.",
                    size=14,
                    color=cores[TEXTO_SECUNDARIO],
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.ElevatedButton(
                    "Ir para Cursos",
                    icon=ft.Icons.ARROW_FORWARD,
                    on_click=on_cursos_click,
                ),
            ],
        ),
    )
