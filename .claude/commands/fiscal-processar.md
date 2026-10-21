---
description: Pipeline de ingestão - organizar entrada/, extrair JSON de NTs e MOCs, atualizar manifest e verificar (--etapa N para uma etapa)
argument-hint: [--etapa 1-5]
---

# /fiscal-processar

**Argumentos**: $ARGUMENTS (vazio = pipeline completo; `--etapa N` = só a etapa N)

| Etapa | Nome | O que faz |
|---|---|---|
| 1 | Organizar | `entrada/` → `fontes/` (regras de `/fiscal-catalogar-atualizar`, passo 0) |
| 2 | Extrair NTs | JSON de NTs **ainda não extraídas** |
| 3 | Extrair MOCs | JSON de MOCs **ainda não extraídos** |
| 4 | Manifest | Registrar/atualizar entradas |
| 5 | Verificar | Schema dos JSONs + status do manifest + estatísticas |

Sem commit (regra 12). **Regra 11**: em `fontes/` a IA só move arquivos vindos de `entrada/`; nunca edita, cria ou copia ali. Use **`python`** (não `python3`). Antes de tudo confirme `python -c "import fitz, yaml, docx, lxml"`;
se falhar, pare e oriente `pip install -r requirements.txt` (ou `/fiscal-diagnostico`).

## Etapa 1 — Organizar
Aplique **exatamente** a classificação, nomenclatura e verificação de duplicata (SHA256 contra todo `fontes/`)
de `/fiscal-catalogar-atualizar` (passo 0). Arquivo não identificado: liste, **não mova**, pergunte.
Remoção de duplicata exige a confirmação do `rm`.

## Etapa 2 — Extrair NTs
Para cada PDF em `fontes/{nfe,cte,mdfe}/notas-tecnicas/` cujo JSON em `catalogo/nt/<doc>/` não existe
(ou com `--forcar` no pedido do usuário):
```bash
python scripts/python/extrair_nt.py "<pdf>" --manifest manifest.yaml
```
Mostre a saída completa quando houver `ERRO`/Traceback (não esconda com `grep`).

## Etapa 3 — Extrair MOCs
Para cada `.pdf`/`.docx` em `fontes/{nfe,cte,mdfe}/moc/` sem JSON em `catalogo/moc/<doc>/`:
```bash
python scripts/python/extrair_moc.py "<arquivo>" --manifest manifest.yaml
```

## Etapa 4 — Manifest
`extrair_nt.py`/`extrair_moc.py` marcam `extraida` quando o arquivo já tem entrada. Itens novos precisam
ser registrados antes (id, documento, tipo, nt, versao, titulo, arquivo, sha256, status_ingestao, confianca).
```bash
python scripts/python/atualizar_manifest.py --list
```

## Etapa 5 — Verificar
- Contagem de JSONs: compare com o número de PDFs/DOCX em `fontes/` (não use contagens fixas).
- **Rode o verificador**: `python scripts/python/verificar_extracao.py` (schema, origem relativa, título/versão,
  cobertura de texto, IDs e cStat do PDF fora do JSON, mensagens cortadas, cronograma, marcações) e mostre o resumo por
  arquivo. Pendência BLOQUEANTE (código de saída 1) = extração não confiável: não siga para `/fiscal-gerar-md`
  nem para calendário até resolver ou registrar em `/fiscal-duvidas --registrar`. Detalhes na skill `revisar-extracao`.
- Extração vazia (0 seções) ou regressiva → `/fiscal-duvidas --registrar`.
- MDs de NT/MOC faltando → sugerir `/fiscal-gerar-md`.

## Relatório final
Movidos N (duplicatas M) · NTs extraídas N · MOCs extraídos N · Manifest: N entradas, pendentes: lista · Próximo passo.

## Erros
| Erro | Ação |
|---|---|
| Arquivo não identificado | Listar e não mover; pedir decisão |
| Duplicata (mesmo SHA256) | Remover de `entrada/` (com confirmação) |
| Extração vazia | Registrar em duvidas-abertas |
| Manifest não atualizado | Conferir caminho (separadores `/` vs `\`) |
| `ModuleNotFoundError` | `pip install -r requirements.txt` |
