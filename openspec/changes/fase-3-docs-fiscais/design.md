# Design

## Context

Ver proposal.md (Why). Estado observado: `catalogo/nt/<doc>/*.json` (NTs com `cronograma`, `secoes` tipo `regras`/`tabela`/`texto`, `estatisticas`) e `catalogo/moc/<doc>/*.json` (`regras_validacao`, `campos_leiaute`) existem; `manifest.yaml` lista as fontes; `docs/duvidas-abertas.md` tem formato fixo por entrada. Não existem `docs-fiscais/`, `calendario/` populado, `catalogo/legendas/` populado nem XSD catalogado. Só `scripts/js/sincronizar_ia.js` existe em JS; as dependências `js-yaml` e `ejs` já estão no `package.json`. Alguns JSONs trazem acentuação corrompida em campos de texto, e o gerador não deve corrigi-los.

## Goals / Non-Goals

**Goals:**
- Gerar os blocos AUTO de forma determinística e idempotente, sem tocar no texto manual.
- Calcular vigência em um módulo reutilizável, com a data de hoje injetável para teste.
- Entregar documentos úteis já com os dados atuais, declarando o que falta de forma verificável: fontes pendentes, XSD, legendas revisadas, calendário e modelos sem conteúdo no catálogo, num bloco `cobertura`.

**Non-Goals:**
- `calendario.yaml`/`gerar_calendario.js`, catálogo de XSD, chamada automática do script pelo `/fiscal-processar`.
- Interpretar cores ou reextrair NTs.
- Redação por IA dentro dos blocos AUTO (a IA só escreve as partes manuais).

## Decisions

1. **Vigência derivada do `cronograma` das NTs, sem esperar o calendário (direção escolhida pelo usuário).**
   Alternativa: implementar `calendario.yaml` primeiro. Rejeitada por bloquear a fase-3 em outra fase; o custo é duplicar a lógica no futuro, mitigado pelo módulo `vigencia.js` independente, que o gerador de calendário reutilizará.

2. **Geração dos blocos em JS, com marcadores `AUTO:BEGIN/END <nome>` e substituição por regex ancorada.**
   Alternativa: template EJS do arquivo inteiro. Rejeitada porque sobrescreveria o texto manual (regra 11 do AGENTS). A substituição por marcador preserva o resto do arquivo.

3. **Validar todos os marcadores de um arquivo antes de escrever qualquer bloco** (contagem de BEGIN/END, ordem, nomes conhecidos). Falha rápida e arquivo intacto em caso de erro. Escrita via arquivo temporário e renomeação.

4. **Data de hoje injetável** (parâmetro `--hoje AAAA-MM-DD`, padrão `new Date()` local). Alternativa: sempre usar o relógio. Rejeitada por tornar os testes instáveis.

5. **Texto do catálogo reproduzido literal**, escapando só o necessário para Markdown (barras `|` em tabelas). Sem reparo de encoding nem de datas. Itens sem dado viram `NAO ENCONTRADO NAS FONTES`.

6. **Ordem determinística** (documento, NT, versão, página, id) para a saída ser estável e o diff útil.

7. **Parsing de data só para `DD/MM/AAAA` exato**; qualquer outro texto fica literal com situação `indeterminada`.

8. **Dúvidas por documento** lendo o campo `Documento:` das entradas; entradas sem esse campo vão para `_COMUM.md` apenas se existir bloco para isso, senão são ignoradas com aviso.

9. **Vigência em módulo compartilhado e exportado** (`scripts/js/lib/vigencia.js`, exportando `parseData`, `situacao` e `calcularLinhas`). O gerador de docs, o verificador e o futuro `gerar_calendario.js` importam dele; ninguém reimplementa. Alternativa: função interna do gerador. Rejeitada por duplicar a regra quando o calendário nascer.

10. **Dois commands de IA** em `.claude/commands/`: `/fiscal-docs-gerar` (roda o script, mostra o diff dos blocos AUTO, orienta só as partes manuais) e `/fiscal-docs-validar` (roda a validação e relata). A correção de uma divergência é feita no gerador ou no catálogo e regenerada, nunca editando dentro de bloco AUTO. Após criar, `npm run sincronizar-ia`.

11. **Validação em dois níveis, por script, não a olho.** (a) doc <-> JSON em JS, comparação exata (ids, cStat, datas, contagens vs `estatisticas`, fontes do manifest, itens sem origem). (b) doc/JSON <-> original em Python com PyMuPDF (`python -I`), buscando no texto da página indicada o cStat, as datas e a mensagem, com espaços e acentos normalizados só para comparar. O que não for achado vira `NAO CONFIRMADO NO ORIGINAL`, nunca OK. A marcação por cor é conferida por amostra no `/fiscal-docs-validar`, pois cor não prova sozinha. A validação é critério de fechamento da change.

12. **Bloco AUTO `cobertura` na seção 2.** Lista, por documento: NTs e MOCs ingeridos (do manifest e do catálogo); fontes pendentes (de `docs/ARQUIVOS_NECESSARIOS.md`); presença de XSD catalogado, de `catalogo/legendas/<doc>.yaml` e de `calendario/calendario.yaml` (testada no sistema de arquivos, não declarada à mão); e os modelos do documento (NF-e 55/65; CT-e 57/67/64/Simplificado; MDF-e 58) com a indicação de que há ou não conteúdo específico no catálogo, por busca textual, rotulada como "não encontrado por busca não prova ausência". Alternativas: texto manual fixo (rejeitada, envelhece e fica falso quando algo for ingerido) e seção nova fora do template (rejeitada, quebra o template da seção 7.1 do REFERENCIA). Se o formato de `ARQUIVOS_NECESSARIOS.md` não for interpretável, o bloco aponta o arquivo em vez de inventar a lista.

Layout:

```
catalogo/nt/<doc>/*.json --+
catalogo/moc/<doc>/*.json -+--> leitores --> blocos (texto MD) --+
manifest.yaml ------------+                                       |
docs/duvidas-abertas.md ---+       vigencia.js(hoje, cronograma) -+
                                                                  v
                       docs-fiscais/<DOC>.md (so entre AUTO:BEGIN/END)
```

## Risks / Trade-offs

- [Seções 3/4 incompletas sem XSD] → aviso explícito no documento; refinar na fase-4.
- [Duas lógicas de vigência quando o calendário nascer] → módulo único reutilizável e teste de contrato.
- [Documento com marcador quebrado por edição manual] → validação prévia com erro claro, nada escrito.
- [JSONs com acentuação corrompida aparecem nos blocos] → reprodução literal e registro em `docs/duvidas-abertas.md` se afetar uma citação; correção é da extração, não do gerador.
- [Índice de regras grande demais em MD] → colunas enxutas (cStat, aplicação, marcação, origem) e resumo da mensagem, sem texto integral.
- [Falso "não confirmado" por quebra de linha ou acento corrompido no PDF] → normalização na comparação e relatório separando "não confirmado" de "divergente".
- [PDF/DOCX sem camada de texto] → limite conhecido; o item fica `NAO CONFIRMADO NO ORIGINAL` com o motivo.
- [Bloco `cobertura` desatualizado ou impreciso] → derivado do sistema de arquivos e do catálogo a cada execução, e conferido pelo verificador.
- [Regra nova inteira sem cor] → o bloco informa a marcação como `SEM_MARCA`, nunca "inalterada".

## Migration Plan

Criar os arquivos e rodar `npm run docs-fiscais`. Reverter apagando `docs-fiscais/` e o script; nenhuma outra pasta é alterada. A integração com `/fiscal-processar` fica para uma change posterior.
