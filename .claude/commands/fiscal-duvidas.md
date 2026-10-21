---
description: Listar, priorizar e registrar dúvidas abertas do projeto (docs/duvidas-abertas.md)
argument-hint: [NF-e|CT-e|MDF-e] [--prioridade alta|media|baixa] [--registrar]
---

# /fiscal-duvidas

**Argumentos**: $ARGUMENTS

Fonte: `docs/duvidas-abertas.md` (formato definido no próprio arquivo). Se não existir, crie-o
a partir do modelo em `docs/duvidas-abertas.md` do repositório ou avise que está vazio.

## Modo listar (padrão)

1. Rode `date`. Leia o arquivo; filtre por documento/prioridade se informados.
2. Prioridade: **ALTA** = impede implementação ou gera erro em produção · **MEDIA** = afeta qualidade,
   há workaround · **BAIXA** = inconveniente.
3. Formato:

```
DÚVIDAS ABERTAS - <data>   Filtro: <doc|todas>   Total: N (ALTA x, MEDIA y, BAIXA z)
== PRIORIDADE ALTA ==
[#001] <título>
- Documento / NT-MOC / Página / Trecho / O que parece errado / Impacto / Status
== MEDIA == ... == BAIXA == ...
RESUMO: impedem implementação N · com workaround N · acadêmicas N
```

4. Para cada ALTA sugira como resolver (outra fonte, testar em homologação) e quem responde
   (SEFAZ, fornecedor, fórum — rotular não oficial).
5. Termine com `FONTES` (as NT/MOC citadas em cada dúvida).

## Modo `--registrar`

Registra uma dúvida nova (regras 8 e 9 do AGENTS.md: contradição entre fontes, cor sem item na
descrição, campo de NT ausente no XSD, extração suspeita). Pergunte/infira os campos, atribua o
próximo `#NNN`, **acrescente** ao fim do arquivo (nunca reescreva as existentes) com `Status: pendente`
e a data de hoje. Evite duplicatas: Grep antes por NT/regra/trecho.

## Resolver

Mudança de status (`pendente` → `resolvida`) só com confirmação do usuário; registre a fonte que resolveu.
