---
name: revisar-extracao
description: QA da extracao de NTs. Conferir amostra da extração contra o PDF. Verificar itens da secao 3.x sem marcação. Reportar ERRO_MUDANCA_SEM_MARCACAO.
allowed-tools: Bash(node:*), Read
---

# Skill: Revisar Extracao

## Quando usar
- Apos extrair uma NT para conferir qualidade
- Quando suspeitar que a extracao perdeu marcações
- Quando precisar validar se todas as mudancas foram capturadas

## Checklist de revisao

### 1. Conferir cabecalho
- [ ] NT, versao e documento fiscal estao corretos?
- [ ] Arquivo_origem aponta para o arquivo correto?
- [ ] SHA256 foi calculado?

### 2. Conferir cronograma
- [ ] Todas as versoes estao listadas?
- [ ] Datas de homologacao e producao conferem com o PDF?
- [ ] Textos literais (ex: "Ate 05/10/2026") foram preservados?

### 3. Conferir descricao das alteracoes
- [ ] Todos os itens da secao 3.x estao presentes?
- [ ] Cada item esta associado a versao correta?
- [ ] Nenhum item foi omitido?

### 4. Conferir marcações no corpo
- [ ] Texto amarelo foi capturado como AMARELO?
- [ ] Texto verde foi capturado como VERDE?
- [ ] Texto riscado vermelho foi capturado como EXCLUIDO?
- [ ] Sem falsos positivos (cor estrutural tratada como revisao)?

### 5. Cruzar descricao x marcações
- [ ] Cada item da descricao tem marcação correspondente?
- [ ] Se nao tem: e regra nova inteira (SEM_MARCA) ou ERRO?
- [ ] Cada marcação tem item correspondente na descricao?
- [ ] Se nao tem: registrar como AMBIGUA ou ERRO_MUDANCA_SEM_MARCACAO

### 6. Conferir tabelas
- [ ] Tabelas de leiaute foram reconstruidas corretamente?
- [ ] Colunas conferem (#, ID, Campo, Descricao, etc.)
- [ ] Tabelas de regras foram reconstruidas?
- [ ] Nenhuma linha foi perdida ou mesclada incorretamente?

### 7. Conferir legendas
- [ ] Mapa cor -> versao em `catalogo/legendas/<doc>.yaml` esta correto?
- [ ] Conferencia com "Controle de Versoes" do documento?

## Erros que podem ocorrer

| Erro | O que fazer |
|---|---|
| ERRO_COR_NAO_MAPEADA | Cor de revisao sem entrada na legenda -> listar cores |
| ERRO_PDF_ESCANEADO | Pagina sem camada de texto -> marcar para OCR manual |
| ERRO_TABELA_QUEBRADA | Colunas inconsistentes -> revisar extrair_nt.py |
| ERRO_MUDANCA_SEM_MARCACAO | Item na descricao sem marcação -> investigar |
| ERRO_VERSAO_AMBIGUA | Nao achou versao no cabecalho -> verificar formato |

## Amostras para conferir

Para as NTs de exemplo:
- **NT NF-e 2026.007**: conferir paginas 6 e 9
- **NT CT-e 2026.004**: conferir paginas 5, 7, 8 e 9

## Referencia
Leia `docs/legenda-cores.md` para detalhes do algoritmo de cores.
Leia `docs/REFERENCIA.md` secao 4.1 para conceitos de marcações.