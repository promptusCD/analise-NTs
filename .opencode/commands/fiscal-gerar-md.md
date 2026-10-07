---
name: fiscal-gerar-md
description: "Gerar (ou regenerar) o MD de uma NT ou MOC a partir do JSON robusto extraido - a IA le o JSON e produz MD legivel"
---

# /gerar-md <nt|moc>

Gerar o Markdown de uma NT ou MOC a partir do JSON estruturado em `catalogo/`.
O Python nao gera MD: a IA e responsavel pela formatacao.

## Argumentos

- `<nt|moc>`: identificador do documento (obrigatorio)
  - NT: numero da NT (ex: `2025.001`) ou caminho do JSON
  - MOC: nome do arquivo (ex: `MOC_CTe_VisaoGeral_v4.00`) ou caminho do JSON
- `--forcar`: sobrescrever MD existente (opcional)

**Argumentos fornecidos**: $ARGUMENTS

## Fluxo de execucao

### 1. Localizar o JSON

- NT: `catalogo/nt/<doc>/<nt>.json` (doc = `nfe` | `cte` | `mdfe`)
  - Ex: `/gerar-md 2025.001` -> `catalogo/nt/cte/CTe_NT_2025_001_RTC_v1.14b.json`
- MOC: `catalogo/moc/<doc>/<nome>.json`
  - Ex: `/gerar-md MOC_CTe_VisaoGeral_v4.00` -> `catalogo/moc/cte/MOC_CTe_VisaoGeral_v4.00.json`
- Se nao encontrar: listar JSONs disponiveis no diretorio e pedir escolha
  (`ERRO_JSON_NAO_ENCONTRADO`)

### 2. Ler o JSON inteiro

Ler o arquivo completo e verificar a estrutura:

- NT (`tipo_documento: "NT"`): `nt`, `versao`, `documento`, `titulo`,
  `cronograma[]`, `secoes[]` (tipos `tabela` | `regras` | `texto`),
  `estatisticas`
- MOC (`tipo_documento: "MOC"`): `documento`, `versao`, `secoes[]`
  (hierarquicas com `subsecoes[]`), `regras_validacao[]`, `campos_leiaute[]`

Se o JSON estiver vazio ou sem `secoes`, interromper e sugerir re-extrair
(`/fiscal-reextrair` ou `python scripts/python/extrair_nt.py <pdf>`).

### 3. Gerar o MD

Escrever em `catalogo/nt/<doc>/<nt>.md` ou `catalogo/moc/<doc>/<nome>.md`
(mesmo nome do JSON, extensao `.md`).

Estrutura do MD gerado:

1. **Cabecalho**: titulo (`# NT 2025.001 v1.14b - <titulo>` ou
   `# MOC CT-e v4.00 - <titulo>`), documento, arquivo de origem e SHA256
2. **Cronograma** (NT): tabela com versao / homologacao / producao,
   preservando datas LITERAIS do JSON (`Ate 05/10/2026` nunca e convertido)
3. **Secoes**: numeracao e titulo originais (`## 3.1 Descricao`)
4. **Rodape**: estatisticas de extracao e nota de que a fonte e o PDF
   original em `fontes/`

Regras de formatacao por tipo de secao:

| Tipo no JSON | Formatacao no MD |
|---|---|
| `tabela` | Cada linha vira bullet com o campo/nome em negrito; colunas secundarias em texto normal. Se a tabela for pequena (<= 4 colunas e <= 6 linhas), pode virar tabela MD |
| `regras` | Cada regra em bullet: `**<id>**` + `cStat <cStat>` + `efeito` + **mensagem**; `condicao` em texto; notas (`Excecao`/`Observacao`) como sub-bullet |
| `texto` | Paragrafos corridos, um bullet por paragrafo quando forem itens de lista da propria NT |

Regras gerais de formatacao:

- Datas no formato `DD/MM/AAAA` em **negrito**
- Tags XML (`infCte`, `cMunEmi`, ...) em `` `backticks` ``
- Marcacao de cor do JSON vira sufixo visivel: `_ (alterado - amarelo)_` para
  `AMARELO`, `_ (versao posterior - verde)_` para `VERDE`,
  `_ (EXCLUIDO)_` para `EXCLUIDO`; `SEM_MARCA` nao leva sufixo
- A cor nunca prova sozinha: nao afirmar vigencia/exclusao com base apenas
  na cor - manter o texto extraido
- Nao inventar regra, cStat, tag ou data que nao esteja no JSON
- Tudo em pt-BR

### 4. Validar

- Conferir que todo `id` de regra do JSON aparece no MD
- Conferir que nenhuma data foi reescrita (copiar literais)
- Conferir que nenhuma secao do JSON ficou de fora

### 5. Resumo

Exibir:

- Documento gerado (numero/versao, caminho do MD)
- Contagem: secoes, tabelas, regras, paragrafos
- Marcacoes encontradas (AMARELO/VERDE/EXCLUIDO/SEM_MARCA)
- Proximo passo sugerido

## Erros tratados

| Erro | Acao |
|---|---|
| `ERRO_JSON_NAO_ENCONTRADO` | Listar JSONs disponiveis e pedir escolha |
| `ERRO_JSON_VAZIO` | Sugerir re-extracao do PDF |
| `ERRO_MD_EXISTENTE` | Avisar que MD ja existe, perguntar se sobrescreve (ou usar `--forcar`) |

## Exemplos

```
/gerar-md 2025.001                 # NT CT-e 2025.001
/gerar-md MOC_CTe_VisaoGeral_v4.00 # MOC CT-e
```
