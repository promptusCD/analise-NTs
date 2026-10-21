# Spec Delta

## Purpose

Permitir que cada usuário declare, em arquivo local, os caminhos dos seus projetos backEnd e frontEnd que a IA pode consultar para conferir compatibilidade com NTs/MOCs, garantindo que esses projetos sejam acessados apenas para leitura.

## ADDED Requirements

### Requirement: Arquivo de configuração local de projetos
O sistema SHALL ler os projetos do usuário de `projetos.yaml` na raiz do repositório. O arquivo MUST estar no `.gitignore` e MUST NOT ser versionado.

#### Scenario: Arquivo ignorado pelo git
- **WHEN** o usuário cria `projetos.yaml` com caminhos da sua máquina
- **THEN** `git status` não o lista como arquivo a versionar

#### Scenario: Arquivo ausente
- **WHEN** um fluxo que depende dos projetos roda e `projetos.yaml` não existe
- **THEN** a IA orienta copiar `projetos.exemplo.yaml` para `projetos.yaml` e não procura projetos em outros lugares

### Requirement: Template versionado
O sistema SHALL fornecer `projetos.exemplo.yaml` versionado, com comentários explicando cada campo e um exemplo de backEnd e de frontEnd.

#### Scenario: Template cobre os campos
- **WHEN** o usuário abre `projetos.exemplo.yaml`
- **THEN** encontra `id`, `tipo` (`backend` ou `frontend`), `caminho`, `documentos`, `ignorar`, `incluir` (opcional) e `dicas` (opcional), cada um comentado

#### Scenario: Orientação de permissões locais
- **WHEN** o usuário lê os comentários do template
- **THEN** vê como bloquear escrita e liberar leitura dos caminhos no `.claude/settings.local.json`, sem alterar o `settings.json` versionado

### Requirement: Campos de cada projeto
Cada projeto MUST informar `id` único, `tipo` e `caminho`. O campo `documentos` SHALL restringir a análise aos documentos fiscais indicados (`nfe`, `cte`, `mdfe`); sem ele, todos se aplicam.

#### Scenario: Projeto restrito a um documento
- **WHEN** um projeto declara `documentos: [nfe]` e a análise é de uma NT de MDF-e
- **THEN** esse projeto é pulado e a resposta informa o motivo

#### Scenario: Entrada inválida
- **WHEN** um projeto não tem `id`, `tipo` ou `caminho`, ou `tipo` não é `backend` nem `frontend`
- **THEN** a IA aponta a entrada inválida e segue com as demais

### Requirement: Caminho inexistente não interrompe a análise
O sistema SHALL tratar um `caminho` que não existe como aviso, sem abortar a análise dos outros projetos.

#### Scenario: Um caminho quebrado entre vários
- **WHEN** dois projetos estão configurados e o caminho de um deles não existe
- **THEN** a resposta avisa sobre o caminho inexistente e analisa o outro projeto normalmente

### Requirement: Projetos do usuário são somente leitura
A IA MUST NOT criar, editar, mover, copiar para dentro, nem apagar arquivos dos projetos configurados. O `AGENTS.md` SHALL registrar essa regra e as respostas MUST NOT reproduzir trechos extensos do código do usuário.

#### Scenario: Pedido de alteração no projeto do usuário
- **WHEN** durante a análise de compatibilidade a IA identifica algo a corrigir no projeto do usuário
- **THEN** ela apenas descreve o ajuste necessário e não altera nenhum arquivo do projeto

#### Scenario: Nada do projeto é copiado para o repositório
- **WHEN** a análise termina
- **THEN** nenhum arquivo ou trecho de código do projeto do usuário foi gravado em `catalogo/`, `docs/` ou qualquer outra pasta deste repositório
