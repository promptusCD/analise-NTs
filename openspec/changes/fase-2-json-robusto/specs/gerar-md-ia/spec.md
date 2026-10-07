## Purpose

Workflow para IA gerar MD a partir do JSON. A IA le o JSON estruturado e gera MD legivel com formatacao inteligente (bullets, destaque de campos, datas, alteracoes).

## ADDED Requirements

### Requirement: IA gera MD a partir do JSON
O sistema SHALL permitir que a IA gere MD a partir do JSON estruturado.

#### Scenario: Command para gerar MD
- **WHEN** o usuario executa `/gerar-md <nt>` ou `/gerar-md <moc>`
- **THEN** a IA le o JSON correspondente e gera MD legivel

### Requirement: Formatacao inteligente
O sistema SHALL gerar MD com formatacao inteligente.

#### Scenario: Tabelas como bullets
- **WHEN** o JSON contem secao do tipo "tabela"
- **THEN** o MD mostra cada linha como bullet com campo em destaque

#### Scenario: Regras destacadas
- **WHEN** o JSON contem secao do tipo "regras"
- **THEN** o MD mostra cada regra como bullet com ID, cStat e mensagem destacados

#### Scenario: Datas destacadas
- **WHEN** o JSON contem datas no formato DD/MM/YYYY
- **THEN** o MD mostra datas em negrito

### Requirement: Fluxo de trabalho atualizado
O sistema SHALL atualizar o fluxo de trabalho do usuario.

#### Scenario: Novo fluxo de extracao
- **WHEN** o usuario executa `/ingerir-nt <arquivo>`
- **THEN** o sistema extrai JSON robusto e a IA gera MD automaticamente

#### Scenario: Regenerar MD
- **WHEN** o usuario executa `/gerar-md <nt>` para NT ja extraida
- **THEN** a IA regenera o MD a partir do JSON existente

### Requirement: Documentacao atualizada
O sistema SHALL atualizar a documentacao com o novo fluxo.

#### Scenario: README atualizado
- **WHEN** a documentacao e atualizada
- **THEN** o README.md mostra o novo fluxo de trabalho (extrair JSON -> IA gera MD)