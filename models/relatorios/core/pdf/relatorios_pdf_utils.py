import flet as ft
from models.avaliacoes.core.feedback import mostrar_feedback
from models.relatorios.core.pdf.export_pdf import (
    normalizar_nome_curso, 
    gerar_pdf_completo,
)

NOMES_EIXOS = {
    1: "Organização Didático-Pedagógica",
    2: "Corpo Docente e Tutorial",
    3: "Infraestrutura",
}

def calcular_medias_pdf(resultados_filtrados: list[dict]) -> dict[int, float | None]:
    """Processa a lista de resultados e calcula a média aritmética por eixo."""
    acumuladores = {1: [], 2: [], 3: []}

    for resultado in resultados_filtrados:
        eixos = resultado.get("eixos", {})
        if not isinstance(eixos, dict):
            continue

        for eixo_id in (1, 2, 3):
            valor = eixos.get(eixo_id)
            if valor is None:
                continue

            try:
                valor = float(valor)
            except (TypeError, ValueError):
                continue

            if valor > 0:
                acumuladores[eixo_id].append(valor)

    medias = {}
    for eixo_id, notas in acumuladores.items():
        medias[eixo_id] = sum(notas) / len(notas) if notas else None

    return medias

async def processar_exportacao_pdf(
    page: ft.Page, 
    resultados_filtrados: list[dict], 
    semestre_atual: str | None,
    eixo_atual: int | None = None,
) -> None:
    """Valida os dados atuais e prepara os agregados para a geração do PDF."""
    
    if not resultados_filtrados:
        mostrar_feedback(page, "Não existem dados para gerar o PDF.", sucesso=False)
        return

    medias = calcular_medias_pdf(resultados_filtrados)
    medias_validas = {eixo_id: media for eixo_id, media in medias.items() if media is not None}

    if not medias_validas:
        mostrar_feedback(page, "Não existem médias disponíveis para gerar o PDF.", sucesso=False)
        return

    semestre_pdf = semestre_atual if semestre_atual is not None else "Todos"
    quantidade_avaliacoes = len(resultados_filtrados)

    cursos = sorted(
        {
            normalizar_nome_curso(
                resultado.get("curso_nome", resultado.get("curso", ""))
            )
            for resultado in resultados_filtrados
            if resultado.get("curso_nome") or resultado.get("curso")
        }
    )

    await gerar_pdf_completo(
        page,
        medias=medias_validas,
        nomes_eixos=NOMES_EIXOS,
        semestre=semestre_pdf,
        quantidade_avaliacoes=quantidade_avaliacoes,
        cursos=cursos,
        resultados=resultados_filtrados,
        eixo_selecionado=eixo_atual,
    )
