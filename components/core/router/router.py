"""
Módulo de Roteamento (Router)
    Responsável por mapear as strings de rota aos respectivos construtores de View.
"""
import logging as lg
import flet as ft
from typing import Callable

# Importação dos Identificadores das Rotas
from components.core.router.rotas_cts import (
    ROTA_INICIAL,
    ROTA_LOGIN,
    ROTA_INICIO,
    ROTA_DASHBOARD,
    ROTA_DASHBOARD_VISAO_GERAL,
    ROTA_DASHBOARD_AVALIACOES,
    ROTA_AVALIACOES,
    ROTA_RELATORIOS,
    ROTA_RELATORIOS_DASHBOARD,
    ROTA_RELATORIOS_DADOS,
    ROTA_CURSOS,
    ROTA_INDICADORES,
    ROTA_DESENVOLVEDORES,
    ROTA_FORMULARIO,
    ROTA_CONFIGURACOES,
    ROTA_CONTA,
)

# Construtores de tela (Views)
from components.landing.landing import ViewLanding
from components.landing.indicadores.indicadores_view import ViewIndicadores
from components.landing.desenvolvedores import ViewDesenvolvedores
from models.login.login import ViewLogin
from models.inicio.inicio import ViewInicio
from models.cursos.cursos import ViewCursos
from models.dashboard.dashboard import ViewDashboard, ViewDashboardAvaliacoes
from models.avaliacoes.avaliacoes import ViewAvaliacoes
from models.relatorios.relatorios import ViewRelatorios, ViewRelatoriosDados
from models.formulario.formulario import ViewFormulario
from models.configuracoes.configuracoes import ViewConfiguracoes
from models.conta.conta import ViewConta

logger = lg.getLogger(__name__)

# Definição do Tipo (Type Alias) de acordo com o contrato
ViewBuilder = Callable[[ft.Page, Callable[[str], None]], ft.View]

'''
Tabela de Roteamento:
    Vincula diretamente a string da rota (chave) ao construtor da tela (valor).
'''
ROTAS: dict[str, ViewBuilder] = {
    ROTA_INICIAL: ViewLanding,
    ROTA_INDICADORES: ViewIndicadores,
    ROTA_DESENVOLVEDORES: ViewDesenvolvedores,
    ROTA_LOGIN: ViewLogin,
    ROTA_INICIO: ViewInicio,
    ROTA_DASHBOARD: ViewDashboard,
    ROTA_DASHBOARD_VISAO_GERAL: ViewDashboard,
    ROTA_DASHBOARD_AVALIACOES: ViewDashboardAvaliacoes,
    ROTA_AVALIACOES: ViewAvaliacoes,
    ROTA_RELATORIOS: ViewRelatorios,
    ROTA_RELATORIOS_DASHBOARD: ViewRelatorios,
    ROTA_RELATORIOS_DADOS: ViewRelatoriosDados,
    ROTA_CURSOS: ViewCursos,
    ROTA_FORMULARIO: ViewFormulario,
    ROTA_CONFIGURACOES: ViewConfiguracoes,
    ROTA_CONTA: ViewConta,
}

def obter_view(rota: str) -> ViewBuilder:
    """
    Retorna a view correspondente à rota informada.
        Caso a rota não exista no mapeamento, retorna ViewLogin como fallback e registra um aviso para facilitar o diagnóstico.
    """
    view = ROTAS.get(rota)
    
    if view is None:
        # Padrão de Fallback + Log para rotas inexistentes
        logger.warning("Rota desconhecida: '%s'. Redirecionando para login.", rota)
        return ViewLogin
        
    return view
