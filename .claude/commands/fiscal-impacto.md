---
description: Gerar checklist de implementação para o time de desenvolvimento a partir de uma NT (campos, regras, rejeições, eventos, datas)
argument-hint: <NT, ex. 2026.004 ou NT-CT-e-2026.004> [versão]
---

# /fiscal-impacto

**Argumentos**: $ARGUMENTS

## Fluxo

1. Rode `date`.
2. **Localizar a NT**: normalize o argumento (`NT-CT-e-2026.004`, `CTe NT 2026.004`, `2026.004` → número
   `2026.004` + documento) e busque em `catalogo/nt/<doc>/` arquivos `*_<AAAA>_<NNN>_*`
   (ex.: `CTe_NT_2026_004_v1.00.json`). Mais de uma versão: use a mais recente e diga qual; ambiguidade
   real (documentos diferentes com o mesmo número): pergunte. Não achou: `NAO ENCONTRADO NAS FONTES`
   e sugerir `/fiscal-ingerir-nt`.
3. Siga a skill **resumo-impacto-dev** (formato, fontes, comparação entre versões e fallback quando
   `catalogo/campos|regras` e `calendario.yaml` não existem).
4. Regras: use `cStat` e `id_unico` como chave (em CT-e o `id` repete entre tabelas e pode ser vazio) e a
   `mensagem` completa. O `cronograma[]` traz uma linha por implantação (`homologacao`, `producao`, `descricao`)
   com literais como "Até 05/10/2026"; datas de "bloco" que estão só em observações de regras não entram no
   `cronograma[]` — leia-as nas notas da regra (skill `atualizar-calendario`).
5. Termine **sempre** com `FONTES` e a situação (com a data de hoje) de cada bloco de datas.

O resultado deve ser pronto para virar tarefas em Jira/Linear/Asana (um item = uma tarefa).
