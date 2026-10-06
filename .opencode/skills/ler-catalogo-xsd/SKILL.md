---
name: ler-catalogo-xsd
description: Como navegar o catalogo de XSDs. Ocorrencias, patterns, enumeracoes. Como cruzar tag de NT com XSD para verificar se campo existe no schema.
allowed-tools: Bash(node:*), Read
---

# Skill: Ler Catalogo XSD

## Quando usar
- Quando precisar saber se uma tag XML existe no schema vigente
- Quando precisar saber tipo, ocorrencia, tamanho de um campo
- Quando precisar cruzar NT (campo citado) com XSD (campo existe)

## Estrutura do catalogo

`catalogo/campos/<doc>.json` contem todos os campos extraidos dos XSDs:

```json
{
  "caminho_completo": "infCte/vPrest/vTPrestLiq",
  "tipo": "TDec_1302",
  "minOccurs": "0",
  "maxOccurs": "1",
  "tamanho": "13,2",
  "pattern": null,
  "enumeration": null,
  "documentacao": "Valor liquido da prestacao",
  "arquivo_xsd": "cte_v4.00.xsd",
  "nt_origem": "2026.004",
  "classificacao": "NOVO"
}
```

## Como consultar

### 1. Por nome da tag
```bash
node scripts/js/consultar.js campo vTPrestLiq CT-e
```

### 2. Por caminho completo
```bash
node scripts/js/consultar.js campo "infCte/vPrest/vTPrestLiq" CT-e
```

### 3. Cruzamento NT x XSD
Quando uma NT menciona um campo novo, verifique se ele existe no XSD:
- Se existe no XSD = campo implementado no schema
- Se nao existe = registrar em duvidas-abertas.md ("NT cita campo ausente no pacote XSD vN")

## Classificacao de campos

| Classificacao | Significado |
|---|---|
| NOVO | Campo adicionado por NT |
| ALTERADO | Campo existente com mudanca de tipo/ocorrencia |
| EXCLUIDO | Campo removido por NT |
| INALTERADO | Campo do MOC original, sem NT que altere |

## Diferenca entre catalogo/campos e catalogo/regras

- `catalogo/campos/<doc>.json` = TAGS do XML (estrutura do documento)
- `catalogo/regras/<doc>.json` = REGRAS de validacao (cStat, efeito)

Um campo pode ter multiplas regras associadas.

## Referencia
Leia `docs/REFERENCIA.md` secao 5.3 para a estrutura do catalogo de campos.