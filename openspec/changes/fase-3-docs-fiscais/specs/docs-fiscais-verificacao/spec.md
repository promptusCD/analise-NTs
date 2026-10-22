# Spec Delta

## Purpose

Garantir, por verificação automatizada e somente leitura, que cada documento fiscal gerado bate com o JSON do catálogo e com os arquivos originais (NTs, MOCs) em `fontes/`.

## ADDED Requirements

### Requirement: Conferência documento contra JSON
O sistema SHALL verificar que cada regra do JSON (id, cStat, efeito, marcação, página) aparece no índice do documento, que as contagens batem com as estatísticas do JSON e que cada linha do cronograma aparece com data literal idêntica e situação recalculada.

#### Scenario: Regra ausente no documento
- **WHEN** uma regra do JSON não consta no índice
- **THEN** a verificação falha e informa a NT, o id e a página

#### Scenario: Contagem divergente
- **WHEN** o total de regras do documento difere do total do JSON
- **THEN** a verificação falha mostrando os dois números

### Requirement: Nenhum item sem origem
A verificação SHALL falhar quando o documento listar regra, cStat, data ou fonte que não exista no JSON ou no manifest, e quando uma regra EXCLUIDA aparecer como vigente.

#### Scenario: Item inventado
- **WHEN** o documento contém um cStat inexistente no catálogo
- **THEN** a verificação falha apontando o item

### Requirement: Conferência contra os originais
A verificação SHALL confirmar no texto do arquivo original em `fontes/`, na página indicada, a presença do cStat, das datas do cronograma e da mensagem de cada regra citada. O que não for localizado MUST ser reportado como `NAO CONFIRMADO NO ORIGINAL`, nunca como correto.

#### Scenario: Item confirmado
- **WHEN** o cStat e a mensagem aparecem na página citada do PDF
- **THEN** o item conta como confirmado no original

#### Scenario: Item não localizado
- **WHEN** o texto não é encontrado, por exemplo em PDF sem camada de texto
- **THEN** o item é reportado como `NAO CONFIRMADO NO ORIGINAL` com o motivo

#### Scenario: Diferença de espaços e acentos
- **WHEN** o texto difere do original apenas por espaços, quebras de linha ou acentuação corrompida
- **THEN** a comparação normaliza esses elementos e o relatório separa "não confirmado" de "divergente"

### Requirement: Somente leitura e relatório
A verificação MUST NOT alterar `fontes/`, `catalogo/` ou os documentos, e SHALL produzir relatório no terminal com contagens, divergências e não confirmados, saindo com código de erro quando houver divergência.

#### Scenario: Divergência
- **WHEN** há ao menos uma divergência
- **THEN** o código de saída é diferente de zero

#### Scenario: Nada alterado
- **WHEN** a verificação termina
- **THEN** `git status` não mostra mudança causada por ela

### Requirement: Amostra de marcação por cor
A validação conduzida pela IA SHALL conferir por amostra, contra a página do original, itens marcados como AMARELO, VERDE e EXCLUIDO, cruzando com a descrição das alterações, pois a cor não prova sozinha.

#### Scenario: Marcação coerente
- **WHEN** um item amarelo é conferido
- **THEN** o relatório indica se a descrição das alterações da NT o confirma

### Requirement: Achados conhecidos
A verificação SHALL reconhecer divergências já registradas em `docs/duvidas-abertas.md` e apresentá-las como achado conhecido, sem escondê-las.

#### Scenario: Dúvida já registrada
- **WHEN** o cStat 890 do MOC CT-e não consta nas regras extraídas
- **THEN** o relatório o lista como achado conhecido com a referência da dúvida

### Requirement: Cobertura coerente com o repositório
A verificação SHALL conferir que o bloco `cobertura` bate com o estado real: cada NT e MOC listado como ingerido existe no catálogo e no manifest, e cada ausência declarada (XSD, legenda, calendário) corresponde a arquivo realmente inexistente.

#### Scenario: Ausência declarada que não existe
- **WHEN** o documento declara ausência de legenda mas o arquivo da legenda existe
- **THEN** a verificação falha apontando a incoerência

#### Scenario: Ingerido sem arquivo
- **WHEN** uma NT listada como ingerida não tem JSON em `catalogo/`
- **THEN** a verificação falha apontando a NT
