# Proposal

## Why

O projeto responde "o que a NT/MOC diz" e "o que muda no sistema" (`/fiscal-impacto`), mas de forma
genérica: não olha o código do usuário. Quem mantém um backend/frontend de NF-e, CT-e ou MDF-e ainda
precisa conferir manualmente se cada tag, `cStat` e campo da NT já existe no seu sistema. Falta uma forma
de o usuário apontar os seus projetos e pedir à IA essa conferência.

## What Changes

- Novo arquivo de configuração local `projetos.yaml` (na raiz, **no `.gitignore`**) onde o usuário lista
  seus projetos backEnd/frontEnd (id, tipo, caminho, documentos cobertos, pastas ignoradas, dicas).
- Novo `projetos.exemplo.yaml` versionado, servindo de template e documentando o formato.
- Novo command `/fiscal-compatibilidade <NT> [projeto]` que cruza a NT/MOC/XSD do catálogo com os
  projetos configurados por **busca por chave** (tag XML, `cStat`, nome de campo) e responde **no chat**.
- Nova regra no `AGENTS.md`: projetos do usuário são **somente leitura** (análoga à regra 11 de `fontes/`).
- Sem relatório em disco e sem índice pré-gerado por script. Validar a lógica de uma regra no código do
  usuário não faz parte do command: o usuário pede diretamente à IA, fora dele.
- O `settings.json` versionado **não** recebe caminhos do usuário. Bloqueio duro de escrita e
  `additionalDirectories` ficam no `.claude/settings.local.json` de cada pessoa (documentado no exemplo).

## Capabilities

### New Capabilities
- `projetos-usuario-config`: arquivo `projetos.yaml`/`projetos.exemplo.yaml` que declara os projetos do
  usuário, seu formato, validação básica e a garantia de acesso somente leitura.
- `compatibilidade-nt-projeto`: verificação, por busca de chaves, da presença de itens de uma NT/MOC nos
  projetos configurados, via `/fiscal-compatibilidade`, com resposta em chat e citação das duas pontas.

### Modified Capabilities
<!-- Nenhuma: openspec/specs/ ainda está vazio. -->

## Impact

- Novos: `projetos.exemplo.yaml`, `.claude/commands/fiscal-compatibilidade.md`, espelho em
  `.opencode/commands/` (via `npm run sincronizar-ia`).
- Alterados: `.gitignore` (+ `projetos.yaml`), `AGENTS.md` (nova regra de somente leitura e menção ao
  command), `docs/REFERENCIA.md` (documentar o fluxo e a configuração local de permissões),
  `openspec/config.yaml` apenas se a lista de commands do contexto precisar ser atualizada (decisão do apply).
- Sem mudança em scripts Python/JS de extração, no catálogo ou em `fontes/`.
- Contexto completo do projeto: `docs/REFERENCIA.md`.
- Risco principal: leitura de pastas fora do repositório (código do cliente). Mitigado por somente leitura,
  ausência de relatório em disco e citação apenas de `arquivo:linha`.
