# Evalytics

O Evalytics apoia a autoavaliação institucional de cursos superiores. A aplicação permite gerenciar cursos, organizar indicadores por eixo, registrar avaliações e suas evidências e gerar relatórios.

A interface utiliza Python e Flet. A aplicação utiliza o Firebase Authentication para autenticação e o Cloud Firestore para armazenamento de dados. O repositório inclui uma API desenvolvida com FastAPI para avaliações e evidências.

Os procedimentos de avaliação e exportação de resultados estão no [Guia de uso](docs/guia-de-uso.md). A estrutura do projeto e os fluxos de armazenamento estão descritos no [Mapa técnico](docs/mapa-tecnico.md).

## Execução local no Windows

Em caso de falha na preparação do ambiente ou na autenticação, consulte o [Diagnóstico da instalação](#diagnóstico-da-instalação).

### 1. Preparação do ambiente

Instale o Python 3.12 e o Git. Execute os comandos a seguir no PowerShell para clonar o repositório, criar o ambiente virtual e instalar as dependências.

```powershell
git clone https://github.com/maia18/evalytics-app.git
cd evalytics-app
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

O arquivo `requirements.txt` inclui dependências específicas do Windows. Este procedimento descreve a execução da aplicação Flet.

### 2. Configuração do Firebase de desenvolvimento

Solicite à equipe a chave de API da aplicação Firebase e o arquivo JSON da conta de serviço com acesso ao Firestore de desenvolvimento. Ambos devem pertencer ao mesmo projeto Firebase. Verifique se a autenticação por e-mail e senha está habilitada nesse projeto.

1. Na raiz do repositório, crie o arquivo `.env` conforme o exemplo a seguir e substitua o valor indicado pela chave de API.

   ```dotenv
   FIREBASE_API_KEY=chave_do_projeto_de_desenvolvimento
   ```

2. Salve o JSON da conta de serviço em `database/services/firebase_credentials.json`. A aplicação lê esse arquivo ao inicializar o cliente Firestore e utiliza o banco de dados com ID `default`.
3. Em uma nova cópia do repositório, crie o módulo local `database/services/firebase_keys.py` conforme o exemplo a seguir.

   ```python
   import os

   from dotenv import load_dotenv

   load_dotenv()
   FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")
   ```

   Se o módulo já existir, verifique se ele carrega o arquivo `.env` e exporta `FIREBASE_API_KEY`.

O Git ignora os três arquivos locais. Mantenha a chave de API no `.env` e o JSON da conta de serviço fora do controle de versão.

### 3. Inicialização e autenticação

Execute o comando a seguir na raiz do projeto.

```powershell
.\venv\Scripts\python.exe main.py
```

Na tela de login, informe o e-mail e a senha de uma conta do projeto Firebase de desenvolvimento. Para criar uma conta, selecione **Cadastre-se**. Após a autenticação, abra a tela de cursos ou de indicadores e verifique se os dados de desenvolvimento são carregados pelo Firestore.

## Diagnóstico da instalação

Execute as verificações na raiz do projeto, no PowerShell.

| Sintoma | Verificação |
| --- | --- |
| `python` não é encontrado ou abre a Microsoft Store | Execute `Get-Command python -All` e `python --version`. Confirme que o comando aponta para uma instalação funcional do Python 3.12. Após instalar ou ajustar o caminho do Python, abra uma nova janela do PowerShell. |
| O executável do ambiente virtual não inicia | Execute `.\venv\Scripts\python.exe --version`. Se a pasta do projeto foi movida ou a instalação original do Python foi removida, renomeie o ambiente virtual antigo e recrie-o na pasta atual seguindo a etapa de preparação. |
| O pip exibe `No matching distribution found` | Confira o nome e a versão do pacote citados na mensagem. Verifique a versão do Python no ambiente virtual, o acesso ao índice de pacotes configurado e se ele disponibiliza a versão indicada no `requirements.txt`. |
| A inicialização exibe `ModuleNotFoundError` | Execute `.\venv\Scripts\python.exe -m pip check` e confirme que a instalação das dependências foi concluída. Se o módulo ausente for `database.services.firebase_keys`, crie o arquivo local conforme a etapa de configuração do Firebase. |
| A aplicação não encontra `firebase_credentials.json` | Execute `Test-Path -LiteralPath .\database\services\firebase_credentials.json -PathType Leaf`. Se o resultado for `False`, salve o arquivo da conta de serviço no caminho indicado na etapa de configuração. |
| O login falha no Firebase Authentication | Verifique se o `.env` está na raiz do projeto e contém `FIREBASE_API_KEY`. Confirme que a chave e a conta de usuário pertencem ao mesmo projeto Firebase e que a autenticação por e-mail e senha está habilitada. |
| O login funciona, mas os dados não são carregados | Consulte a mensagem no terminal. Verifique se a conta de serviço pertence ao projeto de desenvolvimento, se tem acesso ao Firestore e se o banco de dados com ID `default` está disponível. |
