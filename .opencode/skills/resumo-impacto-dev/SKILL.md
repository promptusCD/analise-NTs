---
name: resumo-impacto-dev
description: Como transformar uma NT em checklist de implementacao para desenvolvedores. Lista de campos novos/alterados/removidos, regras novas, rejeicoes, eventos, ambientes e datas.
allowed-tools: Bash(node:*), Read
---

# Skill: Resumo de Impacto para Desenvolvedor

## Quando usar
- Quando precisar gerar um checklist de implementacao a partir de uma NT
- Quando o time de desenvolvimento precisar saber o que mudar no sistema
- Quando precisar listar campos, regras e eventos novos/alterados/excluidos

## Formato de saida

O command `/impacto <nt>` gera um resumo com:

```
CAMPOS NOVOS:
- <tag> (<grupo pai>) [<modelos>] - descricao

CAMPOS ALTERADOS:
- <tag> (<grupo pai>) [<modelos>] - o que mudou

CAMPOS EXCLUIDOS:
- <tag> (<grupo pai>) [<modelos>] - motivo

REGRAS NOVAS:
- <ID> (cStat <codigo>) - descricao - quem aplica

REGRAS ALTERADAS:
- <ID> (cStat <codigo>) - o que mudou

REGRAS EXCLUIDAS:
- <ID> (cStat <codigo>) - motivo da exclusao

EVENTOS NOVOS:
- <tpEvento> - <nome> - autorizador - schema

REJEICOES NOVAS:
- <cStat> - <mensagem> - quando ocorre

DATAS:
- Homologacao: <data>
- Producao: <data>

IMPACTO NO EMISSOR:
- O que o sistema precisa implementar
- O que precisa ser removido
- O que precisa ser testado
```

## Como gerar

### 1. Ler a NT extraida
Consulte `catalogo/nt/<doc>/<nt>_v<versao>.json`

### 2. Ler o catalogo de campos
Consulte `catalogo/campos/<doc>.json` para cruzar tags com XSD

### 3. Ler o catalogo de regras
Consulte `catalogo/regras/<doc>.json` para regras de validacao

### 4. Ler o calendario
Consulte `calendario/calendario.yaml` para datas de vigencia

### 5. Compilar o resumo
Combine todas as fontes em um checklist acionavel.

## Exemplo de uso

```
/impacto NT-CT-e-2026.004
```

Saida: checklist completo do que o time de desenvolvimento precisa
implementar para a NT CT-e 2026.004, incluindo campos, regras,
eventos, rejeicoes e datas.

## Importante
- Sempre citar a fonte (NT, versao, pagina)
- Indicar a situacao de cada item (futura/homologacao/producao)
- Separar por modelo quando aplicavel (CT-e, CT-e OS, GTV-e, CT-e Simp.)