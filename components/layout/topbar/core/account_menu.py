from typing import Callable

import flet as ft

from components.core.constants.constants import SURFACE
from components.core.router.rotas_cts import ROTA_CONTA

from components.layout.topbar.core.account_shared import (
    _exibir_dialogo,
    _fechar_dialogo,
    _notificar,
    salvar_nome_perfil,
    consultar_dados_perfil,
)
from components.layout.topbar.core.account_security import abrir_dialogo_alterar_senha
from components.layout.topbar.core.account_profile import abrir_perfil
from components.layout.topbar.core.account_settings import (
    abrir_ajuda,
    abrir_configuracoes_conta,
    abrir_sobre,
)
from components.layout.topbar.core.account_activity import (
    _chave_data_atividade,
    _formatar_data_atividade,
    abrir_atividade_recente,
)


def criar_menu_conta(
    page: ft.Page,
    cores: dict[str, str],
    mudar_tela: Callable[[str], None],
) -> ft.Container:
    return ft.Container(
        width=34,
        height=34,
        alignment=ft.Alignment.CENTER,
        tooltip="Minha conta",
        ink=True,
        border_radius=17,
        bgcolor=cores[SURFACE],
        border=ft.Border.all(1, "#40394A"),
        on_click=lambda e: mudar_tela(ROTA_CONTA),
        content=ft.Icon(ft.Icons.PERSON_OUTLINE, size=18, color="#B69CFF"),
    )
