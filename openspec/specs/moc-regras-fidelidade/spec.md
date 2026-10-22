# moc-regras-fidelidade Specification

## Purpose

Garante que regras de validação e campos de leiaute extraídos dos MOCs tenham texto completo e que o JSON seja portável
entre máquinas, no mesmo padrão de fidelidade exigido das Notas Técnicas.

## Requirements

### Requirement: Mensagem de regra de MOC completa
O sistema SHALL preencher a mensagem/descrição de cada item de `regras_validacao` com o texto integral da coluna correspondente.

#### Scenario: Mensagem em várias linhas
- **WHEN** a mensagem de uma regra do MOC NF-e v7.00 (Visão Geral ou Anexo I) quebra em mais de uma linha
- **THEN** o texto completo está no campo de mensagem do item e não em outro campo

#### Scenario: Sem mensagens truncadas no acervo
- **WHEN** os 10 MOCs do acervo são extraídos
- **THEN** nenhuma mensagem de regra termina em preposição/artigo/conjunção nem tem colchetes desbalanceados

### Requirement: Sem perda em relação à extração anterior
O sistema SHALL manter ou ampliar a quantidade de seções, regras e campos de cada MOC já extraído.

#### Scenario: Comparação com a extração anterior
- **WHEN** um MOC é re-extraído
- **THEN** `regras_validacao` e `campos_leiaute` têm quantidade maior ou igual à da extração anterior, ou a diferença é justificada e registrada em `docs/duvidas-abertas.md`

### Requirement: Caminho de origem portável em MOC
O sistema SHALL gravar `arquivo_origem` do MOC relativo à raiz do repositório, com `/` como separador.

#### Scenario: MOC em DOCX
- **WHEN** `MOC_MDFe_Anexo_II_DAMDFE_v3.00b.docx` é extraído
- **THEN** `arquivo_origem` é `fontes/mdfe/moc/MOC_MDFe_Anexo_II_DAMDFE_v3.00b.docx`
