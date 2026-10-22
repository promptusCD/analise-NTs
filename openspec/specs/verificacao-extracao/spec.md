# verificacao-extracao Specification

## Purpose

Torna a qualidade da extração verificável por máquina: testes de aceite com expectativas escritas à mão a partir dos PDFs
e um script que confere qualquer JSON extraído contra o documento de origem.

## Requirements

### Requirement: Testes de aceite com expectativas golden
O repositório SHALL ter testes automatizados que comparam o JSON extraído com expectativas escritas à mão a partir dos PDFs.

#### Scenario: Golden de NTs
- **WHEN** a suíte é executada com os PDFs de `fontes/` presentes
- **THEN** os testes verificam IDs de regra, mensagens, cronograma, título e versão das NTs NF-e 2026.002/2026.007/2026.008/2026.010, CT-e 2025.001/2026.004 e MDF-e 2025.001 contra `tests/golden/*.json`

#### Scenario: PDF ausente
- **WHEN** um PDF de origem não está no repositório
- **THEN** o teste correspondente é ignorado com motivo explícito, e não aprovado em silêncio

#### Scenario: Fontes somente leitura
- **WHEN** a suíte é executada
- **THEN** nenhum arquivo em `fontes/` é criado, alterado ou apagado

### Requirement: Verificador de extração reutilizável
O sistema SHALL oferecer um script que confere um JSON extraído contra seu PDF/DOCX de origem e reporta pendências.

#### Scenario: Relatório de conferência
- **WHEN** o script é executado para uma NT
- **THEN** o relatório informa validade no schema, cobertura de texto, IDs de regra do PDF ausentes/excedentes no JSON, mensagens suspeitas de truncamento, cronograma vazio ou com valores inválidos e alertas de marcação, e termina com código de saída diferente de zero quando houver pendência bloqueante

#### Scenario: Integração com o pipeline
- **WHEN** a etapa 5 de `/fiscal-processar` é executada
- **THEN** ela roda o verificador para todos os JSONs e exibe o resumo por arquivo
