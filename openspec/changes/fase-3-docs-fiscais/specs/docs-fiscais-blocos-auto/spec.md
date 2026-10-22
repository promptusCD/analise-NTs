# Spec Delta

## Purpose

Gerar de forma determinística os blocos AUTO dos documentos fiscais a partir do catálogo, do manifest e das dúvidas abertas, sem tocar no conteúdo escrito à mão.

## ADDED Requirements

### Requirement: Escrita restrita aos marcadores AUTO
O script `npm run docs-fiscais` SHALL reescrever apenas o conteúdo entre `<!-- AUTO:BEGIN <nome> -->` e `<!-- AUTO:END <nome> -->`. Todo o texto fora dos marcadores MUST permanecer byte a byte igual.

#### Scenario: Conteúdo manual intacto
- **WHEN** o script roda sobre um documento com texto manual entre blocos
- **THEN** o texto manual fica idêntico e só os blocos AUTO mudam

#### Scenario: Idempotência
- **WHEN** o script roda duas vezes seguidas sem mudança nas fontes
- **THEN** a segunda execução não altera nenhum arquivo

### Requirement: Marcadores inválidos interrompem a escrita
O script SHALL validar os marcadores antes de escrever. Marcador ausente, duplicado, sem par ou com nome desconhecido MUST causar erro com o arquivo e o nome do bloco, sem escrever nada naquele documento.

#### Scenario: Par desbalanceado
- **WHEN** um `AUTO:BEGIN` não tem o `AUTO:END` correspondente
- **THEN** o script falha, informa o bloco e deixa o arquivo sem alteração

#### Scenario: Seleção de documento
- **WHEN** o usuário informa um documento (`nfe`, `cte` ou `mdfe`)
- **THEN** só esse arquivo é regenerado

### Requirement: Blocos derivados do catálogo
O script SHALL gerar: `fontes_vigentes` (do `manifest.yaml`), `regras` (índice com cStat, aplicação, marcação e NT de origem), `grupos` e `eventos` (do MOC), `em_andamento` e `linha_do_tempo` (do cronograma das NTs, com a situação calculada hoje), `duvidas` (de `docs/duvidas-abertas.md` filtradas pelo documento), `cobertura` (ingeridos, fontes pendentes, presença de XSD, legendas e calendário, modelos sem conteúdo).

#### Scenario: Regra excluída
- **WHEN** uma regra está marcada como EXCLUIDO
- **THEN** o índice a lista como excluída e nunca como vigente

#### Scenario: Citação de origem
- **WHEN** um item é listado em qualquer bloco
- **THEN** ele traz a NT ou MOC, a versão e a página de origem

#### Scenario: Fonte do bloco vazia
- **WHEN** não há dado para um bloco (por exemplo sem NT de MDF-e com eventos)
- **THEN** o bloco informa explicitamente que não há itens, em vez de ficar vazio

### Requirement: Dados nunca corrigidos nem inventados
O script MUST reproduzir o texto do catálogo sem reparar acentuação, completar datas ou deduzir cStat. Item sem informação MUST ser exibido como `NAO ENCONTRADO NAS FONTES`.

#### Scenario: Campo ausente
- **WHEN** uma regra não tem `cStat`
- **THEN** o índice mostra `NAO ENCONTRADO NAS FONTES` nesse campo

### Requirement: Somente leitura nas fontes
O script MUST NOT criar, editar ou apagar nada em `fontes/`, `catalogo/` ou nos projetos listados em `projetos.yaml`.

#### Scenario: Diretórios de entrada intactos
- **WHEN** o script termina
- **THEN** `git status` mostra alterações apenas em `docs-fiscais/`

### Requirement: Cobertura derivada do estado real
O bloco `cobertura` SHALL ser calculado a cada execução a partir do sistema de arquivos, do manifest, do catálogo e de `docs/ARQUIVOS_NECESSARIOS.md`, e MUST NOT depender de texto escrito à mão.

#### Scenario: Legenda passa a existir
- **WHEN** `catalogo/legendas/<doc>.yaml` é criado e o script roda de novo
- **THEN** o bloco deixa de declarar a ausência de legenda desse documento

#### Scenario: NT recém-ingerida
- **WHEN** uma nova NT é ingerida e o script roda
- **THEN** ela aparece entre os ingeridos e sai das pendentes, se constava como pendente
