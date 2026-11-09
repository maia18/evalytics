import flet as ft
from typing import Callable
from components.core.constants.constants import (
    TEXTO_PRINCIPAL,
    COR_PRIMARIA,
)
from models.configuracoes.widgets.indicadores_ui import criar_linha_indicador
from models.configuracoes.widgets.estado_indicadores import EstadoIndicadores
from utils.services.indicadores.indicadores_repository import listar_indicadores_por_eixo

def criar_layout_lista(
    page: ft.Page,
    estado: EstadoIndicadores,
    titulo_pasta: str,
    eixo_id: int,
    callback_voltar: Callable[[], None],
    cores: dict[str, str],
) -> ft.Column:
    """
    Constrói a interface de listagem dos indicadores para um eixo específico.
        Inclui um cabeçalho de navegação e a renderização dinâmica das linhas de dados.
    """

    # 1. Busca os dados no repositório com base no ID do eixo
    lista_da_pasta = listar_indicadores_por_eixo(eixo_id)

    # 2. Constrói o cabeçalho da página (Navegação e Ação)
    controles_lista: list[ft.Control] = [
        
        # Row principal do cabeçalho
        ft.Row(
            
            # SPACE_BETWEEN empurra o grupo "Voltar+Título" para a esquerda
            #   e o botão "Novo" para a extrema direita.
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                
                # Bloco Esquerdo: Botão Voltar e Título
                ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            on_click=lambda _: callback_voltar(),
                        ),
                        ft.Text(
                            titulo_pasta,
                            size=22,
                            weight=ft.FontWeight.BOLD,
                            color=cores[TEXTO_PRINCIPAL],
                        ),
                    ],
                ),
                
                # Bloco Direito: Botão de Ação (Criar Novo)
                ft.ElevatedButton(
                    "Novo Indicador",
                    icon=ft.Icons.ADD,
                    bgcolor=cores[COR_PRIMARIA],
                    color=ft.Colors.WHITE,
                    on_click=lambda e: estado.abrir_modal_novo(),
                ),
            ],
        ),
        
        # Divisor invisível para criar um respiro vertical (margin) de 20px
        ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
    ]

    # 3. Popula a lista com os indicadores recebidos do banco
    for item in lista_da_pasta:
        controles_lista.append(
            criar_linha_indicador(
                page,
                item,
                
                # ATENÇÃO DEV: O uso de `i=item` aqui é obrigatório.
                #   Sem isso, devido ao "late binding" do Python em closures, todos os botões da tela abririam o modal do ÚLTIMO item do loop.
                lambda e, i=item: estado.abrir_modal_criterios(e, i),
                lambda e, i=item: estado.abrir_modal_edicao(e, i),
                lambda i=item: estado.preparar_exclusao(i),
                cores, # Repassa o tema para o componente filho
            )
        )

    # 4. Retorna a estrutura principal com scroll automático
    return ft.Column(
        expand=True,               # Preenche o espaço vertical restante
        scroll=ft.ScrollMode.AUTO, # Adiciona rolagem se a lista for muito longa
        spacing=15,                # Espaço entre os cards de indicadores
        controls=controles_lista,
    )
