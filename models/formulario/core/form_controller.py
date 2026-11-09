import flet as ft
from typing import Callable, Optional
from models.formulario.core.steps import FormularioStepsMixin
from models.formulario.core.render import FormularioRenderMixin

class FormularioController(FormularioStepsMixin, FormularioRenderMixin):
    """
    Controller central do formulário.

        Responsável por:
            - carregar os indicadores ativos do Firestore;
            - armazenar o curso selecionado;
            - controlar o estado das respostas;
            - controlar as justificativas;
            - orquestrar as transições do formulário.
    """

    def __init__(
        self,
        page: ft.Page,
        mudar_tela: Callable[[str], None],
        area_dinamica: ft.Column,
        area_central: ft.Container,
        cores: dict[str, str],
        indicadores: list[dict] | None = None,
    ) -> None:
        self.cores = cores
        self.page = page
        self.mudar_tela = mudar_tela
        self.area_dinamica = area_dinamica
        self.area_central = area_central

        # ==========================================================
        # INDICADORES
        # ==========================================================

        self.indicadores_ativos: list[dict] = []
        self.indicadores_carregados = indicadores is not None
        if indicadores is not None:
            self.definir_indicadores(indicadores)

        # ==========================================================
        # CURSO DA AVALIAÇÃO
        # ==========================================================

        self.curso_id: Optional[str] = None
        self.curso_nome: Optional[str] = None

        # ==========================================================
        # ESTADO DO FORMULÁRIO
        # ==========================================================

        self.estado: dict = {
            "indice_atual": 0,
            "respostas": {},
            "justificativas": {},
        }

    def definir_indicadores(self, indicadores: list[dict]) -> None:
        """Atualiza o catálogo usado pelo formulário sem consultar o banco."""
        self.indicadores_ativos = sorted(
            [item for item in indicadores if item.get("status", "ATIVO") == "ATIVO"],
            key=lambda item: (
                int(item.get("eixo", 0)),
                str(item.get("titulo", "")).lower(),
            ),
        )
        self.indicadores_carregados = True

    def definir_curso(
        self,
        curso_id: str,
        curso_nome: str,
    ) -> None:
        """Define o curso que será associado à avaliação atual."""

        self.curso_id = curso_id
        self.curso_nome = curso_nome

        # Reinicia o formulário ao iniciar uma nova avaliação.
        self.estado["indice_atual"] = 0
        self.estado["respostas"] = {}
        self.estado["justificativas"] = {}
