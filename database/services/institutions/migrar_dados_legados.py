"""Atribui à instituição padrão os cursos e avaliações antigos sem tenant.

Por segurança, a execução sem ``--aplicar`` é apenas uma prévia. Use ``--aplicar``
depois de confirmar que todos os registros legados pertencem à instituição padrão.
"""

import argparse

from database.services.firebase_config import db
from database.services.institutions.institutions_service import (
    COLECAO_AVALIACOES,
    COLECAO_CURSOS,
    INSTITUICAO_PADRAO_ID,
)


def migrar(aplicar: bool = False) -> dict[str, int]:
    totais: dict[str, int] = {}
    for colecao in (COLECAO_CURSOS, COLECAO_AVALIACOES):
        snapshots = list(db.collection(colecao).stream())
        pendentes = [
            snapshot
            for snapshot in snapshots
            if not (snapshot.to_dict() or {}).get("instituicao_id")
        ]
        totais[colecao] = len(pendentes)
        print(f"{colecao}: {len(pendentes)} documento(s) legado(s) sem instituição")

        if not aplicar:
            continue

        for inicio in range(0, len(pendentes), 400):
            lote = db.batch()
            for snapshot in pendentes[inicio : inicio + 400]:
                lote.update(
                    snapshot.reference,
                    {"instituicao_id": INSTITUICAO_PADRAO_ID},
                )
            lote.commit()

    if aplicar:
        print(f"Migração concluída para a instituição '{INSTITUICAO_PADRAO_ID}'.")
    else:
        print("Prévia concluída. Nenhum documento foi alterado; use --aplicar após revisar.")
    return totais


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--aplicar",
        action="store_true",
        help="Grava instituicao_id nos documentos legados sem esse campo.",
    )
    migrar(aplicar=parser.parse_args().aplicar)
