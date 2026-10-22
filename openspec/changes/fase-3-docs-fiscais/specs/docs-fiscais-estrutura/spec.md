# Spec Delta

## Purpose

Fornecer um documento por documento fiscal (NF-e, CT-e, MDF-e) mais um comum e um glossário, com estrutura fixa que a IA e o desenvolvedor leem antes de consultar o catálogo.

## ADDED Requirements

### Requirement: Arquivos por documento fiscal
O sistema SHALL manter em `docs-fiscais/` os arquivos `NFE.md`, `CTE.md`, `MDFE.md`, `_COMUM.md` e `_GLOSSARIO.md`.

#### Scenario: Arquivos presentes
- **WHEN** a fase-3 é concluída
- **THEN** os cinco arquivos existem e o `AGENTS.md` consegue ser seguido sem referência quebrada

### Requirement: Template de nove seções
Cada arquivo de documento SHALL seguir as nove seções do template do `docs/REFERENCIA.md`: identificação, fontes vigentes, mapa do leiaute, eventos, índice de regras, mudanças em andamento, armadilhas, linha do tempo e dúvidas abertas. As seções AUTO MUST ter marcadores nomeados.

#### Scenario: Seções AUTO marcadas
- **WHEN** um documento é aberto
- **THEN** as seções 2, 5, 6, 8 e 9 têm marcadores AUTO, e as seções 3 e 4 combinam texto manual com bloco AUTO

#### Scenario: Seções manuais
- **WHEN** a seção é de identificação ou armadilhas
- **THEN** ela fica fora de qualquer marcador AUTO

### Requirement: Armadilhas conhecidas registradas
As seções de armadilhas SHALL conter as armadilhas já conhecidas comuns e as específicas de cada documento, cada uma com a fonte que a sustenta.

#### Scenario: Armadilha sem fonte
- **WHEN** uma armadilha não tem fonte no catálogo
- **THEN** ela é registrada como pendente de confirmação, e não como regra

### Requirement: Conteúdo comum e glossário
`_COMUM.md` SHALL reunir os conceitos transversais (cStat, ambientes, SVRS, IBS/CBS) e `_GLOSSARIO.md` os termos e siglas, sempre rotulando fonte não oficial.

#### Scenario: Fonte não oficial
- **WHEN** um trecho vem de fornecedor ou fórum
- **THEN** ele leva o selo "nao oficial"

### Requirement: Limitações declaradas
Enquanto não houver XSD catalogado, as seções de mapa do leiaute e eventos SHALL declarar que se baseiam apenas no MOC e podem estar incompletas.

#### Scenario: Leiaute sem XSD
- **WHEN** o leitor abre a seção 3
- **THEN** vê o aviso de que o leiaute vem só do MOC Anexo I, sem conferência com XSD

### Requirement: Lacunas e cobertura declaradas
Cada documento SHALL declarar na seção 2 o que ainda falta: NTs e MOCs ingeridos, fontes pendentes, ausência de XSD catalogado, de legendas de cor revisadas e de calendário, e os modelos do documento sem conteúdo específico no catálogo. A declaração MUST refletir o estado real do repositório.

#### Scenario: Ausências declaradas
- **WHEN** não existe XSD catalogado, legenda do documento ou calendário
- **THEN** a seção de cobertura informa cada ausência e que a vigência vem do cronograma das NTs

#### Scenario: Fontes pendentes
- **WHEN** `docs/ARQUIVOS_NECESSARIOS.md` lista arquivos ainda não obtidos para o documento
- **THEN** eles aparecem como pendentes, e a lista não é inventada se o arquivo não puder ser interpretado

#### Scenario: Modelo sem conteúdo
- **WHEN** nenhum NT ou MOC ingerido traz conteúdo específico de um modelo (por exemplo GTV-e)
- **THEN** o modelo é listado como sem conteúdo no catálogo, com o aviso de que a busca não prova ausência
