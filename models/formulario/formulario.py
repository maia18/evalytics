import asyncio
import flet as ft
from typing import Callable
from components.layout.responsive.responsive import ResponsiveLayout
from database.services.cursos.firestore_courses import curso_esta_ativo, obter_cursos_db
from utils.services.indicadores.indicadores_repository import listar_indicadores
from models.formulario.core.form_controller import FormularioController
from models.formulario.core.formulario_ui import (
    criar_dropdown_cursos,
    criar_card_selecao_curso,
    criar_estado_sem_cursos,
)

def ViewFormulario(page: ft.Page, mudar_tela: Callable[[str], None]) -> ft.View:
    """Constrói a tela de Avaliação Institucional e orquestra seus componentes."""
    
    layout = ResponsiveLayout(
        page,
        titulo_pagina="Avaliação Institucional",
        subtitulo="Preencha o formulário abaixo para contribuir com a melhoria contínua.",
        mudar_tela=mudar_tela,
    )

    area_dinamica_conteudo = ft.Column(
        expand=True,
        spacing=10,
        animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
    )
    area_central = ft.Container(
        expand=True,
        padding=ft.Padding.only(top=5, bottom=10, right=20),
        content=area_dinamica_conteudo,
    )

    # ==========================================================
    # GERENCIAMENTO DO CONTROLLER
    # ==========================================================
    
    controller_existente = getattr(page, "_formulario_controller", None)

    if controller_existente is None:
        controller = FormularioController(
            page=page,
            mudar_tela=mudar_tela,
            area_dinamica=area_dinamica_conteudo,
            area_central=area_central,
            cores=layout.cores,
        )
        page._formulario_controller = controller
    else:
        controller = controller_existente
        controller.page = page
        controller.mudar_tela = mudar_tela
        controller.area_dinamica = area_dinamica_conteudo
        controller.area_central = area_central
        controller.cores = layout.cores

    # ==========================================================
    # CARREGAMENTO DE DADOS E EVENTOS
    # ==========================================================
    
    cursos: list[dict] = []
    dropdown_curso = criar_dropdown_cursos(cursos, layout.cores)

    def iniciar_avaliacao(e: ft.ControlEvent) -> None:
        curso_id = dropdown_curso.value

        if not curso_id:
            page.show_dialog(ft.SnackBar(content=ft.Text("Selecione um curso para iniciar a avaliação."), bgcolor=ft.Colors.RED_700))
            return

        curso_selecionado = next((c for c in cursos if c.get("id") == curso_id), None)
        if not curso_selecionado:
            page.show_dialog(ft.SnackBar(content=ft.Text("Não foi possível localizar o curso selecionado."), bgcolor=ft.Colors.RED_700))
            return

        controller.definir_curso(curso_id=curso_id, curso_nome=curso_selecionado.get("nome", ""))
        controller.atualizar_renderizacao()

    # ==========================================================
    # ROTEAMENTO INTERNO DA VIEW
    # ==========================================================
    
    if controller.curso_id and controller.curso_nome:
        controller.atualizar_renderizacao() # Avaliação já em andamento, pula a seleção
        
    else:
        area_dinamica_conteudo.controls = [
            ft.Container(
                expand=True,
                alignment=ft.Alignment.CENTER,
                content=ft.ProgressRing(),
            )
        ]

    layout.add_content(area_central)
    view = layout.criar_view("/formulario")

    async def carregar_dados_formulario() -> None:
        nonlocal cursos, dropdown_curso
        try:
            tarefas = [asyncio.to_thread(listar_indicadores)]
            if not (controller.curso_id and controller.curso_nome):
                tarefas.append(asyncio.to_thread(obter_cursos_db))
            dados = await asyncio.gather(*tarefas)
            controller.definir_indicadores(dados[0])
            if len(dados) > 1:
                cursos = [curso for curso in dados[1] if curso_esta_ativo(curso)]
        except Exception:
            cursos = []

        if controller.curso_id and controller.curso_nome:
            controller.atualizar_renderizacao()
        elif cursos:
            dropdown_curso = criar_dropdown_cursos(cursos, layout.cores)
            area_dinamica_conteudo.controls = [
                criar_card_selecao_curso(
                    dropdown_curso,
                    layout.cores,
                    getattr(page, "is_dark_mode", False),
                    iniciar_avaliacao,
                )
            ]
        else:
            area_dinamica_conteudo.controls = [
                criar_estado_sem_cursos(layout.cores, lambda _: mudar_tela("/cursos"))
            ]
        page.update()

    if not controller.indicadores_carregados or not (controller.curso_id and controller.curso_nome):
        page.run_task(carregar_dados_formulario)
    return view
