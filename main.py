import logging
import flet as ft

logger = logging.getLogger(__name__)

async def main(page: ft.Page) -> None:
    try:
        # ======================================================
        # CONFIGURAÇÃO DA APLICAÇÃO
        # ======================================================
        
        from components.core.globals import configurar_aplicacao
        configurar_aplicacao(page) 

        # ======================================================
        # FILE PICKER COMPARTILHADO
        # ======================================================

        seletor_arquivos = ft.FilePicker()
        
        page.file_picker_evidencias = seletor_arquivos
        page.services.append(seletor_arquivos)
        logger.info(
            "FilePicker de evidências registrado."
        )

        # ======================================================
        # TEMA
        # ======================================================
        
        from components.core.theme.theme_config import configurar_tema

        page.is_dark_mode = True
        configurar_tema(page, page.is_dark_mode)

        # ======================================================
        # AUTENTICAÇÃO E SESSÃO
        # ======================================================
        
        from components.core.auth.auth_state import auth_state
        from database.services.firebase_keys import FIREBASE_API_KEY

        await auth_state.inicializar_storage(page)
        sessao_restaurada = await auth_state.restaurar_sessao(
            page=page,
            api_key=FIREBASE_API_KEY,
        )

        # ======================================================
        # NAVEGAÇÃO INICIAL
        # ======================================================
        
        from components.core.router.rotas_cts import ROTA_INICIAL
        from components.core.navigator import Navigator
        
        if sessao_restaurada:
            logger.info(
                "Sessão persistida restaurada com sucesso."
            )
            Navigator(page).go("/inicio")

        else:
            logger.info(
                "Nenhuma sessão persistida encontrada."
            )
            Navigator(page).go(ROTA_INICIAL)

    except Exception:
        logger.exception(
            "Falha ao inicializar a aplicação."
        )
        raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    ft.run(
        main,
        assets_dir="assets",
    )