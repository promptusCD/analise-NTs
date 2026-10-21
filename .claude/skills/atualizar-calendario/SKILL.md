---
name: atualizar-calendario
description: Como extrair datas de vigência das NTs, atualizar calendario/calendario.yaml e gerar MD/HTML. Granularidade por item, nunca inventar data, situação calculada pela data de hoje. Use ao ingerir NT ou consultar vigência.
allowed-tools: Read, Edit, Grep, Bash(node:*), Bash(date:*)
---

# Skill: Atualizar Calendário

## Quando usar
- Ingerir NT nova (extrair datas do cronograma)
- Saber a situação atual de um item
- Gerar calendário em MD/HTML

## Fonte única
`calendario/calendario.yaml` é a FONTE ÚNICA; `CALENDARIO.md` e `calendario.html` são gerados
(e ignorados pelo git). **Nunca edite o .md/.html** — edite o .yaml e rode o gerador.

> Estado atual: `calendario.yaml` e `scripts/js/gerar_calendario.js` **ainda não existem**.
> Se faltarem, não invente: crie o yaml só com datas lidas das NTs (formato abaixo), avise
> que o gerador não existe e **não** escreva MD/HTML à mão.

## Granularidade por item
Uma NT tem vários itens com datas DIFERENTES. Exemplo (CT-e NT 2026.004 v1.00, conferir no JSON):
- Bloco A: homologação 13/10/2026, produção 16/11/2026 (campos de valor líquido, etc.)
- Bloco B: homologação 16/11/2026, produção 14/12/2026 (CT-e Simplificado)
- Bloco C: homologação 01/02/2027, produção 01/03/2027 (ICMS previsto, regras 1051-1053)

## De onde extrair datas
1. **Tabela de cronograma** da NT (geralmente pág. 3): versão, homologação, produção.
2. **Observações nas regras**: "Implantação: homologação …, produção …" (não estão no cronograma).
3. **Exceções**: "Até 05/10/2026" → guardar em `texto_original`, nunca reinterpretar.
   Para calcular situação, trate "Até DD/MM/AAAA" como data-limite, mas mostre o literal.
4. Leia do JSON em `catalogo/nt/<doc>/*.json` (`cronograma[]`), não do PDF.

## Regras
1. **Nunca inventar data**: `homologacao: PENDENTE` quando a NT não informa.
2. Nova versão da mesma NT → atualiza a linha e move a anterior para `historico_versoes`.
3. **Situação pela data de hoje** (rode `date`; não assuma):
   - `futura` — homologação não começou
   - `em_homologacao` — entre início da homologação e início da produção
   - `prazo_homologacao_encerrado` — janela de homologação fechou (data-limite passou) e produção ainda não começou
   - `em_producao` — produção já começou
   - `excluida` — item revogado por NT posterior
   - `indefinida` — datas PENDENTE (não calcular)
4. Datas em ISO no yaml (`2026-10-13`) + `texto_original` quando houver texto literal.

## Gerar saída
```bash
node scripts/js/gerar_calendario.js
```
Gera `calendario/CALENDARIO.md` e `calendario/calendario.html`.

## Erros
- `ERRO_DATA_NAO_ENCONTRADA` → `PENDENTE`, não inventar
- `ERRO_DATAS_CONFLITANTES` → mostrar as duas, marcar revisão, registrar em `docs/duvidas-abertas.md`

## Referência
`docs/REFERENCIA.md` seção 6.
