import asyncio
import requests
import flet as ft
from typing import Callable
from datetime import date, datetime

from components.core.auth.auth_state import auth_state
from components.core.constants.constants import TEXTO_PRINCIPAL, TEXTO_SECUNDARIO, SURFACE, COR_PRIMARIA
from components.core.router.rotas_cts import (
    ROTA_AVALIACOES,
    ROTA_CONFIGURACOES,
    ROTA_DASHBOARD_VISAO_GERAL,
    ROTA_INICIAL,
    ROTA_RELATORIOS,
)
from database.services.firebase_keys import FIREBASE_API_KEY
from utils.services.avaliacoes.avaliacoes_service import listar_avaliacoes


def _exibir_dialogo(page: ft.Page, titulo: str, conteudo: ft.Control, cores: dict[str, str]):
    dialogo = ft.AlertDialog(
        modal=True,
        bgcolor=cores[SURFACE],
        shape=ft.RoundedRectangleBorder(radius=14),
        title=ft.Text(titulo, color=cores[TEXTO_PRINCIPAL], weight=ft.FontWeight.W_700),
        content=ft.Container(width=420, content=conteudo),
        actions=[
            ft.TextButton(
                "Fechar",
                on_click=lambda e: _fechar_dialogo(page, dialogo),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.overlay.append(dialogo)
    dialogo.open = True
    page.update()
    return dialogo


def _fechar_dialogo(page: ft.Page, dialogo: ft.AlertDialog):
    dialogo.open = False
    page.update()


def _notificar(page: ft.Page, mensagem: str, sucesso: bool):
    snackbar = ft.SnackBar(
        content=ft.Text(mensagem, color=ft.Colors.WHITE),
        bgcolor=ft.Colors.GREEN_700 if sucesso else ft.Colors.RED_700,
    )
    page.overlay.append(snackbar)
    snackbar.open = True
    page.update()


async def abrir_perfil(
    page: ft.Page,
    cores: dict[str, str],
    ao_salvar: Callable[[str, str], None],
):
    largura_dialogo = max(220, min(500, (page.width or 600) - 48))
    altura_dialogo = max(180, min(520, (page.height or 760) - 180))
    usuario = auth_state.usuario or {}
    email_atual = usuario.get("email", "")
    nome_atual = usuario.get("displayName") or usuario.get("name") or ""
    nome_titulo = ft.Text(nome_atual or "Seu perfil", size=17, weight=ft.FontWeight.W_700, color=cores[TEXTO_PRINCIPAL])
    avatar_perfil = ft.CircleAvatar(
        radius=26,
        bgcolor=COR_PRIMARIA,
        color=ft.Colors.WHITE,
        content=ft.Text(
            "".join(parte[0] for parte in (nome_atual or email_atual.partition("@")[0]).split()[:2]).upper() or "U",
            size=18,
            weight=ft.FontWeight.W_700,
        ),
    )
    campo_nome = ft.TextField(
        label="Nome de exibição",
        value=nome_atual,
        hint_text="Como seu nome deve aparecer no Evalytics",
        text_style=ft.TextStyle(color=cores[TEXTO_PRINCIPAL]),
        label_style=ft.TextStyle(color=cores[TEXTO_SECUNDARIO]),
        border_color=ft.Colors.GREY_600,
        focused_border_color=COR_PRIMARIA,
        border_radius=8,
    )
    campo_email = ft.TextField(
        label="E-mail da conta",
        value=email_atual or "E-mail indisponível",
        read_only=True,
        text_style=ft.TextStyle(color=cores[TEXTO_SECUNDARIO]),
        label_style=ft.TextStyle(color=cores[TEXTO_SECUNDARIO]),
        border_color=ft.Colors.GREY_700,
        border_radius=8,
    )
    status_email = ft.Container(
        padding=ft.Padding.symmetric(horizontal=10, vertical=7),
        bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.GREY_400),
        border_radius=8,
        content=ft.Row(
            spacing=8,
            controls=[
                ft.Icon(ft.Icons.INFO_OUTLINE, size=16, color=ft.Colors.GREY_400),
                ft.Text("Consultando status do e-mail...", size=11, color=cores[TEXTO_SECUNDARIO]),
            ],
        ),
    )
    dialogo = None

    def atualizar_status_email(verificado: bool):
        cor = "#69C982" if verificado else "#F5A348"
        rotulo = "E-mail confirmado" if verificado else "E-mail ainda não confirmado"
        status_email.bgcolor = ft.Colors.with_opacity(0.12, cor)
        status_email.content.controls[0].name = (
            ft.Icons.VERIFIED_OUTLINED if verificado else ft.Icons.MARK_EMAIL_UNREAD_OUTLINED
        )
        status_email.content.controls[0].color = cor
        status_email.content.controls[1].value = rotulo
        status_email.content.controls[1].color = cor

    async def alterar_senha(e):
        campo_atual = ft.TextField(
            label="Senha atual", password=True, can_reveal_password=True,
            border_radius=8, border_color=ft.Colors.GREY_600,
            focused_border_color=COR_PRIMARIA,
        )
        campo_nova = ft.TextField(
            label="Nova senha", password=True, can_reveal_password=True,
            border_radius=8, border_color=ft.Colors.GREY_600,
            focused_border_color=COR_PRIMARIA,
        )
        campo_confirmacao = ft.TextField(
            label="Confirme a nova senha", password=True, can_reveal_password=True,
            border_radius=8, border_color=ft.Colors.GREY_600,
            focused_border_color=COR_PRIMARIA,
        )
        dialogo_senha = None

        async def salvar_senha(ev):
            senha_atual = campo_atual.value or ""
            senha_nova = campo_nova.value or ""
            if not email_atual:
                _notificar(page, "Não foi possível obter o e-mail da conta para validar a senha atual.", False)
                return
            if not senha_atual:
                _notificar(page, "Informe a senha atual.", False)
                return
            if len(senha_nova) < 6:
                _notificar(page, "A nova senha deve ter pelo menos 6 caracteres.", False)
                return
            if senha_nova != (campo_confirmacao.value or ""):
                _notificar(page, "A confirmação da nova senha não corresponde.", False)
                return

            try:
                autenticacao = await asyncio.to_thread(
                    requests.post,
                    f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}",
                    json={"email": email_atual, "password": senha_atual, "returnSecureToken": True},
                    timeout=15,
                )
                dados_autenticacao = autenticacao.json()
            except (requests.RequestException, ValueError):
                _notificar(page, "Falha de conexão ao validar a senha atual.", False)
                return

            if autenticacao.status_code != 200:
                erro = dados_autenticacao.get("error", {}).get("message", "")
                mensagem = "A senha atual está incorreta." if erro in {
                    "INVALID_LOGIN_CREDENTIALS", "INVALID_PASSWORD"
                } else "Não foi possível validar a senha atual."
                _notificar(page, mensagem, False)
                return

            try:
                resposta = await asyncio.to_thread(
                    requests.post,
                    f"https://identitytoolkit.googleapis.com/v1/accounts:update?key={FIREBASE_API_KEY}",
                    json={
                        "idToken": dados_autenticacao["idToken"],
                        "password": senha_nova,
                        "returnSecureToken": True,
                    },
                    timeout=15,
                )
                dados = resposta.json()
            except (requests.RequestException, ValueError, KeyError):
                _notificar(page, "Falha de conexão ao atualizar a senha. Tente novamente.", False)
                return

            if resposta.status_code != 200:
                erro = dados.get("error", {}).get("message", "")
                mensagem = (
                    "Sua sessão expirou. Entre novamente e tente alterar a senha."
                    if erro == "CREDENTIAL_TOO_OLD_LOGIN_AGAIN"
                    else "Não foi possível alterar a senha. Verifique a sessão e tente novamente."
                )
                _notificar(page, mensagem, False)
                return

            await auth_state.atualizar_dados_usuario(dados)
            dialogo_senha.open = False
            _notificar(page, "Senha alterada com sucesso.", True)

        dialogo_senha = ft.AlertDialog(
            modal=True,
            bgcolor=cores[SURFACE],
            shape=ft.RoundedRectangleBorder(radius=14),
            title=ft.Text("Alterar senha", color=cores[TEXTO_PRINCIPAL], weight=ft.FontWeight.W_700),
            content=ft.Container(
                width=400,
                content=ft.Column(
                    tight=True,
                    spacing=12,
                    controls=[
                        ft.Text("Confirme sua senha atual para proteger a conta.", size=12, color=cores[TEXTO_SECUNDARIO]),
                        campo_atual,
                        campo_nova,
                        campo_confirmacao,
                    ],
                ),
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda ev: _fechar_dialogo(page, dialogo_senha)),
                ft.ElevatedButton(
                    "Atualizar senha",
                    bgcolor=COR_PRIMARIA,
                    color=ft.Colors.WHITE,
                    on_click=salvar_senha,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(dialogo_senha)
        dialogo_senha.open = True
        page.update()

    async def salvar(e):
        nome = (campo_nome.value or "").strip()
        token = auth_state.id_token
        if not nome:
            _notificar(page, "Informe um nome para exibição.", False)
            return
        if not token or not FIREBASE_API_KEY:
            _notificar(page, "Não foi possível validar sua sessão para atualizar o perfil.", False)
            return

        try:
            resposta = await asyncio.to_thread(
                requests.post,
                f"https://identitytoolkit.googleapis.com/v1/accounts:update?key={FIREBASE_API_KEY}",
                json={"idToken": token, "displayName": nome, "returnSecureToken": True},
                timeout=15,
            )
            dados = resposta.json()
        except (requests.RequestException, ValueError):
            _notificar(page, "Falha de conexão ao atualizar o perfil. Tente novamente.", False)
            return

        if resposta.status_code != 200:
            mensagem = dados.get("error", {}).get("message", "Não foi possível salvar o perfil.")
            if mensagem == "TOKEN_EXPIRED":
                mensagem = "Sua sessão expirou. Entre novamente para atualizar o perfil."
            _notificar(page, mensagem, False)
            return

        await auth_state.atualizar_dados_usuario(dados)
        email = dados.get("email") or email_atual
        nome_salvo = dados.get("displayName") or nome
        ao_salvar(nome_salvo, email)
        nome_titulo.value = nome_salvo
        avatar_perfil.content.value = "".join(parte[0] for parte in nome_salvo.split()[:2]).upper() or "U"
        dialogo.open = False
        _notificar(page, "Perfil atualizado.", True)

    dialogo = ft.AlertDialog(
        modal=True,
        bgcolor=cores[SURFACE],
        shape=ft.RoundedRectangleBorder(radius=14),
        title=ft.Text("Meu perfil", color=cores[TEXTO_PRINCIPAL], weight=ft.FontWeight.W_700),
        content=ft.Container(
            width=largura_dialogo,
            height=altura_dialogo,
            content=ft.Column(
                spacing=16,
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    ft.Container(
                        padding=16,
                        bgcolor=cores[SURFACE],
                        border=ft.Border.all(1, ft.Colors.with_opacity(0.16, ft.Colors.GREY_400)),
                        border_radius=12,
                        content=ft.Row(
                            spacing=14,
                            controls=[
                                avatar_perfil,
                                ft.Column(
                                    expand=True,
                                    spacing=4,
                                    controls=[
                                        nome_titulo,
                                        ft.Text(email_atual or "E-mail indisponível", size=12, color=cores[TEXTO_SECUNDARIO]),
                                        ft.Text("Conta Evalytics", size=10, color=cores[TEXTO_SECUNDARIO]),
                                    ],
                                ),
                            ],
                        ),
                    ),
                    ft.Text("DADOS DA CONTA", size=10, weight=ft.FontWeight.W_700, color=cores[TEXTO_SECUNDARIO]),
                    campo_nome,
                    campo_email,
                    status_email,
                    ft.Text("SEGURANÇA", size=10, weight=ft.FontWeight.W_700, color=cores[TEXTO_SECUNDARIO]),
                    ft.Container(
                        padding=14,
                        bgcolor=cores[SURFACE],
                        border=ft.Border.all(1, ft.Colors.with_opacity(0.16, ft.Colors.GREY_400)),
                        border_radius=12,
                        content=ft.Row(
                            wrap=True,
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Row(
                                    spacing=10,
                                    controls=[
                                        ft.Icon(ft.Icons.LOCK_OUTLINE, color=COR_PRIMARIA),
                                        ft.Column(
                                            spacing=2,
                                            controls=[
                                                ft.Text("Senha", size=12, weight=ft.FontWeight.W_600, color=cores[TEXTO_PRINCIPAL]),
                                                ft.Text("Atualize sua senha de acesso", size=10, color=cores[TEXTO_SECUNDARIO]),
                                            ],
                                        ),
                                    ],
                                ),
                                ft.OutlinedButton("Alterar", on_click=alterar_senha),
                            ],
                        ),
                    ),
                ],
            ),
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: _fechar_dialogo(page, dialogo)),
            ft.ElevatedButton(
                "Salvar alterações",
                bgcolor=COR_PRIMARIA,
                color=ft.Colors.WHITE,
                on_click=salvar,
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.overlay.append(dialogo)
    dialogo.open = True
    page.update()

    if auth_state.id_token and FIREBASE_API_KEY:
        try:
            consulta = await asyncio.to_thread(
                requests.post,
                f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={FIREBASE_API_KEY}",
                json={"idToken": auth_state.id_token},
                timeout=10,
            )
            if consulta.status_code == 200:
                usuarios = consulta.json().get("users", [])
                if usuarios:
                    dados_perfil = usuarios[0]
                    await auth_state.atualizar_dados_usuario(dados_perfil)
                    email_atual = dados_perfil.get("email", email_atual)
                    nome_perfil = dados_perfil.get("displayName") or nome_atual
                    if nome_perfil:
                        campo_nome.value = nome_perfil
                        nome_titulo.value = nome_perfil
                        avatar_perfil.content.value = "".join(parte[0] for parte in nome_perfil.split()[:2]).upper()
                    campo_email.value = email_atual or "E-mail indisponível"
                    ao_salvar(nome_perfil or "Conta", email_atual)
                    status_email.visible = True
                    atualizar_status_email(bool(dados_perfil.get("emailVerified")))
                    page.update()
                else:
                    status_email.content.controls[1].value = "Status do e-mail indisponível no momento"
                    page.update()
            else:
                status_email.content.controls[1].value = "Não foi possível consultar a verificação do e-mail"
                page.update()
        except (requests.RequestException, ValueError):
            status_email.content.controls[1].value = "Status do e-mail indisponível no momento"
            page.update()
    else:
        status_email.content.controls[1].value = "Status do e-mail indisponível no momento"
        page.update()


def abrir_ajuda(page: ft.Page, cores: dict[str, str], mudar_tela: Callable[[str], None]):
    conteudo = ft.Column(
        tight=True,
        spacing=12,
        controls=[
            ft.Text("Comece por uma avaliação, acompanhe os indicadores no dashboard e consulte os relatórios para analisar os resultados.", color=ft.Colors.GREY_400, size=13),
            ft.Text("Atalhos", color=cores[TEXTO_PRINCIPAL], weight=ft.FontWeight.W_600),
            ft.Row(
                wrap=True,
                controls=[
                    ft.TextButton("Avaliações", on_click=lambda e: mudar_tela(ROTA_AVALIACOES)),
                    ft.TextButton("Dashboard", on_click=lambda e: mudar_tela(ROTA_DASHBOARD_VISAO_GERAL)),
                    ft.TextButton("Relatórios", on_click=lambda e: mudar_tela(ROTA_RELATORIOS)),
                ],
            ),
            ft.Divider(),
            ft.Text("O contato de suporte da instituição não está configurado no aplicativo.", size=11, color=ft.Colors.GREY_500),
        ],
    )
    _exibir_dialogo(page, "Ajuda e suporte", conteudo, cores)


def abrir_sobre(page: ft.Page, cores: dict[str, str]):
    conteudo = ft.Column(
        tight=True,
        spacing=10,
        controls=[
            ft.Text("Evalytics", size=18, weight=ft.FontWeight.W_700, color=cores[TEXTO_PRINCIPAL]),
            ft.Text(
                "Sistema de avaliação institucional para organizar cursos e indicadores, acompanhar resultados e gerar relatórios em PDF e CSV.",
                size=13,
                color=ft.Colors.GREY_400,
            ),
        ],
    )
    _exibir_dialogo(page, "Sobre o Evalytics", conteudo, cores)


def _chave_data_atividade(valor) -> float:
    try:
        if isinstance(valor, datetime):
            return valor.timestamp()
        if isinstance(valor, date):
            return datetime.combine(valor, datetime.min.time()).timestamp()
        if isinstance(valor, str):
            data = datetime.fromisoformat(valor.replace("Z", "+00:00"))
            return data.timestamp()
    except (OverflowError, OSError, TypeError, ValueError):
        pass
    return 0.0


def _formatar_data_atividade(valor) -> str:
    try:
        if isinstance(valor, datetime):
            return valor.strftime("%d/%m/%Y")
        if isinstance(valor, date):
            return valor.strftime("%d/%m/%Y")
        if isinstance(valor, str):
            return datetime.fromisoformat(valor.replace("Z", "+00:00")).strftime("%d/%m/%Y")
    except (OverflowError, OSError, TypeError, ValueError):
        pass
    return "Data indisponível"


async def abrir_atividade_recente(
    page: ft.Page,
    cores: dict[str, str],
    mudar_tela: Callable[[str], None],
):
    lista_atividades = ft.Column(height=340, spacing=8, scroll=ft.ScrollMode.AUTO)
    conteudo = ft.Column(
        tight=True,
        spacing=12,
        controls=[
            ft.Text("Avaliações institucionais mais recentes.", size=12, color=cores[TEXTO_SECUNDARIO]),
            lista_atividades,
            ft.TextButton(
                "Ver todas as avaliações",
                icon=ft.Icons.ARROW_FORWARD,
                on_click=lambda e: mudar_tela(ROTA_AVALIACOES),
            ),
        ],
    )
    lista_atividades.controls.append(
        ft.Row(
            spacing=10,
            controls=[
                ft.ProgressRing(width=18, height=18, stroke_width=2),
                ft.Text("Carregando avaliações...", size=12, color=cores[TEXTO_SECUNDARIO]),
            ],
        )
    )
    _exibir_dialogo(page, "Atividade recente", conteudo, cores)

    avaliacoes = await asyncio.to_thread(listar_avaliacoes)
    recentes = sorted(
        avaliacoes,
        key=lambda item: _chave_data_atividade(item.get("data_avaliacao")),
        reverse=True,
    )[:5]

    lista_atividades.controls.clear()
    if not recentes:
        lista_atividades.controls.append(
            ft.Container(
                padding=16,
                border=ft.Border.all(1, ft.Colors.with_opacity(0.16, ft.Colors.GREY_400)),
                border_radius=10,
                content=ft.Text("Nenhuma avaliação encontrada.", size=12, color=cores[TEXTO_SECUNDARIO]),
            )
        )
    else:
        for avaliacao in recentes:
            curso = avaliacao.get("curso_nome") or "Curso sem identificação"
            data = _formatar_data_atividade(avaliacao.get("data_avaliacao"))
            lista_atividades.controls.append(
                ft.Container(
                    padding=12,
                    bgcolor=cores[SURFACE],
                    border=ft.Border.all(1, ft.Colors.with_opacity(0.16, ft.Colors.GREY_400)),
                    border_radius=10,
                    content=ft.Row(
                        spacing=10,
                        controls=[
                            ft.Container(
                                width=34,
                                height=34,
                                border_radius=9,
                                bgcolor=ft.Colors.with_opacity(0.12, COR_PRIMARIA),
                                alignment=ft.Alignment.CENTER,
                                content=ft.Icon(ft.Icons.ASSIGNMENT_OUTLINED, size=18, color=COR_PRIMARIA),
                            ),
                            ft.Column(
                                expand=True,
                                spacing=3,
                                controls=[
                                    ft.Text(
                                        curso,
                                        size=12,
                                        weight=ft.FontWeight.W_600,
                                        color=cores[TEXTO_PRINCIPAL],
                                        max_lines=1,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                    ),
                                    ft.Text(data, size=10, color=cores[TEXTO_SECUNDARIO]),
                                ],
                            ),
                        ],
                    ),
                )
            )
    page.update()


def criar_menu_conta(
    page: ft.Page,
    cores: dict[str, str],
    mudar_tela: Callable[[str], None],
) -> ft.PopupMenuButton:
    usuario = auth_state.usuario or {}
    email_inicial = usuario.get("email", "")
    nome_inicial = usuario.get("displayName") or usuario.get("name") or ""
    nome_email = email_inicial.partition("@")[0]
    estado = {
        "nome": nome_inicial or nome_email or "Carregando conta...",
        "email": email_inicial,
    }
    consulta_perfil = {"em_andamento": False, "concluida": bool(email_inicial)}

    def obter_iniciais(nome: str) -> str:
        partes = [parte for parte in nome.replace(".", " ").replace("_", " ").split() if parte]
        return "".join(parte[0] for parte in partes[:2]).upper() or "U"

    nome_avatar = estado["nome"]
    texto_inicial = "…" if nome_avatar == "Carregando conta..." else obter_iniciais(nome_avatar)
    avatar_texto = ft.Text(texto_inicial, size=10, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)
    nome_texto = ft.Text(estado["nome"], size=12, weight=ft.FontWeight.W_600, color=cores[TEXTO_PRINCIPAL])
    email_texto = ft.Text(
        estado["email"] or "Buscando dados da conta...",
        size=10,
        color=ft.Colors.GREY_500,
    )

    def atualizar_identificacao(nome: str, email: str):
        estado["email"] = email or ""
        estado["nome"] = nome or estado["email"].partition("@")[0] or "Conta"
        identificador_avatar = estado["nome"]
        avatar_texto.value = obter_iniciais(identificador_avatar)
        nome_texto.value = estado["nome"]
        email_texto.value = estado["email"] or "E-mail indisponível"
        page.update()

    async def carregar_identificacao(e=None):
        if consulta_perfil["em_andamento"] or consulta_perfil["concluida"]:
            return
        token = auth_state.id_token
        if not token or not FIREBASE_API_KEY:
            consulta_perfil["concluida"] = True
            atualizar_identificacao("Conta", "")
            return

        consulta_perfil["em_andamento"] = True
        try:
            resposta = await asyncio.to_thread(
                requests.post,
                f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={FIREBASE_API_KEY}",
                json={"idToken": token},
                timeout=8,
            )
            usuarios = resposta.json().get("users", []) if resposta.status_code == 200 else []
            if usuarios:
                dados = usuarios[0]
                await auth_state.atualizar_dados_usuario(dados)
                email = dados.get("email", "")
                nome = dados.get("displayName") or dados.get("name") or email.partition("@")[0]
                atualizar_identificacao(nome or "Conta", email)
            else:
                atualizar_identificacao("Conta", "")
        except (requests.RequestException, ValueError):
            atualizar_identificacao("Conta", "")
        finally:
            consulta_perfil["em_andamento"] = False
            consulta_perfil["concluida"] = True

    async def fazer_logout(e):
        await auth_state.encerrar_sessao(page)
        mudar_tela(ROTA_INICIAL)

    async def abrir_perfil_click(e):
        await abrir_perfil(page, cores, atualizar_identificacao)

    async def abrir_atividade_click(e):
        await abrir_atividade_recente(page, cores, mudar_tela)

    menu = ft.PopupMenuButton(
        content=ft.CircleAvatar(
            radius=14,
            bgcolor=COR_PRIMARIA,
            color=ft.Colors.WHITE,
            content=avatar_texto,
        ),
        items=[
            ft.PopupMenuItem(
                content=ft.Column(spacing=2, controls=[nome_texto, email_texto]),
                height=56,
            ),
            ft.PopupMenuItem(
                content="Meu perfil",
                icon=ft.Icons.PERSON_OUTLINE,
                on_click=abrir_perfil_click,
            ),
            ft.PopupMenuItem(
                content="Atividade recente",
                icon=ft.Icons.HISTORY,
                on_click=abrir_atividade_click,
            ),
            ft.PopupMenuItem(
                content="Ajuda e suporte",
                icon=ft.Icons.HELP_OUTLINE,
                on_click=lambda e: abrir_ajuda(page, cores, mudar_tela),
            ),
            ft.PopupMenuItem(
                content="Configurações",
                icon=ft.Icons.SETTINGS_OUTLINED,
                on_click=lambda e: mudar_tela(ROTA_CONFIGURACOES),
            ),
            ft.PopupMenuItem(
                content="Sobre o Evalytics",
                icon=ft.Icons.INFO_OUTLINE,
                on_click=lambda e: abrir_sobre(page, cores),
            ),
            ft.PopupMenuItem(content=ft.Divider(height=1), height=12),
            ft.PopupMenuItem(content="Sair", icon=ft.Icons.LOGOUT, on_click=fazer_logout),
        ],
        bgcolor=cores[SURFACE],
        menu_position=ft.PopupMenuPosition.UNDER,
        shape=ft.RoundedRectangleBorder(radius=10),
        tooltip="Menu da conta",
        on_open=carregar_identificacao,
    )
    if not email_inicial:
        page.run_task(carregar_identificacao)
    return menu
