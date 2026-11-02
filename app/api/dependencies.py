"""Acesso autorizado a avaliações e limpeza de operações incompletas."""

from fastapi import HTTPException

from .config import INSTITUICAO_PADRAO_ID, bucket, db, logger


def get_owned_evaluation(
    evaluation_id: str,
    uid: str,
    instituicao_id: str = INSTITUICAO_PADRAO_ID,
):
    referencia = db.collection("avaliacoes").document(evaluation_id)
    snapshot = referencia.get()

    if not snapshot.exists:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada.")

    dados = snapshot.to_dict() or {}
    if dados.get("usuario_id") != uid:
        raise HTTPException(
            status_code=403,
            detail="Você não tem acesso a esta avaliação.",
        )
    if dados.get("instituicao_id", INSTITUICAO_PADRAO_ID) != instituicao_id:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada.")
    return referencia, dados


def cleanup_partial_evaluation(evaluation_ref, uploaded_paths: list[str]) -> None:
    """Remove os arquivos e o documento de uma operação incompleta."""
    for caminho in uploaded_paths:
        try:
            bucket.blob(caminho).delete()
        except Exception:
            logger.exception("Falha ao remover upload parcial: %s", caminho)

    if evaluation_ref is not None:
        try:
            evaluation_ref.delete()
        except Exception:
            logger.exception(
                "Falha ao remover avaliação incompleta: %s",
                evaluation_ref.id,
            )
