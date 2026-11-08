import asyncio

import requests
import flet as ft

from components.core.auth.auth_state import auth_state
from components.core.constants.constants import COR_PRIMARIA, TEXTO_PRINCIPAL, TEXTO_SECUNDARIO
from database.services.firebase_keys import FIREBASE_API_KEY
from .account_shared import _fechar_dialogo, _notificar
def abrir_dialogo_alterar_senha(page: ft.Page, cores: dict[str, str], email: str) -> None:
    campo_atual = ft.TextField(label="Senha atual", password=True, can_reveal_password=True)
    campo_nova = ft.TextField(label="Nova senha", password=True, can_reveal_password=True)
    campo_confirmacao = ft.TextField(label="Confirme a nova senha", password=True, can_reveal_password=True)
    dialogo = None

    async def salvar(e):
        senha_atual = campo_atual.value or ""
        senha_nova = campo_nova.value or ""
        if not email:
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
                json={"email": email, "password": senha_atual, "returnSecureToken": True},
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
        dialogo.open = False
        _notificar(page, "Senha alterada com sucesso.", True)

    dialogo = ft.AlertDialog(
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
            ft.TextButton("Cancelar", on_click=lambda e: _fechar_dialogo(page, dialogo)),
            ft.ElevatedButton("Atualizar senha", bgcolor=COR_PRIMARIA, color=ft.Colors.WHITE, on_click=salvar),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.overlay.append(dialogo)
    dialogo.open = True
    page.update()


