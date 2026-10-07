---
name: fiscal-processar
description: "Executa o pipeline completo de ingestao: organizar entrada/ -> fontes/, extrair JSON de NTs e MOCs, atualizar manifest e verificar. Suporta --etapa N para etapas individuais"
---

# /fiscal-processar [--etapa N]

Executa o pipeline completo: `entrada/` -> `fontes/` -> JSON em `catalogo/` -> `manifest.yaml` -> relatorio final.

Sem argumentos, executa todas as etapas em sequencia. Com `--etapa N`, executa somente a etapa indicada.

**Argumentos fornecidos**: $ARGUMENTS

## Etapas

| Etapa | Nome          | O que faz                                                        |
|-------|---------------|------------------------------------------------------------------|
| 1     | Organizar     | Move arquivos de `entrada/` para `fontes/` (identifica tipo e documento; remove duplicatas) |
| 2     | Extrair NTs   | Gera JSON de todas as NTs de `fontes/<doc>/notas-tecnicas/`      |
| 3     | Extrair MOCs  | Gera JSON de todos os MOCs de `fontes/<doc>/moc/`                |
| 4     | Atualizar manifest | Registra NTs/MOCs novos no `manifest.yaml`                   |
| 5     | Verificar     | Confere JSONs gerados e status do manifest; exibe estatisticas   |

Exemplos:
- `/fiscal-processar` -> pipeline completo
- `/fiscal-processar --etapa 1` -> so organiza `entrada/`
- `/fiscal-processar --etapa 5` -> so verifica

---

### Etapa 1 - Organizar entrada/

Para cada arquivo em `entrada/`:

1. **Identificar tipo** pelo nome:
   - Contem `_NT_` -> Nota Tecnica -> `fontes/<doc>/notas-tecnicas/`
     - `CTe_NT_*` / `CT_NT_*` -> CT-e
     - `MDFe_NT_*` / `MDF_NT_*` -> MDF-e
     - `NT_*` sem prefixo de documento -> NF-e
   - Comeca com `MOC_` -> MOC (PDF ou DOCX) -> `fontes/<doc>/moc/`
     - `MOC_CTe_*` -> CT-e ; `MOC_MDFe_*` -> MDF-e ; `MOC_NFe_*` -> NF-e
2. **Calcular SHA256** do arquivo.
3. **Verificar duplicata**: se ja existe arquivo em `fontes/` com o mesmo SHA256,
   remover de `entrada/` **sem mover** (registrar como "duplicata removida").
4. **Mover** para o destino identificado (renomear para o padrao
   `<DOC>_NT_<numero>_v<versao>.pdf` ou manter o nome original do MOC).
5. Arquivo **nao identificado**: listar e NAO mover; pedir decisao do usuario.

```bash
for f in entrada/*; do
  case "$(basename "$f")" in
    CTe_NT_*|CT_NT_*)   dest="fontes/cte/notas-tecnicas/" ;;
    MDFe_NT_*|MDF_NT_*) dest="fontes/mdfe/notas-tecnicas/" ;;
    NT_*)               dest="fontes/nfe/notas-tecnicas/" ;;
    MOC_CTe_*)          dest="fontes/cte/moc/" ;;
    MOC_MDFe_*)         dest="fontes/mdfe/moc/" ;;
    MOC_NFe_*)          dest="fontes/nfe/moc/" ;;
    *) echo "NAO IDENTIFICADO: $f"; continue ;;
  esac
  [ -f "$f" ] || continue
  sha=$(sha256sum "$f" | cut -d' ' -f1)
  # Duplicata: mesmo SHA256 de um arquivo ja presente em fontes/
  # (nao confiar no manifest: alguns shas estao truncados)
  if find "$dest" -type f \( -name "*.pdf" -o -name "*.docx" \) -exec sha256sum {} + 2>/dev/null | grep -q "$sha"; then
    echo "DUPLICATA REMOVIDA: $f"
    rm "$f"
  else
    mv "$f" "$dest"
    echo "MOVIDO: $(basename "$f") -> $dest"
  fi
done
```

### Etapa 2 - Extrair NTs

```bash
for pdf in fontes/nfe/notas-tecnicas/*.pdf fontes/cte/notas-tecnicas/*.pdf fontes/mdfe/notas-tecnicas/*.pdf; do
  python3 scripts/python/extrair_nt.py "$pdf" --manifest manifest.yaml 2>&1 | grep -E "(Concluido|ERRO)"
done
```

Saida: `catalogo/nt/<doc>/<arquivo>.json` (somente JSON - sem MD).

### Etapa 3 - Extrair MOCs

```bash
for moc in fontes/nfe/moc/*.pdf fontes/cte/moc/*.pdf fontes/mdfe/moc/*.pdf fontes/mdfe/moc/*.docx; do
  python3 scripts/python/extrair_moc.py "$moc" --manifest manifest.yaml 2>&1 | grep -E "(Concluido|ERRO)"
done
```

Saida: `catalogo/moc/<doc>/<arquivo>.json`.

### Etapa 4 - Atualizar manifest

- NTs: o proprio `extrair_nt.py` marca `status_ingestao: extraida` quando o
  arquivo ja tem entrada no `manifest.yaml`. NTs novas precisam ser registradas
  (id, documento, tipo, nt, versao, titulo, arquivo, sha256, status_ingestao, confianca).
- MOCs: `extrair_moc.py` registra automaticamente via `adicionar_manifest_moc`
  (arquivos novos entram com `status_ingestao: extraida`).

```bash
python3 scripts/python/atualizar_manifest.py --list
```

### Etapa 5 - Verificar resultado

```bash
echo "NTs:" && find catalogo/nt -name "*.json" | wc -l   # esperado: 9 atual + novas
echo "MOCs:" && find catalogo/moc -name "*.json" | wc -l # esperado: 10 atual + novas
python3 scripts/python/atualizar_manifest.py --list      # todas com status 'extraida'
```

- Conferir que todo JSON carrega e passa no schema
  (`scripts/python/utils/json_schema.py`, funcoes `validate_nt_json`/`validate_moc_json`).
- Registrar NTs/MOCs com extracao vazia ou regressiva como duvida em `docs/duvidas-abertas.md`.

## Relatorio final

Exibir ao final do pipeline completo:

- Arquivos organizados: N movidos de `entrada/` (e M duplicatas removidas)
- NTs extraidas: N JSONs em `catalogo/nt/`
- MOCs extraidos: N JSONs em `catalogo/moc/`
- Manifest: N entradas, todas com status `extraida` (ou lista de pendentes)

## Erros tratados

| Erro | Acao |
|---|---|
| Arquivo nao identificado em `entrada/` | Listar e nao mover; pedir decisao |
| Duplicata (mesmo SHA256) | Remover de `entrada/` sem mover |
| Extracao vazia (0 secoes) | Registrar em `docs/duvidas-abertas.md` |
| Manifest nao atualizado | Conferir caminho do arquivo (normalizar separadores) |