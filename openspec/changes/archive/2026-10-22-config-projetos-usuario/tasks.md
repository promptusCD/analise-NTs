# Tasks

## 1. Configuração dos projetos

- [x] 1.1 Criar `projetos.exemplo.yaml` com os campos `id`, `tipo`, `caminho`, `documentos`, `ignorar`, `incluir`, `dicas`, um exemplo de backEnd e um de frontEnd, e comentários sobre permissões locais (`settings.local.json`). Verificar: `python -c "import yaml; yaml.safe_load(open('projetos.exemplo.yaml', encoding='utf-8'))"` roda sem erro.
- [x] 1.2 Adicionar `projetos.yaml` ao `.gitignore`. Verificar: após copiar o exemplo para `projetos.yaml`, `git status` não o lista, e `git check-ignore projetos.yaml` imprime o nome do arquivo.
- [x] 1.3 Documentar em `docs/REFERENCIA.md` o arquivo de projetos, os campos, o fluxo (copiar o exemplo) e a configuração local de permissões. Verificar: a seção existe e todos os campos do template estão descritos.

## 2. Regra de somente leitura

- [x] 2.1 Adicionar ao `AGENTS.md` regra nova: projetos listados em `projetos.yaml` são somente leitura, sem cópia de código para o repositório, citando só `arquivo:linha` (e mencionar o novo command no contexto). Verificar: a regra aparece numerada após as existentes sem renumerar as anteriores (a regra 12 continua sendo a de ingestão) e `CLAUDE.md` continua importando o `AGENTS.md`.

## 3. Command `/fiscal-compatibilidade`

- [x] 3.1 Criar `.claude/commands/fiscal-compatibilidade.md` (frontmatter com `description`, `argument-hint` e `allowed-tools` somente de leitura) com o fluxo: ler `projetos.yaml` (tratar ausência, entrada inválida e caminho inexistente), resolver a NT como no `/fiscal-impacto`, `date`, filtrar por `documentos`, extrair chaves do catálogo, tratar EXCLUÍDO como remoção. Verificar: o arquivo cobre cada cenário das specs `projetos-usuario-config` e `compatibilidade-nt-projeto`.
- [x] 3.2 No mesmo command, descrever a varredura por chave (Grep antes de Read, respeitando `incluir`/`ignorar`/`dicas`), os critérios por tipo (backend x frontend), a classificação "encontrado em `arquivo:linha`" x "não encontrado por busca", o aviso de que não é prova de ausência, o formato de resposta do `AGENTS.md` com vigência e "Fontes" nas duas pontas, e a orientação de pedir validação de lógica diretamente à IA. Verificar: revisão contra os requisitos "Verificação por busca de chave", "Critérios por tipo de projeto" e "Resposta em chat com vigência e fontes".
- [x] 3.3 Rodar `npm run sincronizar-ia` e depois `node scripts/js/sincronizar_ia.js --check`. Verificar: o espelho `.opencode/commands/fiscal-compatibilidade.md` existe e o `--check` termina sem divergência.

## 4. Verificação integrada

- [x] 4.1 Com um `projetos.yaml` local apontando para uma pasta de teste temporária (backend e frontend fictícios com uma tag e um `cStat` de uma NT já ingerida), rodar `/fiscal-compatibilidade <NT>`. Verificar: a resposta indica "encontrado" com `arquivo:linha` para o que existe, "não encontrado por busca" para o resto, traz vigência com a data de hoje e "Fontes" nas duas pontas, e nenhum arquivo novo aparece em `git status` além dos desta change.
- [ ] 4.2 Testar os casos de borda: sem `projetos.yaml`, `id` inexistente, caminho inexistente entre dois projetos, `documentos` incompatível com a NT e NT não ingerida. Verificar: cada caso produz a mensagem prevista nas specs, sem abortar os demais projetos.
- [x] 4.3 Rodar `openspec validate config-projetos-usuario --strict`. Verificar: termina sem erros.
