## Purpose

Extrair informacoes de PDFs e DOCXs de Manuais de Orientacao do Contribuinte (MOCs), gerando JSON com estrutura de secoes, regras de validacao e campos do leiaute. O MOC e o consolidado base que as NTs incrementam.

## ADDED Requirements

### Requirement: Extrair estrutura de secoes do MOC
O sistema SHALL extrair a hierarquia de secoes (cabecalhos) do MOC, mantendo numeracao e titulos.

#### Scenario: MOC com secoes numeradas
- **WHEN** o MOC contem secoes como "1. Identificacao", "2. Leiaute", "3. Regras de Validacao"
- **THEN** o JSON contem array `secoes` com objetos `{numero, titulo, pagina_inicio}`

### Requirement: Extrair regras de validacao do MOC
O sistema SHALL extrair regras de validacao do MOC (tabelas com ID, cStat, descricao), que sao a base que as NTs alteram.

#### Scenario: Tabela de regras no MOC
- **WHEN** o MOC contem tabela de regras com colunas ID, cStat, descricao
- **THEN** o JSON contem array `regras` com objetos `{id, cStat, descricao, secao}`

### Requirement: Extrair campos do leiaute do MOC
O sistema SHALL extrair campos do leiaute (tags XML) do MOC, incluindo tipo, ocorrencia e descricao.

#### Scenario: Tabela de leiaute no MOC
- **WHEN** o MOC contem tabela de campos com tag, tipo, ocorrencia
- **THEN** o JSON contem array `campos` com objetos `{tag, tipo, minOccurs, maxOccurs, descricao}`

### Requirement: Suportar PDF e DOCX
O sistema SHALL processar tanto PDFs quanto DOCXs de MOCs.

#### Scenario: MOC em PDF
- **WHEN** o arquivo e `MOC_CTe_VisaoGeral_v4.00.pdf`
- **THEN** o sistema extrai usando PyMuPDF

#### Scenario: MOC em DOCX
- **WHEN** o arquivo e `MOC_MDFe_Anexo_II_DAMDFE_v3.00b.docx`
- **THEN** o sistema extrai usando python-docx

### Requirement: Gerar JSON e MD para MOCs
O sistema SHALL gerar JSON estruturado e MD legivel para cada MOC processado.

#### Scenario: Saida do MOC
- **WHEN** o MOC e processado com sucesso
- **THEN** sao gerados `catalogo/moc/<doc>/MOC_<doc>_v<ver>.json` e `.md`

### Requirement: Detectar documento fiscal do MOC
O sistema SHALL detectar automaticamente se o MOC e de NF-e, CT-e ou MDF-e pelo nome do arquivo.

#### Scenario: MOC de CT-e
- **WHEN** o arquivo segue nomenclatura `MOC_CTe_*.pdf`
- **THEN** o campo `documento` no JSON e `CT-e`

### Requirement: Nao extrair marcacoes de cor de MOCs
O sistema SHALL NAO tentar detectar marcacoes de cor em MOCs, pois MOCs sao consolidados sem delta visual.

#### Scenario: MOC sem marcacoes
- **WHEN** um MOC e processado
- **THEN** o JSON nao contem campo `marcacoes` nos itens (diferente das NTs)