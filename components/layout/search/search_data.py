import unicodedata
from difflib import SequenceMatcher

import flet as ft

from components.core.router.rotas_cts import ROTA_AVALIACOES, ROTA_CURSOS


def normalizar_busca(texto: str) -> str:
    decomposicao = unicodedata.normalize("NFD", texto.casefold())
    return "".join(
        caractere
        for caractere in decomposicao
        if unicodedata.category(caractere) != "Mn"
    )


def corresponde_busca(texto: str, consulta: str) -> bool:
    """Aceita trechos, termos separados e pequenos erros de digitação."""
    alvo = normalizar_busca(texto)
    termo = normalizar_busca(consulta).strip()
    if not termo:
        return False
    if termo in alvo:
        return True

    palavras_alvo = alvo.split()
    palavras_consulta = termo.split()
    for palavra in palavras_consulta:
        if any(
            palavra in candidata
            or (
                len(palavra) >= 5
                and len(candidata) >= 5
                and SequenceMatcher(None, palavra, candidata).ratio() >= 0.8
            )
            for candidata in palavras_alvo
        ):
            continue
        return False
    return True


def carregar_dados_internos_busca() -> dict[str, list[dict]]:
    """Carrega cursos e registros acessíveis à instituição atual."""
    from database.services.cursos.firestore_courses import obter_cursos_db
    from utils.services.avaliacoes.avaliacoes_service import listar_avaliacoes
    from utils.services.indicadores.indicadores_repository import listar_indicadores

    return {
        "cursos": obter_cursos_db(),
        "avaliacoes": listar_avaliacoes(),
        "indicadores": listar_indicadores(),
    }


def buscar_dados_internos(
    consulta: str, dados: dict[str, list[dict]]
) -> list[dict]:
    """Pesquisa cursos, avaliações, indicadores e notas sem expor justificativas."""
    from utils.services.relatorio.relatorio_utils import obter_semestre

    resultados = []

    for curso in dados.get("cursos", []):
        nome = str(curso.get("nome") or "Curso sem nome").strip()
        codigo = str(curso.get("codigo") or "").strip()
        departamento = str(curso.get("departamento") or "").strip()
        coordenador = str(curso.get("coordenador") or "").strip()
        ativo = curso.get("ativo", curso.get("status", True))
        status = "Ativo" if ativo is True or str(ativo).casefold() in {"ativo", "true", "1"} else "Inativo"
        campos = " ".join((nome, codigo, departamento, coordenador, status))
        if corresponde_busca(campos, consulta):
            detalhes = [parte for parte in (codigo, departamento, status) if parte]
            resultados.append(
                {
                    "categoria": "Cursos",
                    "titulo": nome,
                    "detalhe": " · ".join(detalhes) or "Curso cadastrado",
                    "icone": ft.Icons.SCHOOL_OUTLINED,
                    "rota": ROTA_CURSOS,
                    "termo_curso": nome,
                }
            )

    nomes_eixos = {
        1: "Organização Didático-Pedagógica",
        2: "Corpo Docente e Tutorial",
        3: "Infraestrutura",
    }
    indicadores = {
        str(indicador.get("id")): indicador
        for indicador in dados.get("indicadores", [])
        if indicador.get("id")
    }
    avaliacoes = sorted(
        dados.get("avaliacoes", []),
        key=lambda item: str(item.get("data_avaliacao") or ""),
        reverse=True,
    )
    for avaliacao in avaliacoes:
        curso = str(avaliacao.get("curso_nome") or "Curso não informado").strip()
        data = avaliacao.get("data_avaliacao")
        semestre = obter_semestre(data)
        if hasattr(data, "strftime"):
            data_texto = data.strftime("%d/%m/%Y")
            mes_texto = f"{data.year}.{1 if data.month <= 6 else 2}"
        else:
            data_texto = str(data or "")[:10]
            mes_texto = ""
            try:
                ano, mes, dia = data_texto.split("-")
                data_texto = f"{dia}/{mes}/{ano}"
                mes_texto = f"{ano}.{1 if int(mes) <= 6 else 2}"
            except ValueError:
                pass

        respostas = avaliacao.get("respostas") or {}
        texto_avaliacao = normalizar_busca(
            f"{curso} {semestre} {data_texto} {mes_texto} avaliação avaliação institucional"
        )
        correspondencias = []
        if corresponde_busca(texto_avaliacao, consulta):
            correspondencias.append(("", "", "", consulta))
        itens_resposta = respostas.items() if isinstance(respostas, dict) else []
        for indicador_id, nota in itens_resposta:
            indicador = indicadores.get(str(indicador_id), {})
            titulo = str(indicador.get("titulo") or "Indicador").strip()
            descricao = str(indicador.get("descricao") or "").strip()
            criterios = indicador.get("criterios") or {}
            texto_criterios = (
                " ".join(str(criterio) for criterio in criterios.values())
                if isinstance(criterios, dict)
                else str(criterios)
            )
            eixo = indicador.get("eixo")
            try:
                nome_eixo = nomes_eixos.get(int(eixo), f"Eixo {eixo}" if eixo else "")
            except (TypeError, ValueError):
                nome_eixo = ""
            texto_resposta = normalizar_busca(
                f"{titulo} {descricao} {texto_criterios} {nome_eixo} eixo {eixo} {nota}"
            )
            if corresponde_busca(texto_resposta, consulta):
                correspondencias.append((titulo, nome_eixo, str(nota), titulo))

        if not correspondencias:
            continue
        if correspondencias[0][:3] == ("", "", ""):
            correspondencias = [correspondencias[0]]

        for titulo_indicador, nome_eixo, nota, termo_resultado in correspondencias:
            resultados.append(
                {
                    "categoria": "Avaliações",
                    "titulo": (
                        f"{titulo_indicador} · {nota}/5"
                        if titulo_indicador
                        else f"Avaliação · {curso}"
                    ),
                    "detalhe": " · ".join(
                        parte
                        for parte in (
                            f"Curso: {curso}",
                            f"Eixo: {nome_eixo}" if nome_eixo else "",
                            f"Semestre {semestre}" if semestre else "",
                            data_texto,
                            f"{len(respostas)} respostas",
                        )
                        if parte
                    ),
                    "icone": ft.Icons.ASSIGNMENT_OUTLINED,
                    "rota": ROTA_AVALIACOES,
                    "termo_avaliacao": termo_resultado,
                }
            )

    return resultados
