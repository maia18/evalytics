import asyncio

import requests
import flet as ft

from components.core.auth.auth_state import auth_state
from components.core.constants.constants import TEXTO_PRINCIPAL, SURFACE
from database.services.firebase_keys import FIREBASE_API_KEY
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


async def salvar_nome_perfil(page: ft.Page, nome: str) -> dict | None:
    """Atualiza o nome de exibição no Firebase e no estado local."""
    nome = (nome or "").strip()
    token = auth_state.id_token
    if not nome:
        _notificar(page, "Informe um nome para exibição.", False)
        return None
    if not token or not FIREBASE_API_KEY:
        _notificar(page, "Não foi possível validar sua sessão para atualizar o perfil.", False)
        return None
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
        return None
    if resposta.status_code != 200:
        mensagem = dados.get("error", {}).get("message", "Não foi possível salvar o perfil.")
        if mensagem == "TOKEN_EXPIRED":
            mensagem = "Sua sessão expirou. Entre novamente para atualizar o perfil."
        _notificar(page, mensagem, False)
        return None

    await auth_state.atualizar_dados_usuario(dados)
    _notificar(page, "Perfil atualizado.", True)
    return dados


async def consultar_dados_perfil() -> dict | None:
    """Busca os dados atuais do usuário autenticado no Firebase."""
    token = auth_state.id_token
    if not token or not FIREBASE_API_KEY:
        return None
    try:
        resposta = await asyncio.to_thread(
            requests.post,
            f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={FIREBASE_API_KEY}",
            json={"idToken": token},
            timeout=10,
        )
        if resposta.status_code != 200:
            return None
        usuarios = resposta.json().get("users", [])
        if not usuarios:
            return None
        dados = usuarios[0]
        await auth_state.atualizar_dados_usuario(dados)
        return dados
    except (requests.RequestException, ValueError):
        return None


