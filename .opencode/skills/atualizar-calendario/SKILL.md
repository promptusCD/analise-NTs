---
name: atualizar-calendario
description: Como extrair datas de vigencia das NTs, atualizar calendario.yaml e gerar MD/HTML. Granularidade por item. Nunca inventar data. Calcular situacao automaticamente.
allowed-tools: Bash(node:*), Read
---

# Skill: Atualizar Calendario

## Quando usar
- Ao ingerir uma NT nova (extrair datas do cronograma)
- Quando precisar saber a situacao atual de um item
- Quando precisar gerar o calendario em MD ou HTML

## Fonte Unica

`calendario/calendario.yaml` e a FONTE UNICA. Os arquivos:
- `calendario/CALENDARIO.md` (gerado)
- `calendario/calendario.html` (gerado)

NUNCA edite .md ou .html diretamente. Edite o .yaml e rode o script.

## Granularidade por item

Uma NT pode ter multiplos itens com datas DIFERENTES.

Exemplo - NT CT-e 2026.004 v1.00:
```
Bloco A: homologacao 13/10/2026, producao 16/11/2026
  - campos de valor liquido, excecao aliquotas, ajuste vTotDFe,
    eliminacao EPEC/FSDA, emissao offline, evento credito presumido

Bloco B: homologacao 16/11/2026, producao 14/12/2026
  - mudanca estrutura CT-e Simplificado

Bloco C: homologacao 01/02/2027, producao 01/03/2027
  - validacao ICMS previsto (regras 1051-1053)
```

## Como extrair datas

### 1. Da tabela de cronograma (geralmente pagina 3)
- Versao, data de homologacao, data de producao

### 2. De observacoes dentro das regras
- Ex: "Implantacao: homologacao 01/02/2027, producao 01/03/2027"
- Essas datas NAO estao na tabela de cronograma

### 3. De excecoes
- Ex: "Ate 05/10/2026" (texto literal, nao reinterpretar)

## Regras de atualizacao

1. **Nunca inventar data.** Se a NT nao informa: `homologacao: PENDENTE`
2. **Atualizar linha existente** quando sair nova versao da mesma NT
3. **Guardar historico** em `historico_versoes`
4. **Calcular situacao** pela data de hoje:
   - `futura` - homologacao nao comecou
   - `em_homologacao` - entre inicio e fim
   - `prazo_homologacao_encerrado` - homologacao encerrou
   - `em_producao` - producao ja comecou
5. **Texto literal**: "Ate 05/10/2026" guardar como `texto_original`

## Gerar saida

```bash
node scripts/js/gerar_calendario.js
```

Gera:
- `calendario/CALENDARIO.md` - com emojis 🟦 🟧
- `calendario/calendario.html` - com celulas coloridas

## Erros

- `ERRO_DATA_NAO_ENCONTRADA` - criar "pendente", nao inventar
- `ERRO_DATAS_CONFLITANTES` - mostrar as duas, marcar revisao

## Referencia
Leia `docs/REFERENCIA.md` secao 6 para detalhes do calendario.