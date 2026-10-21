---
name: revisar-extracao
description: QA da extração de NTs/MOCs. Valida o JSON contra o schema, confere amostra contra o PDF, verifica itens da descrição de alterações sem marcação e reporta ERRO_MUDANCA_SEM_MARCACAO. Use após extrair ou quando suspeitar de perda de marcações.
allowed-tools: Read, Grep, Glob, Bash(python:*), Bash(node:*)
---

# Skill: Revisar Extração

## Quando usar
- Após extrair uma NT/MOC
- Suspeita de marcações perdidas
- Validar se todas as mudanças foram capturadas

## 0. Verificação automática (faça primeiro)
```bash
python scripts/python/verificar_extracao.py                       # todos os JSON de catalogo/
python scripts/python/verificar_extracao.py catalogo/nt/cte/<arquivo>.json
python -m pytest tests/python -q -m "not lento"                   # testes de aceite (golden) das NTs
```
O verificador confere, contra o PDF/DOCX de origem: schema, `arquivo_origem` relativo, título e
versão, cobertura de texto, IDs de regra (NF-e) e **cStat impressos no PDF que não viraram regra**,
mensagens de rejeição cortadas, cronograma vazio/inválido e marcações perdidas. Código de saída ≠ 0
= pendência **bloqueante**; avisos pedem revisão manual.
Extração vazia ou regressiva (menos seções/regras/campos que a versão anterior) vira dúvida em
`docs/duvidas-abertas.md`. Para NT nova, acrescente a expectativa em `tests/golden/` (metadados,
cronograma, regras) lendo as páginas do PDF — o golden é escrito à mão, nunca copiado do JSON.

## 1. Cabeçalho
- [ ] NT, versão, documento corretos? `arquivo_origem` e SHA256 corretos (batem com `manifest.yaml`)?

## 2. Cronograma
- [ ] Uma entrada por linha da tabela que tenha data; datas conferem com o PDF; literais (`Até 05/10/2026`, `Já implantado`, `07/2025`) preservados; `-`/`-x-` viram vazio
- [ ] `cronograma` vazio só se o PDF realmente não tem tabela de datas (nunca versão/data inventada)

## 3. Descrição das alterações (seção 3.x)
- [ ] Todos os itens presentes, na versão correta, nenhum omitido

## 4. Marcações no corpo
- [ ] Amarelo/verde/riscado capturados conforme `catalogo/legendas/<doc>.yaml`
- [ ] Sem falsos positivos (cor estrutural ou DADO tratada como revisão)

## 5. Cruzamento descrição × marcação
- [ ] Item sem marcação → regra nova inteira (`SEM_MARCA`) ou erro? Se erro: `ERRO_MUDANCA_SEM_MARCACAO`
- [ ] Marcação sem item → `AMBIGUA` + `docs/duvidas-abertas.md`

## 6. Tabelas
- [ ] Leiaute e regras reconstruídos; colunas (#, ID, Campo, Descrição…) certas; nenhuma linha perdida/mesclada

## 7. Legendas
- [ ] Mapa cor → versão confere com o "Controle de Versões" do documento

## Conferência visual contra o PDF
Renderize a página do PDF de `fontes/` (somente leitura) e veja as cores a olho: no Claude Code, use a
ferramenta Read com `pages` (ex.: `pages: "6"`); em outras IAs, renderize com PyMuPDF para PNG fora de `fontes/`. Amostras de referência (golden):
- NT NF-e 2026.007: págs. 6 e 9
- NT CT-e 2026.004: págs. 5, 7, 8 e 9

## Erros
| Erro | Ação |
|---|---|
| ERRO_COR_NAO_MAPEADA | Listar cores e contagem; pedir revisão da legenda |
| ERRO_PDF_ESCANEADO | Marcar para OCR manual |
| ERRO_TABELA_QUEBRADA | Revisar `extrair_nt.py` / `utils/parsing.py` |
| ERRO_MUDANCA_SEM_MARCACAO | Investigar; registrar em duvidas-abertas |
| ERRO_VERSAO_AMBIGUA | Verificar formato do cabeçalho |

## Resultado
Relatório com: itens OK, itens com problema (com página), dúvidas registradas e próximo passo.
Ao concluir sem pendências, `status_ingestao` pode ir a `revisada`
(`python scripts/python/atualizar_manifest.py --arquivo <path> --status revisada`) — só com ok do usuário.

## Referências
`scripts/python/utils/cores.py`, `docs/REFERENCIA.md` seção 4.1. (`docs/legenda-cores.md` ainda não existe.)
