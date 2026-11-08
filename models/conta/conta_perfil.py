import flet as ft

from components.core.auth.auth_state import auth_state
from components.core.constants.constants import BORDA, COR_PRIMARIA, TEXTO_PRINCIPAL, TEXTO_SECUNDARIO
from components.core.router.rotas_cts import ROTA_INICIAL
from components.layout.topbar.core.account_menu import consultar_dados_perfil, salvar_nome_perfil
from models.conta.conta_utils import _card
def criar_secao_perfil(page, layout, cores, nome, email, mudar_tela, altura_form_perfil):
    partes_nome = nome.split()
    campo_primeiro_nome = ft.TextField(
        label="Nome",
        value=partes_nome[0] if partes_nome and nome != "Conta" else "",
        hint_text="Seu nome",
        expand=True,
        text_style=ft.TextStyle(color=cores[TEXTO_PRINCIPAL]),
        label_style=ft.TextStyle(color=cores[TEXTO_SECUNDARIO]),
        border_color=cores[BORDA],
        focused_border_color=COR_PRIMARIA,
        border_radius=8,
    )
    campo_sobrenome = ft.TextField(
        label="Sobrenome",
        value=" ".join(partes_nome[1:]) if len(partes_nome) > 1 else "",
        hint_text="Seu sobrenome",
        expand=True,
        text_style=ft.TextStyle(color=cores[TEXTO_PRINCIPAL]),
        label_style=ft.TextStyle(color=cores[TEXTO_SECUNDARIO]),
        border_color=cores[BORDA],
        focused_border_color=COR_PRIMARIA,
        border_radius=8,
    )
    campo_email = ft.TextField(
        label="E-mail",
        value=email if email != "E-mail indisponível" else "",
        read_only=True,
        expand=True,
        text_style=ft.TextStyle(color=cores[TEXTO_SECUNDARIO]),
        label_style=ft.TextStyle(color=cores[TEXTO_SECUNDARIO]),
        border_color=cores[BORDA],
        border_radius=8,
    )

    def atualizar_perfil(nome_atualizado: str, email_atualizado: str) -> None:
        nome_final = nome_atualizado or (email_atualizado or "Conta").partition("@")[0]
        partes = nome_final.split()
        campo_primeiro_nome.value = partes[0] if partes else ""
        campo_sobrenome.value = " ".join(partes[1:])
        campo_email.value = email_atualizado or ""
        avatar_perfil.content.value = iniciais_perfil()
        page.update()

    async def salvar_perfil(e) -> None:
        nome_completo = " ".join(
            parte.strip()
            for parte in (campo_primeiro_nome.value or "", campo_sobrenome.value or "")
            if parte.strip()
        )
        dados = await salvar_nome_perfil(page, nome_completo)
        if dados:
            atualizar_perfil(
                str(dados.get("displayName") or nome_completo),
                str(dados.get("email") or campo_email.value or ""),
            )

    async def carregar_perfil() -> None:
        dados = await consultar_dados_perfil()
        if dados:
            atualizar_perfil(
                str(
                    dados.get("displayName")
                    or dados.get("name")
                    or " ".join(filter(None, (campo_primeiro_nome.value, campo_sobrenome.value)))
                ),
                str(dados.get("email") or campo_email.value or ""),
            )
            status_seguranca.value = (
                "E-mail confirmado" if dados.get("emailVerified") else "E-mail ainda não confirmado"
            )
            status_seguranca.color = "#69C982" if dados.get("emailVerified") else "#F5A348"
            page.update()

    async def deslogar(e) -> None:
        await auth_state.encerrar_sessao(page)
        mudar_tela(ROTA_INICIAL)

    botao_deslogar_lateral = ft.Container(
        height=40,
        padding=ft.Padding.symmetric(horizontal=9, vertical=5),
        border_radius=8,
        ink=True,
        tooltip="Deslogar",
        on_click=lambda e: page.run_task(deslogar, e),
        content=ft.Row(
            spacing=9,
            controls=[
                ft.Icon(ft.Icons.LOGOUT, size=17, color=cores[TEXTO_SECUNDARIO]),
                ft.Text("Sair", size=11, color=cores[TEXTO_PRINCIPAL]),
            ],
        ),
    )

    def iniciais_perfil() -> str:
        return "".join(
            parte.strip()[0]
            for parte in (campo_primeiro_nome.value, campo_sobrenome.value)
            if parte and parte.strip()
        ).upper() or "?"

    avatar_perfil = ft.Container(
        width=50,
        height=50,
        border_radius=12,
        bgcolor="#302747" if layout.controller.dark_mode else "#EEE9FB",
        alignment=ft.Alignment.CENTER,
        content=ft.Text(
            iniciais_perfil(),
            size=16,
            weight=ft.FontWeight.W_700,
            color="#B69CFF" if layout.controller.dark_mode else COR_PRIMARIA,
        ),
    )

    def atualizar_iniciais_avatar(e=None) -> None:
        avatar_perfil.content.value = iniciais_perfil()
        page.update()

    campo_primeiro_nome.on_change = atualizar_iniciais_avatar
    campo_sobrenome.on_change = atualizar_iniciais_avatar

    formulario_dados = ft.Column(
        spacing=0,
        controls=[
            ft.Row(
                spacing=14,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    avatar_perfil,
                    ft.Column(
                        spacing=4,
                        controls=[
                            ft.Text("Dados pessoais", size=15, weight=ft.FontWeight.W_700, color=cores[TEXTO_PRINCIPAL]),
                            ft.Text("Atualize as informações exibidas na sua conta.", size=11, color=cores[TEXTO_SECUNDARIO]),
                        ],
                    ),
                ],
            ),
            ft.Container(height=30),
            ft.Text("INFORMAÇÕES DA CONTA", size=10, weight=ft.FontWeight.W_700, color=cores[TEXTO_SECUNDARIO]),
            ft.Container(height=10),
            ft.ResponsiveRow(
                spacing=14,
                run_spacing=8,
                controls=[
                    ft.Container(col={"xs": 12, "md": 6}, content=ft.Row(controls=[campo_primeiro_nome])),
                    ft.Container(col={"xs": 12, "md": 6}, content=ft.Row(controls=[campo_sobrenome])),
                    ft.Container(col={"xs": 12}, content=ft.Row(controls=[campo_email])),
                ],
            ),
            ft.Container(height=6),
            ft.Row(
                spacing=6,
                controls=[
                    ft.Icon(ft.Icons.LOCK_OUTLINE, size=13, color=cores[TEXTO_SECUNDARIO]),
                    ft.Text("O e-mail é usado para entrar na conta e não pode ser editado aqui.", size=10, color=cores[TEXTO_SECUNDARIO]),
                ],
            ),
        ],
    )
    rodape_perfil = ft.Column(
        spacing=12,
        controls=[
            ft.Divider(height=1, color=cores[BORDA]),
            ft.ResponsiveRow(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                run_spacing=10,
                controls=[
                    ft.Container(
                        col={"xs": 12, "md": 8},
                        alignment=ft.Alignment.CENTER_LEFT,
                        content=ft.Text(
                            "As alterações serão aplicadas ao seu perfil Evalytics.",
                            size=10,
                            color=cores[TEXTO_SECUNDARIO],
                        ),
                    ),
                    ft.Container(
                        col={"xs": 12, "md": 4},
                        alignment=ft.Alignment.CENTER_RIGHT,
                        content=ft.ElevatedButton(
                            "Salvar alterações",
                            icon=ft.Icons.CHECK,
                            bgcolor=COR_PRIMARIA,
                            color=ft.Colors.WHITE,
                            on_click=lambda e: page.run_task(salvar_perfil, e),
                        ),
                    ),
                ],
            ),
        ],
    )
    conteudo_formulario_perfil = ft.Column(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN if altura_form_perfil else ft.MainAxisAlignment.START,
        spacing=20,
        controls=[formulario_dados, rodape_perfil],
    )
    cartao_perfil = ft.Container(
        height=altura_form_perfil,
        padding=ft.Padding.only(top=12, bottom=12),
        content=conteudo_formulario_perfil,
    )

    status_seguranca = ft.Text(
        "Consultando status do e-mail...",
        size=11,
        color=cores[TEXTO_SECUNDARIO],
    )

    return {
        'cartao': cartao_perfil,
        'campo_email': campo_email,
        'status_seguranca': status_seguranca,
        'carregar_perfil': carregar_perfil,
        'deslogar': deslogar,
        'botao_deslogar_lateral': botao_deslogar_lateral,
        'conteudo_formulario_perfil': conteudo_formulario_perfil,
    }
