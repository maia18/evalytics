"""Rotas de saúde, listagem e criação de avaliações."""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import ValidationError

from ..auth import get_institution_id, get_user_id, require_user
from ..config import (
    MAX_FILE_SIZE,
    bucket,
    db,
    INSTITUICAO_PADRAO_ID,
    logger,
)
from ..dependencies import cleanup_partial_evaluation
from ..schemas import EvaluationPayload, EvidenceManifestItem
from ..validation import (
    safe_filename,
    safe_path_segment,
    validate_file,
    validate_manifest,
)

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/avaliacoes")
def list_evaluations(user: dict = Depends(require_user)):
    logger.info("Iniciando listagem de avaliações.")
    uid = get_user_id(user)
    logger.info("UID autenticado obtido.")

    instituicao_id = get_institution_id(user)
    colecao = db.collection("avaliacoes")
    documentos_por_id = {
        documento.id: documento
        for documento in (
            colecao.where("usuario_id", "==", uid)
            .where("instituicao_id", "==", instituicao_id)
            .stream()
        )
    }
    if instituicao_id == INSTITUICAO_PADRAO_ID:
        for documento in colecao.where("usuario_id", "==", uid).stream():
            documentos_por_id.setdefault(documento.id, documento)

    avaliacoes = []
    for documento in documentos_por_id.values():
        dados = documento.to_dict() or {}
        if dados.get("instituicao_id", INSTITUICAO_PADRAO_ID) != instituicao_id:
            continue
        dados["id"] = documento.id
        avaliacoes.append(dados)

    avaliacoes.sort(
        key=lambda item: item.get("data_avaliacao", ""),
        reverse=True,
    )
    return {"avaliacoes": avaliacoes}


@router.post("/avaliacoes", status_code=201)
async def create_evaluation(
    avaliacao: str = Form(...),
    evidencias: str = Form("[]"),
    files: list[UploadFile] = File(default=[]),
    user: dict = Depends(require_user),
):
    uid = get_user_id(user)

    try:
        payload = EvaluationPayload.model_validate_json(avaliacao)
        manifest_data = json.loads(evidencias)
        if not isinstance(manifest_data, list):
            raise ValueError("O manifesto deve ser uma lista.")
        manifest = [
            EvidenceManifestItem.model_validate(item)
            for item in manifest_data
        ]
    except (ValueError, ValidationError, TypeError) as exc:
        raise HTTPException(
            status_code=400,
            detail="Dados da avaliação ou lista de evidências inválidos.",
        ) from exc

    evaluation_ref = None
    uploaded_paths: list[str] = []
    try:
        validate_manifest(manifest, files)
        now = datetime.now(timezone.utc).isoformat()
        evaluation_ref = db.collection("avaliacoes").document()
        evaluation_ref.set({
            "curso_id": payload.curso_id,
            "curso_nome": payload.curso_nome,
            "instituicao_id": get_institution_id(user),
            "data_avaliacao": now,
            "respostas": payload.respostas,
            "justificativas": payload.justificativas,
            "usuario_id": uid,
            "evidencias": [],
        })

        evidence_documents = []
        for upload, item in zip(files, manifest, strict=True):
            content = await upload.read(MAX_FILE_SIZE + 1)
            mime = validate_file(upload, content)
            filename = safe_filename(item.filename)
            extension = Path(filename).suffix.lower()
            indicador_path = safe_path_segment(item.indicador_id)
            evidence_id = str(uuid.uuid4())
            object_path = (
                f"evidencias/{uid}/{evaluation_ref.id}/"
                f"{indicador_path}/{evidence_id}{extension}"
            )

            blob = bucket.blob(object_path)
            blob.metadata = {
                "ownerUid": uid,
                "evaluationId": evaluation_ref.id,
                "indicatorId": item.indicador_id,
                "originalFilename": filename,
            }
            # Registrar antes do upload permite limpar falhas parciais.
            uploaded_paths.append(object_path)
            blob.upload_from_string(content, content_type=mime)
            evidence_documents.append({
                "id": evidence_id,
                "upload_id": item.upload_id,
                "indicador_id": item.indicador_id,
                "nome": filename,
                "caminho_storage": object_path,
                "content_type": mime,
                "tamanho_bytes": len(content),
                "criado_em": now,
            })

        evaluation_ref.update({"evidencias": evidence_documents})
        logger.info(
            "Avaliação %s criada para o usuário %s. Evidências: %s",
            evaluation_ref.id,
            uid,
            len(evidence_documents),
        )
        return {"id": evaluation_ref.id, "evidencias": evidence_documents}

    except HTTPException:
        cleanup_partial_evaluation(evaluation_ref, uploaded_paths)
        raise
    except Exception as exc:
        cleanup_partial_evaluation(evaluation_ref, uploaded_paths)
        logger.exception("Erro ao salvar avaliação e evidências.")
        raise HTTPException(
            status_code=500,
            detail="Não foi possível salvar a avaliação e suas evidências.",
        ) from exc
    finally:
        for upload in files:
            try:
                await upload.close()
            except Exception:
                logger.warning("Não foi possível fechar um arquivo recebido.")
