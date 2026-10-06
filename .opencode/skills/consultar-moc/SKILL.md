---
name: consultar-moc
description: Como achar regras no MOC (Manual de Orientacao do Contribuinte) vigente. Qual versao vale em cada data. Como conciliar MOC x NT (NT altera o MOC ate ser consolidada).
allowed-tools: Bash(node:*), Read
---

# Skill: Consultar MOC

## Quando usar
- Quando precisar saber qual MOC e a versao vigente de um documento fiscal
- Quando precisar encontrar uma regra de validacao no MOC
- Quando precisar conciliar informacoes do MOC com NTs

## Sobre os MOCs

Cada documento fiscal tem seu MOC:
- **NF-e**: MOC v7.00 (Visao Geral + Anexo I Leiaute + Anexo II DANFE + Anexo III Contingencia)
- **CT-e**: MOC v4.00 (Visao Geral + Anexo I Leiaute + Anexo II DACTE)
- **MDF-e**: MOC v3.00b (Visao Geral + Anexo I Leiaute + Anexo II DAMDFE)

## Como consultar

### 1. Identificar o MOC correto
Leia `docs-fiscais/<DOC>.md` secao "Fontes vigentes" para saber qual
MOC e a versao atual.

### 2. Encontrar a regra
- O Anexo I do MOC contem o leiaute (campos) e as regras de validacao
- Cada regra tem: ID, descricao, cStat (codigo de rejeicao), efeito

### 3. Conciliar MOC x NT
- O MOC e a versao CONSOLIDADA (inclui todas as NTs ja aplicadas)
- NTs mais recentes podem alterar regras do MOC sem atualizar o MOC
- Para saber se uma regra foi alterada por NT, consulte:
  - `catalogo/regras/<doc>.json` - campo "nt_origem"
  - `docs-fiscais/<DOC>.md` secao "Regras de validacao"

### 4. Verificar vigencia
Uma regra pode ter sido:
- Criada pelo MOC original (status: ativa, a menos que NT tenha excluido)
- Alterada por NT (status: alterada, com versao de origem)
- Excluida por NT (status: excluida, com versao de exclusao)

## MOC Online
O portal do SPED oferece MOC online:
- NF-e: http://moc.sped.fazenda.pr.gov.br/NFe_NFCe/VisaoGeral.html
- CT-e: http://moc.sped.fazenda.pr.gov.br/CTe/index.html

## Referencia
Leia `docs/REFERENCIA.md` secao 7 para o template dos docs-fiscais.
Leia `docs/ARQUIVOS_NECESSARIOS.md` para saber quais MOCs precisam ser baixados.