---
description: "Ingerir uma nova Nota Tecnica: move para fontes/, registra no manifest, extrai com marcações de cor, cataloga, atualiza calendario e docs-fiscais"
---

# /ingerir-nt <arquivo>

Ingerir uma nova Nota Tecnica (NT) no repositorio.

## Argumentos
- `<arquivo>`: caminho para o PDF ou DOCX da NT (obrigatorio)
- `--forcar`: sobrescrever se a NT ja foi ingerida (opcional)

**Argumentos fornecidos**: $ARGUMENTS

## Fluxo de execucao

### 1. Validar entrada
- Verificar se o arquivo existe
- Verificar se e PDF ou DOCX
- Calcular SHA256 do arquivo

### 2. Identificar a NT
- Ler cabecalho para extrair: NT, versao, documento fiscal (NF-e/CT-e/MDF-e)
- Se nao conseguir identificar: `ERRO_VERSAO_AMBIGUA`

### 3. Mover para fontes/
- Copiar arquivo para `fontes/<doc>/notas-tecnicas/`
- Nomenclatura: `<DOC>_NT_<numero>_v<versao>.pdf`

### 4. Registrar no manifest
- Adicionar entrada em `manifest.yaml`
- Campos: id, documento, tipo, nt, versao, titulo, arquivo, sha256, status_ingestao, confianca

### 5. Extrair com marcações
- Rodar `python scripts/python/extrair_nt.py <arquivo>`
- Saida: `catalogo/nt/<doc>/<nt>_v<versao>.json` + `.md`
- Erros possiveis:
  - `ERRO_COR_NAO_MAPEADA` - cor sem legenda -> listar cores encontradas
  - `ERRO_PDF_ESCANEADO` - pagina sem texto -> marcar para OCR
  - `ERRO_TABELA_QUEBRADA` - colunas inconsistentes

### 6. Atualizar legenda
- Gerar/atualizar `catalogo/legendas/<doc>.yaml`
- Cruzar marcações com secao "Descricao das alteracoes"

### 7. Atualizar calendario
- Extrair datas do cronograma (pagina 3)
- Extrair datas de observacoes dentro das regras
- Atualizar `calendario/calendario.yaml`
- Regenerar `calendario/CALENDARIO.md` e `calendario.html`

### 8. Regenerar docs-fiscais
- Rodar `node scripts/js/atualizar_docs_fiscais.js`
- Atualizar blocos AUTO de `docs-fiscais/<DOC>.md`

### 9. Registrar duvidas
- Listar inconsistencias encontradas em `docs/duvidas-abertas.md`

### 10. Resumo
Exibir:
- NT ingerida (numero, versao, documento)
- Quantidade de itens extraidos
- Cores encontradas e mapeadas
- Duvidas registradas
- Proximo passo sugerido

## Erros tratados

| Erro | Acao |
|---|---|
| `ERRO_COR_NAO_MAPEADA` | Listar cores encontradas com contagem, pedir revisao |
| `ERRO_VERSAO_AMBIGUA` | Pedir informacao manual da NT/versao |
| `ERRO_PDF_ESCANEADO` | Marcar para OCR/revisao manual |
| `ERRO_TABELA_QUEBRADA` | Listar paginas com problema |