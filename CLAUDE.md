@AGENTS.md

# Notas específicas do Claude Code

- Commands em `.claude/commands/` (`/fiscal-*` e `/opsx:*`), skills em `.claude/skills/`.
  A pasta `.opencode/` é a configuração antiga (OpenCode) e fica só como referência histórica.
- `.claude/` é a fonte dos commands/skills fiscais; após editar, rode `npm run sincronizar-ia` (espelha em `.opencode/`, usado por quem não tem Claude).
- Ambiente é Windows: **use `python` (não `python3`, que cai no stub da Microsoft Store)**
  e `node`. Dependências Python em `requirements.txt` (`pip install -r requirements.txt`);
  rode `/fiscal-diagnostico` se algo falhar.
- `fontes/` é só-organização: a IA NUNCA edita/cria/copia ali (Edit/Write negados em `.claude/settings.json`);
  só move (`mv`) o que o usuário colocou em `entrada/`.
- `git commit`/`git push` pedem confirmação (regra 12 do AGENTS.md: não commitar sem o usuário pedir).
- Hoje é obtido com `date` (Bash) ou `Get-Date` (PowerShell) — nunca assuma a data.
- Fluxos de mudança do projeto usam OpenSpec (`/opsx:propose`, `/opsx:apply`, `/opsx:archive`).
