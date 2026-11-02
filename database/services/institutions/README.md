# Instituições e campi

Os documentos de cursos e avaliações recebem `instituicao_id`. O tenant da
sessão vem do claim confiável do Firebase ou do campo
`usuarios/{uid}.instituicao_id`. `EVALYTICS_INSTITUICAO_ID` é o fallback para
instalações sem vínculo individual e, neste projeto, está configurado como
`ufc` por padrão.

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

O seletor de localidade lê os campi ativos deste catálogo; ele não contém uma
lista fixa de instituições no código. Para vincular outra instituição, cadastre
seu documento e campi e atribua seu ID ao perfil dos usuários autorizados.

## Dados existentes

`seed_ufc.py` prepara o cadastro da UFC e seus oito campi. É uma operação
explícita e não é executada ao abrir o app:

```powershell
.\venv\Scripts\python.exe -m database.services.institutions.seed_ufc
```

Antes de etiquetar dados antigos, faça a prévia:

```powershell
.\venv\Scripts\python.exe -m database.services.institutions.migrar_dados_legados
```

Revise se todos os cursos e avaliações listados são da instituição padrão. Só
então execute a migração com `--aplicar`. Ela não remove nem copia documentos;
apenas adiciona `instituicao_id` aos que não têm esse campo.

Durante a transição, documentos antigos sem instituição continuam visíveis
apenas no tenant padrão. Para outros tenants, novos registros já são gravados
com `instituicao_id`.
