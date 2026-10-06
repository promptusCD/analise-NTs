## 1. Estrutura de Diretorios

- [x] 1.1 Criar diretorios `fontes/nfe/notas-tecnicas/`, `fontes/nfe/moc/`, `fontes/nfe/xsd/` e verificar com `Test-Path`
- [x] 1.2 Criar diretorios `fontes/cte/notas-tecnicas/`, `fontes/cte/moc/`, `fontes/cte/xsd/` e verificar com `Test-Path`
- [x] 1.3 Criar diretorios `fontes/mdfe/notas-tecnicas/`, `fontes/mdfe/moc/`, `fontes/mdfe/xsd/` e verificar com `Test-Path`
- [x] 1.4 Criar diretorios `fontes/externas/tabelas/` e verificar com `Test-Path`
- [x] 1.5 Criar diretorios `catalogo/nt/nfe/`, `catalogo/nt/cte/`, `catalogo/nt/mdfe/`, `catalogo/regras/`, `catalogo/campos/`, `catalogo/legendas/` e verificar com `Test-Path`
- [x] 1.6 Criar diretorios `calendario/`, `scripts/python/`, `scripts/js/`, `tests/fixtures/`, `tests/python/`, `tests/js/`, `tests/golden/`, `backlog/` e verificar com `Test-Path`

## 2. Arquivos de Configuracao

- [x] 2.1 Criar `.gitignore` com regras para Python (`__pycache__/`, `venv/`, `*.pyc`), Node.js (`node_modules/`), arquivos temporarios (`*.tmp`, `*.bak`) e saidas geradas (`catalogo/`, `calendario/CALENDARIO.md`, `calendario/calendario.html`)
- [x] 2.2 Criar `package.json` com nome `fiscal-dfe-knowledge`, dependencias `js-yaml`, `ejs`, `node-fetch` e scripts basicos
- [x] 2.3 Criar `requirements.txt` com `pymupdf`, `python-docx`, `lxml`, `pyyaml`, `pytest`, `jinja2`
- [x] 2.4 Criar `manifest.yaml` vazio com comentario de cabecalho

## 3. Organizar NF-e

- [x] 3.1 Mover `entrada/NT2026.007_v1.10...pdf` para `fontes/nfe/notas-tecnicas/` e calcular SHA256
- [x] 3.2 Mover `entrada/NT 2026.002 v1.11...pdf` para `fontes/nfe/notas-tecnicas/` e calcular SHA256
- [x] 3.3 Mover `entrada/NT 2026.008 v1.00...pdf` para `fontes/nfe/notas-tecnicas/` e calcular SHA256
- [x] 3.4 Mover `entrada/NT 2026.010 v1.00...pdf` para `fontes/nfe/notas-tecnicas/` e calcular SHA256
- [x] 3.5 Mover MOC NF-e v7.00 (4 PDFs) para `fontes/nfe/moc/` e calcular SHA256
- [x] 3.6 Mover XSDs NF-e (`NFe-PL_010b_*`, `NFe-PL_010f_*`, `NFe-Eventos_RTC/`, `NT 2025.002 v1.30 - RTC-Eventos_RTC/`, `NT 2025.002 v1.40-Schema_Evento_211110*/`, `BT 2019.001*`) para `fontes/nfe/xsd/` com nomes padronizados e calcular SHA256

## 4. Organizar CT-e

- [x] 4.1 Mover `entrada/CTe_Nota_Tecnica_2026_004_v1.00.pdf` para `fontes/cte/notas-tecnicas/` e calcular SHA256
- [x] 4.2 Mover `entrada/CTe_Nota_Tecnica_2025_001_RTC_v1.14b.pdf` para `fontes/cte/notas-tecnicas/` e calcular SHA256
- [x] 4.3 Mover `entrada/CTe_Nota_Tecnica_2026_002 v1.01-1.pdf` para `fontes/cte/notas-tecnicas/` e calcular SHA256
- [x] 4.4 Mover MOCs CT-e (VisaoGeral, Anexo I, Anexo II) para `fontes/cte/moc/` e calcular SHA256
- [x] 4.5 Mover XSDs CT-e (`PL_CTe_400_NT2026.004 RTC_1.00/`, `NT 2026.001 RTC Vinculacao Pagamento*/`) para `fontes/cte/xsd/` com nomes padronizados e calcular SHA256

## 5. Organizar MDF-e

- [x] 5.1 Mover `entrada/MDFe_Nota_Tecnica_2025_001_1.03.pdf` para `fontes/mdfe/notas-tecnicas/` e calcular SHA256
- [x] 5.2 Mover `entrada/MDFe_Nota_Tecnica_2026_001.pdf` para `fontes/mdfe/notas-tecnicas/` e calcular SHA256 (verificar duplicatas)
- [x] 5.3 Mover MOCs MDF-e (VisaoGeral, Anexo I, Anexo II) para `fontes/mdfe/moc/` e calcular SHA256
- [x] 5.4 Mover XSDs MDF-e (`PL_MDFe_300b_NT012025_1.05/`) para `fontes/mdfe/xsd/` e calcular SHA256

## 6. Organizar Tabelas e Externas

- [x] 6.1 Mover `entrada/tabelas-informes/*.xlsx` para `fontes/externas/tabelas/` e calcular SHA256
- [x] 6.2 Mover `entrada/MOC NFe ABI...pdf` para `fontes/externas/` (NFe ABI minuta) e calcular SHA256

## 7. Verificacao e Limpeza

- [x] 7.1 Verificar que `entrada/` esta vazio (todos os arquivos movidos)
- [x] 7.2 Verificar que nenhum hash SHA256 divergiu (integridade)
- [x] 7.3 Listar duplicatas encontradas e registrar em `docs/duvidas-abertas.md`
- [x] 7.4 Limpar `entrada/` (remover arquivos ja movidos e verificados)

## 8. Manifest e Catalogo

- [x] 8.1 Registrar todos os arquivos movidos em `manifest.yaml` com id, documento, tipo, arquivo, sha256, status_ingestao
- [x] 8.2 Atualizar `docs/CATALOGO_ARQUIVOS.md` com todos os arquivos organizados
- [x] 8.3 Atualizar `docs/ARQUIVOS_NECESSARIOS.md` para refletir que a organizacao foi concluida

## 9. Verificacao Final

- [ ] 9.1 Rodar `node scripts/js/verificar_manifest.js` (se existir) ou verificar manualmente que todos os arquivos estao no manifest
- [ ] 9.2 Confirmar que a estrutura de diretorios esta completa conforme REFERENCIA.md secao 3
- [ ] 9.3 Commit com mensagem "fase-0-setup: estrutura base e organizacao de arquivos"