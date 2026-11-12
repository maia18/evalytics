# Instituições e campi

Os documentos de cursos e avaliações contêm o campo `instituicao_id`. A
aplicação identifica a instituição da sessão pelo atributo confiável
(`claim`) do Firebase ou pelo campo `usuarios/{uid}.instituicao_id`. Na
ausência de vínculo individual, a aplicação utiliza o valor de
`EVALYTICS_INSTITUICAO_ID`, cujo padrão é `ufc`.

## Cadastro no Firestore

```text
instituicoes/{instituicao_id}
  nome: "Nome oficial da instituição"
  sigla: "SIGLA"
  ativa: true

instituicoes/{instituicao_id}/campi/{campus_id}
  nome: "Nome do campus"
  municipio: "Município"
  uf: "UF"
  ativo: true

usuarios/{uid}
  instituicao_id: "instituicao_id"
```

O seletor de localidade consulta os campi ativos deste catálogo. Para vincular
outra instituição, cadastre o documento da instituição e os respectivos
campi. Em seguida, atribua o identificador da instituição ao perfil dos
usuários autorizados.

## Cadastro inicial e migração de dados existentes

Para cadastrar a UFC e seus oito campi, execute o comando a seguir. A
inicialização da aplicação não executa esse procedimento.

```powershell
.\venv\Scripts\python.exe -m database.services.institutions.seed_ufc
```

Para identificar os documentos que seriam alterados pela migração, execute
o comando a seguir.

```powershell
.\venv\Scripts\python.exe -m database.services.institutions.migrar_dados_legados
```

Verifique se todos os cursos e avaliações listados pertencem à instituição
padrão antes de executar a migração com `--aplicar`. A migração adiciona
`instituicao_id` aos documentos que ainda não contêm esse campo.

Durante a migração, a consulta da instituição padrão inclui os documentos
legados sem vínculo institucional. As demais instituições consultam os
documentos associados ao respectivo `instituicao_id`. Novos registros são
gravados com esse campo.
