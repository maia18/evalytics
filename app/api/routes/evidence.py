"""Rotas de listagem, acesso temporário e remoção de evidências."""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException

from ..auth import get_institution_id, get_user_id, require_user
from ..config import bucket, logger
from ..dependencies import get_owned_evaluation

router = APIRouter()


@router.get("/avaliacoes/{evaluation_id}/evidencias")
def list_evidence(
    evaluation_id: str,
    user: dict = Depends(require_user),
):
    uid = get_user_id(user)
    _, dados = get_owned_evaluation(
        evaluation_id,
        uid,
        get_institution_id(user),
    )
    return {"evidencias": dados.get("evidencias", [])}


@router.get("/avaliacoes/{evaluation_id}/evidencias/{evidence_id}/url")
def get_evidence_url(
    evaluation_id: str,
    evidence_id: str,
    user: dict = Depends(require_user),
):
    uid = get_user_id(user)
    _, dados = get_owned_evaluation(
        evaluation_id,
        uid,
        get_institution_id(user),
    )
    evidencia = next(
        (
            item
            for item in dados.get("evidencias", [])
            if item.get("id") == evidence_id
        ),
        None,
    )
    if not evidencia:
        raise HTTPException(status_code=404, detail="Evidência não encontrada.")

    storage_path = evidencia.get("caminho_storage")
    if not storage_path:
        raise HTTPException(
            status_code=500,
            detail="O caminho da evidência não está cadastrado.",
        )

    try:
        blob = bucket.blob(storage_path)
        if not blob.exists():
            raise HTTPException(
                status_code=404,
                detail="Arquivo não encontrado no Storage.",
            )
        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=5),
            method="GET",
        )
        return {"url": url, "expira_em_segundos": 300}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(
            "Não foi possível gerar a URL da evidência %s.",
            evidence_id,
        )
        raise HTTPException(
            status_code=500,
            detail="Não foi possível gerar o link temporário da evidência.",
        ) from exc


@router.delete("/avaliacoes/{evaluation_id}/evidencias/{evidence_id}")
def delete_evidence(
    evaluation_id: str,
    evidence_id: str,
    user: dict = Depends(require_user),
):
    uid = get_user_id(user)
    evaluation_ref, dados = get_owned_evaluation(
        evaluation_id,
        uid,
        get_institution_id(user),
    )
    evidence_list = dados.get("evidencias", [])
    evidencia = next(
        (item for item in evidence_list if item.get("id") == evidence_id),
        None,
    )
    if not evidencia:
        raise HTTPException(status_code=404, detail="Evidência não encontrada.")

    storage_path = evidencia.get("caminho_storage")
    if not storage_path:
        raise HTTPException(
            status_code=500,
            detail="O caminho da evidência não está cadastrado.",
        )

    try:
        bucket.blob(storage_path).delete()
        evaluation_ref.update({
            "evidencias": [
                item for item in evidence_list if item.get("id") != evidence_id
            ]
        })
        logger.info(
            "Evidência %s removida da avaliação %s.",
            evidence_id,
            evaluation_id,
        )
        return {"ok": True}
    except Exception as exc:
        logger.exception("Erro ao excluir evidência %s.", evidence_id)
        raise HTTPException(
            status_code=500,
            detail="Não foi possível excluir a evidência.",
        ) from exc
