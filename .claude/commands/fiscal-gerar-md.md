---
description: Gerar (ou regenerar) o MD de uma NT ou MOC a partir do JSON extraído — a IA formata, o Python não gera MD
argument-hint: <nt|moc> [--forcar]
---

# /fiscal-gerar-md

**Argumentos**: $ARGUMENTS
- NT: número (`2025.001`) ou caminho do JSON · MOC: nome (`MOC_CTe_VisaoGeral_v4.00`) ou caminho
- `--forcar`: sobrescrever MD existente sem perguntar

## Fluxo

### 1. Localizar o JSON
- NT: `catalogo/nt/<doc>/*<aaaa>_<nnn>*.json` · MOC: `catalogo/moc/<doc>/<nome>.json` (doc = `nfe|cte|mdfe`)
- Não achou: liste os JSONs do diretório e peça escolha (`ERRO_JSON_NAO_ENCONTRADO`)
- Várias versões da mesma NT: peça escolha (ou use a mais recente e diga qual)

### 2. Ler e validar
Leia o JSON inteiro (arquivo grande: leia em faixas com offset/limit; nunca resuma sem ler).
- NT: `nt`, `versao`, `documento`, `titulo`, `cronograma[]`, `secoes[]` (`tabela|regras|texto`), `estatisticas`
- MOC: `documento`, `versao`, `secoes[]` (com `subsecoes[]`), `regras_validacao[]`, `campos_leiaute[]`
- Vazio / sem `secoes` → pare e sugira `/fiscal-reextrair` (`ERRO_JSON_VAZIO`)
- MD já existe e não há `--forcar` → pergunte antes de sobrescrever (`ERRO_MD_EXISTENTE`)

### 3. Escrever o MD (mesmo nome do JSON, extensão `.md`)
1. **Cabeçalho**: `# NT 2025.001 v1.14b - <título>` / `# MOC CT-e v4.00 - <título>`, documento, arquivo de origem, SHA256
2. **Cronograma** (NT): tabela versão/homologação/produção, datas LITERAIS
3. **Seções** com numeração e título originais
4. **Rodapé**: estatísticas de extração + nota de que a fonte é o PDF original em `fontes/`

| Tipo | Formatação |
|---|---|
| `tabela` | bullets com campo em negrito (tabela MD se ≤ 4 colunas e ≤ 6 linhas) |
| `regras` | `**<id>**` + `cStat` + `efeito` + **mensagem**; condição em texto; `Exceção`/`Observação` como sub-bullet |
| `texto` | parágrafos; um bullet por item de lista da NT |

Gerais: datas `DD/MM/AAAA` em **negrito** · tags XML em `` `backticks` `` · marcação vira sufixo
(`_(alterado - amarelo)_`, `_(versão posterior - verde)_`, `_(EXCLUÍDO)_`; `SEM_MARCA` sem sufixo) ·
cor nunca prova vigência/exclusão sozinha · não inventar regra, cStat, tag ou data · tudo em pt-BR.

### 4. Validar
Todo `id` de regra do JSON aparece no MD · nenhuma data reescrita · nenhuma seção omitida.
Confira com um script (`python -I -c ...` comparando IDs/datas do JSON com o MD), não a olho.

### 5. Resumo
Documento gerado, caminho, contagens (seções/tabelas/regras/parágrafos), marcações encontradas, próximo passo.

## Erros
`ERRO_JSON_NAO_ENCONTRADO` · `ERRO_JSON_VAZIO` · `ERRO_MD_EXISTENTE`
