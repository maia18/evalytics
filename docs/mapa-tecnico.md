# Mapa técnico do Evalytics

## Onde fica cada parte

| Área | Responsabilidade | Ponto de entrada |
| --- | --- | --- |
| Inicialização | Abre a interface Flet, registra o seletor de arquivos, configura o tema e restaura a sessão. | [main.py](../main.py) |
| Navegação e sessão | Mapeia rotas para telas e guarda o estado da sessão do Firebase Authentication. | [Roteador](../components/core/router/router.py) e [estado de autenticação](../components/core/auth/auth_state.py) |
| Telas | Os módulos em `models/` organizam a interface por funcionalidade. Componentes compartilhados ficam em `components/`. | [Cursos](../models/cursos/cursos.py), [configurações](../models/configuracoes/configuracoes.py), [formulário](../models/formulario/formulario.py) e [relatórios](../models/relatorios/relatorios.py) |
| Serviços da aplicação | Contêm operações sobre avaliações e indicadores e consolidam dados para relatórios. | [Avaliações](../utils/services/avaliacoes/avaliacoes_service.py), [indicadores](../utils/services/indicadores/indicadores_repository.py) e [relatórios](../utils/services/relatorio/relatorio_service.py) |
| Acesso a dados | Configura o cliente Firestore do aplicativo e concentra consultas de cursos e do catálogo institucional. Alguns serviços em `utils/services/` também usam o cliente diretamente. | [Cliente Firestore](../database/services/firebase_config.py), [cursos](../database/services/cursos/firestore_courses.py) e [instituições](../database/services/institutions/institutions_service.py) |
| API HTTP | Expõe rotas FastAPI para avaliações e evidências, com configuração própria do Firebase. | [Aplicação ASGI](../app/api/__init__.py) e [configuração da API](../app/api/config.py) |

## Como o formulário salva uma avaliação

1. A rota `/formulario` abre **Nova Avaliação**. A tela carrega os cursos e indicadores. O seletor apresenta os cursos ativos e o controlador organiza os indicadores ativos por eixo e título. [Tela do formulário](../models/formulario/formulario.py) · [Controlador](../models/formulario/core/form_controller.py)
2. O cartão de cada pergunta usa o ID do indicador para associar a nota, a justificativa e os anexos. Ao clicar em **Finalizar**, o formulário reúne esses dados e chama `salvar_avaliacao`. [Cartão da pergunta](../models/formulario/widgets/card_pergunta.py) · [Envio do formulário](../models/formulario/core/steps.py)
3. O serviço valida os arquivos locais, envia as evidências ao servidor DreamHost e agrupa as URLs retornadas por indicador. Em seguida, cria um documento em `avaliacoes` no Firestore e invalida os caches de consultas. Se ocorrer uma falha, o formulário apresenta uma mensagem e mantém a avaliação aberta para nova tentativa. [Serviço de avaliações](../utils/services/avaliacoes/avaliacoes_service.py) · [Envio do formulário](../models/formulario/core/steps.py)

Exemplo simplificado de um documento gravado pelo aplicativo:

```yaml
curso_id: curso-exemplo
curso_nome: Pedagogia
instituicao_id: instituicao-exemplo
data_avaliacao: <timestamp do Firestore>
respostas:
  indicador-exemplo: 4
justificativas:
  indicador-exemplo: "Os planos de ensino foram revisados no semestre."
evidencias: {}
perguntas:
  - id: indicador-exemplo
    titulo: Planos de ensino
    descricao: Revisão dos planos de ensino do curso.
    eixo: 1
    criterios:
      "4": "Planos revisados e disponíveis para consulta."
```

O campo `perguntas` preserva os títulos, descrições, eixos e critérios usados na avaliação quando o catálogo de indicadores muda. Para uma avaliação com anexos, `evidencias` contém, por indicador, uma lista de objetos com `nome` e `url`. O cadastro de cursos e a leitura de avaliações usam o contexto institucional da sessão. [Serviço de avaliações](../utils/services/avaliacoes/avaliacoes_service.py) · [Instituições e campi](../database/services/institutions/README.md)

## Como a API grava avaliações e evidências

A API também grava na coleção `avaliacoes`. O `POST /avaliacoes` recebe os dados da avaliação, o manifesto de evidências e os arquivos em um formulário multipart. A API valida o token do Firebase, grava o UID em `usuario_id` e armazena os arquivos em Cloud Storage. Nesse fluxo, `evidencias` é uma lista de metadados que inclui `indicador_id` e `caminho_storage`. Em caso de falha durante o envio, a API tenta remover o documento e os arquivos da operação incompleta. [Rota de criação](../app/api/routes/evaluations.py) · [Autenticação](../app/api/auth.py) · [Limpeza](../app/api/dependencies.py)

O formato de `evidencias` depende da origem do registro. O formulário Flet grava um mapa de URLs por indicador e a API grava uma lista de metadados do Cloud Storage.
