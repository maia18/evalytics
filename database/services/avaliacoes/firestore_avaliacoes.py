import logging
from database.services.firebase_config import db
from database.services.institutions.institutions_service import listar_documentos_da_instituicao
from database.services.institutions.institutions_service import obter_instituicao_id_atual
from database.services.memory_cache import obter_cache, salvar_cache
from database.services.cursos.firestore_courses import obter_cursos_db
from utils.services.indicadores.indicadores_repository import listar_indicadores
from utils.services.cursos.curso_utils import (
    criar_indice_cursos_atuais,
    resolver_curso_avaliacao,
)
from .avaliacoes_formatadores import (
    NOMES_EIXOS, 
    definir_cor_nota, 
    formatar_data
)

logger = logging.getLogger(__name__)
COLECAO_AVALIACOES = "avaliacoes"

def obter_respostas_tabela() -> list[dict]:
    """
    Busca as avaliações reais do Firestore e transforma cada resposta de indicador em uma linha da tabela.
        Uma avaliação pode gerar várias linhas, pois cada indicador respondido representa uma resposta individual.
    """
    chave_cache = f"respostas_tabela:{obter_instituicao_id_atual()}"
    encontrado, valor = obter_cache(chave_cache)
    if encontrado:
        return [dict(linha) for linha in valor]

    try:
        documentos = listar_documentos_da_instituicao(COLECAO_AVALIACOES)
        indicadores = listar_indicadores()

        mapa_indicadores = {
            indicador.get("id"): indicador
            for indicador in indicadores
            if indicador.get("id")
        }
        cursos_cadastrados = obter_cursos_db()
        indice_cursos = criar_indice_cursos_atuais(cursos_cadastrados)

        linhas = []

        for documento in documentos:
            dados = documento.to_dict() or {}
            avaliacao_id = documento.id
            curso_atual = resolver_curso_avaliacao(dados, indice_cursos)
            if not curso_atual:
                continue
            curso_nome = curso_atual.get("nome", "Curso não informado")
            
            data_formatada = formatar_data(dados.get("data_avaliacao"))
            respostas = dados.get("respostas", {})

            if not isinstance(respostas, dict):
                continue

            for indicador_id, resposta in respostas.items():
                indicador = mapa_indicadores.get(indicador_id, {})
                titulo_indicador = indicador.get("titulo", "Indicador não encontrado")
                eixo = indicador.get("eixo")
                nome_eixo = NOMES_EIXOS.get(eixo, f"Eixo {eixo}" if eixo else "Geral")

                try:
                    nota = float(resposta)
                except (TypeError, ValueError):
                    continue

                linhas.append(
                    {
                        "id": avaliacao_id[:7].upper(),
                        "data": data_formatada,
                        "curso": curso_nome,
                        "eixo": nome_eixo,
                        "indicador": titulo_indicador,
                        "nota": f"{nota:.1f}",
                        "cor_nota": definir_cor_nota(nota),
                        "comentario": None,
                    }
                )

        # Mais recentes primeiro.
        linhas.sort(key=lambda item: item["data"], reverse=True)

        salvar_cache(
            chave_cache,
            tuple(dict(linha) for linha in linhas),
            15.0,
        )
        return linhas

    except Exception:
        logger.exception("Erro ao buscar respostas das avaliações.")
        return []
