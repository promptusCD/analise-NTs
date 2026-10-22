# Design

## Context

Estado atual observado (ver `proposal.md` para motivação e `specs/` para requisitos):

- `extrair_nt.py` e `extrair_moc.py` leem spans com `extract_page_content` (cada span já traz `bbox`, `marcacao`, cor) e os
  juntam em linhas por posição vertical com `aggregate_spans_into_lines` (tolerância de 3 pt). Em tabela de regras isso
  mistura a coluna esquerda ("Regra de Validação", com notas) com a direita ("Descrição Erro"): a continuação da mensagem
  cai nas notas e a mensagem fica truncada (D2).
- `_merge_line` marca a **linha inteira** com a primeira marcação diferente de `SEM_MARCA` e `classificacao.py` só atribui a
  cor da primeira linha de uma linha de tabela; linhas de continuação entram sem cor (D7).
- `classificacao.py`/`moc.py` só reconhecem cabeçalho que começa com `#` (D1) e `parse_regra` exige `Obrig.` + cStat.
- `parse_cronograma` é um regex sobre o texto corrido; quando falha, inventa versão "1.00" (D3). `parse_nt_metadata` usa a
  primeira linha "longa" das 3 primeiras páginas como título e a regex `v([\d.]+)` do nome do arquivo (D4).
- Teste de viabilidade (2026-10-20): `page.find_tables()` perde espaços e hífens ("RegradeValidação", "5AF1511"), funde
  colunas e falha em tabelas sem borda das NTs de CT-e. Não serve sozinho.
- `tests/` está vazio. O `.venv/` do repo está quebrado; usar `python` global (PyMuPDF 2.0, `import pymupdf`).

## Goals / Non-Goals

**Goals:**
- Corrigir D1–D7 com fidelidade verificável contra os PDFs reais (critérios nos specs).
- Manter o formato do JSON compatível com os consumidores atuais (`/fiscal-gerar-md`, skills, commands); só adicionar campos.
- Deixar a verificação permanente (golden + script), para que "concluída" signifique "conferida contra o PDF".

**Non-Goals:**
- Extrair XSD, gerar `catalogo/regras|campos`, calendário e docs-fiscais (fases seguintes).
- Reescrever o classificador de seções/títulos nem o detector de cor de fundo/riscado (conferidos e adequados nas páginas golden).
- OCR de PDFs escaneados.

## Decisions

### D-1: Linearização por coluna antes da classificação (em vez de reescrever o classificador)
Novo módulo `utils/colunas.py`, chamado por uma função de página que substitui `aggregate_spans_into_lines`. Para cada página:
1. Detecta **cabeçalho de tabela** pelos spans (sinônimos: `#|Campo|ID`, `Modelo`, `Regra de Validação`, `Aplic.`, `Msg|cStat`,
   `Efeito`, `Descrição Erro|Mensagem`, `Ele`, `Pai`, `Tipo`, `Ocor.`, `Tam.`, `Descrição/Observação`) e deriva as fronteiras x das colunas.
2. Tabela que continua na página seguinte **sem cabeçalho** reutiliza as fronteiras da última tabela do mesmo tipo (mesma largura útil da página).
3. Atribui cada span à coluna pelo **centro** do bbox e segmenta **linhas lógicas** quando a coluna do ID contém um token de ID.
4. Emite linhas **canônicas** no formato que `parse_regra`/`parse_linha_tabela` já entendem
   (`<id> <modelo> <condição> Obrig. <cStat> Rej. <mensagem completa>`), um cabeçalho sintético `# ...` normalizado, e uma linha
   por nota da coluna "Regra" (Exceção/Observação/itens `-`), cada uma com seus `trechos` e cor próprios.
5. Fora de tabela mantém o comportamento atual (linhas por y).

Alternativas: (a) `find_tables()` — descartada pelos defeitos medidos, só aceitável para bbox de célula; (b) heurística de
pós-processamento da mensagem (juntar notas suspeitas) — frágil e não resolve D1; (c) reescrever o classificador — risco alto
e não é necessário porque o problema está na montagem das linhas.
Como NTs e MOCs usam o mesmo `aggregate_spans_into_lines`, D-1 corrige as mensagens dos MOCs (`moc-regras-fidelidade`) sem código paralelo.

### D-2: Marcação por trecho
`_merge_line` passa a guardar `trechos[{texto, marcacao}]` e `marcacao` = dominante (`EXCLUIDO > AMARELO > VERDE > …`), reaproveitando
`_marcacao_dominante`. Linhas de tabela acumulam os trechos das continuações; linhas e notas expõem `trechos` quando houver mais de uma marcação.

### D-3: `id_unico` aditivo
`id` continua sendo o impresso no PDF. `id_unico = "<numero da seção>:<id>"` (acrescenta o grupo se ainda colidir). Assunção registrada:
nas NTs de CT-e o `#` é numeração local; a chave de busca real é o `cStat`, que já existe. Consumidores ganham `id_unico` sem quebra.

### D-4: Cronograma pela tabela "Controle de Versões"
`parse_cronograma` é substituído por leitura por coluna da tabela de controle de versões (colunas Versão | Histórico | Implantação Teste/Homologação | Implantação Produção), usando as
mesmas primitivas de D-1. Uma entrada por linha de versão/bloco, com `versao`, `homologacao`, `producao`, `descricao`, mantendo literais ("Até 05/10/2026").
Sem tabela reconhecida: `[]` + aviso `ERRO_DATA_NAO_ENCONTRADA`. Os fallbacks que inventam "1.00" e `00/00/0000` são removidos.

### D-5: Metadados do PDF; caminho relativo
`titulo` vem da **capa** (pág. 1): linhas entre o nome do projeto (`Projeto …`, que quebra em 2–3 linhas) e a linha `Versão …`, sem a linha `Nota Técnica N`, ou o sufixo após `Nota Técnica N –`; o layout da capa varia (título antes ou depois de `Nota Técnica`), por isso o parser trata esses padrões e o golden de metadados cobre as 9 NTs. O título do `manifest.yaml` é um resumo informal (sem acentos) e **não** é usado como fonte; só como último recurso se a capa não tiver título. `versao` vem do nome do arquivo com a regex
`v(\d+(?:\.\d+)*[a-z]?)`, conferida com a capa ("Versão 1.14b de…") e divergência vira aviso. `arquivo_origem` = caminho relativo à raiz do repo (raiz = diretório do `manifest.yaml`), com `/`.

### D-6: Verificação permanente
`tests/python` (pytest) + `tests/golden/*.json` escritos à mão a partir dos PDFs (cronogramas, títulos/versões, IDs e mensagens de regras de referência, marcações das páginas golden);
invariantes gerais calculados de forma **independente** do extrator (IDs por regex sobre `page.get_text()`). O mesmo código vira `scripts/python/verificar_extracao.py` (schema, cobertura de texto, IDs, mensagens
suspeitas, cronograma, marcações), usado pela etapa 5 de `/fiscal-processar` e pela skill `revisar-extracao`. Testes só leem `fontes/`; ausência de PDF → `skip` com motivo.

### D-7: Ordem de trabalho — testes junto com cada correção
Cada grupo de tarefas entrega seus testes (golden vermelho → verde) para que falhas não se acumulem até o fim.

## Risks / Trade-offs

- [Layouts diferentes entre NF-e, CT-e e MDF-e (cabeçalhos e colunas variam; CT-e sem borda)] → perfis de cabeçalho por sinônimos, fronteiras derivadas do cabeçalho real e testes golden por documento; fallback para o comportamento atual quando não houver cabeçalho reconhecido, com aviso no log.
- [Regressão em NTs/MOCs que hoje funcionam] → comparação com o backup `%TEMP%/catalogo_bak` (nenhuma NT/MOC com menos regras/campos) e `verificar_extracao.py` em todos os 19 arquivos antes de concluir.
- [Cabeçalho repetido ou ausente na continuação de página] → reuso das fronteiras da tabela anterior, coberto pelo golden da NT 2026.007 pág. 9.
- [Golden escrito à mão pode ter erro humano] → conferir as páginas renderizadas e registrar a página de origem em cada expectativa.
- [Mais código em `utils/`] → módulo único `colunas.py` com funções puras testáveis por spans sintéticos.

## Migration Plan

1. Implementar por grupos (testes + correção) sem alterar o formato existente, só acrescentando campos.
2. Re-extrair as 9 NTs e 10 MOCs com backup prévio de `catalogo/` (ignorado pelo git) e rodar o verificador e a comparação.
3. Atualizar `json_schema.py`, `docs/REFERENCIA.md`, skills/commands e `design.md` da fase 2; `npm run sincronizar-ia`.
4. Rollback: restaurar `catalogo/` do backup; reverter código via git (nada é commitado pela IA).

## Open Questions

- Decidir depois (não altera specs nem tarefas): arquivar/sincronizar a `fase-2-json-robusto` antes ou depois desta change.
