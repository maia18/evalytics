"""Provisiona o cadastro inicial da UFC no Firestore (execução manual)."""

from firebase_admin import firestore

from database.services.firebase_config import db

INSTITUICAO_ID = "ufc"
CAMPI_UFC = {
    "benfica": {"nome": "Campus do Benfica", "municipio": "Fortaleza", "uf": "CE"},
    "pici": {"nome": "Campus do Pici", "municipio": "Fortaleza", "uf": "CE"},
    "porangabucu": {"nome": "Campus do Porangabuçu", "municipio": "Fortaleza", "uf": "CE"},
    "crateus": {"nome": "Campus de Crateús", "municipio": "Crateús", "uf": "CE"},
    "itapaje": {"nome": "Campus de Itapajé", "municipio": "Itapajé", "uf": "CE"},
    "quixada": {"nome": "Campus de Quixadá", "municipio": "Quixadá", "uf": "CE"},
    "russas": {"nome": "Campus de Russas", "municipio": "Russas", "uf": "CE"},
    "sobral": {"nome": "Campus de Sobral", "municipio": "Sobral", "uf": "CE"},
}


def provisionar_ufc() -> None:
    """Cria/atualiza o documento institucional e os campi oficiais usados no app."""
    instituicao = db.collection("instituicoes").document(INSTITUICAO_ID)
    instituicao.set(
        {
            "nome": "Universidade Federal do Ceará",
            "sigla": "UFC",
            "ativa": True,
            "atualizado_em": firestore.SERVER_TIMESTAMP,
        },
        merge=True,
    )
    batch = db.batch()
    for campus_id, dados in CAMPI_UFC.items():
        referencia = instituicao.collection("campi").document(campus_id)
        batch.set(
            referencia,
            {**dados, "ativo": True, "atualizado_em": firestore.SERVER_TIMESTAMP},
            merge=True,
        )
    batch.commit()


if __name__ == "__main__":
    provisionar_ufc()
