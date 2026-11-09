from typing import Callable

import flet as ft

from components.core.auth.auth_state import auth_state
from components.core.constants.constants import (
    BORDA,
    CARD,
    CARD_SECUNDARIO,
    COR_PRIMARIA,
    TEXTO_PRINCIPAL,
    TEXTO_SECUNDARIO,
)
from components.core.router.rotas_cts import ROTA_CONTA
from components.layout.responsive.responsive import ResponsiveLayout
from models.conta.conta_utils import _nome_usuario
from models.conta.conta_perfil import criar_secao_perfil
from models.conta.conta_secoes_auxiliares import criar_secoes_auxiliares
from models.conta.conta_atividade import criar_secao_atividade
from models.conta.conta_preferencias import criar_secao_preferencias
from models.conta.conta_sobre import criar_secao_sobre


def ViewConta(page: ft.Page, mudar_tela: Callable[[str], None]) -> ft.View:
    """Área única da conta: perfil, atividade recente e preferências."""
    layout = ResponsiveLayout(
        page,
        "Minha conta",
        "Gerencie seu perfil e as preferências da conta.",
        mudar_tela,
    )
    cores = layout.cores
    usuario = auth_state.usuario or {}
    nome = _nome_usuario(usuario)
    email = str(usuario.get("email") or "E-mail indisponível")
    notificacoes_ativas = getattr(page, "notificacoes_ativas", True)
    contador_notificacoes_ativo = getattr(page, "contador_notificacoes_ativo", True)
    largura_pagina = page.width or 1280
    altura_pagina = page.height or 720
    largura_sidebar = (
        0
        if largura_pagina < 700
        else 72 if getattr(page, "sidebar_recolhida", False) else 200
    )
    largura_workspace = max(300, min(1400, largura_pagina - largura_sidebar - 48))
    layout_lateral = largura_workspace >= 768
    altura_workspace = max(360, altura_pagina - 250) if layout_lateral else None
    altura_conteudo_secao = altura_workspace - 38 if altura_workspace else None
    altura_form_perfil = max(240, altura_conteudo_secao - 80) if altura_conteudo_secao else None

    perfil = criar_secao_perfil(page, layout, cores, nome, email, mudar_tela, altura_form_perfil)
    cartao_perfil = perfil["cartao"]
    campo_email = perfil["campo_email"]
    status_seguranca = perfil["status_seguranca"]
    carregar_perfil = perfil["carregar_perfil"]
    deslogar = perfil["deslogar"]
    botao_deslogar_lateral = perfil["botao_deslogar_lateral"]
    conteudo_formulario_perfil = perfil["conteudo_formulario_perfil"]

    secoes_adicionais = criar_secoes_auxiliares(
        page, layout, cores, campo_email, status_seguranca,
        notificacoes_ativas, contador_notificacoes_ativo,
    )
    seguranca = secoes_adicionais["Segurança"]
    notificacoes = secoes_adicionais["Notificações"]
    sobre_evalytics = criar_secao_sobre(page, layout, cores, max(300, altura_conteudo_secao - 14) if altura_conteudo_secao else None)

    cartao_atividade, carregar_atividade = criar_secao_atividade(
        page, layout, cores, mudar_tela
    )
    preferencias = criar_secao_preferencias(page, layout, cores, mudar_tela)
    secoes_conta = {
        "Perfil": cartao_perfil,
        "Atividade recente": cartao_atividade,
        "Preferências": preferencias,
        "Segurança": seguranca,
        "Notificações": notificacoes,
        "Sobre": sobre_evalytics,
    }
    secao_inicial = getattr(page, "_conta_secao_ativa", "Perfil")
    if secao_inicial == "Sobre o Evalytics":
        secao_inicial = "Sobre"
    if secao_inicial not in secoes_conta:
        secao_inicial = "Perfil"
    estado = {"secao": secao_inicial}
    botoes_secoes: dict[str, ft.Container] = {}
    conteudo_secao = ft.Column(
        height=altura_conteudo_secao,
        spacing=14,
        scroll=ft.ScrollMode.AUTO,
    )

    def selecionar_secao(secao: str) -> None:
        estado["secao"] = secao
        page._conta_secao_ativa = secao
        conteudo_secao.controls = [secoes_conta[secao]]
        cor_ativa = "#B69CFF" if layout.controller.dark_mode else COR_PRIMARIA
        fundo_ativo = "#302747" if layout.controller.dark_mode else "#EEE9FB"
        for nome, botao in botoes_secoes.items():
            ativo = nome == secao
            botao.bgcolor = fundo_ativo if ativo else None
            botao.border = ft.Border(
                left=ft.BorderSide(3, COR_PRIMARIA if ativo else "#00000000")
            )
            linha = botao.content
            linha.controls[0].color = cor_ativa if ativo else cores[TEXTO_SECUNDARIO]
            linha.controls[1].color = cor_ativa if ativo else cores[TEXTO_PRINCIPAL]
            linha.controls[1].weight = ft.FontWeight.W_600 if ativo else ft.FontWeight.W_500
        page.update()

    botoes_navegacao = []
    for nome_secao, icone in (
        ("Perfil", ft.Icons.PERSON_OUTLINE),
        ("Atividade recente", ft.Icons.HISTORY),
        ("Preferências", ft.Icons.TUNE_OUTLINED),
        ("Segurança", ft.Icons.SECURITY_OUTLINED),
        ("Notificações", ft.Icons.NOTIFICATIONS_OUTLINED),
        ("Sobre", ft.Icons.INFO_OUTLINE),
    ):
        linha = ft.Row(
            spacing=9,
            controls=[
                ft.Icon(icone, size=17, color=cores[TEXTO_SECUNDARIO]),
                ft.Text(nome_secao, size=11, color=cores[TEXTO_PRINCIPAL]),
            ],
        )
        botao = ft.Container(
            height=40,
            padding=ft.Padding.symmetric(horizontal=9, vertical=5),
            border_radius=8,
            ink=True,
            tooltip=nome_secao,
            on_click=lambda e, secao=nome_secao: selecionar_secao(secao),
            content=linha,
        )
        botoes_secoes[nome_secao] = botao
        botoes_navegacao.append(
            ft.Container(
                col={"xs": 12, "md": 12},
                content=botao,
            )
        )

    espacador_navegacao = ft.Container(
        expand=bool(altura_workspace),
        height=None if altura_workspace else 10,
    )
    painel_navegacao = ft.Container(
        height=altura_workspace,
        padding=16,
        bgcolor=cores[CARD_SECUNDARIO],
        content=ft.Column(
            spacing=10,
            controls=[
                ft.Row(
                    spacing=9,
                    controls=[
                        ft.CircleAvatar(
                            radius=17,
                            bgcolor=COR_PRIMARIA,
                            content=ft.Icon(ft.Icons.PERSON, size=18, color=ft.Colors.WHITE),
                        ),
                        ft.Column(
                            spacing=1,
                            expand=True,
                            controls=[
                                ft.Text(nome, size=12, weight=ft.FontWeight.W_700, color=cores[TEXTO_PRINCIPAL], max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                            ],
                        ),
                    ],
                ),
                ft.Divider(height=1),
                ft.ResponsiveRow(spacing=4, run_spacing=4, controls=botoes_navegacao),
                espacador_navegacao,
                ft.Divider(height=1, color=cores[BORDA]),
                botao_deslogar_lateral,
            ],
        ),
    )
    conteudo_secao.controls = [secoes_conta[estado["secao"]]]
    fundo_ativo = "#302747" if layout.controller.dark_mode else "#EEE9FB"
    cor_ativa = "#B69CFF" if layout.controller.dark_mode else COR_PRIMARIA
    botao_secao_ativa = botoes_secoes[estado["secao"]]
    botao_secao_ativa.bgcolor = fundo_ativo
    botao_secao_ativa.border = ft.Border(left=ft.BorderSide(3, COR_PRIMARIA))
    botao_secao_ativa.content.controls[0].color = cor_ativa
    botao_secao_ativa.content.controls[1].color = cor_ativa
    botao_secao_ativa.content.controls[1].weight = ft.FontWeight.W_600

    workspace = ft.Container(
        height=altura_workspace,
        border=ft.Border.all(1, cores[BORDA]),
        border_radius=14,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        bgcolor=cores[CARD],
        content=ft.ResponsiveRow(
            spacing=0,
            run_spacing=0,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                ft.Container(col={"xs": 12, "md": 3}, content=painel_navegacao),
                ft.Container(
                    col={"xs": 12, "md": 9},
                    padding=ft.Padding.only(left=22, right=22, top=16, bottom=22),
                    content=conteudo_secao,
                ),
            ],
        ),
    )

    workspace.width = largura_workspace
    conteudo = ft.Column(
        expand=True,
        spacing=16,
        scroll=ft.ScrollMode.AUTO,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            workspace,
        ],
    )
    layout.add_content(conteudo)
    view = layout.criar_view(ROTA_CONTA)

    def ajustar_dimensoes_conta(e=None) -> None:
        """Redimensiona a área de conta junto com a janela, sem impor rolagem no desktop."""
        layout.controller.ajustar_responsividade(e)
        largura_atual = page.width or 1280
        altura_atual = page.height or 720
        categoria_compacta = 700 <= largura_atual < 1100
        recolhida = getattr(page, "sidebar_recolhida", None)
        sidebar_atual = (
            0
            if largura_atual < 700
            else 72
            if (bool(recolhida) if recolhida is not None else categoria_compacta)
            else 200
        )
        largura_atual_workspace = max(300, min(1400, largura_atual - sidebar_atual - 48))
        layout_lateral_atual = largura_atual_workspace >= 768
        altura_atual_workspace = max(360, altura_atual - 250) if layout_lateral_atual else None
        altura_atual_secao = altura_atual_workspace - 38 if altura_atual_workspace else None
        altura_atual_perfil = max(240, altura_atual_secao - 80) if altura_atual_secao else None

        conteudo.controls[0].width = largura_atual_workspace
        workspace.width = largura_atual_workspace
        workspace.height = altura_atual_workspace
        painel_navegacao.height = altura_atual_workspace
        conteudo_secao.height = altura_atual_secao
        sobre_evalytics.height = max(300, altura_atual_secao - 14) if altura_atual_secao else None
        cartao_perfil.height = altura_atual_perfil
        espacador_navegacao.expand = bool(altura_atual_workspace)
        espacador_navegacao.height = None if altura_atual_workspace else 10
        conteudo_formulario_perfil.alignment = (
            ft.MainAxisAlignment.SPACE_BETWEEN
            if altura_atual_perfil
            else ft.MainAxisAlignment.START
        )
        page.update()

    page.on_resize = ajustar_dimensoes_conta
    page.run_task(carregar_atividade)
    page.run_task(carregar_perfil)
    return view
