# Tasks

## 1. Infraestrutura de verificação (golden + verificador)

- [x] 1.1 Criar `tests/python/conftest.py` (helpers: abrir PDF de `fontes/` só para leitura, carregar JSON extraído, `skip` com motivo se o PDF faltar) e `pytest.ini`. Verificação: `python -m pytest tests/python -q` coleta os testes e roda sem erro de importação.
- [x] 1.2 Criar `scripts/python/verificar_extracao.py` (schema, cobertura de palavras, IDs de regra PDF×JSON por regex independente, mensagens suspeitas de truncamento, cronograma vazio/inválido, alertas de marcação; código de saída ≠ 0 em pendência bloqueante). Verificação: executado nos 19 JSONs atuais, reporta ao menos D1 (2026.008), D2 (mensagens) e D3 (cronograma) como pendências.
- [x] 1.3 Escrever `tests/python/test_invariantes.py` com os invariantes gerais (IDs PDF == JSON, mensagem sem terminação truncada, nenhuma nota com texto de mensagem, `arquivo_origem` relativo, cronograma sem `00/00/0000`/versão `.`). Verificação: os testes falham hoje apontando os defeitos conhecidos (vermelho esperado, lista de falhas anexada ao relatório da tarefa).
- [x] 1.4 Garantir somente leitura em `fontes/`: teste que compara a lista de arquivos e hashes de `fontes/` antes e depois da suíte. Verificação: o teste passa e nenhum arquivo de `fontes/` aparece em `git status`.

## 2. Metadados e caminho de origem (D4, D5)

- [x] 2.1 Ler, nas páginas renderizadas, o título e a versão de cada uma das 9 NTs e gravar `tests/golden/metadados.json` com a página de origem de cada valor. Verificação: arquivo existe com 9 entradas e `1.14b` para CT-e 2025.001.
- [x] 2.2 Corrigir `parse_nt_metadata`: título pelo cabeçalho de página recorrente (fallback: título do `manifest.yaml`), versão com sufixo alfabético e aviso quando divergir da capa. Verificação: `tests/python/test_metadados.py` (golden de 2.1) passa para as 9 NTs.
- [x] 2.3 Gravar `arquivo_origem` relativo à raiz do repositório com `/` em `gerar_json_nt` e `gerar_json_moc`. Verificação: teste confirma que nenhum JSON contém `:\` nem `Users` e que o caminho existe a partir da raiz.
- [x] 2.4 Atualizar `utils/json_schema.py` para aceitar os novos formatos de metadados. Verificação: `validate_nt_json`/`validate_moc_json` aprovam os JSONs re-extraídos de uma NT e um MOC de exemplo.

## 3. Cronograma (D3)

- [x] 3.1 Ler a tabela "Controle de Versões" das NTs 2026.007, 2026.002 (DANFE), 2025.001 (CT-e), 2026.010, 2026.004 e MDF-e 2025.001 nas páginas renderizadas e gravar `tests/golden/cronograma.json` (datas literais, incluindo "Até DD/MM/AAAA", e a página). Verificação: arquivo existe com as 6 NTs pedidas (mais as outras 3, para cobrir as 9) e as 6 linhas da DANFE 2026.002 (correção: o plano previa 3; a leitura da página mostrou 6).
- [x] 3.2 Escrever `tests/python/test_cronograma.py` a partir do golden. Verificação: o teste falha hoje nas 6 NTs (vermelho esperado).
- [x] 3.3 Implementar leitura por coluna da tabela de controle de versões (primitivas de posição x/y de `utils/colunas.py`, versão/homologação/produção/descrição, literais). Verificação: `test_cronograma.py` passa para as 6 NTs.
- [x] 3.4 Remover os fallbacks que inventam versão "1.00" e `00/00/0000`; registrar `ERRO_DATA_NAO_ENCONTRADA` e devolver `[]`. Verificação: teste com texto sintético sem tabela retorna `[]` e o log contém o aviso.

## 4. Núcleo de extração por coluna

- [x] 4.1 Spike: inspecionar, nas páginas 6 e 9 da NT 2026.007, na 7 da NT 2026.008 e nas 8 e 13 da NT CT-e 2026.004, os spans (`bbox`, texto, cor) e as posições x dos cabeçalhos; registrar em `tests/fixtures/` os spans serializados dessas páginas. Verificação: fixtures existem e o teste de 4.2 as carrega.
- [x] 4.2 Implementar em `utils/colunas.py` a detecção de cabeçalho por sinônimos e fronteiras de coluna, o reuso das fronteiras em tabela sem cabeçalho e a atribuição de span à coluna pelo centro do bbox. Verificação: `tests/python/test_colunas.py` (spans das fixtures e spans sintéticos) passa nos casos: cabeçalho com `#`, sem `#`, sem `Efeito`, continuação sem cabeçalho.
- [x] 4.3 Implementar a segmentação em linhas lógicas por token de ID e a emissão de linhas canônicas + cabeçalho sintético `# ...` + uma linha por nota (com `trechos` e cor). Verificação: teste unitário com a regra 12C02-10 (fixture) gera a linha canônica com a mensagem completa e as notas separadas.
- [x] 4.4 Atualizar `_merge_line`/agregação para guardar `trechos[]` e `marcacao` dominante (D-2) e ligar a função de página por coluna em `extrair_nt.py` e `itens_from_pdf` de `extrair_moc.py`, mantendo o comportamento atual fora de tabela. Verificação: extração das NTs sem tabelas (ex.: MDF-e 2026.001) gera JSON idêntico ao anterior, exceto `extraido_em` e campos novos.

## 5. Regras de NT (D1, D2, D6, D7)

- [x] 5.1 Gravar `tests/golden/regras.json` à mão: IDs completos da NT 2026.008 (11) e mensagens completas de referência (12C02-10, 5AF15-11, B25-90, C12-10, 5BG15-10 da NT 2026.007; duas regras da 2026.008; uma da CT-e 2026.004), com a página de cada uma. Verificação: arquivo existe e cada expectativa tem página.
- [x] 5.2 Ajustar `classificacao.py` para reconhecer o cabeçalho sintético/sem `#` e `parse_regra` com `efeito` ausente (D1). Verificação: `tests/python/test_regras.py` passa para a NT 2026.008 (11 IDs) e para `K01-10` da NT 2026.002 (DANFE). Ampliada na implementação (D8): também regras sem coluna de ID, tabelas sem cabeçalho, `Obrig,`/`Facul.`; verificação adicional: invariante independente por cStat passa nas 9 NTs.
- [x] 5.3 Garantir mensagens completas e notas sem texto de mensagem (D2). Verificação: `test_regras.py` passa para as mensagens do golden e `test_invariantes.py` não acha mensagem truncada nas 9 NTs.
- [x] 5.4 Adicionar `id_unico` às regras (D6) e atualizar `json_schema.py`. Verificação: teste confirma unicidade de `id_unico` em cada JSON de NT e que `id` e `cStat` permanecem iguais ao PDF.
- [x] 5.5 Marcações por trecho nas notas e linhas (D7) e golden das páginas de referência. Verificação: teste da NT 2026.007 pág. 6 e 9 (C12-10 e Exceção 2 de B25-90 AMARELO, C17-10 EXCLUIDO, Observações do C17 AMARELO, Exceção de 12C02-10 VERDE) e da CT-e 2026.004 págs. 5, 7, 8 e 9 passa.

## 6. MOCs

- [x] 6.1 Escrever `tests/python/test_moc.py`: mensagens de regras de MOC sem truncamento e quantidades mínimas por MOC lidas do backup `catalogo_bak` (golden de contagens). Verificação: o teste falha hoje (mensagens truncadas) e as contagens mínimas estão registradas por arquivo.
- [x] 6.2 Aplicar a linearização por coluna ao fluxo de MOC (cabeçalhos de regras/leiaute de NF-e, CT-e e MDF-e) sem perder campos/regras. Verificação: `test_moc.py` passa para os 5 MOCs com regras e `campos_leiaute`/`regras_validacao` ≥ backup em todos os 10 MOCs. Resultado: 0 mensagens cortadas (antes ~300), regras do NF-e Anexo I 238→568, MDF-e Anexo I 0→125, seções do NF-e Visão Geral 161→294 (títulos reais antes perdidos); 2 cStats restantes registrados em `docs/duvidas-abertas.md` (#001, #002).
- [x] 6.3 Conferir o DOCX `MOC_MDFe_Anexo_II_DAMDFE_v3.00b.docx` e o caminho relativo. Verificação: JSON equivalente ao anterior (exceto `extraido_em` e `arquivo_origem`) e teste de caminho passa.

## 7. Re-extração, documentação e fechamento

- [x] 7.1 Fazer backup de `catalogo/` e `manifest.yaml` em `%TEMP%`, re-extrair as 9 NTs e os 10 MOCs com `python scripts/python/extrair_nt.py|extrair_moc.py ... --manifest manifest.yaml` e registrar a saída completa (sem filtrar erros). Verificação: 19 execuções com código 0 e manifest sem entrada nova em `pendente`.
- [x] 7.2 Rodar `verificar_extracao.py` nos 19 JSONs e a comparação com o backup. Verificação: zero pendência bloqueante, nenhuma NT/MOC com menos regras/campos que antes e `python -m pytest tests/python -q` verde.
- [x] 7.3 Regerar o MD de exemplo da CT-e 2025.001 com `/fiscal-gerar-md` e conferir título, versão `1.14b` e cronograma no MD. Verificação: os 3 valores aparecem corretos no MD.
- [x] 7.4 Atualizar `docs/REFERENCIA.md` (seção 5: campos `id_unico`, `trechos`, `cronograma[].descricao`, `arquivo_origem` relativo) e corrigir o `design.md` da `fase-2-json-robusto` (remover "Alterar cronograma (já funciona)"). Verificação: `grep -n "já funciona" openspec/changes/fase-2-json-robusto/design.md` não retorna a linha e a REFERENCIA descreve os campos novos.
- [x] 7.5 Atualizar a skill `revisar-extracao` e os commands `/fiscal-processar` (etapa 5 roda o verificador), `/fiscal-regra` e `/fiscal-impacto` (usar `id_unico`/`cStat`) em `.claude/` e rodar `npm run sincronizar-ia`. Verificação: `node scripts/js/sincronizar_ia.js --check` retorna "Tudo sincronizado.".
- [x] 7.6 Reportar ao usuário o resultado da conferência (tabela por NT/MOC: IDs, mensagens, cronograma, metadados, marcações) para decidir o avanço à próxima etapa. Verificação: relatório entregue com os 19 arquivos e o número de pendências remanescentes.

## Workflow follow-up

- Decisão do usuário: arquivar/sincronizar `fase-2-json-robusto` e arquivar esta change após a revisão.
