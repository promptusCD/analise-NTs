---
description: Mostrar calendário de vigências por documento, ordenado por data de produção, com situação calculada para hoje
argument-hint: [NF-e|CT-e|MDF-e]
---

# /fiscal-calendario

**Argumentos**: $ARGUMENTS (documento opcional; vazio = todos)

## Fluxo

1. Rode `date` e use-a como "hoje".
2. Leia `calendario/calendario.yaml` (skill **atualizar-calendario**). **Se não existir** (hoje não
   existe): monte a tabela a partir de `cronograma[]` dos JSONs em `catalogo/nt/<doc>/` e avise que
   o calendário oficial ainda não foi gerado — ou ofereça criar o yaml.
3. Situação por item: `futura | em_homologacao | prazo_homologacao_encerrado | em_producao | excluida | indefinida` (datas PENDENTE).
4. Ordene por produção crescente (PENDENTE por último); **negrito** no que vence em até 30 dias.
5. Preserve textos literais (`Até 05/10/2026`) e **recalcule** a situação — não copie situação antiga.
6. Opcional: `node scripts/js/gerar_calendario.js` (se existir) para o HTML.

## Formato

```
CALENDÁRIO DE VIGÊNCIAS - <hoje>   Filtro: <doc|todos>
| # | Doc | NT/Versão | Itens | Homologação | Produção | Situação |
LEGENDA: 🟦 homologação · 🟧 produção · **negrito** = vence em ≤ 30 dias
[FONTES] <NT> v<versão> - pág. do cronograma
```

## Erros
- `ERRO_DOCUMENTO_INVALIDO` → aceitar só NF-e, CT-e ou MDF-e
