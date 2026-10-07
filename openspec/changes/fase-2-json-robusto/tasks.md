## 1. Schema JSON

- [x] 1.1 Criar `scripts/python/utils/json_schema.py` com schemas JSON para NTs e MOCs. Verificacao: arquivo existe e schemas definidos.
- [x] 1.2 Definir estrutura JSON para NTs (secoes tipificadas, tabelas, regras, texto). Verificacao: schema aceita JSON de exemplo.
- [x] 1.3 Definir estrutura JSON para MOCs (hierarquia de secoes, regras, campos). Verificacao: schema aceita JSON de exemplo.

## 2. Atualizar extrair_nt.py

- [x] 2.1 Remover toda logica de geracao de MD do `extrair_nt.py`. Verificacao: arquivo nao tem funcoes de MD.
- [x] 2.2 Implementar identificacao de tabelas (cabecalho + linhas). Verificacao: JSON contem secoes do tipo "tabela" com cabecalho e linhas.
- [x] 2.3 Implementar identificacao de regras de validacao (id, aplicacao, cStat, efeito, mensagem). Verificacao: JSON contem secoes do tipo "regras" com campos estruturados.
- [x] 2.4 Implementar identificacao de texto corrido (paragrafos). Verificacao: JSON contem secoes do tipo "texto" com paragrafos.
- [x] 2.5 Atualizar `utils/saida.py` para gerar JSON robusto (remover funcoes de MD). Verificacao: `gerar_json_nt` gera JSON com nova estrutura.
- [x] 2.6 Testar extracao com NF-e 2026.007. Verificacao: JSON gerado tem secoes tipificadas.
- [x] 2.7 Testar extracao com CT-e 2025.001. Verificacao: JSON gerado tem tabelas e regras.

## 3. Atualizar extrair_moc.py

- [x] 3.1 Remover toda logica de geracao de MD do `extrair_moc.py`. Verificacao: arquivo nao tem funcoes de MD.
- [x] 3.2 Corrigir extracao de secoes (titulos, nao numeros). Verificacao: JSON contem secoes com titulos reais.
- [x] 3.3 Implementar extracao de regras de validacao. Verificacao: JSON contem `regras_validacao[]` com campos estruturados.
- [x] 3.4 Implementar extracao de campos do leiaute. Verificacao: JSON contem `campos_leiaute[]` com campos estruturados.
- [x] 3.5 Atualizar `utils/saida.py` para gerar JSON robusto para MOCs. Verificacao: `gerar_json_moc` gera JSON com nova estrutura.
- [x] 3.6 Testar extracao com MOC CT-e v4.00. Verificacao: JSON gerado tem secoes, regras e campos.

## 4. Command `/gerar-md`

- [x] 4.1 Criar `.opencode/commands/fiscal-gerar-md.md` com instrucoes para IA gerar MD. Verificacao: arquivo existe.
- [x] 4.2 Definir fluxo: IA le JSON, identifica secoes, gera MD com formatacao adequada. Verificacao: command documentado.
- [x] 4.3 Testar command com CT-e 2025.001. Verificacao: MD gerado e legivel.

## 5. Atualizar documentacao

- [x] 5.1 Atualizar `README.md` com novo fluxo de trabalho (extrair JSON -> IA gera MD). Verificacao: README mostra fluxo atualizado.
- [x] 5.2 Atualizar `docs/REFERENCIA.md` secao 5 (catalogo) com nova estrutura JSON. Verificacao: REFERENCIA.md descreve nova estrutura.
- [x] 5.3 Atualizar `openspec/config.yaml` com novo command `/gerar-md`. Verificacao: config.yaml lista command.
- [x] 5.4 Atualizar command `/ingerir-nt` para gerar JSON robusto. Verificacao: command documenta novo fluxo.

## 6. Re-extrair tudo

- [x] 6.1 Limpar `catalogo/` (exceto README.md). Verificacao: diretorios vazios.
- [x] 6.2 Re-extrair todas as 9 NTs com nova logica. Verificacao: JSON gerado tem estrutura robusta.
- [x] 6.3 Re-extrair todos os 10 MOCs com nova logica. Verificacao: JSON gerado tem estrutura robusta.
- [x] 6.4 Verificar que manifest.yaml foi atualizado. Verificacao: todas as NTs e MOCs com status `extraida`.
- [x] 6.5 Gerar MD de exemplo para CT-e 2025.001 via `/gerar-md`. Verificacao: MD gerado e legivel.

## 7. Command `/fiscal-processar`

- [x] 7.1 Criar `.opencode/commands/fiscal-processar.md` com pipeline completo. Verificacao: arquivo existe.
- [x] 7.2 Implementar opcao `--etapa N` para executar etapas individuais. Verificacao: command documenta opcoes.
- [x] 7.3 Testar command com entrada/ vazia. Verificacao: command executa sem erro.
- [x] 7.4 Testar command com arquivos em entrada/. Verificacao: arquivos organizados e extraidos.