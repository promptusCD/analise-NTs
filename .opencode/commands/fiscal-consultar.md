---
description: "Consultar informacao fiscal com resposta mastigada, vigencia e fontes citadas"
---

# /consultar <pergunta>

Responder uma pergunta sobre documentacao fiscal com resposta mastigada,
vigencia calculada e fontes citadas.

## Argumentos
- `<pergunta>`: pergunta em linguagem natural (obrigatorio)

**Argumentos fornecidos**: $ARGUMENTS

## Fluxo de execucao

### 1. Identificar o documento fiscal
- Determinar se a pergunta e sobre NF-e, CT-e ou MDF-e
- Se nao conseguir: perguntar ao usuario

### 2. Ler docs-fiscais
- Ler `docs-fiscais/<DOC>.md` (visao geral + armadilhas)
- Ler `docs-fiscais/_COMUM.md` (conceitos transversais)

### 3. Buscar no catalogo
- `catalogo/regras/<doc>.json` - regras de validacao
- `catalogo/campos/<doc>.json` - campos do leiaute
- `catalogo/nt/<doc>/*.json` - extracoes de NTs

### 4. Calcular vigencia
- Para cada regra/campo encontrado, calcular situacao:
  - `futura` | `em_homologacao` | `em_producao` | `excluida`
- Usar data de hoje (rode `date` ou `Get-Date`)

### 5. Formatar resposta

```
[RESUMO - 2-3 linhas]

[DETALHE]
- Campo/regra: <nome>
- cStat: <codigo> (se aplicavel)
- Quem aplica: <SEFAZ/todas>
- NT de origem: <NT> v<versao>, pág. <N>
- Marcação: <AMARELO/VERDE/EXCLUIDO/SEM_MARCA>
- Situacao: <futura/em_homologacao/em_producao/excluida>

[IMPACTO NO EMISSOR]
- O que precisa mudar no sistema

[FONTES]
- <documento> - <NT/MOC/XSD> v<versao> - pág. <N> - <marcação>
```

### 6. Se nao encontrar
- Responder "NAO ENCONTRADO NAS FONTES"
- Sugerir `/atualizar-fontes` ou ingerir NT/MOC/XSD

## Erros tratados

| Erro | Acao |
|---|---|
| `ERRO_FONTE_AUSENTE` | Documento fora do manifest -> avisar, nao responder de memoria |
| `ERRO_SEM_CITACAO` | Resposta sem fonte/versao/pagina -> invalida |