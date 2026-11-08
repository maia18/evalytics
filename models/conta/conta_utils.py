from datetime import datetime

import flet as ft

from components.core.constants.constants import BORDA, CARD
from components.layout.responsive.responsive import ResponsiveLayout
def _nome_usuario(usuario: dict) -> str:
    nome = str(usuario.get("displayName") or usuario.get("name") or "").strip()
    return nome or str(usuario.get("email") or "Conta").partition("@")[0]


def _data_ordenacao(valor) -> float:
    if hasattr(valor, "timestamp"):
        try:
            return float(valor.timestamp())
        except (TypeError, ValueError, OSError):
            pass
    if isinstance(valor, str) and valor.strip():
        try:
            return datetime.fromisoformat(valor.strip().replace("Z", "+00:00")).timestamp()
        except (TypeError, ValueError, OSError):
            pass
    return 0.0


def _data_formatada(valor) -> str:
    if hasattr(valor, "strftime"):
        return valor.strftime("%d/%m/%Y")
    if isinstance(valor, str) and valor.strip():
        try:
            return datetime.fromisoformat(valor.strip().replace("Z", "+00:00")).strftime("%d/%m/%Y")
        except (TypeError, ValueError, OSError):
            return valor[:10]
    return "Data indisponível"


def _card(layout: ResponsiveLayout, conteudo: ft.Control, padding: int = 18) -> ft.Container:
    cores = layout.cores
    return ft.Container(
        bgcolor=cores[CARD],
        padding=padding,
        border_radius=12,
        border=ft.Border.all(1, cores[BORDA]),
        content=conteudo,
    )


