---
description: DESTRUTIVO - limpar catalogo/ e re-extrair todas as NTs e MOCs (exige confirmação explícita)
argument-hint: [--sem-md]
disable-model-invocation: true
---

# /fiscal-reextrair

**Argumentos**: $ARGUMENTS

Use após corrigir bugs em `extrair_nt.py`/`extrair_moc.py` ou para regenerar todo o catálogo.

## 0. Confirmação obrigatória (não pule)
1. Liste o que será apagado: contagem de arquivos em `catalogo/` (JSON, **MDs gerados pela IA**,
   legendas, `stdout/`) e o que será resetado no manifest.
2. Avise: os MDs são produzidos pela IA (`/fiscal-gerar-md`) e as legendas por revisão — apagar custa retrabalho.
   Pergunte ao usuário se prossegue; sem "sim" explícito, **pare**.
3. Faça backup: `cp manifest.yaml manifest.yaml.bak` e `cp -r catalogo "$TEMP/catalogo_bak"` (diretório temporário fora do repositório)
   (`*.bak` já é ignorado pelo git).

## 1. Limpar `catalogo/` (preserva `README.md`)
```bash
find catalogo -type f ! -name README.md -delete
mkdir -p catalogo/nt/{nfe,cte,mdfe} catalogo/moc/{nfe,cte,mdfe} catalogo/legendas
touch catalogo/nt/.gitkeep catalogo/moc/.gitkeep catalogo/legendas/.gitkeep
```

## 2. Resetar status no manifest
Para cada NT (tipo ≠ moc) use o script oficial, sem reescrever o YAML inteiro:
```bash
python scripts/python/atualizar_manifest.py --arquivo "<path no manifest>" --status pendente
```
(percorra com `python scripts/python/atualizar_manifest.py --list`.)

## 3. Re-extrair
Execute as etapas 2 e 3 de `/fiscal-processar` para **todos** os arquivos (mostrando erros completos).

## 4. Verificar
Etapa 5 de `/fiscal-processar`. Compare a nova extração com o backup: se alguma NT/MOC ficou com
**menos** seções/regras que antes, alerte (regressão) e registre em `/fiscal-duvidas --registrar`.
Depois sugira `/fiscal-gerar-md` para os MDs apagados. Sem commit.
