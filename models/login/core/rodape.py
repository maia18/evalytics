import flet as ft

def criar_rodape_termos(cor_texto_secundario: str, cor_primaria: str) -> ft.Container:
    """
    Rodapé de conformidade (Termos de Serviço e Política de Privacidade).
        Utiliza `TextSpan` para permitir diferentes estilos de fonte (cores/links) dentro de um mesmo bloco corrido de texto.
    """
    
    return ft.Container(
        margin=ft.Margin.only(top=10),
        content=ft.Text(
            text_align=ft.TextAlign.CENTER, 
            size=12,
            
            # `spans` permite segmentar uma única string em múltiplos estilos aplicados.
            spans=[
                ft.TextSpan(
                    "Ao continuar, você concorda com nossos ",
                    ft.TextStyle(
                        color=cor_texto_secundario,
                    )
                ),
                ft.TextSpan(
                    "Termos de Serviço",
                    ft.TextStyle(
                        color=cor_primaria, # Aplica a cor de destaque (ex: Azul) no "Link"
                        weight=ft.FontWeight.W_500,
                    )
                ),
                ft.TextSpan(
                    " e ",
                    ft.TextStyle(
                        color=cor_texto_secundario,
                    )
                ),
                ft.TextSpan(
                    "Política de Privacidade",
                    ft.TextStyle(
                        color=cor_primaria, 
                        weight=ft.FontWeight.W_500,
                    )
                ),
            ],
        ),
    )
