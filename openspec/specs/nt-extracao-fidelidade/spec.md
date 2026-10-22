# nt-extracao-fidelidade Specification

## Purpose

Garante que o JSON extraído de uma Nota Técnica reproduza fielmente o PDF de origem: todas as regras, mensagens
completas, cronograma literal, metadados corretos, marcações de cor por trecho e caminhos portáveis.

## Requirements

### Requirement: Todas as regras de validação são extraídas
O sistema SHALL extrair toda regra de validação presente nas tabelas de regras da NT, independentemente do layout do cabeçalho.

#### Scenario: Cabeçalho sem coluna "#" e sem "Efeito"
- **WHEN** a tabela tem cabeçalho `Campo | Modelo | Regra de Validação | Aplic. | Msg | Descrição Erro` (NT NF-e 2026.008)
- **THEN** o JSON contém uma regra para cada ID do PDF (B25-80, I11c-10, I11c-20, NB01-10…) e `efeito` fica vazio sem inventar valor

#### Scenario: Cobertura de IDs
- **WHEN** a NT NF-e 2026.007, 2026.008 ou 2026.002 (DANFE) é extraída
- **THEN** o conjunto de IDs de regra do JSON é igual ao conjunto de IDs impressos nas tabelas do PDF (diferença zero, incluindo `K01-10`)

#### Scenario: Cobertura por cStat
- **WHEN** qualquer NT é extraída
- **THEN** todo cStat que o PDF imprime logo após o valor da coluna Aplic. (`Obrig.`, `Obrig,`, `Facult.`, `Facul.`) pertence a alguma regra do JSON, com ou sem coluna de ID

#### Scenario: Tabela sem coluna de ID
- **WHEN** a tabela de regras não tem coluna de ID (CT-e 2026.004: cStat 1054, 1055–1057, 326; MDF-e 2026.001: cStat 684)
- **THEN** cada regra é extraída com `id` vazio, `cStat` e `mensagem` completos e `id_unico` baseado no cStat

#### Scenario: Tabela de regras sem linha de cabeçalho
- **WHEN** as regras aparecem sem linha de cabeçalho (MDF-e; CT-e "Validações dos Documentos Transportados")
- **THEN** as regras são extraídas como seção do tipo `regras`

#### Scenario: Aplicação com grafia irregular
- **WHEN** a coluna Aplic. traz `Obrig,` (vírgula, regra 1063 da CT-e 2026.004) ou `Facul.` (K01-10 da NT 2026.002)
- **THEN** a regra é extraída normalmente

#### Scenario: Tabela que continua na página seguinte sem cabeçalho
- **WHEN** uma tabela de regras continua na página seguinte sem repetir o cabeçalho (NT 2026.007, pág. 9)
- **THEN** as regras da continuação são extraídas com as mesmas colunas da tabela anterior

### Requirement: Mensagem de rejeição completa
O sistema SHALL preencher `mensagem` com o texto integral da coluna de mensagem, em todas as linhas visuais da regra.

#### Scenario: Mensagem que quebra em várias linhas
- **WHEN** a mensagem da regra 12C02-10 ocupa duas ou mais linhas na coluna "Descrição Erro"
- **THEN** `mensagem` contém o texto completo (inclusive "emitente não cadastrado na Receita Federal") e nenhuma nota repete esse texto

#### Scenario: Nenhuma continuação colada em notas
- **WHEN** a regra 5AF15-11 tem a nota "Observação: Regra de validação para todas as SEFAZ Autorizadoras."
- **THEN** a nota termina em "Autorizadoras." sem trecho da coluna de mensagem

#### Scenario: Mensagem não termina truncada
- **WHEN** qualquer NT do acervo é extraída
- **THEN** nenhuma `mensagem` termina em preposição/artigo/conjunção nem tem colchetes desbalanceados

### Requirement: Identificador único de regra
O sistema SHALL fornecer `id_unico` para cada regra, preservando `id` como impresso no PDF.

#### Scenario: IDs repetidos entre tabelas
- **WHEN** duas tabelas de uma NT de CT-e usam o número `001`
- **THEN** cada regra tem `id` igual ao do PDF e `id_unico` distinto no JSON inteiro, e `cStat` continua disponível como chave de busca

### Requirement: Cronograma literal e sem invenção
O sistema SHALL extrair o cronograma da tabela de controle de versões, mantendo datas literais e sem inventar versão ou data.

#### Scenario: Uma linha por versão
- **WHEN** a NT 2026.002 (DANFE) tem 6 linhas na tabela (1.00 ×3, 1.10, 1.10a e 1.11) com implantações 01/06→15/06, 01/07→03/08, 01/09→05/10 (×3) e "-x-"→14/12/2026
- **THEN** o `cronograma` tem 6 entradas, uma por linha, com `versao` e `descricao` da linha correspondente e `homologacao` vazio na v1.11

#### Scenario: Literais que não são data
- **WHEN** a célula traz "Já implantado", "Implementação futura" ou "07/2025"
- **THEN** o valor é mantido exatamente como impresso, sem converter nem descartar

#### Scenario: Versão sem nenhuma data
- **WHEN** uma linha da tabela não tem valor nas colunas de implantação (ex.: v1.00 a v1.12 da CT-e 2025.001)
- **THEN** essa linha não gera entrada em `cronograma`

#### Scenario: Data com "Até"
- **WHEN** a NT 2026.007 tem a v1.10 com homologação "Até 05/10/2026" e produção 03/11/2026
- **THEN** o `cronograma` contém `homologacao: "Até 05/10/2026"` (literal) e `producao: "03/11/2026"` para a v1.10

#### Scenario: Coluna sem data
- **WHEN** a coluna de implantação em teste é "-" e a produção é 01/12/2026 (NT NF-e 2026.010)
- **THEN** `homologacao` fica vazio e `producao` é "01/12/2026", sem `00/00/0000` nem versão "."

#### Scenario: Cronograma não encontrado
- **WHEN** nenhuma tabela de controle de versões com datas é reconhecida
- **THEN** `cronograma` é `[]`, a extração registra aviso `ERRO_DATA_NAO_ENCONTRADA` e nenhuma versão padrão é criada

### Requirement: Metadados corretos
O sistema SHALL extrair `titulo` e `versao` fiéis ao documento, incluindo sufixo alfabético de versão.

#### Scenario: Título real
- **WHEN** o cabeçalho de página da NT NF-e 2026.007 diz "NT 2026.007 - Emissão por Contribuinte exclusivo do IBS/CBS"
- **THEN** `titulo` é "Emissão por Contribuinte exclusivo do IBS/CBS" e não o texto da capa ("Projeto Nota Fiscal")

#### Scenario: Versão com sufixo
- **WHEN** o arquivo é `CTe_NT_2025_001_RTC_v1.14b.pdf`
- **THEN** `versao` é "1.14b"

### Requirement: Marcação por trecho
O sistema SHALL preservar a marcação de cor no nível do trecho/célula, e a marcação da linha SHALL refletir o trecho mais relevante.

#### Scenario: Observação destacada em linha de leiaute
- **WHEN** as "Observação 1/2" do campo C17 estão em amarelo no PDF (NT 2026.007, pág. 6)
- **THEN** o JSON registra esses trechos como `AMARELO` em `trechos[]` e a marcação da linha é `AMARELO`

#### Scenario: Páginas de referência
- **WHEN** a NT 2026.007 é extraída
- **THEN** C12-10 e a Exceção 2 de B25-90 estão `AMARELO`, C17-10 está `EXCLUIDO` e a Exceção de 12C02-10 está `VERDE`

### Requirement: Caminhos portáveis
O sistema SHALL gravar `arquivo_origem` relativo à raiz do repositório, com `/` como separador.

#### Scenario: Caminho relativo
- **WHEN** qualquer NT é extraída em qualquer máquina
- **THEN** `arquivo_origem` é, por exemplo, `fontes/nfe/notas-tecnicas/NT_2026_007_v1.10.pdf`, sem letra de unidade nem nome de usuário
