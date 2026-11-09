import flet as ft
from datetime import datetime

NOMES_EIXOS = {
    1: "Organização Didático-Pedagógica",
    2: "Corpo Docente e Tutorial",
    3: "Infraestrutura",
}

def definir_cor_nota(nota: float) -> str:
    """Define a cor visual da nota conforme a escala de avaliação."""
    if nota >= 4.0:
        return ft.Colors.GREEN_700
    if nota >= 3.0:
        return ft.Colors.ORANGE_700
    
    return ft.Colors.RED_700

def formatar_data(data) -> str:
    """Converte a data armazenada no Firestore para o formato da tabela."""
    if not data:
        return "Data desconhecida"

    try:
        return data.strftime("%d/%m/%Y, %H:%M")
    except AttributeError:
        texto = str(data).strip()

    # Dados antigos/importados podem estar armazenados como ISO 8601, por
    # exemplo: 2026-10-06T15:30:36.898210.
    try:
        data_obj = datetime.fromisoformat(texto.replace("Z", "+00:00"))
        return data_obj.strftime("%d/%m/%Y, %H:%M")
    except (AttributeError, TypeError, ValueError):
        return texto
