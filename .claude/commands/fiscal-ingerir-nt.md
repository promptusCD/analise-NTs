---
description: Ingerir uma Nota Técnica nova - fontes/, manifest, extração JSON, MD, legenda, calendário, docs-fiscais e dúvidas (sem commit)
argument-hint: <caminho do PDF/DOCX da NT> [--forcar]
---

# /fiscal-ingerir-nt

**Argumentos**: $ARGUMENTS (`--forcar` = reingerir NT já existente)

Fluxo da regra 12 do AGENTS.md: extrair → catalogar → calendário → docs-fiscais → dúvidas.
**NÃO faça commit** — aguarde o usuário.

## Pré-checagem
Rode `/fiscal-diagnostico` mentalmente: `python -c "import fitz, yaml"` precisa funcionar (use `python`,
nunca `python3` no Windows). Se faltar dependência, pare e oriente `pip install -r requirements.txt`.

## Fluxo

0. **Regra 11**: a IA nunca cria/edita/copia nada em `fontes/`; só **move** o que o usuário colocou em
   `entrada/`. Se `<arquivo>` estiver fora de `entrada/` (e fora de `fontes/`), peça ao usuário que o
   coloque em `entrada/`. Se já estiver em `fontes/`, não o mova: pule os passos 4 e vá ao 5.
1. **Validar**: arquivo existe, é PDF/DOCX, calcular SHA256 (`sha256sum`).
2. **Duplicata**: comparar o SHA256 com `fontes/**` e `manifest.yaml` (shas antigos podem estar
   truncados em 16 chars — compare por prefixo). Igual → já ingerida; só continue com `--forcar`.
   Mesmo nome/NT+versão com hash diferente → `ERRO_DUPLICATA_HASH_DIVERGENTE`: alertar, manter ambos.
3. **Identificar**: NT, versão, documento (NF-e/CT-e/MDF-e). Falhou → `ERRO_VERSAO_AMBIGUA`, pedir ao usuário.
4. **Mover** (`mv`, nunca `cp`) de `entrada/` para `fontes/<doc>/notas-tecnicas/` como
   `<DOC>_NT_<AAAA>_<NNN>_v<versão>.pdf` (NF-e usa `NT_<AAAA>_<NNN>_v<versão>[_sufixo].pdf`; veja os
   nomes já existentes). Nunca sobrescreva arquivo existente em `fontes/`.
5. **Registrar** em `manifest.yaml` (id, documento, tipo, nt, versao, titulo, arquivo, sha256,
   status_ingestao, confianca). Confira o formato nas entradas existentes.
6. **Extrair JSON**: `python scripts/python/extrair_nt.py "<arquivo em fontes/>" --manifest manifest.yaml`
   → `catalogo/nt/<doc>/<arquivo>.json` (**somente JSON**; o Python não gera MD). Mostre a saída
   completa se houver `ERRO` ou Traceback — não filtre com grep.
7. **Revisar** com a skill `revisar-extracao` (schema + checklist).
8. **Gerar MD**: `/fiscal-gerar-md <nt>`.
9. **Legenda**: gerar/atualizar `catalogo/legendas/<doc>.yaml` e cruzar marcações × "Descrição das alterações".
10. **Calendário**: skill `atualizar-calendario` (cronograma + datas nas observações) e
    `node scripts/js/gerar_calendario.js` se existir.
11. **docs-fiscais**: `node scripts/js/atualizar_docs_fiscais.js` se existir (blocos AUTO só por script).
    Se o script não existir, avise e **não** edite blocos AUTO à mão.
12. **Dúvidas**: registre inconsistências com `/fiscal-duvidas --registrar`.
13. **Resumo**: NT/versão/documento, seções/tabelas/regras extraídas, cores mapeadas, dúvidas, próximos passos
    (XSD do pacote associado, se faltar → ver `docs/ARQUIVOS_NECESSARIOS.md`).

## Erros
| Erro | Ação |
|---|---|
| `ERRO_COR_NAO_MAPEADA` | Listar cores e contagem; pedir revisão da legenda |
| `ERRO_VERSAO_AMBIGUA` | Pedir NT/versão manualmente |
| `ERRO_PDF_ESCANEADO` | Marcar para OCR/revisão manual |
| `ERRO_TABELA_QUEBRADA` | Listar páginas com problema |
| `ERRO_DUPLICATA_HASH_DIVERGENTE` | Alertar, manter ambos, registrar dúvida |
