---
name: ler-catalogo-xsd
description: Como navegar o catálogo de campos/XSD (ocorrência, tipo, pattern, enumeração) e cruzar tags citadas em NTs com o schema. Use para saber se uma tag existe, seu tipo ou tamanho.
allowed-tools: Read, Grep, Glob, Bash(node:*), Bash(python:*)
---

# Skill: Ler Catálogo XSD

## Quando usar
- Saber se uma tag XML existe no schema vigente
- Tipo, ocorrência, tamanho, pattern ou enumeração de um campo
- Cruzar campo citado em NT com o XSD

## Estado atual (verifique antes!)
`catalogo/campos/<doc>.json` e `scripts/js/consultar.js` **ainda não existem** (planejados
nas próximas fases) e **não há extrator de XSD** em `scripts/python/`. Faça:

1. Se `catalogo/campos/<doc>.json` existir → use-o (formato abaixo).
2. Senão, **fallback**: Grep direto nos XSDs em `fontes/<doc>/xsd/<pacote>/*.xsd`
   (`<xs:element name="<tag>"`), lendo `minOccurs`, `maxOccurs`, `type` e o `xs:simpleType`
   referenciado. Avise ao usuário que o dado vem do XSD bruto, sem catálogo.
3. Se também não houver XSD do pacote em `fontes/` (veja `docs/ARQUIVOS_NECESSARIOS.md`):
   "NAO ENCONTRADO NAS FONTES" + sugerir `/fiscal-atualizar-fontes`.

## Formato do catálogo (quando existir)

```json
{
  "caminho_completo": "infCte/vPrest/vTPrestLiq",
  "tipo": "TDec_1302",
  "minOccurs": "0", "maxOccurs": "1",
  "tamanho": "13,2", "pattern": null, "enumeration": null,
  "documentacao": "...", "arquivo_xsd": "cte_v4.00.xsd",
  "nt_origem": "2026.004", "classificacao": "NOVO"
}
```

Classificação: NOVO | ALTERADO | EXCLUIDO | INALTERADO.

## Cuidados
- **Tag ambígua**: o mesmo nome (`vBC`, `CST`, `cProd`…) aparece em vários caminhos.
  Liste TODOS os caminhos e peça/infira o contexto; nunca escolha um em silêncio.
- **Versão do pacote**: informe qual pacote/versão do XSD foi lido (ex.: `PL_CTe_400_NT2026.004_RTC_v1.00`).
- **Cruzamento NT x XSD**: campo na NT mas ausente no XSD → registrar em
  `docs/duvidas-abertas.md` ("NT cita campo ausente no pacote XSD vN"). XSD
  **não** valida regras de negócio: para isso use `catalogo/regras` / MOC.
- Campo ≠ regra: `campos` = tags do XML; `regras` = validações (cStat, efeito). Um campo pode ter várias regras.

## Referência
`docs/REFERENCIA.md` seção 5.3 e seção 11 (XSDs disponíveis × necessários).
