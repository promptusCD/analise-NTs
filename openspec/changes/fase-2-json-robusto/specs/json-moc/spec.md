## Purpose

Estrutura JSON robusta para MOCs (Manuais de Orientacao do Contribuinte). Inclui hierarquia de secoes, regras de validacao extraidas, campos do leiaute, e metadados completos.

## ADDED Requirements

### Requirement: JSON com hierarquia de secoes
O sistema SHALL gerar JSON com secoes hierarquicas (1, 1.1, 1.1.1).

#### Scenario: Secao com subsecoes
- **WHEN** o MOC contem "1 Introducao" e "1.1 Objetivo"
- **THEN** o JSON contem secao `numero: "1"` com `subsecoes[]` incluindo `numero: "1.1"`

### Requirement: Regras de validacao extraidas
O sistema SHALL extrair regras de validacao do MOC.

#### Scenario: Regra com ID e cStat
- **WHEN** o MOC contem tabela de regras com ID, cStat, descricao
- **THEN** o JSON contem `regras_validacao[]` com `id`, `cStat`, `descricao`, `modelo`, `aplicacao`

### Requirement: Campos do leiaute extraidos
O sistema SHALL extrair campos do leiaute do MOC.

#### Scenario: Campo com tag e tipo
- **WHEN** o MOC contem tabela de campos com tag, tipo, ocorrencia
- **THEN** o JSON contem `campos_leiaute[]` com `tag`, `tipo`, `ocorrencia`, `descricao`

### Requirement: Metadados completos
O sistema SHALL incluir metadados completos no JSON.

#### Scenario: Metadados do MOC
- **WHEN** o MOC e processado
- **THEN** o JSON contem `documento`, `versao`, `tipo_documento: "MOC"`, `arquivo_origem`, `sha256`, `extraido_em`

### Requirement: Suportar PDF e DOCX
O sistema SHALL processar tanto PDFs quanto DOCXs de MOCs.

#### Scenario: MOC em DOCX
- **WHEN** o arquivo e `MOC_MDFe_Anexo_II_DAMDFE_v3.00b.docx`
- **THEN** o sistema extrai usando python-docx e gera JSON