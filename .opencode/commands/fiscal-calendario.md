---
description: "Mostrar calendario de vigencias filtrado por documento fiscal, ordenado por data de producao"
---

# /calendario [doc]

Mostrar calendario de vigencias com situacao calculada para a data de hoje.

## Argumentos
- `[doc]`: documento fiscal (NF-e, CT-e, MDF-e) - opcional, mostra todos se omitido

**Argumentos fornecidos**: $ARGUMENTS

## Fluxo de execucao

### 1. Ler calendario
- Consultar `calendario/calendario.yaml`
- Filtrar por documento se especificado

### 2. Calcular situacao
Para cada item, usar data de hoje:
- `futura` - homologacao nao comecou
- `em_homologacao` - entre inicio e fim
- `prazo_homologacao_encerrado` - homologacao encerrou
- `em_producao` - producao ja comecou

### 3. Ordenar
- Por data de producao crescente
- Destacar em negrito o que vence em ate 30 dias

### 4. Formatar resposta

```
CALENDARIO DE VIGENCIAS - <data de hoje>
Filtro: <documento ou "todos">

| # | Doc | NT/Versao | Itens | Homologacao | Producao | Situacao |
|---|-----|-----------|-------|-------------|----------|----------|
| 1 | NF-e | 2026.007 v1.00 | ... | 01/09/2026 | 03/11/2026 | em_producao |
| 2 | NF-e | 2026.007 v1.10 | ... | Ate 05/10/2026 | 03/11/2026 | em_homologacao |
| 3 | CT-e | 2026.004 v1.00-A | ... | **13/10/2026** | **16/11/2026** | em_homologacao |
| 4 | CT-e | 2026.004 v1.00-B | ... | 16/11/2026 | 14/12/2026 | futura |
| 5 | CT-e | 2026.004 v1.00-C | ... | 01/02/2027 | 01/03/2027 | futura |

LEGENDA:
- Homologacao: azul
- Producao: laranja
- **Negrito**: vence em ate 30 dias
```

### 5. Gerar HTML (opcional)
- Rodar `node scripts/js/gerar_calendario.js` para atualizar HTML
- HTML fica em `calendario/calendario.html`

## Erros tratados

| Erro | Acao |
|---|---|
| `ERRO_DOCUMENTO_INVALIDO` | Avisar que documento deve ser NF-e, CT-e ou MDF-e |