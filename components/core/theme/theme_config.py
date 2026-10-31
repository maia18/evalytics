import flet as ft
from components.core.theme.app_colors import AppColors
from components.core.theme.theme import get_app_theme

def configurar_tema(
    page: ft.Page,
    dark_mode: bool,
) -> dict[str, str]:
    """Configura o tema visual da aplicação e retorna a paleta de cores correspondente ao modo atual."""

    page.theme = get_app_theme(dark_mode)
    page.theme.visual_density = (
        ft.VisualDensity.COMPACT
        if getattr(page, "preferencia_densidade_visual", "standard") == "compact"
        else ft.VisualDensity.STANDARD
    )
    page.theme_mode = (
        ft.ThemeMode.DARK
        if dark_mode
        else ft.ThemeMode.LIGHT
    )

    return AppColors.get(dark_mode)
