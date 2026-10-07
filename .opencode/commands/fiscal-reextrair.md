---
name: fiscal-reextrair
description: "Limpar catalogo/ e re-extrair todas as NTs e MOCs existentes"
---

# /fiscal-reextrair

Limpa o catalogo/ (mantendo README.md) e re-executa a extracao de todas as NTs e MOCs.

## Quando usar

- Apos corrigir bugs no extrair_nt.py ou extrair_moc.py
- Quando a formatacao do MD nao esta boa
- Quando quer regenerar todo o catalogo

## Como funciona

### 1. Limpar catalogo/

```bash
# Remover todos os arquivos exceto README.md
find catalogo -type f ! -name README.md -delete
find catalogo -type d -empty -delete 2>/dev/null

# Recriar diretorios
mkdir -p catalogo/nt catalogo/moc catalogo/legendas
touch catalogo/nt/.gitkeep catalogo/moc/.gitkeep catalogo/legendas/.gitkeep
```

### 2. Resetar manifest

```bash
# Resetar status de todas as NTs para 'pendente'
python3 -c "
import yaml
with open('manifest.yaml', 'r') as f:
    data = yaml.safe_load(f)
for item in data:
    if item.get('tipo') != 'moc':
        item['status_ingestao'] = 'pendente'
with open('manifest.yaml', 'w') as f:
    yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
print('Manifest resetado')
"
```

### 3. Extrair todas as NTs

```bash
for pdf in fontes/nfe/notas-tecnicas/*.pdf fontes/cte/notas-tecnicas/*.pdf fontes/mdfe/notas-tecnicas/*.pdf; do
  echo "=== NT: $(basename $pdf) ==="
  python3 scripts/python/extrair_nt.py "$pdf" --manifest manifest.yaml 2>&1 | grep -E "(Concluido|Itens|ERRO)"
  echo ""
done
```

### 4. Extrair todos os MOCs

```bash
for moc in fontes/nfe/moc/*.pdf fontes/cte/moc/*.pdf fontes/mdfe/moc/*.pdf fontes/mdfe/moc/*.docx; do
  echo "=== MOC: $(basename $moc) ==="
  python3 scripts/python/extrair_moc.py "$moc" --manifest manifest.yaml 2>&1 | grep -E "(Concluido|Secoes|Regras|Campos|ERRO)"
  echo ""
done
```

### 5. Verificar resultado

```bash
echo "=== NTs ===" && find catalogo/nt -name "*.json" | wc -l
echo "=== MOCs ===" && find catalogo/moc -name "*.json" | wc -l
echo "=== Manifest ===" && python3 scripts/python/atualizar_manifest.py --list
```

## Saida esperada

```
=== NTs ===
9
=== MOCs ===
10
=== Manifest ===
Todas as NTs e MOCs com status 'extraida'
```