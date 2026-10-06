---
description: "Buscar novidades nos portais oficiais e comparar com manifest.yaml. Propor o que e novo para ingestao."
---

# /atualizar-fontes

Buscar novidades nos portais oficiais de NF-e, CT-e e MDF-e e comparar
com o que ja temos no manifest.

## Argumentos
- `[doc]`: documento fiscal (NF-e, CT-e, MDF-e) - opcional, busca todos se omitido
- `--forcar`: ignorar cache e buscar novamente (opcional)

**Argumentos fornecidos**: $ARGUMENTS

## Fluxo de execucao

### 1. Consultar portais
Rodar `node scripts/js/detectar_novidades.js` que:
- Acessa paginas de Documentos dos portais oficiais
- Extrai lista de NTs, MOCs e XSDs publicados
- Compara com `manifest.yaml`

### 2. Identificar novidades
Para cada documento encontrado no portal:
- Se nao esta no manifest = NOVO
- Se hash diverge = ALTERADO
- Se esta no manifest mas nao no portal = verificar

### 3. Gerar relatorio

```
RELATORIO DE NOVIDADES - <data>

PORTAL NF-e (SVRS)
- NOVO: NT 2025.002 v1.52 (RTC)
  URL: https://dfe-portal.svrs.rs.gov.br/NFe/...
  Acao: baixar e ingerir

- NOVO: Pacote XSD 010b v1.30
  URL: https://dfe-portal.svrs.rs.gov.br/NFe/...
  Acao: baixar e catalogar

PORTAL CT-e (SVRS)
- ATUALIZADO: Schemas NT 2026.004 (hash mudou)
  Acao: verificar e re-ingestao se necessario

PORTAL MDF-e (SVRS)
- NENHUMA NOVIDADE

RESUMO:
- Novos: 2
- Atualizados: 1
- Sem mudanca: 1
```

### 4. NAO ingerir automaticamente
- Apenas PROPOE o que e novo
- Aprovacao humana antes de ingerir
- Se aprovado, usar `/ingerir-nt`

## Erros tratados

| Erro | Acao |
|---|---|
| `ERRO_PORTAL_INDISPONIVEL` | Tentar 3x, se falhar registrar e alertar |
| `ERRO_HASH_DIVERGENTE` | Alertar que arquivo mudou sem mudar versao |