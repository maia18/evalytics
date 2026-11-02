"""
Arquivo de Constantes (Constants)
    Centraliza todas as dimensões, medidas e paletas de cores da aplicação.
"""
import flet as ft
from typing import Final

# =====================================================================
# DIMENSÕES E MEDIDAS DA INTERFACE
# =====================================================================

WINDOW_WIDTH: Final[int] = 1280  # Largura padrão da janela principal da aplicação (em pixels)
WINDOW_HEIGHT: Final[int] = 720  # Altura padrão da janela principal da aplicação (em pixels)
ALTURA_MAX: Final[int] = 200     # Altura máxima da coluna (utilizada em Gráficos de eixos/barras)
LARGURA_BREAKPOINT_MOBILE = 700   # Define o limite máximo para dispositivos pequenos (celulares e tablets pequenos). Se a largura da tela for menor que 700px, a aplicação adota o modo Mobile.
LARGURA_BREAKPOINT_DESKTOP = 1100  # Define o limite para telas grandes (monitores de notebook e desktop). Acima de 1100px, a aplicação tem espaço de sobra, então adota o modo Desktop completo.

# =====================================================================
# COMPONENTES (SIDEBAR)
# =====================================================================

LARGURA_SIDEBAR_EXPANDIDA = 224 # Sidebar desktop compacta, com espaço suficiente para os rótulos e subtelas.
LARGURA_SIDEBAR_COLAPSADA = 72 # Define a largura (em pixels) da barra lateral quando ela está recolhida (mini-sidebar). 72px é o tamanho exato para mostrar apenas os ícones centralizados, liberando o máximo de espaço útil na tela para o conteúdo principal, ideal para telas médias (tablets) ou quando o usuário prefere focar no dashboard.
LARGURA_SIDEBAR_MOBILE = 250 # Define a largura exata do menu mobile quando ele está aberto. 250px garante espaço suficiente para os textos sem ocupar a tela inteira do celular.
POSICAO_SIDEBAR_MOBILE_FECHADA = -270  # Define a posição (eixo X) da gaveta quando ela está recolhida. O valor é -270px (Largura de 250px + 20px de margem de segurança extra). Essa margem garante que a sombra projetada pela barra lateral (shadow) não fique "vazando" ou visível no canto esquerdo da tela enquanto o menu estiver fechado.
POSICAO_SIDEBAR_MOBILE_ABERTA = 0 # Define a posição da gaveta quando ela está aberta. O valor 0 alinha a borda esquerda do menu exatamente com a borda esquerda da tela do dispositivo.
DURACAO_ANIMACAO_SIDEBAR_MS = 300 # Tempo em milissegundos que a gaveta leva para deslizar de fora para dentro da tela (e vice-versa). 300ms (0.3 segundos) é o tempo de transição padrão recomendado por guias de UI/UX (como o Material Design),mpois é rápido o suficiente para não parecer lento, mas fluido o suficiente para os olhos acompanharem o movimento.
SOMBRA_SIDEBAR_MOBILE = "#33000000" # Define a cor e a opacidade da sombra projetada pela gaveta mobile. O formato em Hexadecimal (#AARRGGBB) significa: - 33: Canal Alpha (Opacidade). Corresponde a cerca de 20% de transparência. - 000000: Cor preta sólida. Isso cria um efeito de profundidade suave, fazendo o menu parecer que está flutuando sobre o conteúdo.
LARGURA_LIMITE_TOGGLE_SIDEBAR = 900 # Largura acima da qual o toggle da sidebar mobile é ignorado (a UI já é tratada como "larga" o suficiente para não precisar de menu-gaveta). ATENÇÃO: este valor (900) é diferente do breakpoint mobile usado em responsiveness.py (700). Isso cria uma faixa de 700-900px onde a sidebar desktop já está visível, mas o toggle mobile ainda pode ser acionado. Mantido como estava para não alterar comportamento sem validação; considerar unificar os breakpoints numa próxima revisão.

# =====================================================================
# COMPONENTES (TABELA DE DADOS)
# =====================================================================

ALTURA_CARD_TABELA_DADOS = 420 # Define uma altura fixa para o card da tabela, evitando problemas de layout infinito
# Centraliza as configurações visuais para manter consistência
PADDING_CARD_PADRAO = 20
BORDA_RADIUS_CARD_PADRAO = 10
SOMBRA_CARD_PADRAO = ft.BoxShadow(spread_radius=1, blur_radius=5, color=ft.Colors.BLACK_12)

# =====================================================================
# COMPONENTES (MENU)
# =====================================================================

# Geometria padrão de todos os botões de menu (sidebar completa e colapsada).
ALTURA_BOTAO_MENU = 45
RAIO_BOTAO_MENU = 8
PADDING_BOTAO_MENU = 10
HOVER_CLARO_BOTAO_MENU = "#CCCCCC" # Cor de hover do botão em modo claro. Não corresponde a COR_BORDA (usada como hover geral do tema em AppColors) — divergência histórica, mantida como estava para não alterar a aparência atual dos botões.

# =====================================================================
# PALETA DE CORES
# =====================================================================

# ---------------------------------------------------------------------
# COR DA MARCA
# ---------------------------------------------------------------------

COR_PRIMARIA: Final[str] = "#4809F4"

# ---------------------------------------------------------------------
# TEXTOS — MODO CLARO
# ---------------------------------------------------------------------

COR_TEXTO_TITULO: Final[str] = "#111827"
COR_TEXTO_SECUNDARIO: Final[str] = "#5F6368"
COR_TEXTO_MUTED: Final[str] = "#777777"

# ---------------------------------------------------------------------
# TEXTOS — MODO ESCURO
# ---------------------------------------------------------------------

TEXTO_PRINCIPAL: Final[str] = "#FFFFFF"
TEXTO_SECUNDARIO: Final[str] = "#A0A0A0"
TEXTO_MUTED: Final[str] = "#777777"

# ---------------------------------------------------------------------
# FUNDOS
# ---------------------------------------------------------------------

# MODO CLARO
COR_FUNDO: Final[str] = "#F7F7F8"

# MODO ESCURO
FUNDO: Final[str] = "#1E1E1E"

# ---------------------------------------------------------------------
# CARDS / SUPERFÍCIES
# ---------------------------------------------------------------------

# MODO CLARO
COR_CARD: Final[str] = "#FFFFFF"
COR_CARD_SECUNDARIO: Final[str] = "#F2F2F3"

# MODO ESCURO
CARD: Final[str] = "#2A2A2A"
CARD_SECUNDARIO: Final[str] = "#252525"

# ---------------------------------------------------------------------
# BORDAS
# ---------------------------------------------------------------------

# MODO CLARO
COR_BORDA: Final[str] = "#E2E2E5"

# MODO ESCURO
BORDA: Final[str] = "#3A3A3A"

# Alias histórico — mantido por compatibilidade
BORDA_NOT_DARKMODE: Final[str] = COR_BORDA

# ---------------------------------------------------------------------
# ESTADOS
# ---------------------------------------------------------------------

SUCESSO: Final[str] = "#81C784"
PERIGO: Final[str] = "#E57373"
AVISO: Final[str] = "#FFB74D"

# ---------------------------------------------------------------------
# ELEMENTOS DE INTERAÇÃO
# ---------------------------------------------------------------------

# Dark Mode
HOVER: Final[str] = "#3A3A3A"
SURFACE: Final[str] = "#333333"

# Light Mode
HOVER_CLARO: Final[str] = "#F0F0F2"
SURFACE_CLARO: Final[str] = "#FFFFFF"

# ---------------------------------------------------------------------
# SOBREPOSIÇÕES
# ---------------------------------------------------------------------

OVERLAY_MODAL: Final[str] = "#00000088"

# ---------------------------------------------------------------------
# ESTILOS GLOBAIS
# ---------------------------------------------------------------------

ESTILO_BOTAO_CANCELAR = ft.ButtonStyle(
    color=ft.Colors.RED_700
)
