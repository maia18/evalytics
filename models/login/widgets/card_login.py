import flet as ft

def criar_card_login(
    campo_nome: ft.Column, 
    campo_email: ft.Column, 
    campo_senha: ft.Column,
    opcoes_extras: ft.Row, 
    btn_login: ft.ElevatedButton, 
    secao_social: ft.Column,
    rodape_cadastro: ft.Row,
) -> ft.Container:
    """Agrupa o formulário sem criar um cartão visual ao redor dele."""
    
    return ft.Container(
        padding=ft.Padding.symmetric(vertical=4),
        content=ft.Column(
            spacing=14,
            controls=[
                campo_nome, 
                campo_email, 
                campo_senha, 
                opcoes_extras, 
                btn_login, 
                secao_social,
                rodape_cadastro,
            ],
        ),
    )
