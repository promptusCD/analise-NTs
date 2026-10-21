---
name: consultar-moc
description: Como achar regras e leiaute no MOC (Manual de Orientação do Contribuinte) vigente, qual versão vale em cada data e como conciliar MOC x NT. Use para perguntas sobre regras de validação, cStat ou campos de NF-e, CT-e e MDF-e.
allowed-tools: Read, Grep, Glob, Bash(node:*), Bash(date:*)
---

# Skill: Consultar MOC

## Quando usar
- Saber qual MOC é o vigente de um documento
- Encontrar regra de validação / campo de leiaute no MOC
- Conciliar MOC com NTs mais novas

## Fontes locais (nesta ordem)

1. `catalogo/moc/<doc>/<arquivo>.json` — MOC extraído. Chaves úteis:
   `secoes[]` (hierárquicas), `regras_validacao[]`, `campos_leiaute[]`.
   Use Grep por ID/cStat/tag nesses JSONs antes de abrir qualquer PDF.
2. `manifest.yaml` — descobre **a versão vigente de cada MOC** (não assuma números de
   cabeça: hoje NF-e v7.00, CT-e v4.00, MDF-e v3.00b, mas confirme no manifest).
3. `docs-fiscais/<DOC>.md` seção "Fontes vigentes" (quando existir).
4. PDF/DOCX em `fontes/<doc>/moc/` — só para conferir citação.

## Estrutura dos MOCs
- NF-e (inclui NFC-e): Visão Geral + Anexo I Leiaute + Anexo II DANFE + Anexo III Contingência
- CT-e: Visão Geral + Anexo I Leiaute + Anexo II DACTE
- MDF-e: Visão Geral + Anexo I Leiaute + Anexo II DAMDFE
- `fontes/externas/MOC_NFe_ABI_*_minuta.pdf` é **minuta** (não oficial/vigente) — rotular como tal.

## Conciliar MOC x NT
- O MOC é a versão consolidada **até a data dele**; NTs posteriores alteram regras sem
  atualizar o MOC.
- Para saber se uma NT mexeu na regra: buscar o ID da regra em `catalogo/nt/<doc>/*.json`
  (e em `catalogo/regras/<doc>.json` quando existir).
- Status: criada pelo MOC (ativa) → alterada por NT (citar NT/versão) → excluída por NT
  (citar NT/versão). Cor nunca prova sozinha (regra 6).
- Se MOC e NT divergirem: mostrar as duas, prevalece a mais recente **oficial** vigente na
  data de hoje, registrar em `docs/duvidas-abertas.md`.

## MOC online (conferência)
- NF-e/NFC-e: http://moc.sped.fazenda.pr.gov.br/NFe_NFCe/VisaoGeral.html
- CT-e: http://moc.sped.fazenda.pr.gov.br/CTe/index.html
- A versão online pode estar à frente da local → rotule a diferença e sugira `/fiscal-atualizar-fontes`.

## Resposta
Siga o formato padrão do AGENTS.md, sempre com **Fontes** (MOC, anexo, versão, página/seção) e vigência.
Se não achar: "NAO ENCONTRADO NAS FONTES".

## Referências
- `docs/REFERENCIA.md` seção 7 (template dos docs-fiscais)
- `docs/ARQUIVOS_NECESSARIOS.md` (o que falta baixar)
