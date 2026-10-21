---
name: interpretar-nota-tecnica
description: Como ler e interpretar uma Nota Técnica fiscal (NF-e, CT-e, MDF-e). Seções, cronograma, legenda de cores, cruzamento cor x "Descrição das alterações" e categorias revisão/estrutural/dado. Use ao extrair, ler ou classificar marcações de uma NT.
allowed-tools: Bash(python:*), Bash(node:*), Read, Grep, Glob
---

# Skill: Interpretar Nota Técnica

## Quando usar
- Extrair informações de uma NT (PDF ou DOCX)
- Entender o que uma NT altera
- Classificar marcações de cor

## Pré-requisitos
- Dependências Python instaladas (`python -c "import fitz"`); se falhar, `/fiscal-diagnostico`.
- Para NTs já extraídas, **não reabra o PDF**: leia `catalogo/nt/<doc>/<arquivo>.json`
  (ex.: `catalogo/nt/cte/CTe_NT_2026_004_v1.00.json`). Só abra o PDF (Read com `pages`)
  para conferir uma citação específica.

## Passo a passo

1. **Identificar**: número da NT, versão, documento (NF-e/CT-e/MDF-e), título.
2. **Cronograma** ("Histórico de Alterações", geralmente pág. 3): versões, datas de
   homologação/produção, itens por versão. Preservar texto literal (`Até 05/10/2026`).
3. **"Descrição das alterações"**: lista OFICIAL do que cada versão altera.
4. **Marcações no corpo** (mapa cor → versão vem de `catalogo/legendas/<doc>.yaml`,
   nunca assuma pela cor):
   - Fundo amarelo / verde: revisão conforme a legenda do documento
   - Texto vermelho riscado: **EXCLUÍDO**
   - Sem marcação: inalterado **ou** regra/seção nova inteira
5. **Cruzar** cor × descrição (a cor nunca prova sozinha — regra 6 do AGENTS.md):

   | Situação | Tratamento |
   |---|---|
   | Item na descrição + marcação no corpo | Confirmado |
   | Item na descrição SEM marcação | Pode ser regra nova inteira (`SEM_MARCA`). Se não for, `ERRO_MUDANCA_SEM_MARCACAO` → registrar em `docs/duvidas-abertas.md` |
   | Marcação SEM item na descrição | `AMBIGUA` → registrar em `docs/duvidas-abertas.md` |

6. **Classificar cada marcação**

   | Categoria | Exemplo | Tratamento |
   |---|---|---|
   | REVISAO | Amarelo/verde/riscado sobre regra | NOVA / ALTERADA / EXCLUIDA |
   | ESTRUTURAL | Cabeçalho de tabela, linhas de grupo | Ignorar |
   | DADO | Tabela de ALC com cores por município (ex.: regra 326 do CT-e) | Preservar como dado, nunca como revisão |
   | AMBIGUA | Texto verde sem fundo claro | Registrar em duvidas-abertas |

7. **Saída do pipeline** (o Python gera SOMENTE JSON; o MD é feito pela IA com `/fiscal-gerar-md`):
   - `catalogo/nt/<doc>/<arquivo>.json`
   - `catalogo/legendas/<doc>.yaml`

## Erros que o extrator detecta

`ERRO_COR_NAO_MAPEADA`, `ERRO_PDF_ESCANEADO`, `ERRO_TABELA_QUEBRADA`,
`ERRO_MUDANCA_SEM_MARCACAO`, `ERRO_VERSAO_AMBIGUA` — tratamento em `/fiscal-ingerir-nt`
e na skill `revisar-extracao`.

## Referências
- `docs/REFERENCIA.md` seção 4.1 (conceito de marcações)
- `scripts/python/utils/cores.py` e `classificacao.py` (algoritmo real de cores)
- `docs/legenda-cores.md` **ainda não existe** — se precisar do algoritmo, leia o código acima
  e registre a lacuna.
