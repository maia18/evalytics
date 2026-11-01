import flet as ft

def criar_cabecalho(cor_texto_titulo: str, cor_texto_secundario: str) -> ft.Column:
    """Cria um cabeçalho compacto para o formulário de autenticação."""
    
    return ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8,
        controls=[
            ft.Text(
                "Fazer login em sua conta",
                size=24,
                weight="bold", 
                color=cor_texto_titulo,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Text(
                "Acesse o Evalytics para gerenciar as avaliações institucionais.",
                size=13,
                color=cor_texto_secundario, 
                text_align=ft.TextAlign.CENTER
            ),
        ],
    )
