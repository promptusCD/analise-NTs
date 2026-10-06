---
description: "Gerar checklist de implementacao para o time de desenvolvimento: campos novos/alterados/removidos, regras, rejeicoes, eventos e datas"
---

# /impacto <nt>

Gerar checklist de implementacao a partir de uma NT para o time de
desenvolvimento.

## Argumentos
- `<nt>`: NT para analisar (ex: NT-CT-e-2026.004, NT-NF-e-2026.007) (obrigatorio)

**Argumentos fornecidos**: $ARGUMENTS

## Fluxo de execucao

### 1. Localizar a NT
- Buscar em `catalogo/nt/<doc>/` por NT matching
- Ler JSON da extracao

### 2. Ler catalogos complementares
- `catalogo/campos/<doc>.json` - campos do leiaute
- `catalogo/regras/<doc>.json` - regras de validacao
- `calendario/calendario.yaml` - datas

### 3. Compilar checklist

```
IMPACTO DA <NT> - CHECKLIST DE IMPLEMENTACAO
Documento: <doc>
Versao: <versao>

========================================
CAMPOS NOVOS
========================================
- <tag> (<grupo pai>) [<modelos>] - descricao
  XSD: <arquivo_xsd>
  Onde usar: <contexto>

========================================
CAMPOS ALTERADOS
========================================
- <tag> (<grupo pai>) [<modelos>] - o que mudou
  Antes: <valor antigo>
  Depois: <valor novo>

========================================
CAMPOS EXCLUIDOS
========================================
- <tag> (<grupo pai>) [<modelos>] - motivo

========================================
REGRAS NOVAS
========================================
- <ID> (cStat <codigo>) - descricao
  Quem aplica: <SEFAZ/todas>
  Modelo: <N>

========================================
REGRAS EXCLUIDAS
========================================
- <ID> (cStat <codigo>) - motivo da exclusao

========================================
EVENTOS NOVOS
========================================
- <tpEvento> - <nome>
  Autorizador: <SEFAZ>
  Schema: <arquivo>

========================================
REJEICOES NOVAS
========================================
- <cStat> - <mensagem> - quando ocorre

========================================
DATAS DE VIGENCIA
========================================
Homologacao: <data>
Producao: <data>

========================================
IMPACTO NO EMISSOR
========================================
1. Implementar campos novos: <lista>
2. Remover campos excluidos: <lista>
3. Implementar regras novas: <lista>
4. Remover regras excluidas: <lista>
5. Testar: <cenarios>
6. Atencao: <armadilhas>
```

## Como usar

```
/impacto NT-CT-e-2026.004
```

O time de desenvolvimento recebe um checklist pronto para criar
tarefas no Jira, Linear ou gestor de projetos.