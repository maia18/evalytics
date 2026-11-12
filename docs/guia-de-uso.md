# Guia de uso do Evalytics

Para consultar a estrutura do projeto e os fluxos de armazenamento das avaliações, acesse o [Mapa técnico](mapa-tecnico.md).

Após a autenticação, utilize o menu lateral para acessar o cadastro de cursos e indicadores, o formulário de avaliação e a exportação de resultados. Se o curso e os indicadores já estiverem cadastrados e ativos, acesse **Nova Avaliação**.

Para dificuldades durante esses procedimentos, consulte a seção [Solução de problemas](#solução-de-problemas).

## 1. Cadastro de cursos

1. Abra **Cursos** e selecione **Adicionar curso**.
2. Informe o nome e o departamento. O campo de coordenador é opcional. A aplicação gera o código do curso automaticamente.
3. Mantenha o status **Ativo** para disponibilizar o curso em **Nova Avaliação**. Clique em **Salvar**.

## 2. Configuração de indicadores

1. Em **Configurações**, selecione a aba **Indicadores** e abra a pasta do eixo avaliativo.
2. Clique em **Novo Indicador**, informe o título e, se necessário, a descrição. Clique em **Salvar**.
3. Clique no título do indicador para abrir **Editar Critérios**. Defina o critério correspondente a cada nota e clique em **Salvar**. O formulário de avaliação apresenta os indicadores ativos.

## 3. Preenchimento e envio da avaliação

1. Abra **Nova Avaliação**, selecione o curso e clique em **Abrir avaliação**.
2. Selecione a nota de cada indicador e registre a justificativa no campo correspondente. Para incluir documentos comprobatórios, selecione **Anexar evidências** no indicador.
3. Clique em **Avançar** para acessar o próximo indicador. Para acessar a primeira pergunta de outro eixo, selecione o eixo correspondente.
4. Na última pergunta, clique em **Finalizar** e aguarde a confirmação **Avaliação Enviada!**.

O formulário aceita até 20 arquivos por indicador, com até 10 MB cada. Entre os formatos aceitos estão PDF, PNG, JPG, DOCX, XLSX e CSV.

## 4. Consulta e exportação de resultados

1. Abra **Relatórios**. Na tela **Dados e Exportação**, selecione o semestre, o curso ou o eixo avaliativo em **Filtros** e clique em **Aplicar filtros**.
2. Clique em **Exportar CSV** para gerar um arquivo de dados ou em **Exportar PDF** para gerar o relatório.
3. Na janela de exportação, selecione o curso, o semestre e o eixo desejados. Selecione **Todos** para incluir todos os valores de um campo. Confirme com **Exportar CSV** ou **Gerar PDF**, conforme o formato selecionado.
4. Na janela de salvamento, informe o nome do arquivo e selecione a pasta de destino.

## Solução de problemas

- **Curso indisponível em Nova Avaliação.** Em **Cursos**, verifique se o curso está cadastrado e com status **Ativo**. Em seguida, acesse **Nova Avaliação** novamente.
- **Indicador ausente no formulário.** Em **Configurações**, acesse **Indicadores** e abra a pasta do eixo correspondente. Verifique se o indicador está cadastrado e ativo.
- **Arquivo de evidência recusado.** Verifique se o arquivo pode ser aberto localmente, se o formato é aceito e se o tamanho está dentro do limite de 10 MB. Cada indicador admite até 20 arquivos. Verifique também se o arquivo já consta na lista de anexos.
- **Falha no envio da avaliação.** Se a aplicação apresentar um erro ao clicar em **Finalizar**, verifique a conexão e repita o envio no mesmo formulário. Aguarde a confirmação **Avaliação Enviada!**.
- **Resultados diferentes dos esperados no relatório.** Verifique os filtros de curso, semestre e eixo. Selecione **Limpar** para restaurar a consulta sem filtros. Antes de confirmar a exportação, verifique também os filtros da janela de exportação.
