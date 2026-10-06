---
description: "Mostrar detalhes de uma regra de validacao: status, NT de origem, cStat, quem aplica, vigencia"
---

# /regra <id ou cStat>

Mostrar detalhes completos de uma regra de validacao.

## Argumentos
- `<id ou cStat>`: ID da regra (ex: C17-10) ou codigo cStat (ex: 229) (obrigatorio)
- `[doc]`: documento fiscal (NF-e, CT-e, MDF-e) - opcional, tenta detectar automaticamente

**Argumentos fornecidos**: $ARGUMENTS

## Fluxo de execucao

### 1. Buscar a regra
- Consultar `catalogo/regras/<doc>.json`
- Buscar por ID ou cStat

### 2. Determinar status
- `ATIVA` - regra vigente, nao alterada
- `ALTERADA` - regra vigente, com NT que modificou
- `EXCLUIDA` - regra revogada por NT
- `NOVA` - regra criada por NT, ainda nao em producao

### 3. Calcular vigencia
- Usar data de hoje para calcular situacao
- Se excluida: mostrar qual NT excluiu e quando

### 4. Formatar resposta

```
[RESUMO]
Regra <ID> - <status> - <resumo>

[DETALHE]
- ID: <id>
- cStat: <codigo>
- Descricao: <descricao completa>
- Modelo: <55/65/57/67/64/58>
- Quem aplica: <SEFAZ/todas>
- NT de origem: <NT> v<versao>
- Pagina: <N>
- Marcação: <AMARELO/VERDE/EXCLUIDO/SEM_MARCA>

[VIGENCIA]
- Situacao: <futura/em_homologacao/em_producao/excluida>
- Homologacao: <data>
- Producao: <data>
- Se excluida: NT <X> v<Y> excluiu em <data>

[FONTES]
- <documento> - <NT/MOC/XSD> v<versao> - pág. <N>
```

### 5. Se excluida
- Alertar: "ATENCAO: esta regra foi EXCLUIDA pela NT X vY"
- Nao explicar como se fosse vigente

## Erros tratados

| Erro | Acao |
|---|---|
| `ERRO_REGRA_EXCLUIDA` | Avisar "excluida pela NT X vY" em vez de explicar como vigente |
| `ERRO_REGRA_NAO_ENCONTRADA` | Sugerir verificar ID ou ingerir NT |