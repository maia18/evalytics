import logging
from typing import Optional
from firebase_admin import firestore
from database.services.firebase_config import db

'''
Configura o logger para este módulo.
    Usar logger.exception() no bloco except salva o stack trace completo (linha do erro), o que facilita muito o debug em produção.
'''
logger = logging.getLogger(__name__)
COLECAO_NOTIFICACOES = "notificacoes" # Extrair nomes de coleções para constantes evita erros de digitação (typos) nas queries.

def adicionar_notificacao(
    tipo: str,
    titulo: str,
    descricao: str,
    usuario_id: str,
) -> Optional[str]:
    """Cria uma nova notificação no banco de dados e retorna seu ID gerado."""
    
    try:
        nova_notificacao = {
            "tipo": tipo,
            "titulo": titulo,
            "descricao": descricao,
            "data_criacao": firestore.SERVER_TIMESTAMP, # O SERVER_TIMESTAMP garante que a data será gravada com o relógio oficial do servidor do Google, evitando bugs se o fuso horário do PC do usuário estiver errado
            
            "lida": False,
            "usuario_id": usuario_id,
        }

        '''
        .add() gera um ID alfanumérico aleatório automaticamente.
            Retorna uma tupla onde o segundo item é a referência do documento (doc_ref).
        '''
        _, doc_ref = db.collection(COLECAO_NOTIFICACOES).add(nova_notificacao)

        return doc_ref.id

    except Exception:
        logger.exception("Erro ao adicionar notificação.")
        return None # Retornar None em vez de quebrar o app permite que o chamador trate o erro graciosamente

def listar_notificacoes(usuario_id: str) -> list[dict]:
    """Busca todas as notificações pertencentes a um usuário específico."""
    
    try:
        # .stream() é mais eficiente em memória que .get() para listas grandes, pois baixa os documentos sob demanda (como um gerador iterável).
        docs = (
            db.collection(COLECAO_NOTIFICACOES)
            .where("usuario_id", "==", usuario_id)
            .stream()
        )

        lista_notificacoes = []

        for doc in docs:
            dado = doc.to_dict() # doc.to_dict() traz os dados (titulo, tipo), mas NÃO traz o ID do documento.
            
            # É necessário injetar manualmente o ID no dicionário para que a UI saiba qual documento atualizar/excluir no futuro.
            dado["id"] = doc.id
            lista_notificacoes.append(dado)

        return lista_notificacoes

    except Exception:
        logger.exception("Erro ao obter notificações.")
        return [] # Retorna lista vazia para não quebrar iteradores na UI (for item in lista)

def contar_notificacoes_nao_lidas(usuario_id: str) -> int:
    """Retorna o número de mensagens pendentes para alimentar o 'Badge' vermelho do sino."""
    
    try:
        # Filtros compostos no Firestore. 
        #   Nota: Dependendo do uso, o Firebase pode exigir a criação de um Índice (Index) no console.
        docs = (
            db.collection(COLECAO_NOTIFICACOES)
            .where("usuario_id", "==", usuario_id)
            .where("lida", "==", False)
            .stream()
        )

        # Expressão geradora pythonica: Conta os itens iterando pelo stream sem precisar carregar a lista inteira na memória do servidor.
        return sum(1 for _ in docs)

    except Exception:
        logger.exception("Erro ao contar notificações não lidas.")
        return 0

def marcar_notificacao_como_lida(notificacao_id: str) -> bool:
    """Atualiza o status de uma única notificação."""
    
    try:
        # .update() altera apenas o campo 'lida', mantendo o resto intacto.
        #   Se usássemos .set(), apagaria o título e a descrição se não os passássemos junto.
        (
            db.collection(COLECAO_NOTIFICACOES)
            .document(notificacao_id)
            .update({"lida": True})
        )
        return True

    except Exception:
        logger.exception("Erro ao marcar notificação como lida.")
        return False

def marcar_todas_como_lidas(usuario_id: str) -> bool:
    """Marca múltiplas notificações como lidas usando 'Batch' (Lote)."""
    
    try:
        # 1. Primeiro, descobre quais documentos precisam ser alterados
        docs = (
            db.collection(COLECAO_NOTIFICACOES)
            .where("usuario_id", "==", usuario_id)
            .where("lida", "==", False)
            .stream()
        )

        # 2. Inicia uma transação em lote (Batch).
        #   Um batch garante "Atomicidade": ou todas as atualizações funcionam, ou nenhuma funciona.
        batch = db.batch()
        quantidade = 0

        # 3. Prepara as instruções de atualização sem enviá-las para a rede ainda
        for doc in docs:
            batch.update(
                doc.reference,
                {"lida": True},
            )
            quantidade += 1

        # 4. Envia todas as alterações em uma única requisição HTTP (muito mais rápido e barato)
        if quantidade > 0:
            batch.commit()

        return True

    except Exception:
        logger.exception("Erro ao marcar todas as notificações como lidas.")
        return False


def excluir_todas_notificacoes(usuario_id: str) -> bool:
    """Exclui em lotes somente as notificações pertencentes ao usuário informado."""
    try:
        docs = (
            db.collection(COLECAO_NOTIFICACOES)
            .where("usuario_id", "==", usuario_id)
            .stream()
        )

        batch = db.batch()
        quantidade = 0
        for doc in docs:
            batch.delete(doc.reference)
            quantidade += 1

            # O Firestore limita cada lote a 500 operações; mantemos margem.
            if quantidade == 450:
                batch.commit()
                batch = db.batch()
                quantidade = 0

        if quantidade:
            batch.commit()

        return True
    except Exception:
        logger.exception("Erro ao excluir todas as notificações do usuário.")
        return False
