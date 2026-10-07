## Purpose

Command que executa o pipeline completo: organizar `entrada/` -> `fontes/`, extrair JSON de NTs e MOCs, atualizar manifest, atualizar catalogo. Suporta opcao `--etapa N` para executar etapas individuais.

## ADDED Requirements

### Requirement: Pipeline completo
O sistema SHALL executar o pipeline completo quando o usuario executa `/fiscal-processar` sem argumentos.

#### Scenario: Execucao completa
- **WHEN** o usuario executa `/fiscal-processar`
- **THEN** o sistema executa todas as etapas em sequencia: organizar entrada/, extrair NTs, extrair MOCs, atualizar manifest, verificar resultado

### Requirement: Execucao por etapa
O sistema SHALL permitir executar etapas individuais com `--etapa N`.

#### Scenario: Etapa 1 - Organizar
- **WHEN** o usuario executa `/fiscal-processar --etapa 1`
- **THEN** o sistema so executa a etapa de organizar `entrada/` -> `fontes/`

#### Scenario: Etapa 2 - Extrair NTs
- **WHEN** o usuario executa `/fiscal-processar --etapa 2`
- **THEN** o sistema so executa a etapa de extrair NTs (JSON)

#### Scenario: Etapa 3 - Extrair MOCs
- **WHEN** o usuario executa `/fiscal-processar --etapa 3`
- **THEN** o sistema so executa a etapa de extrair MOCs (JSON)

#### Scenario: Etapa 4 - Atualizar manifest
- **WHEN** o usuario executa `/fiscal-processar --etapa 4`
- **THEN** o sistema so executa a etapa de atualizar manifest.yaml

#### Scenario: Etapa 5 - Verificar resultado
- **WHEN** o usuario executa `/fiscal-processar --etapa 5`
- **THEN** o sistema so executa a etapa de verificar resultado e mostrar estatisticas

### Requirement: Identificacao automatica de arquivos
O sistema SHALL identificar automaticamente o tipo e documento fiscal de cada arquivo em `entrada/`.

#### Scenario: Identificacao de NT
- **WHEN** o arquivo e `CTe_NT_2026_004_v1.00.pdf`
- **THEN** o sistema identifica como NT do CT-e e move para `fontes/cte/notas-tecnicas/`

#### Scenario: Identificacao de MOC
- **WHEN** o arquivo e `MOC_CTe_VisaoGeral_v4.00.pdf`
- **THEN** o sistema identifica como MOC do CT-e e move para `fontes/cte/moc/`

### Requirement: Verificacao de duplicatas
O sistema SHALL verificar duplicatas antes de mover arquivos.

#### Scenario: Arquivo duplicado
- **WHEN** o arquivo ja existe em `fontes/` com o mesmo SHA256
- **THEN** o sistema remove de `entrada/` sem mover

### Requirement: Relatorio final
O sistema SHALL exibir relatorio final com estatisticas.

#### Scenario: Relatorio de execucao
- **WHEN** o pipeline e concluido
- **THEN** o sistema exibe: arquivos organizados, NTs extraidas, MOCs extraidos, manifest atualizado