import flet as ft


def criar_login_social(
    cor_texto_secundario: str,
    cor_borda: str,
    cor_texto_principal: str,
) -> ft.Column:
    """Renderiza opções visuais de provedores sociais, ainda sem autenticação."""

    divisor = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10,
        controls=[
            ft.Container(height=1, bgcolor=cor_borda, expand=True),
            ft.Text("OU", size=11, color=cor_texto_secundario),
            ft.Container(height=1, bgcolor=cor_borda, expand=True),
        ],
    )

    estilo_botao = ft.ButtonStyle(
        shape=ft.RoundedRectangleBorder(radius=8),
        side=ft.BorderSide(1, cor_borda),
        color=cor_texto_principal,
        padding=ft.Padding.symmetric(horizontal=12, vertical=10),
        overlay_color=ft.Colors.with_opacity(0.06, cor_texto_principal),
    )

    logo_google = ft.Text(
        "G",
        size=16,
        weight=ft.FontWeight.W_700,
        color="#4285F4",
    )
    logo_microsoft = ft.Row(
        tight=True,
        spacing=2,
        controls=[
            ft.Column(
                tight=True,
                spacing=2,
                controls=[
                    ft.Row(tight=True, spacing=2, controls=[
                        ft.Container(width=6, height=6, bgcolor="#F25022"),
                        ft.Container(width=6, height=6, bgcolor="#7FBA00"),
                    ]),
                    ft.Row(tight=True, spacing=2, controls=[
                        ft.Container(width=6, height=6, bgcolor="#00A4EF"),
                        ft.Container(width=6, height=6, bgcolor="#FFB900"),
                    ]),
                ],
            ),
        ],
    )

    botoes = ft.Column(
        spacing=8,
        controls=[
            ft.OutlinedButton(
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                    controls=[logo_google, ft.Text("Entrar com Google", size=12)],
                ),
                width=float("inf"),
                height=40,
                style=estilo_botao,
                on_click=lambda e: None,
                tooltip="Opção visual; login com Google ainda não está disponível",
            ),
            ft.OutlinedButton(
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                    controls=[logo_microsoft, ft.Text("Entrar com Microsoft", size=12)],
                ),
                width=float("inf"),
                height=40,
                style=estilo_botao,
                on_click=lambda e: None,
                tooltip="Opção visual; login com Microsoft ainda não está disponível",
            ),
        ],
    )

    return ft.Column(
        spacing=12,
        controls=[ft.Container(height=2), divisor, botoes],
    )
