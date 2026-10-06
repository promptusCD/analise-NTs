## Purpose

Gerenciar o mapa cor -> versao por documento fiscal. A legenda associa cada marcacao visual (AMARELO, VERDE, EXCLUIDO) a uma versao especifica da NT, permitindo que a IA saiba qual versao cada cor representa.

## ADDED Requirements

### Requirement: Gerar legenda automaticamente apos extracao
O sistema SHALL gerar o arquivo `catalogo/legendas/<doc>.yaml` apos processar todas as NTs de um documento fiscal.

#### Scenario: Legenda da NF-e
- **WHEN** todas as NTs da NF-e sao processadas
- **THEN** e gerado `catalogo/legendas/nfe.yaml` com o mapa cor -> versao de cada NT

### Requirement: Formato YAML da legenda
O sistema SHALL gerar a legenda no formato YAML conforme REFERENCIA.md secao 5.4.

#### Scenario: Estrutura da legenda
- **WHEN** a legenda e gerada
- **THEN** o YAML contem `documento`, `nt`, `legenda` com chaves `AMARELO`, `VERDE`, `EXCLUIDO`, cada uma com `versao`, `hex_proximo` e `confianca`

### Requirement: Atualizar legenda quando nova NT e processada
O sistema SHALL atualizar a legenda existente quando uma nova NT do mesmo documento fiscal e processada.

#### Scenario: Nova NT adicionada a legenda
- **WHEN** uma nova NT da NF-e e processada apos legenda ja existente
- **THEN** a legenda e atualizada com as novas marcacoes, sem perder as anteriores

### Requirement: Incluir confianca na legenda
O sistema SHALL indicar o nivel de confianca da associacao cor -> versao (ALTA, MEDIA, BAIXA).

#### Scenario: Confianca alta
- **WHEN** a marcacao foi detectada com cor clara e cruzada com secao de alteracoes
- **THEN** a confianca e `ALTA`

#### Scenario: Confianca baixa
- **WHEN** a marcacao foi inferida sem cruzamento com secao de alteracoes
- **THEN** a confianca e `BAIXA`