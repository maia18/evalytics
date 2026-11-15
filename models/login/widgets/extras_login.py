import flet as ft

def criar_opcoes_extras(
    cor_texto_secundario: str,
    cor_primaria: str,
) -> tuple[ft.Row, ft.Checkbox]:
    """
    Cria a linha de opções extras do formulário de login.
        Padrão de Retorno (Tupla):
            Retorna a `Row` (para ser desenhada na tela) E a instância do `Checkbox` (para que a função `ViewLogin` pai consiga ler `checkbox_lembrar.value` na hora de autenticar).
    """

    # 1. Instancia o Checkbox guardando sua referência
    checkbox_lembrar = ft.Checkbox(
        label="Lembrar-me",
        label_style=ft.TextStyle(
            color=cor_texto_secundario,
            size=12,
        ),
        fill_color={
            ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT,
            ft.ControlState.SELECTED: cor_primaria,
        },
        border_side={
            ft.ControlState.DEFAULT: ft.BorderSide(1, cor_texto_secundario),
            ft.ControlState.SELECTED: ft.BorderSide(1, cor_primaria),
        },
        check_color=ft.Colors.WHITE,
        overlay_color={
            ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT,
            ft.ControlState.HOVERED: ft.Colors.TRANSPARENT,
            ft.ControlState.FOCUSED: ft.Colors.TRANSPARENT,
            ft.ControlState.PRESSED: ft.Colors.TRANSPARENT,
            ft.ControlState.SELECTED: ft.Colors.TRANSPARENT,
        },
        splash_radius=0,
    )

    # 2. Agrupa o Checkbox e o Link em uma linha
    opcoes = ft.Row(
        # SPACE_BETWEEN é essencial aqui: empurra o Checkbox para a extrema esquerda e o botão "Esqueceu a senha?" para a extrema direita.
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        width=float("inf"),
        wrap=False,
        spacing=0,
        controls=[
            checkbox_lembrar,
            
            # Botão de texto simples sem fundo, ideal para links
            ft.TextButton(
                "Esqueceu a senha?",
                style=ft.ButtonStyle(
                    color=cor_primaria,
                    bgcolor={
                        ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT,
                        ft.ControlState.HOVERED: ft.Colors.TRANSPARENT,
                        ft.ControlState.PRESSED: ft.Colors.TRANSPARENT,
                    },
                    side=ft.BorderSide(0, ft.Colors.TRANSPARENT),
                    overlay_color=ft.Colors.TRANSPARENT,
                    padding=0,
                    text_style=ft.TextStyle(size=12),
                ),
            ),
        ],
    )

    return opcoes, checkbox_lembrar # Devolve a interface (opcoes) e a referência de estado (checkbox)
