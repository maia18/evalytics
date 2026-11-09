import logging
import re
from typing import Optional
from firebase_admin import firestore
from database.services.firebase_config import db
from database.services.institutions.institutions_service import (
    documento_pertence_a_instituicao,
    listar_documentos_da_instituicao,
    obter_instituicao_id_atual,
)
from database.services.memory_cache import invalidar_cache, obter_cache, salvar_cache
from .curso_notificacoes import criar_notificacao_curso

logger = logging.getLogger(__name__)
COLECAO_CURSOS = "cursos"
# Escritas no catálogo invalidam os caches relacionados imediatamente.
CACHE_TTL_SEGUNDOS = 15.0


def _invalidar_cache_cursos() -> None:
    invalidar_cache("cursos:")
    invalidar_cache("cursos_avaliacoes:")
    invalidar_cache("avaliacoes:")
    invalidar_cache("respostas_tabela:")
    invalidar_cache("dashboard:")
    invalidar_cache("resultados:")
    invalidar_cache("resumo_eixos:")


def curso_esta_ativo(curso: dict) -> bool:
    """Normaliza o status de cursos novos e documentos legados."""
    valor = curso.get("ativo", curso.get("status", True))
    if isinstance(valor, bool):
        return valor
    return str(valor).strip().casefold() in {"ativo", "active", "true", "1"}


def _notificar_status_curso(nome: str, ativo: bool) -> None:
    status = "ativado" if ativo else "inativado"
    disponibilidade = (
        "está disponível para avaliações."
        if ativo
        else "não está disponível para novas avaliações."
    )
    criar_notificacao_curso(
        titulo=f"Curso {status}",
        descricao=f"O curso '{nome}' foi {status} e {disponibilidade}",
    )


def gerar_codigo_curso() -> str:
    """Gera o próximo código sequencial CUR-0001 disponível."""
    codigos = {
        str(curso.get("codigo", "")).strip().upper()
        for curso in obter_cursos_db()
    }
    numeros = [
        int(match.group(1))
        for codigo in codigos
        if (match := re.fullmatch(r"CUR-(\d+)", codigo))
    ]
    proximo = max(numeros, default=0) + 1
    while f"CUR-{proximo:04d}" in codigos:
        proximo += 1
    return f"CUR-{proximo:04d}"


def adicionar_curso_db(
    codigo: str,
    nome: str,
    depto: str,
    coord: str,
    ativo: bool = True,
) -> Optional[str]:
    """
    Adiciona um curso na coleção de cursos.
        Retorna o ID do documento criado, ou None em caso de erro.
    """
    try:
        novo_curso = {
            "codigo": codigo,
            "nome": nome,
            "departamento": depto,
            "coordenador": coord,
            "ativo": ativo,
            "instituicao_id": obter_instituicao_id_atual(),
            "timestamp": firestore.SERVER_TIMESTAMP,
        }

        _, doc_ref = db.collection(COLECAO_CURSOS).add(novo_curso)
        _invalidar_cache_cursos()
        logger.info("Curso '%s' adicionado com sucesso.", nome)

        criar_notificacao_curso(
            titulo="Novo curso cadastrado",
            descricao=f"O curso '{nome}' foi cadastrado com sucesso.",
        )

        return doc_ref.id

    except Exception:
        logger.exception("Erro ao adicionar curso.")
        return None

def obter_cursos_db(propagar_erro: bool = False) -> list[dict]:
    """
    Retorna a lista de cursos cadastrados, cada um incluindo seu ID de documento.
    """
    chave_cache = f"cursos:{obter_instituicao_id_atual()}"
    encontrado, valor = obter_cache(chave_cache)
    if encontrado:
        return [dict(curso) for curso in valor]

    try:
        docs = listar_documentos_da_instituicao(COLECAO_CURSOS)
        lista_cursos = []

        for doc in docs:
            dado = doc.to_dict() or {}
            if not documento_pertence_a_instituicao(dado):
                continue
            dado["id"] = doc.id
            lista_cursos.append(dado)

        salvar_cache(chave_cache, tuple(dict(curso) for curso in lista_cursos), CACHE_TTL_SEGUNDOS)
        return lista_cursos

    except Exception:
        logger.exception("Erro ao obter cursos.")
        if propagar_erro:
            raise
        return []

def atualizar_curso_db(
    doc_id: str,
    nome: str,
    depto: str,
    coord: str,
    ativo: bool = True,
) -> bool:
    """
    Atualiza um curso existente.
        Retorna True em caso de sucesso.
    """
    try:
        curso_ref = db.collection(COLECAO_CURSOS).document(doc_id)
        snapshot = curso_ref.get()
        dados_atuais = snapshot.to_dict() or {}
        if not snapshot.exists or not documento_pertence_a_instituicao(dados_atuais):
            return False
        status_anterior = curso_esta_ativo(dados_atuais)
        status_alterado = ativo != status_anterior

        curso_ref.update(
            {
                "nome": nome,
                "departamento": depto,
                "coordenador": coord,
                "ativo": ativo,
            }
        )
        _invalidar_cache_cursos()

        logger.info("Curso '%s' atualizado com sucesso.", nome)

        if status_alterado:
            _notificar_status_curso(nome, ativo)
        else:
            criar_notificacao_curso(
                titulo="Curso atualizado",
                descricao=f"As informações do curso '{nome}' foram atualizadas.",
            )

        return True

    except Exception:
        logger.exception("Erro ao atualizar curso.")
        return False


def atualizar_status_curso_db(doc_id: str, ativo: bool) -> bool:
    """Atualiza apenas o status, sem alterar os demais dados do curso."""
    try:
        curso_ref = db.collection(COLECAO_CURSOS).document(doc_id)
        snapshot = curso_ref.get()
        dados_atuais = snapshot.to_dict() or {}
        if not snapshot.exists or not documento_pertence_a_instituicao(dados_atuais):
            return False
        status_anterior = curso_esta_ativo(dados_atuais)

        curso_ref.update({"ativo": ativo})
        _invalidar_cache_cursos()
        logger.info(
            "Status do curso '%s' alterado para %s.",
            doc_id,
            "ativo" if ativo else "inativo",
        )
        if ativo != status_anterior:
            _notificar_status_curso(dados_atuais.get("nome", doc_id), ativo)
        return True
    except Exception:
        logger.exception("Erro ao atualizar o status do curso '%s'.", doc_id)
        return False

def excluir_curso_db(doc_id: str) -> bool:
    """
    Exclui um curso pelo ID do documento.
        Retorna True em caso de sucesso.
    """
    try:
        curso_ref = db.collection(COLECAO_CURSOS).document(doc_id)
        curso = curso_ref.get()

        if not curso.exists:
            logger.warning("Curso '%s' não encontrado para exclusão.", doc_id)
            return False

        dados_curso = curso.to_dict() or {}
        if not documento_pertence_a_instituicao(dados_curso):
            logger.warning("Curso '%s' pertence a outra instituição.", doc_id)
            return False
        nome_curso = dados_curso.get("nome", doc_id)

        curso_ref.delete()
        _invalidar_cache_cursos()
        logger.info("Curso '%s' excluído com sucesso.", nome_curso)

        criar_notificacao_curso(
            titulo="Curso removido",
            descricao=f"O curso '{nome_curso}' foi removido com sucesso.",
        )

        return True

    except Exception:
        logger.exception("Erro ao excluir curso.")
        return False
