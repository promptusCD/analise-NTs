# Spec Delta

## Purpose

Informar, a partir de uma NT/MOC/XSD do catálogo, quais tags, cStat e campos já aparecem nos projetos do usuário e quais não foram encontrados, por busca de chaves, com resposta no chat e fontes citadas nas duas pontas.

## ADDED Requirements

### Requirement: Command de compatibilidade
O sistema SHALL oferecer `/fiscal-compatibilidade <NT> [projeto]`. Sem `projeto`, analisa todos os projetos de `projetos.yaml` aplicáveis ao documento da NT; com `projeto`, analisa só o `id` informado.

#### Scenario: Análise de todos os projetos
- **WHEN** o usuário roda `/fiscal-compatibilidade 2026.004` e há um backEnd e um frontEnd configurados para CT-e
- **THEN** a resposta cobre os dois projetos

#### Scenario: Projeto específico
- **WHEN** o usuário roda `/fiscal-compatibilidade 2026.004 erp-backend`
- **THEN** somente o projeto `erp-backend` é analisado

#### Scenario: Projeto inexistente
- **WHEN** o `id` informado não está em `projetos.yaml`
- **THEN** a resposta lista os ids disponíveis e não analisa nada

### Requirement: Extração das chaves a partir do catálogo
O sistema SHALL obter as chaves a procurar (tags/campos, `cStat`, eventos) do catálogo da NT, MOC e XSD. Se a NT não for encontrada, MUST responder `NAO ENCONTRADO NAS FONTES` e sugerir ingestão, sem inventar chaves.

#### Scenario: NT ingerida
- **WHEN** a NT existe em `catalogo/nt/<doc>/`
- **THEN** as chaves vêm dos campos e regras dessa NT, e itens marcados como EXCLUÍDO são tratados como remoção, nunca como exigência

#### Scenario: NT não ingerida
- **WHEN** a NT informada não está no catálogo
- **THEN** a resposta é `NAO ENCONTRADO NAS FONTES` com sugestão de `/fiscal-ingerir-nt`

### Requirement: Verificação por busca de chave
O sistema SHALL procurar cada chave nos caminhos do projeto (respeitando `incluir`, `ignorar` e `dicas`) e classificar o resultado como "encontrado em `arquivo:linha`" ou "não encontrado por busca". "Não encontrado" MUST NOT ser apresentado como prova de ausência.

#### Scenario: Chave encontrada
- **WHEN** a tag ou o `cStat` aparece no projeto
- **THEN** o item é listado como encontrado com ao menos um `arquivo:linha`

#### Scenario: Chave não encontrada
- **WHEN** nenhuma ocorrência é achada
- **THEN** o item é listado como "não encontrado por busca", com aviso de que pode estar em constante, configuração ou código gerado

#### Scenario: Validação de lógica fora do escopo
- **WHEN** o usuário quer saber se a regra está corretamente implementada
- **THEN** o command não faz esse julgamento e orienta pedir a verificação diretamente à IA

### Requirement: Critérios por tipo de projeto
A análise de projeto `backend` SHALL priorizar tags/schema, `cStat` de rejeição e eventos. A de projeto `frontend` SHALL priorizar campos exibidos ou digitados e itens de DANFE/DACTE/DAMDFE dos Anexos II.

#### Scenario: Backend
- **WHEN** o projeto é `backend` e a NT cria uma regra com `cStat`
- **THEN** o `cStat` entra nas chaves procuradas

#### Scenario: Frontend
- **WHEN** o projeto é `frontend` e a NT altera um campo do leiaute
- **THEN** o nome do campo ou rótulo entra nas chaves procuradas, e `cStat` de rejeição não é cobrado

### Requirement: Resposta em chat com vigência e fontes
O sistema SHALL responder apenas no chat, sem criar arquivo de relatório. A resposta MUST seguir o formato padrão do `AGENTS.md`, informar a situação de vigência de cada item com a data de hoje e terminar com "Fontes" citando a NT/MOC/XSD e os `arquivo:linha` do projeto.

#### Scenario: Nenhum arquivo gerado
- **WHEN** a análise termina
- **THEN** nenhum arquivo novo foi criado no repositório

#### Scenario: Fontes nas duas pontas
- **WHEN** a resposta é exibida
- **THEN** a seção "Fontes" cita a NT/MOC/XSD (versão, página) e os caminhos `arquivo:linha` do projeto do usuário

#### Scenario: Vigência informada
- **WHEN** um item pertence a regra futura ou em homologação
- **THEN** a resposta mostra a situação e a data de hoje, para o usuário priorizar o que falta
