# Proposal

## Why

A change `fase-2-json-robusto` foi marcada como concluída (32/32), mas a conferência dos JSONs contra os PDFs
reais (2026-10-20) mostrou que o resultado não é confiável para as etapas seguintes (calendário, `/fiscal-regra`,
`/fiscal-impacto`): regras perdidas, mensagens de rejeição truncadas, cronogramas errados e metadados incorretos.
A causa de processo é que `tests/golden`, `tests/fixtures` e `tests/python` estão vazios e as verificações da fase 2
eram do tipo "o JSON tem seções tipificadas", sem comparar com o PDF. A causa técnica é a extração por **linhas
achatadas por posição vertical**, que mistura colunas de tabela, e um `parse_cronograma` em regex que o `design.md`
da fase 2 declarou "já funciona" (premissa falsa). Ver `docs/REFERENCIA.md` (seções 5, 9 e 13) para o contexto.

## What Changes

Defeitos a corrigir (evidência: `catalogo/nt/*.json` × `fontes/*/notas-tecnicas/*.pdf`):

- **D1** NT NF-e 2026.008 tem 11 regras no PDF (B25-80, I11c-10, NB01-10…) e **0** no JSON (cabeçalho
  `Campo | Modelo | Regra de Validação | Aplic. | Msg | Descrição Erro` não é reconhecido); falta `K01-10` na NT 2026.002 DANFE (98 de 99).
- **D2** Mensagem de rejeição truncada: a coluna "Descrição Erro" se mistura com as notas da coluna "Regra"
  (`12C02-10`: "…CNPJ [XX.XXX.XXX/XXXX-DV] do"; `5AF15-11`: nota com "…Autorizadoras. irregular na UF"). ~25–45% das
  regras das NTs e 27–69 `regras_validacao` por MOC.
- **D3** Cronograma errado ou vazio (NT 2026.007 sem a v1.10 "Até 05/10/2026"; DANFE 2026.002 com 1 de 6 linhas;
  CT-e 2025.001 com versão "06"; NT 2026.010 com `.`/`00/00/0000`; MDF-e 2025.001 vazio; fallback inventa "1.00").
- **D4** Metadados: `titulo` quase sempre errado ("Projeto Conhecimento de"); `versao` perde sufixo (`1.14b` → `1.14`).
- **D5** `arquivo_origem` grava caminho absoluto `C:\Users\…` (projeto é compartilhado na empresa).
- **D6** IDs de regra das NTs de CT-e são números de linha reiniciados por tabela (`01`, `001`); não são únicos.
- **D8** (descoberto na implementação) Mais da metade das regras da CT-e 2026.004 (32 de 53 cStats) e todas as das NTs de MDF-e não viram regra: tabelas **sem coluna de ID** e **sem linha de cabeçalho** nunca foram reconhecidas, e a aplicação `Obrig,`/`Facul.` (grafias do PDF) quebrava o reconhecimento.
- **D7** Destaque parcial em linha de tabela é perdido (NT 2026.007 pág. 6, Observações 1/2 do campo C17: amarelo no PDF, `SEM_MARCA` no JSON).

Mudanças:

- Extração de tabelas **por coluna** (posição x das palavras e do cabeçalho), em vez de linhas achatadas.
- Novo parser de cronograma baseado na tabela "Controle de Versões", sem inventar versão nem data.
- Metadados (título, versão com sufixo) lidos do PDF e `arquivo_origem` relativo ao repositório.
- Campo `id_unico` nas regras e marcação por trecho nas linhas/notas.
- Mesma correção de mensagem para `regras_validacao` dos MOCs.
- **Suíte de testes de aceite** (pytest + golden escritos à mão a partir dos PDFs) e script reutilizável
  `verificar_extracao.py` (a auditoria feita manualmente), usado pela etapa 5 de `/fiscal-processar`.
- Re-extração das 9 NTs e 10 MOCs com comparação contra o backup (sem regressão).
- **BREAKING (aditivo, compatível)**: novos campos `id_unico`, `trechos`; `arquivo_origem` passa a ser relativo;
  `cronograma[]` ganha `descricao`; `cronograma` pode ser `[]` (nunca valores inventados).

## Capabilities

### New Capabilities

- `nt-extracao-fidelidade`: o JSON de NT reproduz fielmente o PDF — regras (todas, com mensagem completa e id único),
  cronograma literal, metadados corretos, marcações por trecho e caminhos portáveis.
- `moc-regras-fidelidade`: as `regras_validacao` e `campos_leiaute` do JSON de MOC têm mensagem/descrição completas e
  `arquivo_origem` portável.
- `verificacao-extracao`: toda extração pode ser conferida automaticamente contra o PDF de origem (testes golden e
  script de verificação), com critérios mensuráveis.

### Modified Capabilities

Nenhuma. Os requisitos `json-nt` e `json-moc` da `fase-2-json-robusto` ainda estão só como deltas daquela change
(`openspec/specs/` está vazio, a fase 2 não foi arquivada). Estes specs são complementares e não os alteram; recomenda-se
arquivar/sincronizar a fase 2 antes ou depois desta, por decisão do usuário.

## Impact

- Código: `scripts/python/extrair_nt.py`, `scripts/python/extrair_moc.py`, `scripts/python/utils/{parsing,classificacao,cores,moc,saida,json_schema}.py`,
  novo `scripts/python/utils/colunas.py` e `scripts/python/verificar_extracao.py`.
- Testes: `tests/python/`, `tests/golden/`, `tests/fixtures/` (hoje vazios).
- Dados: re-extração de `catalogo/nt/**` e `catalogo/moc/**` (diretórios ignorados pelo git; `fontes/` só leitura, regra 11).
- Docs/IA: `openspec/changes/fase-2-json-robusto/design.md` (corrigir "cronograma já funciona"), `docs/REFERENCIA.md` seção 5,
  skill `revisar-extracao` e commands `/fiscal-processar`, `/fiscal-regra`, `/fiscal-impacto` (em `.claude/`, depois
  `npm run sincronizar-ia` para `.opencode/`).
- Dependências: nenhuma nova (PyMuPDF, pytest, pyyaml já instalados). Sem commit (regra 12).
