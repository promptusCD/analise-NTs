## Why

O JSON gerado pelo `extrair_nt.py` e muito pobre - uma lista plana de itens com bbox, cor, etc. Sem estrutura de tabelas, sem identificacao de regras de validacao, com secoes mal definidas. O MOC esta completamente quebrado - secoes so tem numeros, nao titulos. O MD gerado por Python e pessimo, nao legivel.

A solucao e redesenhar o JSON para ser robusto e ter a IA gerar o MD a partir do JSON, em vez de Python tentar formatar.

## What Changes

- **BREAKING** Redesenhar estrutura JSON para NTs e MOCs
- **BREAKING** Atualizar `extrair_nt.py` para gerar JSON robusto (sem MD)
- **BREAKING** Atualizar `extrair_moc.py` para gerar JSON robusto (sem MD)
- **Novo** Criar workflow para IA gerar MD a partir do JSON
- **Novo** Criar command `/fiscal-processar` para pipeline completo
- **Novo** Atualizar documentacao e fluxo de utilizacao do usuario
- **Novo** Atualizar README.md com novo fluxo de trabalho

## Capabilities

### New Capabilities

- `json-nt`: Estrutura JSON robusta para NTs fiscais. Inclui secoes tipificadas (tabela, regras, texto), tabelas com cabecalho e linhas estruturadas, regras de validacao identificadas, cronograma, e metadados completos.

- `json-moc`: Estrutura JSON robusta para MOCs. Inclui hierarquia de secoes, regras de validacao extraidas, campos do leiaute, e metadados completos.

- `gerar-md-ia`: Workflow para IA gerar MD a partir do JSON. A IA le o JSON estruturado e gera MD legivel com formatacao inteligente (bullets, destaque de campos, datas, alteracoes).

- `fiscal-processar`: Command que executa o pipeline completo: organizar `entrada/` -> `fontes/`, extrair JSON de NTs e MOCs, atualizar manifest, atualizar catalogo. Suporta opcao `--etapa N` para executar etapas individuais.

### Modified Capabilities

Nenhuma capability existente e modificada (o projeto esta comecando).

## Impact

### Arquivos criados:
- `scripts/python/utils/json_schema.py` -- schemas JSON para NTs e MOCs
- `.opencode/commands/fiscal-gerar-md.md` -- command para IA gerar MD
- `.opencode/commands/fiscal-processar.md` -- command pipeline completo

### Arquivos atualizados:
- `scripts/python/extrair_nt.py` -- gerar JSON robusto, remover MD
- `scripts/python/extrair_moc.py` -- gerar JSON robusto, remover MD
- `scripts/python/utils/saida.py` -- remover funcoes de geracao de MD
- `README.md` -- atualizar fluxo de utilizacao
- `docs/REFERENCIA.md` -- atualizar secao 5 (catalogo)
- `openspec/config.yaml` -- atualizar commands disponiveis

### Dependencias:
- Nenhuma nova dependencia (PyMuPDF, pyyaml, python-docx ja existentas)

### Impacto no emissor:
- O extrator gera JSON mais rico e estruturado
- A IA gera MD mais legivel e formatado
- Fluxo de trabalho mais claro para o usuario

### Referencia:
- docs/REFERENCIA.md -- contexto completo, roadmap (secao 9), estrutura de diretorios (secao 3), catalogo (secao 5)