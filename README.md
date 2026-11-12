# Evalytics

O Evalytics apoia a autoavaliação institucional de cursos superiores. A aplicação permite gerenciar cursos, organizar indicadores por eixo, registrar avaliações e suas evidências e gerar relatórios.

A interface é feita em Python com Flet. O aplicativo usa Firebase Authentication para o login e Cloud Firestore para armazenar os dados. O repositório também inclui uma API FastAPI para avaliações e evidências.

Para preencher uma avaliação e exportar os resultados, consulte o [guia de uso](docs/guia-de-uso.md). Para localizar os componentes e entender como os dados são gravados, veja o [mapa técnico](docs/mapa-tecnico.md).

## Execução local no Windows

### 1. Preparar o ambiente

Instale o Python 3.12 e o Git. No PowerShell, clone o repositório e instale as dependências declaradas no projeto:

```powershell
git clone https://github.com/maia18/evalytics-app.git
cd evalytics-app
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

O arquivo `requirements.txt` inclui dependências específicas do Windows. Os passos abaixo cobrem a execução do aplicativo Flet.

### 2. Configurar o Firebase de desenvolvimento

Solicite à equipe a chave de API do aplicativo Firebase e o JSON da conta de serviço autorizada a acessar o Firestore de desenvolvimento. Use valores do mesmo projeto e confirme que o login por e-mail e senha está habilitado no Firebase Authentication.

1. Na raiz do repositório, crie um arquivo `.env` e substitua o valor de exemplo pela chave de API:

   ```dotenv
   FIREBASE_API_KEY=chave_do_projeto_de_desenvolvimento
   ```

2. Salve o JSON da conta de serviço em `database/services/firebase_credentials.json`. O aplicativo procura esse arquivo ao inicializar o cliente Firestore e usa o banco com ID `default`.
3. Em um clone novo, crie o arquivo local `database/services/firebase_keys.py` com este conteúdo:

   ```python
   import os

   from dotenv import load_dotenv

   load_dotenv()
   FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")
   ```

   Se você já tem esse módulo local, basta conferir se ele carrega o `.env` e exporta `FIREBASE_API_KEY`.

O Git ignora os três arquivos locais. Mantenha a chave de API no `.env` e o JSON da conta de serviço fora do controle de versão.

### 3. Abrir o aplicativo e entrar

Na raiz do projeto, execute:

```powershell
.\venv\Scripts\python.exe main.py
```

Na tela de login, entre com o e-mail e a senha de uma conta do projeto Firebase de desenvolvimento. Se precisar criar uma conta, use **Cadastre-se**. Para conferir a conexão com o Firestore após o login, abra a tela de cursos ou indicadores e verifique se os dados de desenvolvimento são carregados.
