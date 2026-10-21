---
description: Detalhar uma regra de validação (status, NT de origem, cStat, quem aplica, vigência)
argument-hint: <id da regra ou cStat> [NF-e|CT-e|MDF-e]
---

# /fiscal-regra

**Argumentos**: $ARGUMENTS (1º token = ID da regra, ex. `C17-10`, ou cStat numérico, ex. `229`; 2º, opcional = documento)

## Fluxo

1. Rode `date` para a data de hoje.
2. **Buscar**: `catalogo/regras/<doc>.json` (se existir); senão Grep pelo ID/cStat em
   `catalogo/moc/<doc>/*.json` (`regras_validacao`) e `catalogo/nt/<doc>/*.json` (seções do tipo `regras`).
   Documento não informado: procure nos três e liste onde achou.
3. **Vários resultados** (cStat repete entre modelos/documentos; uma regra pode ter vários IDs): liste
   todos em tabela (ID, doc, modelo, NT) e detalhe cada um — não escolha um em silêncio.
   - Nas NTs de CT-e o `id` é só o número da linha e **reinicia a cada tabela** (`001`, `002`…): identifique a
     regra por `id_unico` (`<seção>:<id>`) ou pelo `cStat`, e cite a seção.
   - Em tabelas **sem coluna de ID** (CT-e 1054/1055/326, MDF-e 684) o `id` é vazio: busque pelo `cStat`
     (`id_unico` = `<seção>:cStat<N>`).
   - A `mensagem` do JSON é a completa (coluna "Descrição Erro"); cite-a inteira.
4. **Histórico**: linha do tempo da regra (MOC original → NTs que alteraram/excluíram, cada uma com
   versão e página). Cor nunca prova sozinha: confirme na "Descrição das alterações".
5. **Status**: `ATIVA` | `ALTERADA` | `EXCLUIDA` | `NOVA`. A **situação de vigência** é separada
   (`futura | em_homologacao | em_producao | excluida`) e vem das datas.
6. **Excluída**: abra com "ATENÇÃO: regra EXCLUÍDA pela NT X vY" e não a explique como vigente.

## Formato

```
[RESUMO]  Regra <ID> - <status> - <resumo>
[DETALHE] ID / cStat / Descrição / Modelo / Quem aplica / Efeito / Mensagem
          NT de origem (NT vX, pág. N) / Marcação
[HISTÓRICO] <NT/MOC> v<versão> - criada|alterada|excluída - data
[VIGÊNCIA] Situação / Homologação / Produção (hoje: <data>)
[IMPACTO NO EMISSOR]
[FONTES] <documento> - <NT/MOC> v<versão> - pág. <N> - <marcação>
```

## Erros
- `ERRO_REGRA_NAO_ENCONTRADA` → `NAO ENCONTRADO NAS FONTES`; sugerir conferir o ID ou ingerir a NT/MOC
- `ERRO_PARAMETRO_INVALIDO` → explicar o formato esperado
