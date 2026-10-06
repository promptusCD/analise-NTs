## Why

O projeto fiscal-dfe-knowledge precisa de uma estrutura base organizada antes de
qualquer funcionalidade ser implementada. Atualmente, os arquivos estao todos
misturados em `entrada/`, sem gitignore, sem dependencias configuradas, sem
documentacao basica. Sem essa fundacao, as fases seguintes (extrator, calendario,
docs-fiscais) nao podem comecar.

## What Changes

- Criar estrutura de diretorios conforme definido em `docs/REFERENCIA.md` secao 3
- Configurar `.gitignore` para Python, Node.js e arquivos temporarios
- Criar `package.json` com dependencias Node.js (js-yaml, ejs, node-fetch)
- Criar `requirements.txt` com dependencias Python (pymupdf, python-docx, lxml, pyyaml)
- Criar `manifest.yaml` vazio como fonte unica de registro de fontes
- Mover arquivos de `entrada/` para `fontes/` organizados por documento fiscal
- Atualizar `CATALOGO_ARQUIVOS.md` com todos os arquivos apos organizacao
- Verificar integridade (SHA256) de todos os arquivos movidos

## Capabilities

### New Capabilities

Nenhuma capability de comportamento. Esta e uma change de setup/infraestrutura pura.

### Modified Capabilities

Nenhuma. Comportamento do sistema nao muda.

## Impact

- **Diretorios**: criacao de toda a arvore `fontes/`, `catalogo/`, `calendario/`,
  `scripts/python/`, `scripts/js/`, `tests/`, `backlog/`
- **Git**: `.gitignore` configurado para ignorar `node_modules/`, `venv/`,
  `__pycache__/`, arquivos temporarios
- **Dependencias**: `package.json` e `requirements.txt` prontos para `npm install`
  e `pip install`
- **Arquivos**: todos os 40+ arquivos em `entrada/` organizados em `fontes/`
- **Manifest**: `manifest.yaml` criado como registro central de fontes