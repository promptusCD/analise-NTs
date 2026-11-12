---
description: Gerar plano de implementação aprofundado de uma ou mais NTs (pré-tarefas para análise, campos e envio, regras, cuidados, ordem por prazo e tarefas para desenvolvedores) em docs/
argument-hint: <NT[,NT2...], ex. 2026.004 ou 2026.004 2026.005> [versão] [--anterior <versão>]
---

# /fiscal-plano-dev

**Argumentos**: $ARGUMENTS

Produz um documento em `docs/` para revisão do analista e, depois, para o time de desenvolvimento.
É mais profundo que `/fiscal-impacto`: inclui pré-tarefas com recomendação, o que o sistema deve
enviar, cuidados, ordem de implementação ligada aos prazos e tarefas com critério de aceite.

Modelo de referência (já usado para CT-e 2026.004 v1.01 e 2026.005):
`docs/CTe-NT-2026-004-005-implementacao.md`. Siga a mesma estrutura de seções.

## Fluxo

1. Rode `date`. Use a data de hoje em todas as situações de vigência.

2. **Localizar as NTs.** Normalize cada argumento (`NT-CT-e-2026.004`, `CTe NT 2026.004`, `2026.004`)
   para número + documento. Busque em `catalogo/nt/<doc>/` arquivos `*_<AAAA>_<NNN>_*`.
   - Sem versão: use a mais recente e diga qual.
   - Com `--anterior <versão>`: compare com ela e marque cada item como NOVO, ALTERADO, EXCLUÍDO ou SEM ALTERAÇÃO.
   - Não achou: responda `NAO ENCONTRADO NAS FONTES` e sugira `/fiscal-ingerir-nt`. Pare nessa NT e siga com as outras.

3. **Extrair o conteúdo** (siga a skill `resumo-impacto-dev`):
   - `secoes[]`, `regras[]`, `cronograma[]` e marcações do JSON da NT.
   - Use `cStat` e `id` como chave, e a `mensagem` completa.
   - Trechos truncados na extração: marque como pré-tarefa e confira no PDF.

4. **Conferir no PDF** (`fontes/<doc>/notas-tecnicas/<arquivo>.pdf`, com `fitz` via `python`):
   - Cronograma: página 3 (ou a que tiver "Histórico de Alterações / Cronograma").
   - Todo campo novo ou alterado: a página que o JSON indica.
   - Regras com mensagem quebrada, condição truncada ou mensagem repetida.
   - Use `python -I` para rodar scripts sobre o PDF.

5. **Cruzar com o XSD**: procure o pacote em `fontes/<doc>/xsd/` cujo nome contenha o número da NT
   (ex.: `NT2026.005`). Para cada campo novo, confirme existência, pai (`grep -F` ou `python`) e
   `minOccurs`. Se não houver pacote para a NT, escreva `XSD NAO ENCONTRADO NAS FONTES` e crie
   uma pré-tarefa para obtê-lo com `/fiscal-atualizar-fontes`.

6. **Conferir diferença entre NTs do mesmo pedido**: se houver mais de uma NT, marque o que se sobrepõe
   (campo ou regra em duas NTs) e a ordem de produção entre elas.

7. **Escrever o documento** em `docs/plano-dev-<doc>-<NT>-v<versão>.md`, com esta estrutura:

   1. **Cabeçalho**: status RASCUNHO, data de hoje, NT e versão usadas, fontes.
   2. **Prazos**: tabela com homologação, produção e situação em hoje. Literais como "Até dd/mm/aaaa" são preservados. Se a data já passou, diga "passou".
   3. **Pré-tarefas (P01...)**: uma linha por dúvida, com recomendação padrão e marcação **BLOQUEANTE** quando impedir uma tarefa. Inclua:
      - Dúvidas de extração (texto truncado, mensagem repetida).
      - Dúvidas de pai e ocorrência de campos (NT x XSD).
      - Dúvidas de escopo do emissor (tipos de emissão, perfis, clientes).
      - Checklist de informações que o analista precisa enviar.
   4. **O que muda**: campos (tag, pai, tipo, ocorrência, tamanho, quando enviar, fonte), regras (cStat, efeito, aplicação, resumo, situação), eventos (tpEvent, autor, schema), itens excluídos. Separe por modelo quando aplicável.
   5. **O que o sistema deve enviar**: matriz por situação ou por tipo de documento. Nunca invente a matriz: se a NT não traz, escreva `NAO ENCONTRADO NAS FONTES`.
   6. **Cuidados**: armadilhas (datas, homologação x produção, remoções, cor de texto, validação de XSD antes das regras).
   7. **Ordem de implementação**: fases ligadas aos prazos, mais urgente primeiro. Cada item cita a tarefa T.
   8. **Tarefas para desenvolvedores (T01...)**: escopo, critério de aceite verificável, "depende de" (P ou T).
   9. **Dúvidas em aberto**: lista dos P marcados. Registrar em `docs/duvidas-abertas.md` só depois de respondidas.
   10. **Fontes**: uma linha por fonte, com documento, NT ou XSD, versão, página ou seção, marcação e selo **oficial** ou **não oficial**.

8. **Verificar**: rode `date` de novo se a sessão for longa. Confirme que todo campo, regra e cStat do
   documento aparece no JSON ou no PDF. Se não aparecer, troque por `NAO ENCONTRADO NAS FONTES`.

## Regras

- **Não invente** campo, regra, cStat, data, alíquota ou tag. Sem fonte: `NAO ENCONTRADO NAS FONTES` e pré-tarefa.
- **Hierarquia de fontes**: PDF e XSD prevalecem sobre o JSON. O JSON é índice. Contradição: mostre as duas, registre em `docs/duvidas-abertas.md` depois de o analista confirmar.
- **`fontes/` é só leitura.** Não edite, crie nem copie nada lá.
- **Não faça commit** (AGENTS.md, regra 12).
- **Audiência**: o documento é para o analista e o time de desenvolvimento. Não escreva a linha de audiência dentro dele. Escreva-a na mensagem de resposta, na forma `Written for: ...`.
- **Cor não prova revisão**: cruze a marcação com a seção "Descrição das alterações".
- **Não use `catalogo/campos` ou `catalogo/regras`**: esses catálogos podem não existir. Se não existirem, avise no documento.
- Dados do usuário (projetos, e-mail, nome) não entram no documento.

## Resposta final (no chat)

Em até 6 linhas:
1. Caminho do documento gerado (caminho completo).
2. Quantas pré-tarefas são BLOQUEANTE e quais são.
3. Quantas tarefas T foram geradas.
4. Itens com `NAO ENCONTRADO NAS FONTES` (se houver).
5. Próxima ação para o analista: responder as bloqueantes.

Se o arquivo de destino já existir, pergunte antes de sobrescrever.
