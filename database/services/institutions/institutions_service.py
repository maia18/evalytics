"""Leitura do contexto institucional e catálogo de campi do Evalytics."""

import os

from firebase_admin import firestore
from database.services.firebase_config import db
from database.services.memory_cache import invalidar_cache, obter_cache, salvar_cache

COLECAO_INSTITUICOES = "instituicoes"
COLECAO_CURSOS = "cursos"
COLECAO_AVALIACOES = "avaliacoes"
INSTITUICAO_PADRAO_ID = os.getenv("EVALYTICS_INSTITUICAO_ID", "ufc").strip() or "ufc"


def obter_instituicao_id_atual() -> str:
    """Resolve o tenant da sessão; permite configurar o padrão pelo ambiente."""
    usuario_id = None
    try:
        from components.core.auth.auth_state import auth_state

        usuario = auth_state.usuario or {}
        instituicao_id = usuario.get("instituicao_id")
        if instituicao_id:
            return str(instituicao_id).strip()
        usuario_id = usuario.get("localId") or usuario.get("uid") or usuario.get("user_id")
    except (AttributeError, TypeError):
        pass
    if usuario_id:
        instituicao_usuario = _obter_instituicao_id_usuario(str(usuario_id))
        if instituicao_usuario:
            # Guarda o tenant no estado autenticado desta sessão para que a
            # montagem de cada tela não consulte o perfil repetidamente.
            try:
                usuario["instituicao_id"] = instituicao_usuario
            except (NameError, TypeError):
                pass
            return instituicao_usuario
    return INSTITUICAO_PADRAO_ID


def _obter_instituicao_id_usuario(usuario_id: str) -> str | None:
    """Resolve o vínculo Firestore usuarios/{uid} para evitar tenant desatualizado."""
    try:
        snapshot = db.collection("usuarios").document(usuario_id).get()
        dados = snapshot.to_dict() or {}
        valor = dados.get("instituicao_id")
        return str(valor).strip() if valor else None
    except Exception:
        return None


def documento_pertence_a_instituicao(dados: dict, instituicao_id: str | None = None) -> bool:
    """Mantém dados legados sem tenant na instituição padrão durante a migração."""
    instituicao_atual = instituicao_id or obter_instituicao_id_atual()
    instituicao_documento = dados.get("instituicao_id")
    if instituicao_documento:
        return str(instituicao_documento) == instituicao_atual
    return instituicao_atual == INSTITUICAO_PADRAO_ID


def listar_documentos_da_instituicao(nome_colecao: str, instituicao_id: str | None = None):
    """Lê documentos de uma coleção e limita o resultado ao tenant ativo."""
    chave = instituicao_id or obter_instituicao_id_atual()
    colecao = db.collection(nome_colecao)
    if chave != INSTITUICAO_PADRAO_ID:
        yield from colecao.where("instituicao_id", "==", chave).stream()
        return

    # A instituição padrão ainda pode ter documentos legados sem tenant. Uma
    # única leitura completa os cobre sem executar primeiro a consulta filtrada
    # e depois reler toda a coleção para o fallback.
    for snapshot in colecao.stream():
        dados = snapshot.to_dict() or {}
        if documento_pertence_a_instituicao(dados, chave):
            yield snapshot


def obter_instituicao(instituicao_id: str | None = None) -> dict:
    """Retorna os metadados da instituição atual."""
    chave = instituicao_id or obter_instituicao_id_atual()
    chave_cache = f"instituicao:{chave}"
    encontrado, valor = obter_cache(chave_cache)
    if encontrado:
        return dict(valor)
    try:
        snapshot = db.collection(COLECAO_INSTITUICOES).document(chave).get()
        if snapshot.exists:
            dados = snapshot.to_dict() or {}
            dados["id"] = snapshot.id
            salvar_cache(chave_cache, dict(dados), 300)
            return dados
    except Exception:
        pass
    dados = {"id": chave, "sigla": chave.upper(), "nome": chave.upper()}
    salvar_cache(chave_cache, dict(dados), 300)
    return dados


def listar_campi_instituicao(instituicao_id: str | None = None) -> list[dict]:
    """Lista os campi ativos cadastrados para a instituição da sessão."""
    chave = instituicao_id or obter_instituicao_id_atual()
    chave_cache = f"campi:{chave}"
    encontrado, valor = obter_cache(chave_cache)
    if encontrado:
        return [dict(campus) for campus in valor]
    try:
        snapshots = (
            db.collection(COLECAO_INSTITUICOES)
            .document(chave)
            .collection("campi")
            .stream()
        )
        campi = []
        for snapshot in snapshots:
            campus = snapshot.to_dict() or {}
            if campus.get("ativo", True) is False:
                continue
            campus["id"] = snapshot.id
            campi.append(campus)
        campi = sorted(campi, key=lambda item: str(item.get("nome", "")).casefold())
        salvar_cache(chave_cache, tuple(dict(campus) for campus in campi), 300)
        return campi
    except Exception:
        salvar_cache(chave_cache, (), 30)
        return []


def salvar_instituicao(
    instituicao_id: str,
    nome: str,
    sigla: str,
    ativa: bool = True,
) -> bool:
    """Cria ou atualiza metadados institucionais sem substituir campos extras."""
    chave = instituicao_id.strip()
    if not chave or not nome.strip() or not sigla.strip():
        return False
    try:
        db.collection(COLECAO_INSTITUICOES).document(chave).set(
            {
                "nome": nome.strip(),
                "sigla": sigla.strip().upper(),
                "ativa": ativa,
                "atualizado_em": firestore.SERVER_TIMESTAMP,
            },
            merge=True,
        )
        invalidar_cache(f"instituicao:{chave}")
        return True
    except Exception:
        return False


def salvar_campus(
    campus_id: str,
    nome: str,
    municipio: str,
    uf: str,
    instituicao_id: str | None = None,
    ativo: bool = True,
) -> bool:
    """Cria ou atualiza um campus dentro da instituição correspondente."""
    chave_instituicao = instituicao_id or obter_instituicao_id_atual()
    chave_campus = campus_id.strip()
    if not chave_campus or not nome.strip():
        return False
    try:
        db.collection(COLECAO_INSTITUICOES).document(chave_instituicao).collection(
            "campi"
        ).document(chave_campus).set(
            {
                "nome": nome.strip(),
                "municipio": municipio.strip(),
                "uf": uf.strip().upper(),
                "ativo": ativo,
                "atualizado_em": firestore.SERVER_TIMESTAMP,
            },
            merge=True,
        )
        invalidar_cache(f"campi:{chave_instituicao}")
        return True
    except Exception:
        return False

