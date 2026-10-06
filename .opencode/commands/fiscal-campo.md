---
description: "Mostrar dados de um campo do leiaute: tipo, ocorrencia, tamanho, regras ligadas, NT de origem"
---

# /campo <tag> [doc]

Mostrar dados completos de um campo do leiaute (tag XML).

## Argumentos
- `<tag>`: nome da tag (ex: vTPrestLiq) ou caminho (ex: infCte/vPrest/vTPrestLiq) (obrigatorio)
- `[doc]`: documento fiscal (NF-e, CT-e, MDF-e) - opcional, tenta detectar automaticamente

**Argumentos fornecidos**: $ARGUMENTS

## Fluxo de execucao

### 1. Buscar o campo
- Consultar `catalogo/campos/<doc>.json`
- Buscar por nome da tag ou caminho completo

### 2. Buscar regras relacionadas
- Consultar `catalogo/regras/<doc>.json`
- Filtrar por campo/tag relacionada

### 3. Formatar resposta

```
[RESUMO]
Campo <tag> - <tipo> - <ocorrencia> - <classificacao>

[DADOS DO XSD]
- Caminho: <caminho_completo>
- Tipo: <tipo XSD>
- minOccurs: <N>
- maxOccurs: <N>
- Tamanho: <N,N>
- Pattern: <regex> (se houver)
- Enumeration: <valores> (se houver)
- Documentacao: <texto>

[ORIGEM]
- NT: <NT> v<versao>
- Arquivo XSD: <arquivo>
- Classificacao: <NOVO/ALTERADO/EXCLUIDO/INALTERADO>

[REGRAS RELACIONADAS]
- <ID> (cStat <codigo>) - <resumo> - <status>

[FONTES]
- <documento> - <NT/MOC/XSD> v<versao> - <arquivo_xsd>
```

## Erros tratados

| Erro | Acao |
|---|---|
| `ERRO_CAMPO_NAO_ENCONTRADO` | Sugerir verificar nome ou ingerir XSD |
| `ERRO_PARAMETRO_INVALIDO` | Avisar formato incorreto do argumento |