---
description: "Ler entrada/, organizar automaticamente em fontes/, atualizar manifest e catalogo"
---

# /catalogar-atualizar

Ler todos os arquivos em `entrada/`, identificar o tipo e documento fiscal,
mover para a pasta correta em `fontes/`, atualizar manifest.yaml e
CATALOGO_ARQUIVOS.md.

## Argumentos
- `--dry-run`: apenas mostra o que faria, sem mover (opcional)
- `--limpar`: remove entrada/ apos mover (padrao: sim, com verificacao)

**Argumentos fornecidos**: $ARGUMENTS

## Fluxo de execucao

### 0. Pre-etapa: Organizar entrada/

**REGRA: O usuario pode colar qualquer arquivo em `entrada/` e esta
etapa cuida de organizar automaticamente.**

#### 0.1 Listar tudo em entrada/
```powershell
Get-ChildItem "entrada/" -Recurse -File
```

Se entrada/ estiver vazio: pular para etapa 1 (buscar portais).

#### 0.2 Identificar cada arquivo
Para cada arquivo em entrada/, determinar:

**Tipo do arquivo:**
- `.pdf` = pode ser NT ou MOC
- `.docx` = pode ser MOC
- `.xsd` = schema XML
- `.xlsx` / `.xls` = tabela/informe
- `.zip` = pacote (extrair primeiro)

**Documento fiscal (pelo nome):**
- Nome contem `NFe`, `NF-e`, `NT2026.007`, `NT 2025.002` = NF-e
- Nome contem `CTe`, `CT-e`, `CTe_`, `PL_CTe` = CT-e
- Nome contem `MDFe`, `MDF-e`, `PL_MDFe` = MDF-e
- Nome contem `MOC` + `NF-e` ou `NFe` = MOC NF-e
- Nome contem `MOC` + `CTe` ou `CT-e` = MOC CT-e
- Nome contem `MOC` + `MDFe` ou `MDF-e` = MOC MDF-e
- Nome contem `ABI` = externa (NFe ABI)
- Nome contem `IT ` ou `Tabela` = tabela/informe

**Subtipo (NT vs MOC vs XSD):**
- Se e `.xsd` = XSD
- Se nome contem `MOC` ou `Manual` ou `Anexo` ou `VisaoGeral` = MOC
- Se nome contem `NT` ou `Nota_Tecnica` ou `Nota Tecnica` = NT
- Se e `.xlsx`/`.xls` = tabela

#### 0.3 Mover para pasta correta

| Tipo | Documento | Destino |
|---|---|---|
| NT | NF-e | `fontes/nfe/notas-tecnicas/` |
| NT | CT-e | `fontes/cte/notas-tecnicas/` |
| NT | MDF-e | `fontes/mdfe/notas-tecnicas/` |
| MOC | NF-e | `fontes/nfe/moc/` |
| MOC | CT-e | `fontes/cte/moc/` |
| MOC | MDF-e | `fontes/mdfe/moc/` |
| XSD | NF-e | `fontes/nfe/xsd/<nome_pacote>/` |
| XSD | CT-e | `fontes/cte/xsd/<nome_pacote>/` |
| XSD | MDF-e | `fontes/mdfe/xsd/<nome_pacote>/` |
| Tabela | qualquer | `fontes/externas/tabelas/` |
| Externa | qualquer | `fontes/externas/` |
| ZIP | qualquer | extrair para `entrada/` primeiro, depois re-classificar |

**Nomenclatura padrao:**
- NT: `<DOC>_NT_<numero>_v<versao>.pdf` (ex: `CTe_NT_2026_004_v1.00.pdf`)
- MOC: `MOC_<DOC>_<secao>_<versao>.pdf` (ex: `MOC_NFe_v7.00_Anexo_I_Leiaute.pdf`)
- XSD: manter nome original da pasta
- Tabela: manter nome original

#### 0.4 Verificar duplicatas
Antes de mover, calcular SHA256 e comparar com arquivos ja existentes em fontes/.
- Se hash identico = duplicata, remover de entrada/ sem mover
- Se hash diferente = versao diferente, alertar usuario

#### 0.5 Limpar entrada/
Apos mover tudo com sucesso:
- Verificar que todos os arquivos foram movidos
- Remover entrada/ (diretorios vazios)

### 1. Atualizar manifest.yaml
Registrar cada arquivo movido/criado no manifest com:
- id, documento, tipo, nt, versao, titulo, arquivo, sha256, status_ingestao

### 2. Atualizar CATALOGO_ARQUIVOS.md
Adicionar/atualizar entradas no catalogo para cada arquivo organizado.

### 3. Atualizar ARQUIVOS_NECESSARIOS.md
Marcar itens encontrados como OK. Se todos concluidos, versionar.

### 4. Relatorio final

```
ORGANIZACAO CONCLUIDA - <data>

Arquivos processados: N
- NTs movidas: N
- MOCs movidos: N
- XSDs movidos: N
- Tabelas movidas: N
- Duplicatas removidas: N

Manifest atualizado: sim
Catalogo atualizado: sim
entrada/ limpo: sim
```

## Erros tratados

| Erro | Acao |
|---|---|
| `ERRO_DOCUMENTO_NAO_IDENTIFICADO` | Arquivo nao e NF-e/CT-e/MDF-e -> mover para fontes/externas/ |
| `ERRO_TIPO_NAO_IDENTIFICADO` | Nao e NT/MOC/XSD -> alertar usuario, mover para externas/ |
| `ERRO_DUPLICATA_HASH_DIVERGENTE` | Mesmo arquivo com hash diferente -> alertar, manter ambos |
| `ERRO_ARQUIVO_CORROMPIDO` | SHA256 nao calculavel -> alertar, nao mover |