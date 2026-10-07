## Purpose

Estrutura JSON robusta para NTs fiscais. Inclui secoes tipificadas (tabela, regras, texto), tabelas com cabecalho e linhas estruturadas, regras de validacao identificadas, cronograma, e metadados completos.

## ADDED Requirements

### Requirement: JSON com secoes tipificadas
O sistema SHALL gerar JSON com secoes classificadas por tipo (tabela, regras, texto).

#### Scenario: Secao de tabela
- **WHEN** a NT contem uma tabela de campos (ex: leiaute do imposto)
- **THEN** o JSON contem secao com `tipo: "tabela"`, `cabecalho[]` e `linhas[]`

#### Scenario: Secao de regras
- **WHEN** a NT contem regras de validacao (ex: "001 Se CST...")
- **THEN** o JSON contem secao com `tipo: "regras"` e `regras[]` com id, aplicacao, cStat, efeito, mensagem

#### Scenario: Secao de texto
- **WHEN** a NT contem texto corrido (ex: introducao)
- **THEN** o JSON contem secao com `tipo: "texto"` e `paragrafos[]`

### Requirement: Tabelas com estrutura completa
O sistema SHALL extrair tabelas com cabecalho e linhas estruturadas.

#### Scenario: Tabela de campos
- **WHEN** a NT contem tabela com colunas #, Campo, Ele, Pai, Tipo, Ocor., Tam., Descricao
- **THEN** o JSON contem `cabecalho` com os nomes das colunas e `linhas[]` com objetos cujos campos correspondem ao cabecalho

### Requirement: Regras de validacao identificadas
O sistema SHALL extrair regras de validacao com campos estruturados.

#### Scenario: Regra completa
- **WHEN** a NT contem "001 Se CST do IBS/CBS for informado... Obrig. 311 Rej."
- **THEN** o JSON contem regra com `id: "001"`, `aplicacao: "Obrig."`, `cStat: "311"`, `efeito: "Rej."`, `mensagem: "..."`, `condicao: "..."`

### Requirement: Cronograma com datas literais
O sistema SHALL extrair cronograma mantendo datas literais.

#### Scenario: Data com "Ate"
- **WHEN** o cronograma contem "Ate 05/10/2026"
- **THEN** o JSON armazena `"homologacao": "Ate 05/10/2026"` (literal, nao convertido)

### Requirement: Metadados completos
O sistema SHALL incluir metadados completos no JSON.

#### Scenario: Metadados da NT
- **WHEN** a NT e processada
- **THEN** o JSON contem `nt`, `versao`, `documento`, `titulo`, `arquivo_origem`, `sha256`, `extraido_em`, `tipo_documento: "NT"`

### Requirement: Estatisticas de extracao
O sistema SHALL incluir estatisticas no JSON.

#### Scenario: Estatisticas por marcacao
- **WHEN** a NT e processada
- **THEN** o JSON contem `estatisticas` com `total_secoes`, `total_regras`, `total_tabelas`, `por_marcacao` (AMARELO, VERDE, EXCLUIDO, SEM_MARCA)