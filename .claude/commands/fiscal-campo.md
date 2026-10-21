---
description: Mostrar dados de um campo do leiaute (tipo, ocorrência, tamanho, regras ligadas, NT de origem)
argument-hint: <tag ou caminho/da/tag> [NF-e|CT-e|MDF-e]
---

# /fiscal-campo

**Argumentos**: $ARGUMENTS (tag, ex. `vTPrestLiq`, ou caminho, ex. `infCte/vPrest/vTPrestLiq`; documento opcional)

## Fluxo

1. Rode `date`.
2. Siga a skill **ler-catalogo-xsd** (catálogo se existir; senão Grep nos XSDs de `fontes/<doc>/xsd/`
   e nos `campos_leiaute` de `catalogo/moc/<doc>/*.json`).
3. **Tag ambígua** (mesmo nome em vários caminhos): liste todos os caminhos e detalhe cada um.
4. **Regras relacionadas**: `catalogo/regras/<doc>.json` (se existir) ou Grep da tag nas regras dos
   MOCs/NTs extraídos.
5. **Origem**: NT que criou/alterou (NT vX, pág.), arquivo XSD e pacote, classificação
   NOVO/ALTERADO/EXCLUIDO/INALTERADO, vigência (com data de hoje).

## Formato

```
[RESUMO]  Campo <tag> - <tipo> - <ocorrência> - <classificação>
[DADOS DO XSD] Caminho / Tipo / minOccurs / maxOccurs / Tamanho / Pattern / Enumeration / Documentação
[ORIGEM] NT vX / Arquivo XSD (pacote vN) / Classificação / Situação
[REGRAS RELACIONADAS] <ID> (cStat) - resumo - status
[IMPACTO NO EMISSOR]
[FONTES] <documento> - <NT/MOC/XSD> v<versão> - <arquivo ou pág.>
```

## Erros
- `ERRO_CAMPO_NAO_ENCONTRADO` → `NAO ENCONTRADO NAS FONTES`; sugerir verificar o nome ou ingerir o XSD
- `ERRO_PARAMETRO_INVALIDO`
