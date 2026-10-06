---
name: pesquisar-fontes-externas
description: Onde buscar informacoes fiscais (ACBr, FlexDocs, TecnoSpeed, TDN, portais oficiais). Como rotular "nao oficial". Como registrar em fontes/externas/. Como tratar conflito entre fontes.
allowed-tools: Bash(node:*), Read, WebFetch, WebSearch
---

# Skill: Pesquisar Fontes Externas

## Quando usar
- Quando precisar de informacao que nao esta nas fontes oficiais
- Quando precisar verificar se uma interpretacao esta correta
- Quando precisar buscar contexto sobre uma NT ou regra

## Hierarquia de fontes

```
OFICIAL (NT/MOC/XSD do portal)      SEMPRE prevalece
    |
    v
FORNECEDOR (FlexDocs, TecnoSpeed)   Rotular como "nao oficial"
    |
    v
FORUM (ACBr, blogs)                 Rotular como "nao oficial"
```

## Fontes confiaveis

### Oficiais (confianca ALTA)
**REGRA: Sempre consultar AMBOS os portais (fazenda.gov + dfe-portal.svrs).**

| Portal Primario | URL |
|---|---|
| Portal NF-e (Fazenda) | https://www.nfe.fazenda.gov.br |
| Portal CT-e (Fazenda) | https://www.cte.fazenda.gov.br |
| Portal NFS-e (RTC) | https://www.gov.br/nfse/pt-br/biblioteca/documentacao-tecnica |

| Portal Secundario | URL |
|---|---|
| Portal NF-e (SVRS) | https://dfe-portal.svrs.rs.gov.br/NFe/Documentos |
| Portal CT-e (SVRS) | https://dfe-portal.svrs.rs.gov.br/Cte/Documentos |
| Portal MDF-e (SVRS) | https://dfe-portal.svrs.rs.gov.br/Mdfe/Documentos |

### Fornecedores (confianca MEDIA)
| Fonte | URL | Conteudo |
|---|---|---|
| FlexDocs NF-e | https://flexdocs.net/guiaNFe/ | Guias detalhados de uso |
| FlexDocs CT-e | https://flexdocs.net/guiaCTe/ | Guias detalhados de uso |
| TecnoSpeed Blog | https://blog.tecnospeed.com.br/ | Analises de NTs |
| Unimake Blog | https://blog.unimake.com.br/ | Artigos sobre schemas |

### Comunitarias (confianca BAIXA/MEDIA)
| Fonte | URL | Cuidado |
|---|---|---|
| Forum ACBr | https://www.projetoacbr.com.br/forum/ | Informacoes podem nao ser oficiais |
| Discord ACBr | discord.gg/projetoacbr | Discussao em tempo real |
| Reforma Tributaria | https://www.reformatributaria.com/ | Noticias sobre RTC |

## Como registrar uma fonte externa

Crie um arquivo em `fontes/externas/`:

```markdown
# <titulo>

- URL: <url>
- Data de acesso: <data>
- Nivel de confianca: oficial | fornecedor | forum
- Resumo: <resumo proprio, sem copiar texto longo>
- Confirma fonte oficial: sim/nao/nao se aplica
- Contradiz fonte oficial: sim/nao
```

## Conflito entre fontes

Se uma fonte externa contradiz a oficial:
1. Mostrar as duas versoes
2. Prevalece a oficial
3. Registrar em `docs/duvidas-abertas.md`

## Erros

- `ERRO_CONFLITO_FONTES` - mostrar as duas, prevalece a oficial
- `ERRO_LINK_QUEBRADO` - URL nao acessivel