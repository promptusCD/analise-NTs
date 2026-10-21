---
description: Conferir se tags, cStat e campos de uma NT aparecem nos projetos backEnd/frontEnd do usuário (busca por chave, somente leitura)
argument-hint: <NT, ex. 2026.004 ou NT-CT-e-2026.004> [id do projeto]
allowed-tools: Read, Grep, Glob, Bash(date:*), Bash(ls:*)
---

# /fiscal-compatibilidade

**Argumentos**: $ARGUMENTS (1º = NT; 2º, opcional = `id` de um projeto de `projetos.yaml`)

Responda **só no chat**: não crie relatório nem qualquer arquivo. Os projetos do usuário são
**SOMENTE LEITURA** (regra 13 do AGENTS.md): use apenas Read/Grep/Glob neles; nunca edite, mova, apague
nem copie código deles para este repositório.

## Fluxo

1. Rode `date` (ou `Get-Date`) e guarde a data de hoje.
2. **Projetos**: leia `projetos.yaml` na raiz.
   - Não existe: oriente `cp projetos.exemplo.yaml projetos.yaml`, ajustar os caminhos e rodar de novo.
     Pare aqui; não procure projetos em outros lugares.
   - Entrada sem `id`, `tipo` ou `caminho`, ou com `tipo` fora de `backend|frontend`: aponte a entrada
     inválida e siga com as demais.
   - Foi informado um `id`: analise só ele. Se não existir, liste os `id` disponíveis e pare.
   - `caminho` inexistente (confira com `ls`): avise e siga com os outros projetos.
3. **NT**: normalize o argumento (`NT-CT-e-2026.004`, `CTe NT 2026.004`, `2026.004` → número + documento)
   e localize em `catalogo/nt/<doc>/` os arquivos `*_<AAAA>_<NNN>_*`. Mais de uma versão: use a mais recente
   e diga qual. Ambiguidade real entre documentos: pergunte. Não achou: `NAO ENCONTRADO NAS FONTES` e
   sugerir `/fiscal-ingerir-nt`. Não invente chaves.
4. **Filtro por documento**: pule, informando o motivo, projeto cujo `documentos` não inclui o documento da NT.
5. **Chaves a procurar** (siga a skill **resumo-impacto-dev** e o catálogo; MOC/XSD só para conferir):
   - **backend**: tags/campos do schema, `cStat` de rejeição (e `id_unico`/`id` da regra), eventos
     (`tpEvento`, schema).
   - **frontend**: campos exibidos ou digitados (nome do campo/rótulo e a tag quando aparecer na
     tela/payload) e itens dos Anexos II (DANFE/DACTE/DAMDFE). **Não cobre `cStat` de rejeição.**
   - Item marcado **EXCLUÍDO** na NT vira "remoção a conferir" (procurar o que deveria sair), nunca exigência.
   - Para cada chave guarde: tipo, NT/versão/página, marcação e situação de vigência (futura /
     em_homologacao / em_producao / excluida) com a data de hoje; datas literais ("Até 05/10/2026") não
     se reinterpretam.
6. **Varredura por chave** em cada projeto aplicável:
   - Grep antes de Read; respeite `incluir` (se informado) e `ignorar` (se informado; senão `.git`,
     `node_modules`, `target`, `build`, `dist`, `bin`, `obj`). Use as `dicas` para escolher onde procurar.
   - Procure a tag/nome (com e sem `<>`), o `cStat` numérico próximo de contexto de validação/rejeição e o
     nome do evento. Registre `arquivo:linha`; leia só o mínimo para confirmar que a ocorrência é da chave.
   - Classifique cada item como **encontrado em `arquivo:linha`** ou **não encontrado por busca**.
     "Não encontrado" **não prova ausência** (constante, configuração, código gerado): avise e sugira
     `dicas` em `projetos.yaml`.
   - **Não julgue a lógica.** Se o usuário quiser saber se a regra está correta no código dele, diga que
     isso se pede direto à IA, fora deste command (ex.: "a regra 539 está implementada corretamente?").
7. **Citação**: cite as duas pontas, a NT/MOC/XSD (versão, página, marcação) e os `arquivo:linha` do
   projeto. Trechos de código só se mínimos e necessários.

## Formato (obrigatório, padrão do AGENTS.md)

```
[RESUMO - 2-3 linhas: quantos itens, quantos encontrados / não encontrados por projeto]

[DETALHE] por projeto (id, tipo, caminho)
- Item (campo/regra/evento) | cStat | NT de origem (NT vX, pág. N) | Marcação | Situação (+ data de hoje)
  -> encontrado em arquivo:linha  |  não encontrado por busca
- Projetos pulados / caminhos inexistentes / entradas inválidas

[IMPACTO NO EMISSOR]
- O que parece faltar (priorize por vigência: em_homologacao/futura com data mais próxima primeiro)

[FONTES]
- <documento> - <NT/MOC/XSD> v<versão> - pág. <N> - <marcação>
- <id do projeto>: arquivo:linha (um por ocorrência citada)
```

Resposta sem "Fontes" é inválida (`ERRO_SEM_CITACAO`).
