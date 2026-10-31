import flet as ft

def criar_card_login(
    cabecalho_abas: ft.Row, 
    campo_nome: ft.Column, 
    campo_email: ft.Column, 
    campo_senha: ft.Column,
    opcoes_extras: ft.Row, 
    btn_login: ft.ElevatedButton, 
    secao_social: ft.Column, 
    cor_card: str,
) -> ft.Container:
    """Painel central principal que engloba (wraps) os elementos do formulário de autenticação."""
    
    return ft.Container(
        bgcolor=cor_card, 
        padding=20,
        border_radius=12,
        border=ft.Border.all(1, "#3A3A3A"),
        shadow=ft.BoxShadow(
            blur_radius=18,
            spread_radius=1,
            color="#66000000",
        ),
        content=ft.Column(
            spacing=14,
            controls=[
                cabecalho_abas, 
                campo_nome, 
                campo_email, 
                campo_senha, 
                opcoes_extras, 
                btn_login, 
                secao_social
            ],
        ),
    )
