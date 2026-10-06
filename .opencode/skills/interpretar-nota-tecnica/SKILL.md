---
name: interpretar-nota-tecnica
description: Como ler e interpretar uma Nota Tecnica fiscal. Guia completo de secoes, cronograma, legenda de cores, regra de cruzamento cor x secao de alteracoes, e categorias estrutural/dado/revisao.
allowed-tools: Bash(node:*), Bash(python:*), Read
---

# Skill: Interpretar Nota Tecnica

## Quando usar
- Quando precisar extrair informacoes de uma NT (PDF ou DOCX)
- Quando precisar entender o que uma NT altera
- Quando precisar classificar marcações de cor

## Passo a passo

### 1. Identificar o documento
Leia o cabecalho da NT para extrair:
- Numero da NT (ex: 2026.007)
- Versao (ex: 1.10)
- Documento fiscal (NF-e, CT-e, MDF-e)
- Titulo/resumo

### 2. Ler o cronograma
A secao "Historico de Alteracoes / Cronograma" (geralmente pagina 3) contem:
- Versoes da NT
- Datas de homologacao e producao
- Itens alterados por versao

### 3. Ler "Descricao das alteracoes"
Esta secao lista OFICIALMENTE o que cada versao altera. Cada item tem:
- Numero do item
- Descricao da mudanca
- Versao associada

### 4. Extrair marcações do corpo
Para cada pagina do corpo:
- Fundo amarelo = alterado na versao associada ao amarelo
- Fundo verde = alterado em versao posterior
- Texto vermelho riscado = excluido
- Sem marcação = inalterado ou novo inteiro

### 5. Cruzar marcações com descricao
A cor NUNCA prova sozinha. Cruze:
- Item listado em "Descricao das alteracoes" + marcação no corpo = confirmado
- Item listado SEM marcação = possivelmente novo (regra nova inteira)
- Marcação SEM item listado = registrar em duvidas-abertas.md

### 6. Classificar cada marcação

| Categoria | Exemplo | Tratamento |
|---|---|---|
| REVISAO | Amarelo/verde/riscado sobre texto de regra | Classificar como NOVA/ALTERADA/EXCLUIDA |
| ESTRUTURAL | Cabecalho de tabela, linhas de grupo | Ignorar |
| DADO | Tabela de ALC com cores por municipio | Preservar como dado, nunca como revisao |
| AMBIGUA | Texto verde sem fundo claro | Registrar em duvidas-abertas.md |

### 7. Gerar saida
O script `extrair_nt.py` gera:
- `catalogo/nt/<doc>/<nt>_v<versao>.json` - dados estruturados
- `catalogo/nt/<doc>/<nt>_v<versao>.md` - documento com marcações
- `catalogo/legendas/<doc>.yaml` - mapa cor -> versao

## Erros que o script detecta

- `ERRO_COR_NAO_MAPEADA` - cor de revisao sem entrada na legenda
- `ERRO_PDF_ESCANEADO` - pagina sem camada de texto
- `ERRO_TABELA_QUEBRADA` - tabela com colunas inconsistentes
- `ERRO_MUDANCA_SEM_MARCACAO` - item na descricao sem marcação
- `ERRO_VERSAO_AMBIGUA` - nao achou versao no cabecalho

## Referencia
Leia `docs/legenda-cores.md` para detalhes completos do algoritmo.
Leia `docs/REFERENCIA.md` secao 4.1 para o conceito de marcações.