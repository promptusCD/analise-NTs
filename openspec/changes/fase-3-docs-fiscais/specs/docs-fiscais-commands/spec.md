# Spec Delta

## Purpose

Dar à IA commands para regenerar e validar os documentos fiscais, mantendo as regras de somente leitura das fontes e de não commitar.

## ADDED Requirements

### Requirement: Command de geração
O sistema SHALL oferecer `/fiscal-docs-gerar [nfe|cte|mdfe] [--hoje AAAA-MM-DD]`, que executa a regeneração dos blocos AUTO e informa quais blocos mudaram. Sem argumento de documento, regenera os três.

#### Scenario: Documento específico
- **WHEN** o usuário roda `/fiscal-docs-gerar cte`
- **THEN** só `CTE.md` é regenerado e o resumo lista os blocos alterados

#### Scenario: Falha de marcador
- **WHEN** o script reporta marcador inválido
- **THEN** o command mostra o erro, não edita o arquivo à mão e orienta restaurar o marcador

### Requirement: Command de validação
O sistema SHALL oferecer `/fiscal-docs-validar [nfe|cte|mdfe]`, que executa a verificação do documento contra o JSON e contra os originais e apresenta um relatório com divergências, itens não confirmados e achados já conhecidos.

#### Scenario: Relatório de validação
- **WHEN** o usuário roda `/fiscal-docs-validar`
- **THEN** a resposta traz contagens conferidas, divergências, itens `NAO CONFIRMADO NO ORIGINAL` e as fontes citadas

#### Scenario: Divergência encontrada
- **WHEN** a validação aponta divergência entre documento e JSON
- **THEN** o command indica corrigir o gerador ou o catálogo e regenerar, e registra a dúvida em `docs/duvidas-abertas.md` quando for de dado

### Requirement: Limites dos commands
Os commands MUST NOT editar conteúdo dentro de blocos AUTO, MUST NOT escrever em `fontes/` nem nos projetos de `projetos.yaml`, e MUST NOT fazer commit.

#### Scenario: Tentativa de editar bloco AUTO
- **WHEN** a correção exigiria alterar texto dentro de um bloco AUTO
- **THEN** o command altera o gerador ou o catálogo e regenera, nunca o bloco diretamente

### Requirement: Disponibilidade nas duas ferramentas
Os commands SHALL existir em `.claude/commands/` e estar espelhados em `.opencode/` pela sincronização do projeto.

#### Scenario: Espelho em sincronia
- **WHEN** a verificação de sincronização roda
- **THEN** não aponta diferença para os dois commands
