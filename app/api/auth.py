"""Dependências de autenticação Firebase para as rotas."""

from fastapi import Header, HTTPException
from firebase_admin import auth

from .config import INSTITUICAO_PADRAO_ID, db, logger


def require_user(
    authorization: str | None = Header(default=None),
) -> dict:
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Token de autenticação ausente.",
        )

    esquema, separador, token = authorization.partition(" ")

    if not separador or esquema.lower() != "bearer" or not token.strip():
        raise HTTPException(
            status_code=401,
            detail="Cabeçalho de autenticação inválido.",
        )

    try:
        usuario = auth.verify_id_token(token.strip())
        if not usuario.get("uid"):
            raise ValueError("Token sem UID.")
        return usuario
    except Exception as exc:
        logger.warning("Token Firebase inválido ou expirado.")
        raise HTTPException(
            status_code=401,
            detail="Sessão inválida. Entre novamente.",
        ) from exc


def get_user_id(user: dict) -> str:
    uid = user.get("uid")
    if not uid:
        raise HTTPException(
            status_code=401,
            detail="Não foi possível identificar o usuário.",
        )
    return str(uid)


def get_institution_id(user: dict) -> str:
    """Lê a instituição do claim confiável ou do perfil Firestore do usuário."""
    instituicao_id = user.get("instituicao_id")
    if instituicao_id:
        return str(instituicao_id)
    try:
        perfil = db.collection("usuarios").document(get_user_id(user)).get()
        dados = perfil.to_dict() or {}
        instituicao_id = dados.get("instituicao_id")
        if instituicao_id:
            return str(instituicao_id)
    except Exception:
        logger.exception("Falha ao resolver instituição do usuário autenticado.")
    return INSTITUICAO_PADRAO_ID
