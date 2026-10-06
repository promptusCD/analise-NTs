---
description: "Listar e priorizar duvidas abertas do projeto"
---

# /duvidas

Listar e priorizar as duvidas abertas do projeto.

## Argumentos
- `[doc]`: documento fiscal (NF-e, CT-e, MDF-e) - opcional, mostra todos se omitido
- `--prioridade <alta|media|baixa>`: filtrar por prioridade - opcional

**Argumentos fornecidos**: $ARGUMENTS

## Fluxo de execucao

### 1. Ler duvidas
- Consultar `docs/duvidas-abertas.md`
- Filtrar por documento e prioridade se especificado

### 2. Classificar prioridade

| Prioridade | Criterio |
|---|---|
| ALTA | Impede implementacao ou gera erro em producao |
| MEDIA | Afeta qualidade mas tem workaround |
| BAIA | Inconveniente, nao bloqueia |

### 3. Formatar resposta

```
DUVIDAS ABERTAS - <data>
Filtro: <documento ou "todas">
Total: <N> (ALTA: X, MEDIA: Y, BAIA: Z)

========================================
PRIORIDADE ALTA
========================================

[#001] <titulo>
- Documento: <doc>
- NT/MOC: <referencia>
- Pagina: <N>
- Trecho: <trecho problematico>
- O que parece errado: <descricao>
- Impacto: <por que e alta prioridade>
- Status: pendente

========================================
PRIORIDADE MEDIA
========================================

[#002] <titulo>
...

========================================
PRIORIDADE BAIA
========================================

[#003] <titulo>
...

========================================
RESUMO
========================================
- Duvidas que impedem implementacao: <N>
- Duvidas com workaround: <N>
- Duvidas academicas: <N>
```

### 4. Sugestoes
Para cada duvida ALTA, sugerir:
- Como resolver (buscar em outra fonte, testar em homologacao, etc.)
- Quem pode responder (SEFAZ, fornecedor, forum)