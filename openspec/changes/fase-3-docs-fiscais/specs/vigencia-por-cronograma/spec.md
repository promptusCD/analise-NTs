# Spec Delta

## Purpose

Calcular a situação de vigência de cada item de uma NT a partir da data de hoje e do cronograma literal extraído, sem digitar a situação nem inventar datas.

## ADDED Requirements

### Requirement: Situação calculada pela data de hoje
O sistema SHALL calcular a situação de vigência de cada linha do cronograma comparando a data de hoje com as datas de homologação e produção. A situação MUST ser uma de: `futura`, `em_homologacao`, `prazo_homologacao_encerrado`, `em_producao`, `excluida`. A situação MUST NOT ser armazenada em arquivo.

#### Scenario: Antes da homologação
- **WHEN** hoje é anterior à data de homologação da linha
- **THEN** a situação é `futura`

#### Scenario: Em homologação
- **WHEN** hoje é igual ou posterior à homologação e anterior à produção
- **THEN** a situação é `em_homologacao`

#### Scenario: Em produção
- **WHEN** hoje é igual ou posterior à data de produção
- **THEN** a situação é `em_producao`

#### Scenario: Item excluído
- **WHEN** o item está marcado como EXCLUIDO
- **THEN** a situação é `excluida`, independentemente das datas

### Requirement: Datas literais preservadas
O sistema SHALL guardar e exibir as datas do cronograma exatamente como extraídas. Valores não interpretáveis como data (por exemplo "Até 05/10/2026") MUST ser exibidos literalmente e MUST NOT ser reinterpretados.

#### Scenario: Texto no lugar da data
- **WHEN** o campo de produção contém texto que não é uma data simples
- **THEN** o texto é exibido literal e a situação é informada como `indeterminada`, sem calcular data

#### Scenario: Data ausente
- **WHEN** a linha não tem data de homologação ou de produção
- **THEN** o sistema não preenche data, e a situação só é calculada com o que existe

### Requirement: Múltiplas linhas por versão
O sistema SHALL tratar cada linha do cronograma como um item independente, pois a mesma versão de NT pode ter várias linhas.

#### Scenario: Versão com duas linhas
- **WHEN** uma NT tem duas linhas para a versão 1.00 com datas diferentes
- **THEN** cada linha recebe sua própria situação e as duas aparecem na saída

### Requirement: Módulo compartilhado
O cálculo de vigência SHALL ser exposto como módulo reutilizável, importável por qualquer script do projeto (gerador de documentos, verificador e futuro calendário). Para a mesma data de hoje e o mesmo cronograma, todos os consumidores MUST obter o mesmo resultado.

#### Scenario: Mesmo resultado em consumidores diferentes
- **WHEN** o gerador de documentos e o verificador calculam a situação da mesma linha com a mesma data
- **THEN** as situações são idênticas

#### Scenario: Data de hoje injetável
- **WHEN** o consumidor informa uma data de hoje explícita
- **THEN** o cálculo usa essa data e não o relógio do sistema
