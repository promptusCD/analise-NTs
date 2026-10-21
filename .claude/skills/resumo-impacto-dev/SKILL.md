---
name: resumo-impacto-dev
description: Transforma uma NT em checklist de implementação para desenvolvedores (campos, regras, rejeições, eventos, datas, impacto no emissor). Use para "o que muda no sistema" de uma NT. É a lógica por trás de /fiscal-impacto.
allowed-tools: Read, Grep, Glob, Bash(date:*), Bash(node:*)
---

# Skill: Resumo de Impacto para Desenvolvedor

## Quando usar
- Checklist de implementação a partir de uma NT
- Time de dev precisa saber o que mudar
- Listar campos/regras/eventos novos, alterados, excluídos

## Fontes
1. `catalogo/nt/<doc>/<arquivo>.json` (NT extraída; `secoes[]`, `cronograma[]`)
2. `catalogo/campos/<doc>.json` e `catalogo/regras/<doc>.json` **(se existirem)** para cruzar com XSD/regras
3. `calendario/calendario.yaml` **(se existir)**; senão use `cronograma[]` do JSON da NT
4. `catalogo/legendas/<doc>.yaml` para interpretar marcações

Se os catálogos 2–3 não existirem, extraia do próprio JSON da NT e avise quais cruzamentos
não foram feitos (ex.: "campo não verificado contra XSD").

## Escolha da versão
Uma NT pode ter várias versões (v1.00, v1.10…). Use a **mais recente** e compare com a anterior
quando existir: liste o que mudou entre versões ("v1.00 → v1.10"). Informe qual versão foi usada.

## Saída
```
CAMPOS NOVOS / ALTERADOS (antes → depois) / EXCLUÍDOS
  - <tag> (<grupo pai>) [<modelos>] - descrição  (XSD: <arquivo>)
REGRAS NOVAS / ALTERADAS / EXCLUÍDAS
  - <ID> (cStat <código>) - descrição - quem aplica - modelo
EVENTOS NOVOS
  - <tpEvento> - nome - autorizador - schema
REJEIÇÕES NOVAS
  - <cStat> - mensagem - quando ocorre
DATAS (por item/bloco; literais preservados)
  - Homologação / Produção / Situação hoje
IMPACTO NO EMISSOR
  1. Implementar  2. Remover  3. Testar (cenários)  4. Atenção (armadilhas)
FONTES
  - <documento> - <NT> v<versão> - pág. <N> - <marcação>
```

## Regras
- Todo item cita NT, versão, página e **marcação** (AMARELO/VERDE/EXCLUIDO/SEM_MARCA)
- Indique a situação de cada item (futura/em_homologacao/em_producao/excluida) com a data de hoje
- Separe por modelo quando aplicável (NF-e 55, NFC-e 65, CT-e 57, CT-e OS 67, GTV-e 64, CT-e Simp., MDF-e 58)
- Não invente campo, regra, cStat ou data: se não estiver no JSON → "NAO ENCONTRADO NAS FONTES"
- Resultado pronto para virar tarefas (Jira/Linear/Asana)
