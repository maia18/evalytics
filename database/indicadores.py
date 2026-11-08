"""Compatibilidade: expõe o catálogo completo de indicadores do Evalytics."""

from database.indicadores_data import (
    INDICADORES,
    INDICADORES_EIXO_1,
    INDICADORES_EIXO_2,
    INDICADORES_EIXO_3,
)

__all__ = ["INDICADORES", "INDICADORES_EIXO_1", "INDICADORES_EIXO_2", "INDICADORES_EIXO_3"]
