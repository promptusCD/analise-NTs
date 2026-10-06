## 1. Setup e Estrutura

- [x] 1.1 Criar diretorio `scripts/python/utils/` com `__init__.py` e verificar que `scripts/python/` existe. Verificacao: `ls scripts/python/utils/__init__.py` retorna arquivo.
- [x] 1.2 Criar diretorios `catalogo/nt/`, `catalogo/moc/`, `catalogo/legendas/` (vazio, com `.gitkeep` se necessario). Verificacao: diretorios existem.
- [x] 1.3 Verificar que `pymupdf>=1.24.0`, `pyyaml>=6.0` e `python-docx>=1.1.0` estao em `requirements.txt`. Verificacao: `pip install -r requirements.txt` funciona.

## 2. Modulo utils/cores.py -- Deteccao de Cor

- [x] 2.1 Implementar `extract_background_rects(page, target_colors)`: extrai retangulos de fundo colorido via `page.get_drawings()`, filtrando por dimensao minima e proporcao. Verificacao: rodar em NF-e 2026.007 e retornar lista de retangulos AMARELO/VERDE (ou vazia se nao houver).
- [x] 2.2 Implementar `extract_spans_with_color(page)`: extrai spans com cor de texto, bbox, font, flags via `get_text("dict", flags=TEXT_COLLECT_STYLES)`. Verificacao: rodar em NF-e 2026.007 e retornar lista de spans com `text`, `color_hex`, `bbox`.
- [x] 2.3 Implementar `detect_strikethrough(page, spans)`: detecta strikethrough por flag `FZ_STEXT_STRIKEOUT` + deteccao vetorial de linhas horizontais cruzando texto. Verificacao: rodar em NF-e 2026.007 e retornar lista de spans riscados (ou vazia).
- [x] 2.4 Implementar `map_spans_to_background(spans, bg_rects)`: mapeia cada span ao retangulo de fundo via intersecao de centro do bbox com tolerancia 2pt. Verificacao: rodar em NF-e 2026.007 e retornar spans com `marcacao` (AMARELO/VERDE/SEM_MARCA).
- [x] 2.5 Implementar `classify_text_color(color_hex)`: classifica cor do texto como VERMELHO ou NORMAL. Verificacao: testar com hex conhecidos (#FF0000 -> VERMELHO, #000000 -> NORMAL).
- [x] 2.6 Implementar fallback `get_background_color_pixmap(page, rect)`: renderiza area do bbox como pixmap e amostra pixel. Verificacao: rodar em PDF sem retangulos vetoriais e detectar cor.

## 3. Modulo utils/parsing.py -- Parsing de Secoes e Itens

- [x] 3.1 Implementar `parse_nt_metadata(page_texts)`: extrai metadados da NT (nt, versao, documento, titulo) do cabecalho do PDF. Verificacao: rodar em NF-e 2026.007 e retornar dict com metadados preenchidos.
- [x] 3.2 Implementar `parse_cronograma(page_texts)`: extrai datas de homologacao/producao do cronograma, mantendo literais como "Ate 05/10/2026". Verificacao: rodar em CT-e 2026.004 e retornar 3 blocos de cronograma.
- [x] 3.3 Implementar `parse_sections(page_texts)`: identifica secoes numeradas (1, 2, 3.1, 3.2, etc.) e seus titulos. Verificacao: rodar em NF-e 2026.007 e retornar secoes com numeros e titulos.
- [x] 3.4 Implementar `parse_items_from_section(section_text, marcacoes)`: extrai itens individuais de uma secao, associando marcacoes de cor. Verificacao: rodar em secao 3.2 da NF-e 2026.007 e retornar itens com IDs e marcacoes.
- [x] 3.5 Implementar `detect_documento_from_filename(filename)`: detecta NF-e/CT-e/MDF-e pelo nome do arquivo. Verificacao: testar com nomes como `NT_2026_007_v1.10.pdf` -> NF-e, `CTe_NT_2026_004_v1.00.pdf` -> CT-e.
- [x] 3.6 Implementar `calculate_sha256(filepath)`: calcula hash SHA256 do arquivo. Verificacao: rodar em arquivo conhecido e comparar com `sha256sum`.

## 4. Modulo utils/saida.py -- Geracao de JSON e MD

- [x] 4.1 Implementar `gerar_json_nt(metadata, cronograma, itens, estatisticas)`: gera JSON conforme formato REFERENCIA.md secao 5.1, incluindo bloco `estatisticas` com `total_itens` e `por_marcacao` (AMARELO, VERDE, EXCLUIDO, SEM_MARCA). Verificacao: gerar JSON de NF-e 2026.007 e validar estrutura (nt, versao, itens[], cronograma[], estatisticas).
- [x] 4.2 Implementar `gerar_md_nt(json_data)`: gera MD legivel com cabecalho, secoes e itens destacados por marcacao. Verificacao: gerar MD de NF-e 2026.007 e verificar que itens EXCLUIDO e AMARELO estao destacados.
- [x] 4.3 Implementar `gerar_json_moc(metadata, secoes, regras, campos)`: gera JSON para MOC. Verificacao: gerar JSON de MOC CT-e v4.00 e validar estrutura.
- [x] 4.4 Implementar `gerar_md_moc(json_data)`: gera MD legivel para MOC. Verificacao: gerar MD de MOC CT-e v4.00.
- [x] 4.5 Implementar `salvar_saida(json_data, md_content, output_dir)`: salva JSON e MD nos diretorios corretos (`catalogo/nt/<doc>/` ou `catalogo/moc/<doc>/`). Verificacao: arquivos sao criados nos caminhos esperados.

## 5. Modulo utils/manifest.py -- Gerenciamento do Manifest

- [x] 5.1 Implementar `ler_manifest(manifest_path)`: le manifest.yaml e retorna lista de entradas. Verificacao: ler manifest.yaml existente e retornar 9 entradas.
- [x] 5.2 Implementar `atualizar_status_manifest(manifest_path, arquivo, novo_status)`: atualiza `status_ingestao` de uma entrada especifica. Verificacao: atualizar status de NF-e 2026.007 para `extraida` e verificar que outros campos nao mudaram.
- [x] 5.3 Implementar `adicionar_manifest_moc(manifest_path, moc_data)`: adiciona entrada para MOC nao registrado. Verificacao: adicionar MOC CT-e e verificar que entrada foi criada.

## 6. Script Principal extrair_nt.py

- [x] 6.1 Implementar `extrair_nt(pdf_path)`: orquestra extracao completa de uma NT (abrir PDF, extrair paginas, detectar cores, parsear secoes, gerar JSON+MD). Verificacao: rodar em NF-e 2026.007 e gerar `catalogo/nt/nfe/NT_2026_007_v1.10.json` e `.md`.
- [x] 6.2 Implementar CLI com argumentos: `python extrair_nt.py <arquivo.pdf> [--output json|md|both]`. Verificacao: rodar `python extrair_nt.py fontes/nfe/notas-tecnicas/NT_2026_007_v1.10.pdf` funciona.
- [x] 6.3 Implementar integracao com manifest: chamar `atualizar_status_manifest` apos extracao bem-sucedida. Verificacao: manifest.yaml e atualizado apos extracao.
- [x] 6.4 Implementar logging de erros e avisos: logar itens problematicos (SEM_MARCA em secao de alteracoes, fundo nao detectado) no stdout E em arquivo `catalogo/nt/<doc>/stdout/<nt>_v<ver>.log`. Verificacao: log file e criado apos extracao com timestamp, nivel (INFO/WARN/ERROR) e mensagens.

## 7. Script Principal extrair_moc.py

- [x] 7.1 Implementar `extrair_moc(pdf_path)`: orquestra extracao completa de um MOC em PDF (abrir PDF, extrair secoes, regras, campos). Verificacao: rodar em MOC CT-e v4.00 e gerar `catalogo/moc/cte/MOC_CTe_VisaoGeral_v4.00.json` e `.md`.
- [x] 7.2 Implementar `extrair_moc_docx(docx_path)`: extrai MOC de arquivo DOCX usando python-docx. Verificacao: rodar em MOC_MDFe_Anexo_II_DAMDFE_v3.00b.docx e gerar JSON.
- [x] 7.3 Implementar CLI com argumentos: `python extrair_moc.py <arquivo.pdf|docx>`. Verificacao: rodar funciona para PDF e DOCX.
- [x] 7.4 Implementar integracao com manifest: adicionar/atualizar entrada do MOC. Verificacao: manifest.yaml e atualizado.

## 8. Script atualizar_manifest.py

- [x] 8.1 Implementar CLI: `python atualizar_manifest.py --arquivo <path> --status <status>`. Verificacao: rodar e verificar que manifest.yaml e atualizado.
- [x] 8.2 Implementar `--list`: listar status de todas as entradas do manifest. Verificacao: `python atualizar_manifest.py --list` mostra tabela com 9 NTs.

## 9. Validacao: NF-e 2026.007 (NT simples)

- [x] 9.1 Rodar `extrair_nt.py` em `fontes/nfe/notas-tecnicas/NT_2026_007_v1.10.pdf` e verificar que JSON e MD sao gerados em `catalogo/nt/nfe/`. Verificacao: arquivos existem e tem conteudo.
- [x] 9.2 Verificar que itens com fundo amarelo tem marcacao AMARELO no JSON. Verificacao: pelo menos 1 item com `marcacao: AMARELO`.
- [x] 9.3 Verificar que itens com fundo verde tem marcacao VERDE no JSON. Verificacao: pelo menos 1 item com `marcacao: VERDE`.
- [x] 9.4 Verificar que itens excluidos tem marcacao EXCLUIDO no JSON. Verificacao: pelo menos 1 item com `marcacao: EXCLUIDO`.
- [x] 9.5 Verificar que cronograma foi extraido corretamente. Verificacao: JSON contem `cronograma` com pelo menos 1 entrada.
- [x] 9.6 Verificar que manifest.yaml foi atualizado para `status_ingestao: extraida`. Verificacao: manifest mostra `extraida` para NF-e 2026.007.

## 10. Validacao: CT-e 2026.004 (NT complexa)

- [x] 10.1 Rodar `extrair_nt.py` em `fontes/cte/notas-tecnicas/CTe_NT_2026_004_v1.00.pdf`. Verificacao: JSON e MD gerados em `catalogo/nt/cte/`.
- [x] 10.2 Verificar que cronograma tem 3 blocos de datas (A, B, C). Verificacao: JSON contem `cronograma` com 3 entradas.
- [x] 10.3 Verificar que itens de regras de validacao (1051-1053) sao extraidos. Verificacao: JSON contem itens com IDs 1051, 1052, 1053.
- [x] 10.4 Verificar que campos novos (vTPrestLiq, vTotDFe, IBSCBS) sao detectados. Verificacao: JSON contem itens com esses campos.
- [x] 10.5 Verificar que legenda e gerada em `catalogo/legendas/cte.yaml`. Verificacao: arquivo existe e tem AMARELO/VERDE/EXCLUIDO.

## 11. Validacao: MOCs

- [x] 11.1 Rodar `extrair_moc.py` em `fontes/cte/moc/MOC_CTe_VisaoGeral_v4.00.pdf`. Verificacao: JSON e MD gerados em `catalogo/moc/cte/`.
- [x] 11.2 Rodar `extrair_moc.py` em `fontes/mdfe/moc/MOC_MDFe_Anexo_II_DAMDFE_v3.00b.docx`. Verificacao: JSON e MD gerados em `catalogo/moc/mdfe/`.
- [x] 11.3 Verificar que regras de validacao sao extraidas do MOC CT-e. Verificacao: JSON contem `regras` com pelo menos 10 entradas.
- [x] 11.4 Verificar que manifest.yaml foi atualizado com MOCs. Verificacao: manifest contem entradas com `tipo: moc`.

## 12. Execucao em Massa e Legenda

- [x] 12.1 Rodar `extrair_nt.py` em todas as 9 NTs. Verificacao: `catalogo/nt/` contem JSON+MD para nfe, cte, mdfe.
- [x] 12.2 Rodar `extrair_moc.py` em todos os 9 MOCs. Verificacao: `catalogo/moc/` contem JSON+MD para nfe, cte, mdfe.
- [x] 12.3 Verificar que todas as 9 NTs tem `status_ingestao: extraida` no manifest. Verificacao: nenhuma entrada com `pendente`.
- [x] 12.4 Verificar que legendas sao geradas para nfe, cte, mdfe. Verificacao: `catalogo/legendas/` contem 3 arquivos YAML.