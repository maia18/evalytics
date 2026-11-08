import flet as ft
import unicodedata
from datetime import datetime
from typing import Optional
from components.core.constants.constants import TEXTO_PRINCIPAL
from components.widgets.card.card_base import criar_card_base
from models.avaliacoes.layout.cards.card_tabela_linha import criar_linha
from database.services.avaliacoes.firestore_avaliacoes import obter_respostas_tabela

def criar_card_tabela_dados(layout, page: ft.Page, expand: bool = True, height: Optional[int] = None) -> ft.Container:
    """Cartão com uma tabela de respostas recentes e função de exportação."""
    
    '''
    Faz a consulta ao banco de dados no exato momento em que o card é gerado.
        Ao entrar nesta tela, o sistema sempre trará os dados mais recentes salvos na nuvem.
    '''
    dados_tabela = obter_respostas_tabela()
    termo_busca = str(getattr(page, "_busca_avaliacoes_termo", "") or "").strip()
    if termo_busca:
        def normalizar(texto: str) -> str:
            decomposicao = unicodedata.normalize("NFD", texto.casefold())
            return "".join(
                caractere
                for caractere in decomposicao
                if unicodedata.category(caractere) != "Mn"
            )

        termo = normalizar(termo_busca)
        dados_tabela = [
            item
            for item in dados_tabela
            if termo in normalizar(
                " ".join(
                    str(item.get(campo) or "")
                    for campo in ("id", "data", "curso", "eixo", "indicador", "nota")
                )
                + " "
                + _termos_data(item.get("data"), normalizar)
            )
        ]
        del page._busca_avaliacoes_termo
    
    # Constrói o widget nativo de tabela de dados do Flet
    tabela_dados = ft.DataTable(
        expand=True,
        # Definição estrutural do cabeçalho das colunas
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Data")),
            ft.DataColumn(ft.Text("Curso")),
            ft.DataColumn(ft.Text("Eixo")),
            ft.DataColumn(ft.Text("Indicador")),
            ft.DataColumn(ft.Text("Nota")),
            ft.DataColumn(ft.Text("Comentário")),
        ],
        rows=[criar_linha(item) for item in dados_tabela], # Mapeia a lista de dicionários vindas do Firestore diretamente para a função visual que constrói cada linha (Row)
    )

    # Estrutura a interface interna contida no card
    conteudo = ft.Column(
        expand=True,
        controls=[
            # Primeira linha interna: Título alinhado à esquerda, Botão à direita (SPACE_BETWEEN)
            ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Text(
                        "Respostas Recentes (Raw Data)",
                        size=18,
                        weight="bold",
                        color=layout.cores[TEXTO_PRINCIPAL],
                    ),
                ],
            ),
            ft.Divider(color=ft.Colors.GREY_200), # Linha sutil separando o cabeçalho da área dos dados
            ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, controls=[tabela_dados]), # Envelopa a tabela em uma Coluna com scroll automático, garantindo que o card não estoure visualmente os limites da página se houver muitas linhas
        ],
    )

    return criar_card_base(layout.cores, conteudo, expand=expand, height=height) # Delega a finalização visual para uma Factory externa (criar_card_base) que vai aplicar as sombras, bordas e os cantos arredondados padronizados do tema


def _termos_data(data: str, normalizar) -> str:
    """Acrescenta semestre e mês por extenso para a busca global."""
    try:
        data_obj = datetime.strptime(str(data), "%d/%m/%Y")
    except (TypeError, ValueError):
        return ""
    meses = (
        "janeiro", "fevereiro", "março", "abril", "maio", "junho",
        "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
    )
    semestre = 1 if data_obj.month <= 6 else 2
    return normalizar(
        f"{data_obj.year}.{semestre} {data_obj.month:02d}/{data_obj.year} "
        f"{meses[data_obj.month - 1]} {data_obj.year}"
    )
