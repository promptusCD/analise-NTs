---
description: Diagnosticar o ambiente (Python, dependências, Node, OpenSpec) e listar arquivos/scripts referenciados que ainda não existem
---

# /fiscal-diagnostico

Somente leitura. Rode e reporte em tabela (OK / FALTA / AÇÃO):

1. **Ferramentas**: `python --version`, `node --version`, `openspec --version`.
   `python3` no Windows costuma ser o stub da Microsoft Store — use `python`.
2. **Dependências Python**: `python -c "import fitz, docx, lxml, yaml, jinja2, pytest"`.
   Falhou → ação: `pip install -r requirements.txt` (ofereça, não instale sem pedir).
   O `.venv/` do repo pode estar quebrado (sem `Scripts/`); recriar: `python -m venv .venv`.
3. **Node**: `node_modules/` na raiz (`npm install`) — dependências `ejs`, `js-yaml`, `node-fetch`.
4. **Arquivos que o AGENTS.md/commands/skills referenciam**, verifique existência de:
   `docs-fiscais/{NFE,CTE,MDFE,_COMUM}.md`, `docs/duvidas-abertas.md`, `docs/legenda-cores.md`,
   `catalogo/regras/`, `catalogo/campos/`, `calendario/calendario.yaml`,
   `scripts/js/{consultar,gerar_calendario,detectar_novidades,atualizar_docs_fiscais,verificar_manifest}.js`,
   `CATALOGO_ARQUIVOS.md`. Cruze com as fases em `openspec/changes/` para dizer se é "planejado" ou "esquecido".
5. **Consistência**: `entrada/README.md` presente; JSONs de `catalogo/` × entradas `extraida` do manifest;
   arquivos de `fontes/` sem entrada no manifest.
6. **Testes**: `python -m pytest tests -q` (se houver testes) — reporte falhas com a saída.

Termine com a lista priorizada do que bloqueia cada command `/fiscal-*`.
