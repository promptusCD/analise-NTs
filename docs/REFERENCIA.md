# REFERENCIA - Contexto Completo do Projeto fiscal-dfe-knowledge

Este documento consolida todo o contexto, decisoes arquiteturais, fontes e
adaptacoes feitas durante o planejamento do projeto. Leia este arquivo antes
de qualquer alteracao no repositorio.

---

## 1. O Que E Este Projeto

Desenvolvedores de sistemas de emissao fiscal brasileiros precisam acompanhar
Notas Tecnicas (NTs), Manuais de Orientacao do Contribuinte (MOCs) e schemas
XML (XSDs) de NF-e/NFC-e, CT-e/CT-e OS/GTV-e/CT-e Simplificado e MDF-e.

Esses documentos vem em PDF com marcações visuais de cor (amarelo = novo,
verde = alterado em versao posterior, vermelho riscado = excluido) que sao
extremamente dificeis de ler e processar manualmente.

Este projeto transforma esses documentos brutos em conhecimento organizado,
consultavel e com fonte citada. Funciona como "uma biblioteca com um
bibliotecario que sempre cita a pagina".

### Objetivos especificos:

- Extrair informacoes de PDFs mantendo as marcações de cor
- Catalogar regras de validacao, campos e eventos por documento fiscal
- Manter um calendario de vigencias (homologacao/producao)
- Fornecer commands para consulta rapida com citacao de fontes
- Detectar novidades nos portais oficiais automaticamente
- Gerar checklists de implementacao para times de desenvolvimento

---

## 2. Arquitetura: Hibrida Python + JavaScript

```
+===================================================================+
|              ARQUITETURA HIBRIDA PYTHON + JAVASCRIPT               |
+===================================================================+
|                                                                    |
|  EXTRACTION LAYER (Python 3.11+)                                   |
|  +-------------------------------------------------------------+  |
|  |  extrair_nt.py     PDF --> JSON + MD com marcações de cor   |  |
|  |  catalogar_xsd.py  XSD --> JSON catalogo de campos/regras   |  |
|  |                                                             |  |
|  |  Bibliotecas: pymupdf, python-docx, lxml, pyyaml            |  |
|  |  Output: stdout JSON / arquivos em catalogo/                |  |
|  +-------------------------------------------------------------+  |
|       |  child_process.spawn() ou JSON files                      |
|       v                                                            |
|  ORCHESTRATION LAYER (Node.js)                                     |
|  +-------------------------------------------------------------+  |
|  |  manifest.js         gerencia manifest.yaml                  |  |
|  |  calendario.js       calcula situações, gera MD/HTML         |  |
|  |  docs_fiscais.js     regenera blocos AUTO                    |  |
|  |  consultar.js        responde com citações                   |  |
|  |  detectar_novidades.js  compara portais vs manifest          |  |
|  |                                                             |  |
|  |  Bibliotecas: js-yaml, ejs/nunjucks, node-fetch              |  |
|  +-------------------------------------------------------------+  |
|       |                                                            |
|       v                                                            |
|  QUERY LAYER (CLI + opencode)                                      |
|  +-------------------------------------------------------------+  |
|  |  /ingerir-nt <arquivo>    orquestra: move + extrai + cataloga|  |
|  |  /consultar <pergunta>    resposta mastigada com fontes      |  |
|  |  /regra <id>              detalhe de regra + status          |  |
|  |  /campo <tag>             dados XSD + NT                    |  |
|  |  /calendario [doc]        vigências com cores               |  |
|  |  /impacto <nt>            checklist para o dev               |  |
|  |  /atualizar-fontes        busca novidades nos portais       |  |
|  |  /duvidas                 lista priorizada                   |  |
|  +-------------------------------------------------------------+  |
|                                                                    |
|  FUTURE: RAG LAYER                                                 |
|  +-------------------------------------------------------------+  |
|  |  Vector DB (chromadb/qdrant)                                  |  |
|  |  Embeddings dos catálogos + docs-fiscais                     |  |
|  |  Consulta semântica além de keyword matching                |  |
|  +-------------------------------------------------------------+  |
+===================================================================+
```

### Por que Python para extracao?

A biblioteca PyMuPDF (fitz) e insuperavel para extrair informacoes visuais
de PDFs. Ela fornece:
- Cada span de texto com bbox (x, y, largura, altura)
- Retangulos preenchidos (page.get_drawings()) para detectar fundo colorido
- Linhas horizontais para detectar riscado
- Flags de formatação (negrito, italico, strikeout)

Nenhuma biblioteca JavaScript oferece esse nivel de controle sobre PDFs.
Por isso, a extracao roda em Python e o resultado e consumido pelo Node.js
via child_process ou arquivos JSON.

### Por que JavaScript para o resto?

- Ecossistema rico para geracao de HTML (ejs, nunjucks)
- Facilidade com YAML (js-yaml)
- Integracao nativa com CLI (Node.js)
- Futuro: RAG com embeddings (langchain.js, etc.)

---

## 3. Estrutura de Diretorios

```
fiscal-dfe-knowledge/
|
+-- README.md                    # Documentacao principal do projeto
+-- AGENTS.md                    # Regras permanentes da IA
+-- REFERENCIA.md                # Este arquivo (contexto do projeto)
+-- manifest.yaml                # Registro de TODOS os fontes (hash, url, versao)
+-- package.json                 # Dependencias Node.js
+-- requirements.txt             # Dependencias Python
|
+-- entrada/                     # Area de recebimento permanente na raiz (PDFs novos antes de ingerir)
|   +-- *.pdf, *.docx           # NTs e MOCs brutos
|   +-- XSDs/                    # Pacotes de schemas XML
|
+-- docs-fiscais/                # UM ARQUIVO POR DOCUMENTO FISCAL
|   +-- _COMUM.md                # Conceitos transversais (cStat, ambientes, SVRS, IBS/CBS)
|   +-- _GLOSSARIO.md            # Termos e definicoes
|   +-- NFE.md                   # NF-e (55) e NFC-e (65)
|   +-- CTE.md                   # CT-e (57), CT-e OS (67), GTV-e (64), CT-e Simplificado
|   +-- MDFE.md                  # MDF-e (58)
|
+-- fontes/                      # Arquivos originais organizados
|   +-- nfe/
|   |   +-- notas-tecnicas/      # PDF/DOCX das NTs NF-e
|   |   +-- moc/                 # MOC NF-e por versao
|   |   +-- xsd/                 # Pacotes XSD NF-e por versao
|   +-- cte/
|   |   +-- notas-tecnicas/      # PDF/DOCX das NTs CT-e
|   |   +-- moc/                 # MOC CT-e por versao
|   |   +-- xsd/                 # Pacotes XSD CT-e por versao
|   +-- mdfe/
|   |   +-- notas-tecnicas/      # PDF/DOCX das NTs MDF-e
|   |   +-- moc/                 # MOC MDF-e por versao
|   |   +-- xsd/                 # Pacotes XSD MDF-e por versao
|   +-- externas/                # Resumos de fontes nao oficiais
|
+-- catalogo/                    # Camada "mastigada" (gerada por scripts)
|   +-- nt/<doc>/<nt>_v<ver>.json + .md   # NT extraida com marcações
|   +-- regras/<doc>.json         # Indice de regras de validacao
|   +-- campos/<doc>.json         # Tags do leiaute (de XSD + NT)
|   +-- legendas/<doc>.yaml       # Mapa cor->versao de cada NT
|
+-- calendario/
|   +-- calendario.yaml           # FONTE UNICA de vigencias
|   +-- CALENDARIO.md             # Gerado pelo script
|   +-- calendario.html           # Gerado, com cores azul/laranja
|
+-- scripts/
|   +-- python/                   # Extracao (PyMuPDF)
|   |   +-- extrair_nt.py         # PDF/DOCX -> JSON/MD com marcações
|   |   +-- catalogar_xsd.py      # XSD -> catalogo de campos
|   +-- js/                       # Orquestracao (Node.js)
|       +-- gerar_calendario.js   # YAML -> MD/HTML
|       +-- atualizar_docs_fiscais.js  # Regenera blocos AUTO
|       +-- verificar_manifest.js # Checa hashes e arquivos
|       +-- detectar_novidades.js # Compara portais vs manifest
|       +-- consultar.js          # Responde com citações
|
+-- tests/
|   +-- fixtures/                 # PDFs de exemplo para testes
|   +-- python/                   # Testes dos scripts Python
|   +-- js/                       # Testes dos scripts JS
|   +-- golden/                   # Perguntas e respostas esperadas
|
+-- backlog/                      # Uma tarefa por arquivo
+-- docs/
|   +-- duvidas-abertas.md        # Inconsistencias e pendencias
|   +-- legenda-cores.md          # Documentacao da deteccao de cor
|   +-- ARQUIVOS_NECESSARIOS.md   # Lista de downloads manuais
|
+-- .opencode/                    # Commands, agents, skills
+-- .github/workflows/            # CI/CD semanal
```

### Diferenca entre fontes/ e catalogo/

- `fontes/` = arquivos ORIGINAIS do governo, NUNCA editados
- `catalogo/` = versao "mastigada" gerada por scripts, com marcações de cor
  interpretadas, classificacoes (NOVA, ALTERADA, EXCLUIDA) e metadados

### Diferenca entre docs-fiscais/ e catalogo/

- `docs-fiscais/` = documento HUMANO + blocos AUTO gerados por script
  - O que esta FORA de blocos AUTO e editado manualmente
  - O que esta DENTRO de blocos AUTO nunca deve ser editado
- `catalogo/` = dados estruturados (JSON) gerados integralmente por scripts

---

## 4. Conceitos Fundamentais

### 4.1 Marcacoes de Cor nas NTs

As NTs usam marcações visuais no PDF para indicar mudancas:

| Marcação Visual | Codigo | Significado |
|---|---|---|
| Fundo amarelo (#FFFF00) | AMARELO | Trecho novo/alterado na versao associada a essa cor |
| Fundo verde (#00FF00) | VERDE | Trecho alterado em versao posterior |
| Texto vermelho riscado | EXCLUIDO | Regra/texto excluido |
| Sem marcação | SEM_MARCA | Inalterado ou regra nova inteira |

**IMPORTANTE:** A cor nunca prova sozinha. Sempre cruzar com a secao
"Descricao das alteracoes" do proprio documento.

Cores tambem podem ser:
- **ESTRUTURAL**: cabecalho de tabela, linhas de grupo (ignorar)
- **DADO**: cores que definem informacao (ex: areas de livre comercio)
- **AMBIGUA**: precisa revisao humana

### 4.2 Hierarquia de Fontes

1. **Oficial** (portal do governo): NT, MOC, XSD - SEMPRE prevalece
2. **Fornecedor** (FlexDocs, TecnoSpeed, Unimake): documentacao tecnica util
3. **Forum** (ACBr, blogs): informacoes rapidas mas nao oficiais

Conflito entre fontes: mostrar as duas, prevalece a oficial, registrar em
`docs/duvidas-abertas.md`.

### 4.3 Vigencia

Toda regra tem uma situacao calculada pela data de hoje:
- `futura` - ainda nao entrou em vigor
- `em_homologacao` - periodo de teste
- `prazo_homologacao_encerrado` - homologacao encerrou, aguardando producao
- `em_producao` - vigente em producao
- `excluida` - foi revogada por NT posterior

Nunca usar memoria para calcular vigencia. Sempre comparar com a data atual.

### 4.4 Blocos AUTO

Nos docs-fiscais, blocos gerados por script usam marcadores:
```
<!-- AUTO:BEGIN regras -->
... conteudo gerado automaticamente ...
<!-- AUTO:END regras -->
```

**NUNCA editar manualmente dentro de um bloco AUTO.**
O script `atualizar_docs_fiscais.js` regenera esses blocos.

---

## 5. O Catalogo (Camada "Mastigada")

O catalogo e o coracao do projeto. Ele transforma PDFs brutos em JSON
estruturado e consultavel.

### 5.1 catalogo/nt/<doc>/<nt>_v<versao>.json

Extracao completa de uma NT com marcações interpretadas.

```json
{
  "nt": "2026.007",
  "versao": "1.10",
  "documento": "NF-e",
  "titulo": "Emissao por Contribuinte exclusivo do IBS/CBS",
  "arquivo_origem": "fontes/nfe/notas-tecnicas/NT_2026_007_v1.10.pdf",
  "sha256": "...",
  "extraido_em": "2026-10-06T...",
  "cronograma": [
    {
      "versao": "1.00",
      "homologacao": "2026-09-01",
      "producao": "2026-11-03"
    },
    {
      "versao": "1.10",
      "homologacao": "Ate 05/10/2026",
      "producao": "2026-11-03"
    }
  ],
  "itens": [
    {
      "pagina": 6,
      "texto": "C17-10 - IE do emitente nao informada",
      "marcacoes": [
        {"tipo": "EXCLUIDO", "hex": "#FF0000", "versao_inferida": "1.00"}
      ],
      "classificacao_cor": "REVISAO"
    }
  ]
}
```

### 5.2 catalogo/regras/<doc>.json

Indice de todas as regras de validacao de um documento fiscal.

```json
{
  "documento": "NF-e",
  "regras": [
    {
      "id": "C17-10",
      "cStat": "229",
      "resumo": "IE do emitente nao informada",
      "modelo": "55",
      "nt_origem": "2026.007",
      "versao_origem": "1.00",
      "status": "EXCLUIDA",
      "vigencia": "excluida",
      "aplicacao": "todas as SEFAZ Autorizadoras",
      "nt_exclusao": "2026.007",
      "versao_exclusao": "1.00"
    }
  ]
}
```

### 5.3 catalogo/campos/<doc>.json

Tags do leiaute extraidas dos XSDs, com metadados.

```json
{
  "documento": "CT-e",
  "pacote_xsd": "PL_CTe_400_NT2026.004 RTC_1.00",
  "campos": [
    {
      "caminho_completo": "infCte/vPrest/vTPrestLiq",
      "tipo": "TDec_1302",
      "minOccurs": "0",
      "maxOccurs": "1",
      "tamanho": "13,2",
      "pattern": null,
      "enumeration": null,
      "documentacao": "Valor liquido da prestacao sem tributos",
      "arquivo_xsd": "cte_v4.00.xsd",
      "nt_origem": "2026.004",
      "classificacao": "NOVO"
    }
  ]
}
```

### 5.4 catalogo/legendas/<doc>.yaml

Mapa cor -> versao, deduzido pela concordancia entre itens e marcações.

```yaml
documento: NF-e
nt: "2026.007"
legenda:
  AMARELO:
    versao: "1.00"
    hex_proximo: "#FFFF00"
    confianca: ALTA
  VERDE:
    versao: "1.10"
    hex_proximo: "#00FF00"
    confianca: ALTA
  EXCLUIDO:
    cor_texto: "#FF0000"
    riscado: true
    confianca: ALTA
```

---

## 6. Calendario de Vigencias

### 6.1 Fonte Unica

`calendario/calendario.yaml` e a fonte unica. Os arquivos `.md` e `.html`
sao gerados por `scripts/js/gerar_calendario.js`.

### 6.2 Granularidade

Uma NT pode ter multiplos itens com datas diferentes. O calendario trabalha
por ITEM, nao so por NT.

Exemplo: NT CT-e 2026.004 v1.00 tem 3 blocos de datas:
- Bloco A: homologacao 13/10/2026, producao 16/11/2026
- Bloco B: homologacao 16/11/2026, producao 14/12/2026
- Bloco C: homologacao 01/02/2027, producao 01/03/2027

### 6.3 Calculo de Situacao

A situacao e calculada pela data de hoje, nunca digitada:
- `futura` - data de homologacao ainda nao chegou
- `em_homologacao` - entre inicio e fim de homologacao
- `prazo_homologacao_encerrado` - homologacao encerrou, producao nao comecou
- `em_producao` - data de producao ja passou

### 6.4 Cores no HTML

- Azul (🟦) = homologacao
- Laranja (🟧) = producao
- Negrito = vence em ate 30 dias

---

## 7. Docs Fiscais

### 7.1 Template

Cada arquivo (NFE.md, CTE.md, MDFE.md) segue este template:

```markdown
# <DOC> - <nome completo>
## 1. Identificacao                    (manual)
## 2. Fontes vigentes                  (AUTO: fontes_vigentes)
## 3. Mapa do leiaute                  (manual + AUTO: grupos)
## 4. Eventos                          (manual + AUTO: eventos)
## 5. Regras de validacao - indice     (AUTO: regras)
## 6. Mudancas em andamento            (AUTO: em_andamento)
## 7. Armadilhas e padroes de leitura  (manual - checklist para a IA)
## 8. Linha do tempo de NTs            (AUTO: linha_do_tempo)
## 9. Duvidas abertas deste documento  (AUTO: duvidas)
```

### 7.2 Armadilhas Ja Conhecidas

**Comum aos tres:**
- Regra nova inteira muitas vezes nao vem marcada com cor
- Texto extraido de PDF sem camada visual faz regra excluida parecer vigente
- Um mesmo numero de versao pode ter multiplas linhas no cronograma

**NF-e (NT 2026.007):**
- Contribuinte exclusivo do IBS/CBS = nao informa emit/IE
- Autorizacao centralizada na SVRS
- NFC-e (65) sem IE e rejeitada
- LCC-RFB de Producao deve ser usada mesmo em homologacao

**CT-e (NT 2026.004):**
- IBS/CBS sao "por fora" mas compoem vTPrest
- Em 2026 vTotDFe repete vTPrest (nao soma IBS/CBS)
- EPEC (tpEmis=4) e FSDA (tpEmis=5) eliminados
- Contingencia offline e tpEmis=2
- CT-e Simplificado: IBSCBS sai de imp e vai para det

**MDF-e:**
- Nenhuma NT ingerida ainda
- Criar arquivo com PENDENTE onde faltar fonte

---

## 8. Mapeamento de Fontes

### 8.1 Portais Oficiais

**REGRA: Sempre consultar AMBOS os portais (fazenda.gov + dfe-portal.svrs).**
O portal da fazenda.gov e o primario (MOC, NTs oficiais).
O portal da SVRS e o secundario (XSDs, schemas, complementos).

| Portal Primario | URL | Documentos |
|---|---|---|
| NF-e (Fazenda) | https://www.nfe.fazenda.gov.br | MOC, NTs, Tabelas, Informes NF-e/NFC-e |
| CT-e (Fazenda) | https://www.cte.fazenda.gov.br | MOC, NTs CT-e/CT-e OS/GTV-e |
| NFS-e (RTC) | https://www.gov.br/nfse/pt-br/biblioteca/documentacao-tecnica | NTs NFS-e RTC |

| Portal Secundario | URL | Documentos |
|---|---|---|
| NF-e (SVRS) | https://dfe-portal.svrs.rs.gov.br/NFe/Documentos | XSDs, schemas, eventos NF-e/NFC-e |
| CT-e (SVRS) | https://dfe-portal.svrs.rs.gov.br/Cte/Documentos | XSDs, schemas CT-e |
| MDF-e (SVRS) | https://dfe-portal.svrs.rs.gov.br/Mdfe/Documentos | XSDs, NTs MDF-e (nao tem portal proprio) |

### 8.2 Fontes Secundarias (Fornecedores)

| Fonte | URL | Nivel | Conteudo |
|---|---|---|---|
| FlexDocs | https://flexdocs.net/guiaNFe/ | fornecedor | Guias detalhados de uso NF-e |
| FlexDocs CT-e | https://flexdocs.net/guiaCTe/ | fornecedor | Guias detalhados de uso CT-e |
| TecnoSpeed Blog | https://blog.tecnospeed.com.br/ | fornecedor | Analises de NTs |
| TecnoSpeed Docs | https://atendimento.tecnospeed.com.br | fornecedor | Documentacao tecnica |
| Unimake Blog | https://blog.unimake.com.br/ | fornecedor | Artigos sobre schemas |

### 8.3 Fontes Comunitarias

| Fonte | URL | Nivel | Cuidado |
|---|---|---|---|
| Forum ACBr | https://www.projetoacbr.com.br/forum/ | forum | Informacoes podem nao ser oficiais |
| Discord ACBr | discord.gg/projetoacbr | forum | Discussao em tempo real |
| Reforma Tributaria | https://www.reformatributaria.com/ | blog | Noticias sobre RTC |

### 8.4 Hierarquia

```
OFICIAL (NT/MOC/XSD do portal)      SEMPRE prevalece
    |
    v
FORNECEDOR (FlexDocs, TecnoSpeed)   Rotular como "nao oficial"
    |
    v
FORUM (ACBr, blogs)                 Rotular como "nao oficial"
```

Conflito: mostrar as duas versoes, prevalece a oficial, registrar duvida.

---

## 9. Sequencia de Changes (Roadmap)

| Change | Nome | Objetivo | Dependencias |
|---|---|---|---|
| 1 | fase-0-setup | Estrutura, gitignore, package.json, requirements.txt, AGENTS.md, README | - |
| 2 | fase-0.5-organizacao | Mover entrada/ para fontes/, criar ARQUIVOS_NECESSARIOS, CATALOGO_ARQUIVOS, versionamento | fase-0 |
| 3 | fase-1-extrator-nt | extrair_nt.py + legenda de cores + manifest | fase-0 |
| 4 | fase-2-calendario | calendario.yaml + gerar_calendario.js | fase-0 |
| 5 | fase-3-docs-fiscais | NFE.md, CTE.md, MDFE.md + atualizar_docs_fiscais.js | fase-1, fase-2 |
| 6 | fase-4-xsd-moc | catalogar_xsd.py + ingestao de MOCs | fase-0 |
| 7 | fase-5-commands-skills | Commands do .opencode + skills (self-contained) | fase-1 a 4 |
| 8 | fase-6-qualidade | test_golden.py/js + deteccao de inconsistencias | fase-1 a 5 |
| 9 | fase-7-fontes-externas | Busca em portais (fazenda.gov + svrs) + GitHub Actions | fase-1 |

---

## 10. Adaptacoes do Prompt Original para JavaScript

O prompt original foi escrito para Python. Aqui estao as adaptacoes:

| Python (original) | JavaScript (adaptado) | Observacao |
|---|---|---|
| pymupdf (fitz) | Python via child_process | PyMuPDF e insuperavel para PDF |
| python-docx | mammoth (leitura) | DOCX e secundario |
| lxml | libxmljs2 ou fast-xml-parser | Para XSD parsing |
| pyyaml | js-yaml | YAML em JS |
| pytest | vitest ou jest | Testes em JS |
| jinja2 | ejs ou nunjucks | Templates HTML |
| scripts/*.py | scripts/python/ + scripts/js/ | Separados por linguagem |
| tests/*.py | tests/python/ + tests/js/ | Separados por linguagem |

### Nomes de arquivos Python (mantidos do original):
- `extrair_nt.py` - extracao de PDF com marcações de cor
- `catalogar_xsd.py` - catalogacao de schemas XML

### Nomes de arquivos JavaScript (novos):
- `gerar_calendario.js` - YAML -> MD/HTML
- `atualizar_docs_fiscais.js` - regenera blocos AUTO
- `verificar_manifest.js` - checa hashes e arquivos
- `detectar_novidades.js` - compara portais vs manifest
- `consultar.js` - responde com citacoes

---

## 11. XSDs Disponiveis vs Necessarios

### Ja temos (em entrada/XSDs/ - aguardando organizacao para fontes/):

| Pacote | Pasta | Conteudo | Status |
|---|---|---|---|
| NFe-PL_010f_v1.04 | entrada/XSDs/ | 5 XSDs (nfe_v4.00, leiauteNFe_v4.00, tiposBasico_v4.00, DFeTiposBasicos_v1.00, xmldsig) | OK |
| NFe-PL_010b_v1.30 | entrada/XSDs/NFe-PL_010b_NT2025_002_v1.30/ | Pacote NF-e NT 2025.002 v1.30 | OK |
| NFe-Eventos_RTC | entrada/XSDs/ | 17 XSDs de eventos (e110001, e112110-e112150, e211110-e211150, e212110, e212120, e412120, e412130) | OK |
| Eventos_RTC_v1.30 | entrada/XSDs/NT 2025.002 v1.30 - RTC-Eventos_RTC/ | Eventos RTC NF-e v1.30 | OK |
| Evento_211110_v1.40 | entrada/XSDs/NT 2025.002 v1.40-Schema_Evento_211110.../ | Evento credito presumido | OK |
| Eventos_Fisco_v1.23 | entrada/XSDs/BT 2019.001 v.1.23- Eventos do Fisco/ | Eventos do Fisco (Insucesso CTe, RegPass Auto MDFe) | OK |
| PL_CTe_400_NT2026.004 RTC_1.00 | entrada/XSDs/ | ~50+ XSDs (CT-e, CT-e OS, GTV-e, CT-e Simp., eventos) | OK |
| PL_CTe_400_NT2026.001_v1.01c | entrada/XSDs/NT 2026.001 RTC Vinculacao Pagamento.../ | CT-e vinculacao pagamento split | OK |
| PL_MDFe_300b_NT012025_1.05 | entrada/XSDs/ | ~30+ XSDs (MDF-e, modais, eventos) | OK |

### Falta baixar (ver ARQUIVOS_NECESSARIOS.md):

| Pacote | Prioridade | Portal |
|---|---|---|
| MDF-e NT 2026.001 | IMPORTANTE | Portal MDF-e SVRS |

---

## 12. Notas Tecnicas Conhecidas

### Ja temos (PDFs):

| NT | Documento | Versao | Tema |
|---|---|---|---|
| NT 2026.007 v1.10 | NF-e | 1.10 | Emissao por Contribuinte exclusivo IBS/CBS |
| NT CT-e 2026.004 v1.00 | CT-e | 1.00 | Reforma Tributaria do Consumo (CT-e) |

### Publicadas nos portais (para baixar):

**NF-e (Portais: nfe.fazenda.gov.br + dfe-portal.svrs.rs.gov.br):**
- NT 2025.002 v1.52 - RTC (Reforma Tributaria)
- NT 2026.002 v1.11 - DANFE Simplificado Tipo 2
- NT 2026.007 v1.00 - Contribuinte sem IE (versao anterior da que temos)
- NT 2026.008 v1.00 - Valor Liquido do Produto
- NT 2026.009 v1.00 - Correcao de regra
- NT 2026.010 v1.00 - DANFE impressao

**CT-e (Portais: cte.fazenda.gov.br + dfe-portal.svrs.rs.gov.br):**
- NT 2026.004 - RTC (ja temos)
- NT 2026.002 v1.01 - Evolucoes RTC
- NT 2025.001 v1.14b - RTC (minuta)
- NT 2024.003 - PAA (Provedor de Assinatura)
- NT 2024.002 v1.05 - CT-e Simplificado

**MDF-e (Portal: dfe-portal.svrs.rs.gov.br/Mdfe):**
- NT 2026.001 v1.00 - Alteracao de regra de validacao
- NT 2025.001 v1.03 - Ajustes de layout e regras
- NT 2024.002 v1.01 - CT-e simplificado suporte
- NT 2024.001 v1.02 - Ajustes de layout

---

## 13. Testes de Aceite (Golden Tests)

O ambiente so esta pronto quando todos estes testes passam:

| # | Pergunta | Resposta esperada |
|---|---|---|
| 1 | Regra C17-10 da NF-e esta vigente? | Excluida pela NT 2026.007 v1.00, rej. 229 |
| 2 | 5E17-70 (rej. 246) esta vigente? | Excluida (substituida por regras da LCC-RFB) |
| 3 | O que mudou na v1.10 da NT 2026.007? | 5 itens da secao 3.2, todos em VERDE |
| 4 | Quando vTPrestLiq entra em producao no CT-e? | Homologacao 13/10/2026, producao 16/11/2026 |
| 5 | Quando entram validacoes 1051-1053? | Homologacao 01/02/2027, producao 01/03/2027 |
| 6 | Estrutura do CT-e Simplificado muda quando? | Homologacao 16/11/2026, producao 14/12/2026 |
| 7 | tpEmis 4 e 5 ainda valem no CT-e? | Nao: EPEC e FSDA eliminados |
| 8 | Cores da tabela ALC sao marcações de revisao? | Nao: sao dado |
| 9 | Como calcular vTotDFe em 2026? | Repetir vTPrest (nao somar IBS/CBS) |
| 10 | /calendario CT-e | Lista 3 linhas com situacao calculada |
| 11 | Qualidade | Aponta 4 pontos em duvidas-abertas.md |
| 12 | Pergunta sobre MDF-e | "NAO ENCONTRADO NAS FONTES" |

---

## 14. Glossario do Projeto

| Termo | Significado |
|---|---|
| NT | Nota Tecnica - documento que altera regras/campos de um DFe |
| MOC | Manual de Orientacao do Contribuinte - visao geral + regras |
| XSD | XML Schema Definition - estrutura obrigatoria do XML |
| DFe | Documento Fiscal Eletronico (NF-e, CT-e, MDF-e, etc.) |
| cStat | Codigo de status retornado pela SEFAZ (ex: 100=autorizado, 229=rejeicao) |
| RTC | Reforma Tributaria do Consumo (IBS + CBS) |
| IBS | Imposto sobre Bens e Servicos (novo tributo, LC 214/25) |
| CBS | Contribuicao sobre Bens e Servicos (novo tributo, LC 214/25) |
| IS | Imposto Seletivo (novo tributo) |
| CCC | Cadastro Centralizado de Contribuintes |
| LCC-RFB | Lista Centralizada de Contribuintes da Receita Federal |
| SVRS | Sefaz Virtual do Rio Grande do Sul (autorizadora) |
| ENCAT | Equipe Nacional de Coordenadores de Administracao Tributaria |
| CONFAZ | Conselho Nacional de Politica Fazendaria |
| PL | Pacote de Liberacao (de schemas) |
| EPEC | Evento Previo de Emissao em Contingencia (eliminado na NT 2026.004) |
| FSDA | Formulario de Seguranca do DACTE Autenticado (eliminado) |
| TAC | Transportador Autonomo de Cargas |
| MEI | Microempreendedor Individual |
| ALC | Area de Livre Comercio |
| ZFM | Zona Franca de Manaus |
| PAA | Provedor de Assinatura e Autorizacao |
| Split Payment | Sistema de pagamento onde tributos sao retidos na transacao |

---

## 15. Versionamento do ARQUIVOS_NECESSARIOS

### Regra Fundamental
**NUNCA EXCLUIR** o arquivo `docs/ARQUIVOS_NECESSARIOS.md`.

### Regra de Versao e Data
Funciona como changes do OpenSpec:
- **Em andamento (ativo)**: ARQUIVOS_NECESSARIOS sem data e sem versao. Significa que ainda ha documentos pendentes para importar.
- **Concluido (arquivado)**: Quando TODOS os documentos foram importados com sucesso, adicionar data e versao ao arquivo, copiar para `docs/historico-arquivos/` e criar um novo ARQUIVOS_NECESSARIOS para o proximo ciclo.

### Formato do Cabecalho

**Quando ativo (pendente):**
```markdown
# Arquivos Necessarios - Download Manual
> Status: ATIVO (em andamento)
> Documentos pendentes: N
```

**Quando concluido (arquivado):**
```markdown
# Arquivos Necessarios - Download Manual
> Status: CONCLUIDO
> Versao: v1
> Data de conclusao: 2026-10-06
> Documentos importados: N/N
```

### Fluxo de Versionamento
1. Criar ARQUIVOS_NECESSARIOS.md **sem data e sem versao** (status ATIVO)
2. A cada `/atualizar-fontes`, atualizar status dos itens
3. Quando todos os itens estiverem OK:
   - Adicionar data e versao ao cabecalho
   - Copiar para `docs/historico-arquivos/ARQUIVOS_NECESSARIOS_vN_YYYY-MM-DD.md`
   - Criar novo ARQUIVOS_NECESSARIOS.md (sem data/versao) para o proximo ciclo
4. NUNCA deletar o historico

### Formato do Historico
```
docs/historico-arquivos/
├── ARQUIVOS_NECESSARIOS_v1_2026-10-06.md  (ciclo 1 concluido)
├── ARQUIVOS_NECESSARIOS_v2_2026-10-20.md  (ciclo 2 concluido)
└── ...
```

---

## 16. Catalogo de Arquivos (CATALOGO_ARQUIVOS.md)

### O Que E
Arquivo `docs/CATALOGO_ARQUIVOS.md` que lista TODOS os arquivos do projeto
com data de criacao, localizacao, versao e descricao. Facilita a consulta
da IA aos documentos disponiveis.

### Quando E Atualizado
- **Automaticamente**: por commands que criam arquivos (`/ingerir-nt`, `/atualizar-fontes`)
- **Manualmente**: via command `/catalogar-atualizar`

### Estrutura
Cada secao do catalogo contem:
- **Fontes Oficiais** (fontes/): NTs, MOCs, XSDs organizados por documento
- **Catalogo Gerado** (catalogo/): JSONs e MDs gerados por scripts
- **Documentacao** (docs/): Arquivos .md do projeto
- **Scripts** (scripts/): Scripts Python e JS
- **XSDs** (entrada/XSDs/ ou fontes/*/xsd/): Pacotes de schemas
- **Tabelas** (fontes/externas/tabelas/): Tabelas e informes tecnicos

### Campos por Entrada
- `caminho`: caminho relativo do arquivo
- `data_criacao`: data em que foi adicionado ao projeto
- `versao`: versao do documento (se aplicavel)
- `descricao`: descricao curta
- `status`: OK | PENDENTE | ATUALIZADO

---

## 17. Commands Self-Contained

### Principio
Todos os commands fiscal-* sao **self-contained**: a IA executa tudo
internamente. O usuario NUNCA precisa lembrar de rodar `node scripts/...`
ou `python scripts/...`. Basta digitar `/comando` e a IA faz tudo.

### Commands Disponiveis

| Command | Descricao | Executa |
|---|---|---|
| `/ingerir-nt <arquivo>` | Ingerir NT nova | Python (extrair_nt.py) + JS (calendario, docs) |
| `/consultar <pergunta>` | Consulta com fontes | Leitura de catalogo + formatacao |
| `/regra <id>` | Detalhe de regra | Leitura de catalogo |
| `/campo <tag>` | Dados de campo XSD | Leitura de catalogo |
| `/calendario [doc]` | Vigencias filtradas | Leitura de calendario.yaml |
| `/impacto <nt>` | Checklist para dev | Leitura de catalogo + NT |
| `/atualizar-fontes` | Buscar novidades + versionar | WebFetch (portais) + JS |
| `/duvidas` | Lista priorizada | Leitura de duvidas-abertas.md |
| `/catalogar-atualizar` | Organizar entrada/, atualizar manifest e catalogo | Classificacao + movimentacao + escrita |

### Permissoes
A IA deve ter acesso a:
- Bash (para rodar scripts Python e JS)
- Read/Write (para ler e criar arquivos)
- WebFetch/WebSearch (para buscar informacoes nos portais)

---

## 18. Organizacao do entrada/ para fontes/

### Estrutura Destino

```
fontes/
├── nfe/
│   ├── notas-tecnicas/
│   │   └── NT_2026_007_v1.10.pdf
│   ├── moc/
│   │   └── (PENDENTE - baixar do nfe.fazenda.gov.br)
│   └── xsd/
│       ├── PL_NFe_010b_v1.30/
│       ├── PL_NFe_010f_v1.04/
│       ├── Eventos_RTC/
│       ├── Eventos_RTC_v1.30/
│       ├── Evento_211110_v1.40/
│       └── Eventos_Fisco_v1.23/
├── cte/
│   ├── notas-tecnicas/
│   │   └── CTe_NT_2026_004_v1.00.pdf
│   ├── moc/
│   │   ├── MOC_CTe_VisaoGeral_v4.00.pdf
│   │   ├── MOC_CTe_Anexo_II_DACTE_v4.00.pdf
│   │   └── (PENDENTE - Anexo I Leiaute)
│   └── xsd/
│       ├── PL_CTe_400_NT2026.004_RTC_v1.00/
│       └── PL_CTe_400_NT2026.001_v1.01c/
├── mdfe/
│   ├── notas-tecnicas/
│   │   └── (PENDENTE - NT 2026.001)
│   ├── moc/
│   │   ├── MOC_MDFe_VisaoGeral_v3.00b.pdf
│   │   └── MOC_MDFe_Anexo_I_v3.00b.pdf
│   └── xsd/
│       └── PL_MDFe_300b_NT012025_v1.05/
└── externas/
    └── tabelas/
        ├── IT_2025_002_v1.70_cClassTrib.xlsx
        ├── IT_2025_002_v1.70_cCredPres.xlsx
        ├── IT_2025_002_v1.70_Tabelas_Classificacao_IBS_CBS.xlsx
        ├── IT_2026_001_v1.01_Meios_Pagamento_Split.xlsx
        └── Tabela_meios_pagamento_2026-03-04.xlsx
```

### Regras de Organizacao
1. **Mover, nao copiar**: arquivo sai de `entrada/` e vai para `fontes/`
2. **Verificar antes de limpar**: confirmar que TODOS os arquivos foram movidos corretamente
3. **SHA256**: calcular hash antes e depois para garantir integridade
4. **entrada/ permanente**: `entrada/` e uma pasta permanente na raiz do projeto, nao precisa ser limpa
5. **Nomenclatura**: nomes padronizados conforme tabela acima

### Mapeamento entrada/ -> fontes/

| De (entrada/) | Para (fontes/) |
|---|---|
| NT2026.007_v1.10...pdf | fontes/nfe/notas-tecnicas/ |
| CTe_Nota_Tecnica_2026_004_v1.00.pdf | fontes/cte/notas-tecnicas/ |
| MOC_CTe_VisaoGeral_v4.00.pdf | fontes/cte/moc/ |
| MOC_CTe_Anexo II_DACTE_v4.00.pdf | fontes/cte/moc/ |
| MOC_MDFe_VisaoGeral_v3.00b.pdf | fontes/mdfe/moc/ |
| MOC_MDFe_Anexo I_...v3.00b.pdf | fontes/mdfe/moc/ |
| XSDs/NFe-PL_010b_* | fontes/nfe/xsd/PL_NFe_010b_v1.30/ |
| XSDs/NFe-PL_010f_* | fontes/nfe/xsd/PL_NFe_010f_v1.04/ |
| XSDs/NFe-Eventos_RTC/ | fontes/nfe/xsd/Eventos_RTC/ |
| XSDs/NT 2025.002 v1.30 - RTC-Eventos_RTC/ | fontes/nfe/xsd/Eventos_RTC_v1.30/ |
| XSDs/NT 2025.002 v1.40-Schema_Evento_211110.../ | fontes/nfe/xsd/Evento_211110_v1.40/ |
| XSDs/BT 2019.001 v.1.23- Eventos do Fisco/ | fontes/nfe/xsd/Eventos_Fisco_v1.23/ |
| XSDs/PL_CTe_400_NT2026.004 RTC_1.00/ | fontes/cte/xsd/PL_CTe_400_NT2026.004_RTC_v1.00/ |
| XSDs/NT 2026.001 RTC Vinculacao Pagamento.../ | fontes/cte/xsd/PL_CTe_400_NT2026.001_v1.01c/ |
| XSDs/PL_MDFe_300b_NT012025_1.05/ | fontes/mdfe/xsd/PL_MDFe_300b_NT012025_v1.05/ |
| tabelas-informes/*.xlsx | fontes/externas/tabelas/ |