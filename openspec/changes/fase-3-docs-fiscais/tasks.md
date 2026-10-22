# Tasks

## 1. Módulo de vigência

- [ ] 1.1 Criar `scripts/js/lib/vigencia.js` como módulo compartilhado exportando `parseData`, `situacao(linha, hoje)` e `calcularLinhas`, com parser estrito de `DD/MM/AAAA`. Verificar: teste em `tests/js/vigencia.test.js` cobrindo futura, em_homologacao, em_producao, excluida e texto literal ("Até 05/10/2026") como `indeterminada`; um segundo script de teste importa o módulo e obtém o mesmo resultado; `node --test tests/js` passa.
- [ ] 1.2 Tratar linhas repetidas da mesma versão e data ausente. Verificar: teste com duas linhas da versão 1.00 do cronograma da CT-e NT 2026.004 devolvendo situações independentes.

## 2. Leitura do catálogo

- [ ] 2.1 Criar `scripts/js/lib/catalogo.js` que lista NTs/MOCs por documento (`nfe`, `cte`, `mdfe`) em ordem determinística. Verificar: teste que carrega `catalogo/` real e confere 4 NTs NF-e, 3 CT-e, 2 MDF-e.
- [ ] 2.2 Ler `manifest.yaml` e `docs/duvidas-abertas.md` (filtro por `Documento:`). Verificar: teste com fixture de duas entradas de documentos diferentes.
- [ ] 2.3 Ler `docs/ARQUIVOS_NECESSARIOS.md` (fontes pendentes por documento) e detectar presença de XSD catalogado, `catalogo/legendas/<doc>.yaml` e `calendario/calendario.yaml`. Verificar: teste com fixtures de arquivo presente e ausente, e com formato não interpretável devolvendo "não interpretável" em vez de lista inventada.

## 3. Geradores de bloco

- [ ] 3.1 Gerar `fontes_vigentes` e `linha_do_tempo` (cronograma + situação de hoje, datas literais). Verificar: teste de snapshot com `--hoje` fixo.
- [ ] 3.2 Gerar `regras` (cStat, aplicação, marcação, NT/MOC, versão, página), com excluídas rotuladas e `NAO ENCONTRADO NAS FONTES` para campo ausente. Verificar: teste que uma regra EXCLUIDO não aparece como vigente e que o total bate com `estatisticas.total_regras`.
- [ ] 3.3 Gerar `grupos`, `eventos`, `em_andamento` e `duvidas`. Verificar: teste de bloco vazio exibindo mensagem explícita; `em_andamento` lista só itens futuros ou em homologação.
- [ ] 3.4 Gerar o bloco `cobertura` (ingeridos, pendentes, XSD/legendas/calendário, modelos sem conteúdo por busca textual com o aviso de que busca não prova ausência). Verificar: teste de snapshot com o estado atual (sem XSD, sem legendas, sem calendário) e teste que cria uma legenda de fixture e vê a ausência sumir.

## 4. Script de atualização

- [ ] 4.1 Criar `scripts/js/atualizar_docs_fiscais.js` (argumentos: documento opcional, `--hoje`, `--check`) com validação prévia de marcadores e escrita atômica só entre AUTO. Verificar: testes para par desbalanceado (erro, arquivo intacto), nome desconhecido e idempotência (2ª execução sem diff).
- [ ] 4.2 Garantir que nada é escrito fora de `docs-fiscais/`. Verificar: após rodar, `git status --short` lista apenas `docs-fiscais/` e os arquivos novos de scripts/testes.

## 5. Documentos

- [ ] 5.1 Criar `NFE.md`, `CTE.md` e `MDFE.md` com as nove seções, partes manuais e marcadores AUTO (incluindo `cobertura` na seção 2). Verificar: o script roda sem erro nos três e as seções 2, 5, 6, 8 e 9 são preenchidas, com a cobertura declarando as ausências reais.
- [ ] 5.2 Preencher as armadilhas (seção 7.2 do REFERENCIA) com fonte, e o aviso de leiaute sem XSD nas seções 3 e 4. Verificar: revisão manual de cada armadilha contra a NT citada; sem fonte fica "pendente de confirmação".
- [ ] 5.3 Criar `_COMUM.md` e `_GLOSSARIO.md`. Verificar: fonte não oficial rotulada; glossário cobre as siglas da seção de glossário do REFERENCIA.

## 6. Commands para a IA

- [ ] 6.1 Criar `.claude/commands/fiscal-docs-gerar.md` (roda `npm run docs-fiscais`, resume blocos alterados, proíbe editar bloco AUTO, `fontes/` e commit). Verificar: leitura do command contra o padrão de `fiscal-gerar-md.md` e execução manual com `cte`.
- [ ] 6.2 Criar `.claude/commands/fiscal-docs-validar.md` (roda os dois verificadores, conduz a amostra de marcação por cor e apresenta o relatório com fontes). Verificar: execução manual produz o relatório com as seções previstas.
- [ ] 6.3 Rodar `npm run sincronizar-ia` e depois `node scripts/js/sincronizar_ia.js --check`. Verificar: sem diferença para os dois commands.

## 7. Verificação minuciosa

- [ ] 7.1 Criar `scripts/js/verificar_docs_fiscais.js` (doc <-> JSON: regras, cStat, marcação, página, cronograma literal, situação, contagens vs `estatisticas`, fontes do manifest, itens sem origem, excluídas como vigentes, e coerência do bloco `cobertura` com o catálogo, o manifest e o sistema de arquivos). Verificar: testes com fixture válida e com cada falha induzida (regra removida, cStat inventado, data alterada, ausência declarada que não existe) saindo com código diferente de zero.
- [ ] 7.2 Criar `scripts/python/verificar_docs_vs_fontes.py` (PyMuPDF, `python -I`, somente leitura em `fontes/`; confere cStat, datas e mensagem na página citada, com normalização de espaços e acentos). Verificar: teste pytest com PDF de fixture confirmando um item e reportando `NAO CONFIRMADO NO ORIGINAL` para outro.
- [ ] 7.3 Reconhecer achados conhecidos de `docs/duvidas-abertas.md`. Verificar: o cStat 890 do MOC CT-e aparece como achado conhecido, não como erro novo.

## 8. Fechamento

- [ ] 8.1 Rodar `npm run docs-fiscais`, `python -m pytest` e `node --test tests/js`. Verificar: tudo passa; resultado registrado.
- [ ] 8.2 Executar a validação minuciosa (`/fiscal-docs-validar`) sobre as 9 NTs e os MOCs dos 3 documentos: doc <-> JSON <-> original, mais a amostra de marcação AMARELO/VERDE/EXCLUIDO conferida contra a página do PDF. Verificar: relatório final sem divergência; os não confirmados explicados; resumo apresentado ao usuário antes de arquivar.
- [ ] 8.3 Registrar divergências de dado em `docs/duvidas-abertas.md` e atualizar `docs/REFERENCIA.md` se algo divergir do implementado. Verificar: nenhuma menção a arquivo inexistente nas seções 7 e fase-3.
