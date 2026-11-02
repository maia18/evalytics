import asyncio
from datetime import datetime
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
from components.core.router.rotas_cts import ROTA_AVALIACOES, ROTA_CONTA, ROTA_INICIAL
from components.core.theme.darkmode_toggle import toggle_dark_mode
from components.core.theme.theme_config import configurar_tema
from components.layout.responsive.responsive import ResponsiveLayout
from components.layout.topbar.core.account_menu import (
    abrir_dialogo_alterar_senha,
    consultar_dados_perfil,
    salvar_nome_perfil,
)
from database.services.cursos.firestore_courses import obter_cursos_db
from utils.services.avaliacoes.avaliacoes_service import listar_avaliacoes


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


def ViewConta(page: ft.Page, mudar_tela: Callable[[str], None]) -> ft.View:
    """Área única da conta: perfil, atividade recente e preferências."""
    layout = ResponsiveLayout(page, "Minha conta", "Perfil, atividade e preferências.", mudar_tela)
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

    partes_nome = nome.split()
    campo_primeiro_nome = ft.TextField(
        label="Nome",
        value=partes_nome[0] if partes_nome and nome != "Conta" else "",
        hint_text="Seu nome",
        expand=True,
        text_style=ft.TextStyle(color=cores[TEXTO_PRINCIPAL]),
        label_style=ft.TextStyle(color=cores[TEXTO_SECUNDARIO]),
        border_color=cores[BORDA],
        focused_border_color=COR_PRIMARIA,
        border_radius=8,
    )
    campo_sobrenome = ft.TextField(
        label="Sobrenome",
        value=" ".join(partes_nome[1:]) if len(partes_nome) > 1 else "",
        hint_text="Seu sobrenome",
        expand=True,
        text_style=ft.TextStyle(color=cores[TEXTO_PRINCIPAL]),
        label_style=ft.TextStyle(color=cores[TEXTO_SECUNDARIO]),
        border_color=cores[BORDA],
        focused_border_color=COR_PRIMARIA,
        border_radius=8,
    )
    campo_email = ft.TextField(
        label="E-mail",
        value=email if email != "E-mail indisponível" else "",
        read_only=True,
        expand=True,
        text_style=ft.TextStyle(color=cores[TEXTO_SECUNDARIO]),
        label_style=ft.TextStyle(color=cores[TEXTO_SECUNDARIO]),
        border_color=cores[BORDA],
        border_radius=8,
    )

    def atualizar_perfil(nome_atualizado: str, email_atualizado: str) -> None:
        nome_final = nome_atualizado or (email_atualizado or "Conta").partition("@")[0]
        partes = nome_final.split()
        campo_primeiro_nome.value = partes[0] if partes else ""
        campo_sobrenome.value = " ".join(partes[1:])
        campo_email.value = email_atualizado or ""
        avatar_perfil.content.value = iniciais_perfil()
        page.update()

    async def salvar_perfil(e) -> None:
        nome_completo = " ".join(
            parte.strip()
            for parte in (campo_primeiro_nome.value or "", campo_sobrenome.value or "")
            if parte.strip()
        )
        dados = await salvar_nome_perfil(page, nome_completo)
        if dados:
            atualizar_perfil(
                str(dados.get("displayName") or nome_completo),
                str(dados.get("email") or campo_email.value or ""),
            )

    async def carregar_perfil() -> None:
        dados = await consultar_dados_perfil()
        if dados:
            atualizar_perfil(
                str(
                    dados.get("displayName")
                    or dados.get("name")
                    or " ".join(filter(None, (campo_primeiro_nome.value, campo_sobrenome.value)))
                ),
                str(dados.get("email") or campo_email.value or ""),
            )
            status_seguranca.value = (
                "E-mail confirmado" if dados.get("emailVerified") else "E-mail ainda não confirmado"
            )
            status_seguranca.color = "#69C982" if dados.get("emailVerified") else "#F5A348"
            page.update()

    async def deslogar(e) -> None:
        await auth_state.encerrar_sessao(page)
        mudar_tela(ROTA_INICIAL)

    botao_deslogar_lateral = ft.Container(
        height=40,
        padding=ft.Padding.symmetric(horizontal=9, vertical=5),
        border_radius=8,
        ink=True,
        tooltip="Deslogar",
        on_click=lambda e: page.run_task(deslogar, e),
        content=ft.Row(
            spacing=9,
            controls=[
                ft.Icon(ft.Icons.LOGOUT, size=17, color=cores[TEXTO_SECUNDARIO]),
                ft.Text("Deslogar", size=11, color=cores[TEXTO_PRINCIPAL]),
            ],
        ),
    )

    def iniciais_perfil() -> str:
        return "".join(
            parte.strip()[0]
            for parte in (campo_primeiro_nome.value, campo_sobrenome.value)
            if parte and parte.strip()
        ).upper() or "?"

    avatar_perfil = ft.Container(
        width=50,
        height=50,
        border_radius=12,
        bgcolor="#302747" if layout.controller.dark_mode else "#EEE9FB",
        alignment=ft.Alignment.CENTER,
        content=ft.Text(
            iniciais_perfil(),
            size=16,
            weight=ft.FontWeight.W_700,
            color="#B69CFF" if layout.controller.dark_mode else COR_PRIMARIA,
        ),
    )

    def atualizar_iniciais_avatar(e=None) -> None:
        avatar_perfil.content.value = iniciais_perfil()
        page.update()

    campo_primeiro_nome.on_change = atualizar_iniciais_avatar
    campo_sobrenome.on_change = atualizar_iniciais_avatar

    formulario_dados = ft.Column(
        spacing=0,
        controls=[
            ft.Row(
                spacing=14,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    avatar_perfil,
                    ft.Column(
                        spacing=4,
                        controls=[
                            ft.Text("Dados pessoais", size=15, weight=ft.FontWeight.W_700, color=cores[TEXTO_PRINCIPAL]),
                            ft.Text("Atualize as informações exibidas na sua conta.", size=11, color=cores[TEXTO_SECUNDARIO]),
                        ],
                    ),
                ],
            ),
            ft.Container(height=30),
            ft.Text("INFORMAÇÕES DA CONTA", size=10, weight=ft.FontWeight.W_700, color=cores[TEXTO_SECUNDARIO]),
            ft.Container(height=10),
            ft.ResponsiveRow(
                spacing=14,
                run_spacing=8,
                controls=[
                    ft.Container(col={"xs": 12, "md": 6}, content=ft.Row(controls=[campo_primeiro_nome])),
                    ft.Container(col={"xs": 12, "md": 6}, content=ft.Row(controls=[campo_sobrenome])),
                    ft.Container(col={"xs": 12}, content=ft.Row(controls=[campo_email])),
                ],
            ),
            ft.Container(height=6),
            ft.Row(
                spacing=6,
                controls=[
                    ft.Icon(ft.Icons.LOCK_OUTLINE, size=13, color=cores[TEXTO_SECUNDARIO]),
                    ft.Text("O e-mail é usado para entrar na conta e não pode ser editado aqui.", size=10, color=cores[TEXTO_SECUNDARIO]),
                ],
            ),
        ],
    )
    rodape_perfil = ft.Column(
        spacing=12,
        controls=[
            ft.Divider(height=1, color=cores[BORDA]),
            ft.ResponsiveRow(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                run_spacing=10,
                controls=[
                    ft.Container(
                        col={"xs": 12, "md": 8},
                        alignment=ft.Alignment.CENTER_LEFT,
                        content=ft.Text(
                            "As alterações serão aplicadas ao seu perfil Evalytics.",
                            size=10,
                            color=cores[TEXTO_SECUNDARIO],
                        ),
                    ),
                    ft.Container(
                        col={"xs": 12, "md": 4},
                        alignment=ft.Alignment.CENTER_RIGHT,
                        content=ft.ElevatedButton(
                            "Salvar alterações",
                            icon=ft.Icons.CHECK,
                            bgcolor=COR_PRIMARIA,
                            color=ft.Colors.WHITE,
                            on_click=lambda e: page.run_task(salvar_perfil, e),
                        ),
                    ),
                ],
            ),
        ],
    )
    conteudo_formulario_perfil = ft.Column(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN if altura_form_perfil else ft.MainAxisAlignment.START,
        spacing=20,
        controls=[formulario_dados, rodape_perfil],
    )
    cartao_perfil = ft.Container(
        height=altura_form_perfil,
        padding=ft.Padding.only(top=12, bottom=12),
        content=conteudo_formulario_perfil,
    )

    status_seguranca = ft.Text(
        "Consultando status do e-mail...",
        size=11,
        color=cores[TEXTO_SECUNDARIO],
    )

    def atualizar_preferencias_notificacoes(e=None) -> None:
        page.notificacoes_ativas = bool(switch_notificacoes.value)
        page.contador_notificacoes_ativo = bool(switch_contador.value)
        topbar = getattr(page, "_topbar_notificacoes", None)
        if topbar is not None:
            topbar.aplicar_preferencias_notificacoes()
        page.update()

    switch_notificacoes = ft.Switch(
        value=notificacoes_ativas,
        active_color=COR_PRIMARIA,
        on_change=atualizar_preferencias_notificacoes,
    )
    switch_contador = ft.Switch(
        value=contador_notificacoes_ativo,
        active_color=COR_PRIMARIA,
        on_change=atualizar_preferencias_notificacoes,
    )
    seguranca = _card(
        layout,
        ft.Column(
            spacing=14,
            controls=[
                ft.Column(
                    spacing=4,
                    controls=[
                        ft.Text("Segurança da conta", size=15, weight=ft.FontWeight.W_700, color=cores[TEXTO_PRINCIPAL]),
                        ft.Text("Acompanhe a proteção dos dados de acesso.", size=11, color=cores[TEXTO_SECUNDARIO]),
                    ],
                ),
                ft.Container(
                    padding=12,
                    border=ft.Border.all(1, cores[BORDA]),
                    border_radius=8,
                    content=ft.Row(
                        spacing=9,
                        controls=[
                            ft.Icon(ft.Icons.MARK_EMAIL_READ_OUTLINED, size=18, color=cores[TEXTO_SECUNDARIO]),
                            ft.Text("Verificação do e-mail", size=12, color=cores[TEXTO_PRINCIPAL]),
                            ft.Container(expand=True),
                            status_seguranca,
                        ],
                    ),
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            spacing=3,
                            controls=[
                                ft.Text("Senha", size=12, color=cores[TEXTO_PRINCIPAL]),
                                ft.Text("Altere sua senha de acesso.", size=10, color=cores[TEXTO_SECUNDARIO]),
                            ],
                        ),
                        ft.OutlinedButton(
                            "Alterar senha",
                            icon=ft.Icons.LOCK_OUTLINE,
                            on_click=lambda e: abrir_dialogo_alterar_senha(page, cores, campo_email.value or ""),
                        ),
                    ],
                ),
            ],
        ),
    )
    notificacoes = _card(
        layout,
        ft.Column(
            spacing=14,
            controls=[
                ft.Column(
                    spacing=4,
                    controls=[
                        ft.Text("Notificações", size=15, weight=ft.FontWeight.W_700, color=cores[TEXTO_PRINCIPAL]),
                        ft.Text("Escolha quais avisos aparecem no aplicativo.", size=11, color=cores[TEXTO_SECUNDARIO]),
                    ],
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            spacing=2,
                            controls=[
                                ft.Text("Notificações no aplicativo", size=12, color=cores[TEXTO_PRINCIPAL]),
                                ft.Text("Mostrar o sino e o painel de notificações.", size=10, color=cores[TEXTO_SECUNDARIO]),
                            ],
                        ),
                        switch_notificacoes,
                    ],
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            spacing=2,
                            controls=[
                                ft.Text("Contador de não lidas", size=12, color=cores[TEXTO_PRINCIPAL]),
                                ft.Text("Exibir a quantidade pendente sobre o sino.", size=10, color=cores[TEXTO_SECUNDARIO]),
                            ],
                        ),
                        switch_contador,
                    ],
                ),
            ],
        ),
    )

    lista_atividade = ft.Column(
        height=280,
        spacing=0,
        scroll=ft.ScrollMode.AUTO,
        controls=[
            ft.Row(
                spacing=10,
                controls=[
                    ft.ProgressRing(width=17, height=17, stroke_width=2),
                    ft.Text("Carregando atividade recente...", size=12, color=cores[TEXTO_SECUNDARIO]),
                ],
            )
        ],
    )

    def linha_atividade(avaliacao: dict) -> ft.Control:
        respostas = avaliacao.get("respostas", {})
        total_respostas = len(respostas) if isinstance(respostas, dict) else 0
        return ft.Container(
            padding=ft.Padding.symmetric(vertical=10, horizontal=2),
            border=ft.Border(bottom=ft.BorderSide(1, cores[BORDA])),
            ink=True,
            on_click=lambda e: mudar_tela(ROTA_AVALIACOES),
            content=ft.Row(
                spacing=10,
                controls=[
                    ft.Icon(ft.Icons.ASSIGNMENT_OUTLINED, size=18, color=COR_PRIMARIA),
                    ft.Column(
                        expand=True,
                        spacing=3,
                        controls=[
                            ft.Text(
                                str(avaliacao.get("curso_nome") or "Curso sem identificação"),
                                size=12,
                                weight=ft.FontWeight.W_600,
                                color=cores[TEXTO_PRINCIPAL],
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            ft.Text(
                                f"{_data_formatada(avaliacao.get('data_avaliacao'))} · {total_respostas} respostas",
                                size=10,
                                color=cores[TEXTO_SECUNDARIO],
                            ),
                        ],
                    ),
                    ft.Icon(ft.Icons.CHEVRON_RIGHT, size=18, color=cores[TEXTO_SECUNDARIO]),
                ],
            ),
        )

    async def carregar_atividade() -> None:
        try:
            avaliacoes, cursos = await asyncio.gather(
                asyncio.to_thread(listar_avaliacoes),
                asyncio.to_thread(obter_cursos_db),
            )
            cursos_validos = {
                str(curso.get("nome") or "").strip().casefold()
                for curso in cursos
                if str(curso.get("nome") or "").strip()
            }
            avaliacoes_validas = [
                avaliacao
                for avaliacao in avaliacoes
                if str(avaliacao.get("curso_nome") or "").strip().casefold() in cursos_validos
            ]
            avaliacoes_validas.sort(
                key=lambda item: _data_ordenacao(item.get("data_avaliacao")),
                reverse=True,
            )
            recentes = avaliacoes_validas[:8]
            lista_atividade.controls = (
                [linha_atividade(item) for item in recentes]
                if recentes
                else [
                    ft.Container(
                        padding=ft.Padding.symmetric(vertical=18),
                        content=ft.Text("Nenhuma atividade recente encontrada.", size=12, color=cores[TEXTO_SECUNDARIO]),
                    )
                ]
            )
        except Exception:
            lista_atividade.controls = [
                ft.Text("Não foi possível carregar a atividade agora.", size=12, color=ft.Colors.RED_400)
            ]
        page.update()

    cartao_atividade = _card(
        layout,
        ft.Column(
            spacing=8,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            spacing=3,
                            controls=[
                                ft.Text("Atividade recente", size=16, weight=ft.FontWeight.W_700, color=cores[TEXTO_PRINCIPAL]),
                                ft.Text("Últimas avaliações registradas na instituição.", size=11, color=cores[TEXTO_SECUNDARIO]),
                            ],
                        ),
                        ft.TextButton(
                            "Ver todas",
                            icon=ft.Icons.ARROW_FORWARD,
                            on_click=lambda e: mudar_tela(ROTA_AVALIACOES),
                        ),
                    ],
                ),
                lista_atividade,
            ],
        )
    )

    tema_atual = bool(getattr(page, "is_dark_mode", False))
    densidade_atual = getattr(page, "preferencia_densidade_visual", "standard")
    preferencias_pendentes = {"tema": tema_atual, "densidade": densidade_atual}
    def aplicar_preferencias(e) -> None:
        tema_mudou = preferencias_pendentes["tema"] != bool(getattr(page, "is_dark_mode", False))
        densidade_atualizada = getattr(page, "preferencia_densidade_visual", "standard")
        densidade_mudou = preferencias_pendentes["densidade"] != densidade_atualizada
        if not tema_mudou and not densidade_mudou:
            aviso = ft.SnackBar(content=ft.Text("As preferências já estão aplicadas."))
            page.overlay.append(aviso)
            aviso.open = True
            page.update()
            return

        page.preferencia_densidade_visual = preferencias_pendentes["densidade"]
        if tema_mudou:
            toggle_dark_mode(page, bool(getattr(page, "is_dark_mode", False)), mudar_tela, ROTA_CONTA)
        else:
            configurar_tema(page, bool(getattr(page, "is_dark_mode", False)))
            mudar_tela(ROTA_CONTA)

    preferencias = _card(
        layout,
        ft.Column(
            spacing=14,
            controls=[
                ft.Column(
                    spacing=3,
                    controls=[
                        ft.Text("Preferências", size=16, weight=ft.FontWeight.W_700, color=cores[TEXTO_PRINCIPAL]),
                        ft.Text("Ajuste a aparência da sua interface.", size=11, color=cores[TEXTO_SECUNDARIO]),
                    ],
                ),
                ft.Divider(height=1),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            spacing=2,
                            controls=[
                                ft.Text("Tema escuro", size=12, color=cores[TEXTO_PRINCIPAL]),
                                ft.Text("Alterna entre os temas claro e escuro.", size=10, color=cores[TEXTO_SECUNDARIO]),
                            ],
                        ),
                        ft.Switch(
                            value=tema_atual,
                            active_color=COR_PRIMARIA,
                            on_change=lambda e: preferencias_pendentes.update(tema=bool(e.control.value)),
                        ),
                    ],
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            spacing=2,
                            controls=[
                                ft.Text("Densidade compacta", size=12, color=cores[TEXTO_PRINCIPAL]),
                                ft.Text("Reduz espaçamentos da interface.", size=10, color=cores[TEXTO_SECUNDARIO]),
                            ],
                        ),
                        ft.Switch(
                            value=densidade_atual == "compact",
                            active_color=COR_PRIMARIA,
                            on_change=lambda e: preferencias_pendentes.update(
                                densidade="compact" if e.control.value else "standard"
                            ),
                        ),
                    ],
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            spacing=2,
                            controls=[
                                ft.Text("Idioma", size=12, color=cores[TEXTO_PRINCIPAL]),
                                ft.Text("Português (Brasil)", size=10, color=cores[TEXTO_SECUNDARIO]),
                            ],
                        ),
                        ft.Icon(ft.Icons.LANGUAGE, size=18, color=cores[TEXTO_SECUNDARIO]),
                    ],
                ),
                ft.Divider(height=1, color=cores[BORDA]),
                ft.Row(
                    expand=True,
                    alignment=ft.MainAxisAlignment.END,
                    controls=[
                        ft.ElevatedButton(
                            "Aplicar alterações",
                            icon=ft.Icons.CHECK,
                            bgcolor=COR_PRIMARIA,
                            color=ft.Colors.WHITE,
                            on_click=aplicar_preferencias,
                        ),
                    ],
                ),
            ],
        )
    )

    secoes_conta = {
        "Perfil": cartao_perfil,
        "Atividade recente": cartao_atividade,
        "Preferências": preferencias,
        "Segurança": seguranca,
        "Notificações": notificacoes,
    }
    secao_inicial = getattr(page, "_conta_secao_ativa", "Perfil")
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
