import flet as ft

def criar_login_social(cor_texto_secundario: str, cor_borda: str, cor_texto_principal: str) -> ft.Column:
    """Seção de autenticação por terceiros: divisor 'OU CONTINUE COM' + botões sociais."""
    
    # Cria uma linha horizontal com texto no meio (padrão comum em formulários de login moderno)
    divisor = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        controls=[
            # Containers vazios com expand=True funcionam como as linhas do divisor (ocupam todo o espaço restante)
            ft.Container(height=1, bgcolor=cor_borda, expand=True),
            ft.Text("OU CONTINUE COM", size=12, color=cor_texto_secundario, weight=ft.FontWeight.W_500),
            ft.Container(height=1, bgcolor=cor_borda, expand=True),
        ],
    )

    # Estilo base compartilhado para todos os botões sociais (borda outline, cantos levemente arredondados)
    estilo_botao_social = ft.ButtonStyle(
        shape=ft.RoundedRectangleBorder(radius=4),
        side=ft.BorderSide(1, cor_borda),
        padding=ft.Padding.symmetric(vertical=15),
    )

    botoes = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        spacing=10,  # Substitui os Containers manuais de espaçamento, mantendo o mesmo resultado visual
        controls=[
            # Botão G (Google)
            ft.OutlinedButton(content=ft.Text("G", color=cor_texto_principal, weight=ft.FontWeight.BOLD), style=estilo_botao_social, expand=True),
            # Botão Windows (Microsoft)
            ft.OutlinedButton(content=ft.Icon(ft.Icons.WINDOW, color=cor_texto_principal), style=estilo_botao_social, expand=True),
            # Botão Apple
            ft.OutlinedButton(content=ft.Icon(ft.Icons.APPLE, color=cor_texto_principal), style=estilo_botao_social, expand=True),
        ],
    )

    return ft.Column(spacing=14, controls=[ft.Container(height=8), divisor, botoes])
