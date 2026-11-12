# Verificação após atualizações

Execute este roteiro no ambiente de desenvolvimento após alterações que afetem a autenticação, o formulário, o armazenamento ou a exportação de resultados. Consulte o [README](../README.md) para configurar e iniciar a aplicação e o [Mapa técnico](mapa-tecnico.md) para identificar os componentes envolvidos.

## Preparação

- Utilize uma conta Firebase de desenvolvimento com acesso à instituição de teste.
- Identifique um curso ativo e um indicador ativo com critérios cadastrados. Utilize dados fictícios e um PDF de teste sem informações pessoais. O envio do formulário grava a avaliação no Firestore de desenvolvimento e envia o anexo ao serviço de armazenamento utilizado pela aplicação.
- Registre a revisão testada, a data e a instituição. Identifique a avaliação de teste pela combinação de curso, horário de envio e texto da justificativa.

## Roteiro de verificação

| Etapa | Procedimento | Resultado esperado |
| --- | --- | --- |
| Autenticação | Inicie a aplicação e entre com a conta de desenvolvimento. Se houver uma sessão restaurada, encerre-a antes de verificar o login. | A aplicação exibe a tela inicial e permite acessar **Cursos** e **Nova Avaliação**. |
| Formulário e evidência | Abra **Nova Avaliação**, selecione o curso, atribua uma nota ao indicador, registre a justificativa de teste e anexe o PDF. | O formulário apresenta o indicador e exibe o nome do PDF na lista de anexos correspondente. |
| Envio | Avance até a última pergunta e selecione **Finalizar**. | A aplicação exibe **Avaliação Enviada!**. |
| Consulta | Abra **Relatórios** e aplique os filtros de curso e semestre da avaliação. | A tabela apresenta a avaliação enviada e os resultados dos eixos respondidos. |
| Exportação | Exporte em PDF e CSV, selecionando o curso e o semestre na janela de cada exportação. Abra os arquivos gerados e localize a avaliação de teste. | Ambos os arquivos apresentam o indicador, a nota, a justificativa e a referência da evidência. O PDF também apresenta o resumo de resultados. |

Registre o resultado de cada etapa como **Aprovada**, **Reprovada** ou **Bloqueada**. Em caso de falha, registre a mensagem exibida, a etapa afetada e o resultado observado. Consulte o [Guia de uso](guia-de-uso.md#solução-de-problemas) para as verificações iniciais.
