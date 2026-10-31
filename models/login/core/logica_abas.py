import flet as ft
from typing import Callable
from models.login.core.tab_style import criar_estilo_aba

def obter_funcao_alternar(
    btn_aba_signin: ft.TextButton, 
    btn_aba_signup: ft.TextButton, 
    campo_nome: ft.Column,
    opcoes_extras: ft.Row, 
    btn_login: ft.ElevatedButton, 
    cor_texto_titulo: str, 
    cor_primaria: str,
) -> Callable[[ft.ControlEvent], None]:
    """
    Fábrica (Closure) que gera a função responsável por alternar a UI entre o modo 'Login' e o modo 'Cadastro'.
        Recebe as referências físicas dos botões e campos de texto e devolve a função (alternar_modo) que será plugada no `on_click`.
    """

    def alternar_modo(e: ft.ControlEvent) -> None:
        
        is_signup = e.control.data == "signup" # Descobre qual botão foi clicado através da propriedade `data` definida na View

        '''1. Altera a aparência dos botões (Qual está ativo)'''
        btn_aba_signin.style = criar_estilo_aba(
            not is_signup, 
            cor_primaria, 
            cor_texto_titulo
        )
        btn_aba_signup.style = criar_estilo_aba(
            is_signup, 
            cor_primaria, 
            cor_texto_titulo
        )

        '''2. Mostra ou esconde campos dependendo do contexto'''
        campo_nome.visible = is_signup          # Oculta "Nome" no Login
        opcoes_extras.visible = not is_signup   # Oculta "Lembrar senha" no Cadastro

        '''3. Troca o rótulo do botão de ação primária'''
        btn_login.text = "Criar conta" if is_signup else "Entrar"

        '''4. Envia as modificações para serem renderizadas'''
        e.page.update()

    return alternar_modo
