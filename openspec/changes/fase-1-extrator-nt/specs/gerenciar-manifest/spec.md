## Purpose

Atualizar o status de ingestao no manifest.yaml, controlando o ciclo de vida de cada fonte: pendente -> extraida -> revisada.

## ADDED Requirements

### Requirement: Atualizar status para extraida
O sistema SHALL mudar o campo `status_ingestao` de `pendente` para `extraida` no manifest.yaml quando uma NT e processada com sucesso.

#### Scenario: NT processada com sucesso
- **WHEN** `extrair_nt.py` gera JSON e MD com sucesso para uma NT
- **THEN** o manifest.yaml e atualizado: `status_ingestao: extraida` para essa NT

### Requirement: Identificar NT no manifest por arquivo
O sistema SHALL identificar qual entrada do manifest corresponde ao arquivo processado, comparando o caminho do arquivo.

#### Scenario: Matching por caminho
- **WHEN** o arquivo `fontes/nfe/notas-tecnicas/NT_2026_007_v1.10.pdf` e processado
- **THEN** o manifest atualiza a entrada cujo campo `arquivo` corresponde

### Requirement: Nao alterar outros campos do manifest
O sistema SHALL alterar apenas o campo `status_ingestao`, preservando todos os outros campos (id, documento, tipo, nt, versao, titulo, arquivo, sha256, confianca).

#### Scenario: Preservacao de campos
- **WHEN** o manifest e atualizado
- **THEN** os campos `id`, `documento`, `tipo`, `nt`, `versao`, `titulo`, `arquivo`, `sha256`, `confianca` permanecem inalterados

### Requirement: Atualizar MOCs no manifest
O sistema SHALL criar entradas no manifest para MOCs processados que ainda nao estao registrados.

#### Scenario: MOC nao registrado
- **WHEN** um MOC e processado e nao existe entrada correspondente no manifest
- **THEN** uma nova entrada e criada com `tipo: moc` e `status_ingestao: extraida`

### Requirement: Calcular SHA256 ao atualizar manifest
O sistema SHALL recalcular o SHA256 do arquivo ao atualizar o manifest, para garantir integridade.

#### Scenario: SHA256 atualizado
- **WHEN** o manifest e atualizado
- **THEN** o campo `sha256` contem o hash atual do arquivo (pode ter mudado se o arquivo foi substituido)