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
    
    chaves_ordenacao = {1: "data", 5: "nota"}
    # A tabela sempre abre pelas respostas mais recentes.
    dados_tabela.sort(
        key=lambda item: _chave_ordenacao(item.get("data"), "data"),
        reverse=True,
    )
    estado_ordenacao = {"indice": 1, "crescente": False}
    icones_ordenacao = {}

    def ordenar_coluna(indice: int) -> None:
        if indice not in chaves_ordenacao:
            return

        if estado_ordenacao["indice"] == indice:
            estado_ordenacao["crescente"] = not estado_ordenacao["crescente"]
        else:
            estado_ordenacao["indice"] = indice
            estado_ordenacao["crescente"] = True

        chave = chaves_ordenacao[indice]
        dados_ordenados = sorted(
            dados_tabela,
            key=lambda item: _chave_ordenacao(item.get(chave), chave),
            reverse=not estado_ordenacao["crescente"],
        )
        for coluna, icone in icones_ordenacao.items():
            if coluna == indice:
                icone.icon = (
                    ft.Icons.ARROW_UPWARD
                    if estado_ordenacao["crescente"]
                    else ft.Icons.ARROW_DOWNWARD
                )
                icone.tooltip = (
                    "Ordem crescente" if estado_ordenacao["crescente"]
                    else "Ordem decrescente"
                )
            else:
                icone.icon = ft.Icons.SWAP_VERT
                icone.tooltip = "Ordenar esta coluna"
        tabela_dados.rows = [criar_linha(item) for item in dados_ordenados]
        page.update()

    colunas = ("ID", "Data", "Curso", "Eixo", "Indicador", "Nota", "Comentário")

    def criar_cabecalho(indice: int, nome: str):
        if indice not in chaves_ordenacao:
            return ft.Text(nome)

        icone = ft.Icon(
            icon=(
                ft.Icons.ARROW_DOWNWARD
                if indice == estado_ordenacao["indice"]
                else ft.Icons.SWAP_VERT
            ),
            size=17,
        )
        icones_ordenacao[indice] = icone
        largura = 220 if indice == 1 else 120
        return ft.Container(
            width=largura,
            height=48,
            on_click=lambda e, coluna=indice: ordenar_coluna(coluna),
            ink=True,
            content=ft.Row(
                width=largura,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[ft.Text(nome), icone],
            ),
        )

    # A seta faz parte do rótulo e fica ancorada à borda direita da coluna.
    tabela_dados = ft.DataTable(
        expand=True,
        # Linhas com eixo/indicador extensos precisam crescer para exibir
        # o texto inteiro em múltiplas linhas, sem recortá-lo na altura padrão.
        data_row_min_height=56,
        data_row_max_height=160,
        column_spacing=20,
        # Definição estrutural do cabeçalho das colunas
        columns=[
            ft.DataColumn(
                criar_cabecalho(indice, nome),
            )
            for indice, nome in enumerate(colunas)
        ],
        rows=[criar_linha(item) for item in dados_tabela], # Mapeia a lista de dicionários vindas do Firestore diretamente para a função visual que constrói cada linha (Row)
    )

    # Estrutura a interface interna contida no card
    conteudo = ft.Column(
        expand=True,
        controls=[
            # Primeira linha interna: Título alinhado à esquerda, Botão à direita (SPACE_BETWEEN)
            ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
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
    data_obj = _parse_data_tabela(data)
    if data_obj is None:
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


def _chave_ordenacao(valor, campo: str):
    """Gera chaves consistentes para ordenar texto, datas e notas."""
    if campo == "data":
        return _parse_data_tabela(valor) or datetime.min

    if campo == "nota":
        try:
            return (0, float(valor))
        except (TypeError, ValueError):
            return (1, str(valor or "").casefold())

    texto = unicodedata.normalize("NFD", str(valor or "").casefold())
    return "".join(caractere for caractere in texto if unicodedata.category(caractere) != "Mn")


def _parse_data_tabela(valor) -> Optional[datetime]:
    """Lê datas exibidas em formato brasileiro ou armazenadas em ISO 8601."""
    if isinstance(valor, datetime):
        return valor

    texto = str(valor or "").strip()
    try:
        return datetime.fromisoformat(texto.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        pass

    for formato in ("%d/%m/%Y, %H:%M", "%d/%m/%Y %H:%M", "%d/%m/%Y"):
        try:
            return datetime.strptime(texto, formato)
        except ValueError:
            continue
    return None
