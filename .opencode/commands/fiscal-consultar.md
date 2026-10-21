---
description: Consultar informação fiscal (NF-e, CT-e, MDF-e) com resposta mastigada, vigência e fontes citadas
argument-hint: <pergunta em linguagem natural>
---

# /fiscal-consultar

Responda a pergunta abaixo seguindo as regras do AGENTS.md (CLAUDE.md).

**Pergunta**: $ARGUMENTS

## Fluxo

1. **Documento**: NF-e/NFC-e, CT-e (inclui CT-e OS, GTV-e, Simplificado) ou MDF-e. Se a pergunta
   cruzar documentos, responda por documento. Se não der para saber, pergunte.
2. **Data de hoje**: rode `date` (Bash) ou `Get-Date`. Informe-a na resposta.
3. **Leia** `docs-fiscais/<DOC>.md` e `docs-fiscais/_COMUM.md`. **Se não existirem** (hoje não
   existem), avise em uma linha e siga com o catálogo.
4. **Busque** (Grep antes de Read; os JSON são grandes):
   - `catalogo/regras/<doc>.json`, `catalogo/campos/<doc>.json` (se existirem)
   - `catalogo/nt/<doc>/*.json` — NTs extraídas
   - `catalogo/moc/<doc>/*.json` — MOCs extraídos (`regras_validacao`, `campos_leiaute`)
   - `calendario/calendario.yaml` (se existir) ou `cronograma[]` do JSON da NT
   - `catalogo/legendas/<doc>.yaml` para interpretar marcações
5. **Vigência** de cada regra/campo: `futura | em_homologacao | em_producao | excluida`, com datas.
   Regra marcada EXCLUÍDO nunca é explicada como vigente.
6. **Fontes externas** só se o acervo não responder (skill `pesquisar-fontes-externas`) e sempre com o selo "não oficial".
7. **Contradição** entre fontes: mostre as duas, prevalece a oficial, registre em
   `docs/duvidas-abertas.md` (`/fiscal-duvidas --registrar`).
8. **Não achou**: responda `NAO ENCONTRADO NAS FONTES` e sugira `/fiscal-atualizar-fontes` ou
   ingestão. Nunca responda de memória.

## Formato (obrigatório)

```
[RESUMO - 2-3 linhas]
[DETALHE]
- Campo/regra / cStat / Quem aplica / NT de origem (NT vX, pág. N) / Marcação / Situação (+ data de hoje)
[IMPACTO NO EMISSOR]
[FONTES]
- <documento> - <NT/MOC/XSD> v<versão> - pág. <N> - <marcação>
```

Resposta sem "Fontes" é inválida (`ERRO_SEM_CITACAO`).
