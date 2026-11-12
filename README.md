# Evalytics

O Evalytics apoia a autoavaliação institucional de cursos superiores. A aplicação permite gerenciar cursos, organizar indicadores por eixo, registrar avaliações e suas evidências e gerar relatórios.

A interface utiliza Python e Flet. A aplicação utiliza o Firebase Authentication para autenticação e o Cloud Firestore para armazenamento de dados. O repositório inclui uma API desenvolvida com FastAPI para avaliações e evidências.

Os procedimentos de avaliação e exportação de resultados estão no [Guia de uso](docs/guia-de-uso.md). A estrutura do projeto e os fluxos de armazenamento estão descritos no [Mapa técnico](docs/mapa-tecnico.md).

## Execução local no Windows

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
