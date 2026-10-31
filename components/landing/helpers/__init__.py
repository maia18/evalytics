"""
Pacote de componentes auxiliares da Landing Page.
"""
from components.landing.helpers.etapas import criar_etapa
from components.landing.helpers.recursos import criar_card_recurso
from components.landing.helpers.indicadores import criar_indicador
from components.landing.helpers.modal_simulacao import abrir_modal_simulacao

__all__ = [
    "criar_etapa",
    "criar_card_recurso",
    "criar_indicador",
    "abrir_modal_simulacao",
]
