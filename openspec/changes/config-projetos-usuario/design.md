# Design

## Context

Os commands `/fiscal-*` em `.claude/commands/` são prompts em Markdown que orientam a IA a consultar
`catalogo/` e responder no formato do `AGENTS.md`. Não há script que leia projetos externos, e o
`.claude/settings.json` (versionado) só protege `fontes/`. O arquivo `manifest.yaml` já estabelece YAML como
formato de configuração. Os espelhos em `.opencode/` são gerados por `npm run sincronizar-ia`.
Motivação e escopo: ver `proposal.md`; requisitos: ver `specs/`.

## Goals / Non-Goals

**Goals:**
- Um único ponto de configuração (`projetos.yaml`) para os projetos do usuário, sem dados de máquina no git.
- Um command no mesmo estilo dos `/fiscal-*`, sem código novo de execução.
- Leitura segura: somente leitura e sem cópia de código do cliente para o repositório.

**Non-Goals:**
- Validar a lógica das regras no código do usuário (o usuário pede diretamente à IA).
- Relatório em disco, índice/script de varredura e integração com Jira/CI.
- Alterar `settings.json`, scripts Python/JS, `catalogo/` ou `fontes/`.

## Decisões

### 1. `projetos.yaml` local + `projetos.exemplo.yaml` versionado
Caminhos absolutos são específicos da máquina, então o real vai no `.gitignore` e o template é versionado.
- *Alternativa*: `projetos.yaml` versionado com caminhos relativos. Descartada: só funciona se todos
  mantiverem os projetos em pastas irmãs.
- *Alternativa*: variáveis de ambiente. Descartada: pior de documentar e não carregam `tipo`/`documentos`.

### 2. Campos do arquivo
`id`, `tipo`, `caminho`, `documentos`, `ignorar`, e opcionais `incluir` e `dicas`.
`documentos` evita varrer o código errado; `ignorar` evita estourar contexto com `node_modules`/`build`;
`dicas` em texto livre costuma valer mais que heurística automática. O template já traz `ignorar` com
padrões comuns (`.git`, `node_modules`, `target`, `build`, `dist`, `bin`, `obj`).

### 3. Só busca por chave (abordagem A)
O command faz Grep/Glob das chaves (tag XML, `cStat`, nome de campo) e reporta `arquivo:linha`.
- *Alternativa*: leitura dirigida para julgar a lógica. Fora do command: o usuário pede à IA em conversa.
- *Alternativa*: script que gera um índice (`catalogo/projetos/*.json`). Descartada: vira camada extra e
  guarda dados do cliente em disco. Reavaliar só se a varredura ficar lenta.

### 4. Command novo `/fiscal-compatibilidade`
Segue o padrão de `/fiscal-consultar`: resolve a NT (mesma normalização do `/fiscal-impacto`), roda `date`,
lê o catálogo, extrai chaves, varre, responde no formato padrão. O command declara `allowed-tools` apenas de
leitura (Read, Grep, Glob, Bash somente para `date`/`ls`).
- *Alternativa*: estender `/fiscal-impacto`. Descartada por ora: manter responsabilidades separadas;
  `/fiscal-impacto` pode apontar para o novo command depois.

### 5. Chaves por tipo de projeto
Backend: tags do schema, `cStat` de rejeição, eventos. Frontend: campos exibidos/digitados e itens dos
Anexos II (DANFE/DACTE/DAMDFE). Itens EXCLUÍDO na NT viram "remoção a conferir", nunca exigência.

### 6. Somente leitura sem tocar no `settings.json`
A regra vai no `AGENTS.md` (nova regra, análoga à 11) e no `allowed-tools` do command. Bloqueio duro e
`additionalDirectories` são por pessoa e ficam no `.claude/settings.local.json`, explicado nos comentários
de `projetos.exemplo.yaml` e em `docs/REFERENCIA.md`.
- *Alternativa*: `deny` no `settings.json` versionado. Descartada: exigiria caminhos do usuário no git.

### 7. Resposta só no chat
Evita artefato com referências ao código do cliente. O formato do `AGENTS.md` é mantido, com "Fontes" citando
NT/MOC/XSD e `arquivo:linha`.

## Riscos / Trade-offs

- [Falso negativo: regra em constante, configuração ou código gerado] → resposta diz "não encontrado por
  busca", nunca "ausente", e sugere usar `dicas`.
- [Falso positivo: a string existe mas não implementa a regra (comentário, teste)] → o command não julga
  lógica; avisa e orienta a pedir verificação direta à IA.
- [Leitura fora do repositório pede aprovação ou `additionalDirectories`] → documentado no template; é
  configuração local por pessoa.
- [Exposição de código do cliente no chat] → só `arquivo:linha` e trechos mínimos; nada gravado no repo.
- [Varredura grande consome contexto] → `ignorar`/`incluir`, Grep antes de Read, filtro por `documentos`.
- [Spec e command podem divergir] → tasks incluem checagem manual com um projeto de exemplo e
  `npm run sincronizar-ia -- --check`.
