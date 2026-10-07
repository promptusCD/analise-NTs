# fiscal-dfe-knowledge

Repositorio de conhecimento fiscal que transforma documentos brutos do governo
(Notas Tecnicas, MOCs e XSDs de NF-e/NFC-e, CT-e e MDF-e) em conhecimento
organizado, consultavel e com fonte citada.

---

## O Que E Este Projeto

Desenvolvedores de sistemas de emissao fiscal precisam acompanhar Notas
Tecnicas que alteram regras, campos e validacoes dos documentos fiscais
eletronicos. Esses documentos vem em PDF com marcações visuais de cor
(amarelo = novo, verde = alterado, vermelho riscado = excluido) que sao
extremamente dificeis de ler manualmente.

Este projeto automatiza essa leitura e organiza o conhecimento em:
- **Catalogo estruturado** (JSON) de regras, campos e eventos
- **Calendario de vigencias** com situacao calculada automaticamente
- **Docs fiscais** (NFE.md, CTE.md, MDFE.md) como ponto de entrada para a IA
- **Commands** para consulta rapida com citacao de fontes

**Analogia:** e uma biblioteca com um bibliotecario que sempre cita a pagina.

---

## Arquitetura

```
EXTRACAO (Python 3.11+)
  pymupdf + python-docx + lxml
  scripts/python/extrair_nt.py    -> catalogo/nt/<doc>/*.json
  scripts/python/extrair_moc.py   -> catalogo/moc/<doc>/*.json
  scripts/python/catalogar_xsd.py
        |
        v  (JSON robusto: secoes tipificadas, tabelas, regras)
IA GERA O MD (opencode)
  /gerar-md <nt|moc>  -> le o JSON e escreve catalogo/**/*.md legivel
        |
        v  (JSON + MD)
ORQUESTRACAO (Node.js)
  js-yaml + ejs + node-fetch
  scripts/js/gerar_calendario.js
  scripts/js/atualizar_docs_fiscais.js
  scripts/js/consultar.js
  scripts/js/detectar_novidades.js
        |
        v
CONSULTA (CLI + opencode)
  /consultar, /regra, /campo, /calendario
  /ingerir-nt, /gerar-md, /fiscal-processar
  /impacto, /atualizar-fontes
```

**Regra de ouro do fluxo:** Python so extrai JSON. Quem formata o MD e a IA
(`scripts/python/utils/saida.py` nao tem mais nenhuma funcao de MD).

---

## Estrutura do Projeto

```
fiscal-dfe-knowledge/
├── README.md                    # Este arquivo
├── AGENTS.md                    # Regras permanentes da IA
├── manifest.yaml                # Registro de todas as fontes
├── package.json                 # Dependencias Node.js
├── requirements.txt             # Dependencias Python
│
├── entrada/                     # Area de recebimento (permanente na raiz)
│   ├── *.pdf, *.docx            # NTs e MOCs brutos
│   ├── XSDs/                    # Pacotes de schemas XML
│   └── tabelas-informes/        # Tabelas e informes tecnicos
│
├── fontes/                      # Arquivos organizados por documento
│   ├── nfe/
│   │   ├── notas-tecnicas/      # PDFs das NTs NF-e
│   │   ├── moc/                 # MOC NF-e
│   │   └── xsd/                 # Pacotes XSD NF-e
│   ├── cte/
│   │   ├── notas-tecnicas/      # PDFs das NTs CT-e
│   │   ├── moc/                 # MOC CT-e
│   │   └── xsd/                 # Pacotes XSD CT-e
│   ├── mdfe/
│   │   ├── notas-tecnicas/      # PDFs das NTs MDF-e
│   │   ├── moc/                 # MOC MDF-e
│   │   └── xsd/                 # Pacotes XSD MDF-e
│   └── externas/                # Fontes nao oficiais
│       └── tabelas/             # Tabelas e informes
│
├── catalogo/                    # Camada "mastigada" (gerada por scripts)
│   ├── nt/<doc>/*.json + .md    # NTs extraidas com marcações
│   ├── regras/<doc>.json        # Indice de regras de validacao
│   ├── campos/<doc>.json        # Tags do leiaute
│   └── legendas/<doc>.yaml      # Mapa cor -> versao
│
├── calendario/
│   ├── calendario.yaml          # Fonte unica de vigencias
│   ├── CALENDARIO.md            # Gerado
│   └── calendario.html          # Gerado, com cores
│
├── docs-fiscais/                # Documentacao por documento fiscal
│   ├── _COMUM.md                # Conceitos transversais
│   ├── _GLOSSARIO.md            # Termos e definicoes
│   ├── NFE.md                   # NF-e (55) e NFC-e (65)
│   ├── CTE.md                   # CT-e (57), CT-e OS (67), GTV-e (64)
│   └── MDFE.md                  # MDF-e (58)
│
├── scripts/
│   ├── python/                  # Extracao (PyMuPDF)
│   └── js/                      # Orquestracao (Node.js)
│
├── docs/
│   ├── REFERENCIA.md            # Contexto completo do projeto
│   ├── ARQUIVOS_NECESSARIOS.md  # Status de downloads
│   ├── CATALOGO_ARQUIVOS.md     # Indice de todos os arquivos
│   ├── historico-arquivos/      # Versoes anteriores do ARQUIVOS_NECESSARIOS
│   ├── duvidas-abertas.md       # Inconsistencias e pendencias
│   └── legenda-cores.md         # Algoritmo de deteccao de cor
│
└── .opencode/
    ├── commands/                # Commands para a IA
    └── skills/                  # Skills interpretativas
```

---

## Commands Disponiveis

Todos os commands sao self-contained: basta digitar o comando e a IA
executa tudo internamente. Nao e necessario rodar scripts manualmente.

### `/ingerir-nt <arquivo>`
Ingerir uma nova Nota Tecnica no repositorio.
- Move o arquivo para `fontes/<doc>/notas-tecnicas/`
- Registra no manifest.yaml
- Extrai JSON robusto com secoes tipificadas (Python)
- Atualiza catalogo, calendario e docs-fiscais
- Gera o MD automaticamente (IA le o JSON)
- Lista duvidas encontradas

### `/gerar-md <nt|moc>`
Gerar (ou regenerar) o MD de uma NT ou MOC a partir do JSON extraido.
- Le `catalogo/nt/<doc>/*.json` ou `catalogo/moc/<doc>/*.json`
- Tabelas viram bullets com campo em destaque
- Regras aparecem com ID, cStat e mensagem destacados
- Datas em negrito, datas literais preservadas
- Nao e preciso re-extrair o PDF para ajustar a formatacao
- Exemplo: `/gerar-md 2025.001`

### `/fiscal-processar [--etapa N]`
Pipeline completo: organizar `entrada/` -> `fontes/`, extrair JSON de NTs e
MOCs, atualizar manifest, verificar resultado.
- Sem argumentos: executa todas as etapas
- `--etapa N`: executa apenas a etapa N (1 organizar, 2 NTs, 3 MOCs,
  4 manifest, 5 verificar)
- Exemplo: `/fiscal-processar --etapa 2`

### `/consultar <pergunta>`
Responder uma pergunta sobre documentacao fiscal.
- Busca no catalogo (JSON)
- Calcula vigencia automaticamente
- Formata com citacao de fontes
- Exemplo: `/consultar "A regra C17-10 da NF-e esta vigente?"`

### `/regra <id ou cStat>`
Mostrar detalhes de uma regra de validacao.
- Status: ativa/alterada/excluida
- NT de origem e versao
- Quem aplica (SEFAZ/todas)
- cStat e mensagem de rejeicao
- Exemplo: `/regra C17-10`

### `/campo <tag> [doc]`
Mostrar dados de um campo do leiaute (tag XML).
- Tipo, ocorrencia, tamanho
- Regras relacionadas
- NT de origem
- Exemplo: `/campo vTPrestLiq CT-e`

### `/calendario [doc]`
Mostrar calendario de vigencias filtrado.
- Ordenado por data de producao
- Situacao calculada para hoje
- Cores: azul (homologacao), laranja (producao)
- Exemplo: `/calendario CT-e`

### `/impacto <nt>`
Gerar checklist de implementacao para o time de desenvolvimento.
- Campos novos/alterados/removidos
- Regras novas e excluidas
- Eventos novos
- Rejeicoes
- Datas de vigencia
- Exemplo: `/impacto NT-CT-e-2026.004`

### `/atualizar-fontes`
Buscar novidades nos portais oficiais.
- Consulta nfe.fazenda.gov.br + dfe-portal.svrs.rs.gov.br
- Compara com manifest.yaml
- Propoe o que e novo (nao ingere automaticamente)
- Versiona ARQUIVOS_NECESSARIOS

### `/duvidas`
Listar e priorizar duvidas abertas.
- Classifica por prioridade (alta/media/baixa)
- Sugere como resolver

### `/catalogar-atualizar`
Ler `entrada/`, organizar automaticamente em `fontes/`, atualizar manifest e catalogo.
- Identifica tipo (NT/MOC/XSD/Tabela) e documento fiscal (NF-e/CT-e/MDF-e)
- Move para a pasta correta em `fontes/`
- Verifica duplicatas por SHA256
- Atualiza manifest.yaml e CATALOGO_ARQUIVOS.md

---

## Fluxo de Utilizacao

Este e o fluxo padrao para adicionar novos documentos ao repositorio.

### Passo 1: Verificar o que falta

Rode `/atualizar-fontes` para consultar os portais oficiais e ver o que
e novo. A IA compara o que esta nos portais com o que ja temos no
manifest.yaml e gera um relatorio de novidades.

```
/atualizar-fontes
```

Saida: lista de NTs, MOCs e XSDs novos disponiveis nos portais.

### Passo 2: Baixar os arquivos

Acesse os links indicados no relatorio e baixe os arquivos manualmente.
Coloque TUDO na pasta `entrada/` — nao precisa se preocupar em organizar.

```
entrada/
├── NT_2026.009_v1.00.pdf          ← NT nova
├── MOC_NFe_v8.00.pdf              ← MOC atualizado
├── PL_CTe_400_NT2026.005.zip      ← XSD novo
└── Tabela_CFOP_v2.00.xlsx         ← Tabela
```

### Passo 3: Organizar e catalogar

Rode `/catalogar-atualizar`. A IA le tudo em `entrada/`, identifica
automaticamente o que e cada arquivo, move para a pasta correta em
`fontes/` e atualiza o manifest e o catalogo.

```
/catalogar-atualizar
```

O que acontece:
1. Le todos os arquivos em `entrada/`
2. Identifica: NT, MOC, XSD ou Tabela
3. Identifica: NF-e, CT-e ou MDF-e
4. Move para `fontes/<doc>/<tipo>/`
5. Verifica duplicatas (SHA256)
6. Atualiza manifest.yaml
7. Atualiza CATALOGO_ARQUIVOS.md
8. Limpa `entrada/`

### Passo 4: Ingerir NTs novas (se houver NTs)

Se foram adicionadas NTs novas, rode `/ingerir-nt` para cada uma.
A IA extrai as marcações de cor, cataloga regras e campos, atualiza
o calendario e os docs-fiscais.

```
/ingerir-nt fontes/nfe/notas-tecnicas/NT_2026_009_v1.00.pdf
```

O que acontece:
1. Extrai marcações de cor (Python/PyMuPDF)
2. Gera JSON robusto em `catalogo/nt/<doc>/` (secoes tipificadas)
3. A IA gera o MD a partir do JSON (`/gerar-md`)
4. Atualiza legenda de cores
5. Atualiza calendario de vigencias
6. Regenera blocos AUTO dos docs-fiscais
7. Registra duvidas encontradas

Se quiser so regenerar o MD sem re-extrair o PDF (ex.: para ajustar a
formatacao), use `/gerar-md <nt>`:

```
/gerar-md 2026.007
```

### Passo 5: Verificar impacto (para desenvolvedores)

Se voce e desenvolvedor e precisa saber o que mudar no sistema de
emissao, rode `/impacto` para gerar um checklist.

```
/impacto NT-CT-e-2026.004
```

Saida: campos novos/alterados/removidos, regras, rejeicoes, eventos,
datas de vigencia — pronto para criar tarefas no Jira/Linear.

### Passo 6: Consultar (uso diario)

No dia a dia, use `/consultar` para tirar duvidas rapidas.

```
/consultar "A regra C17-10 da NF-e esta vigente?"
/consultar "Quando entra em producao o vTPrestLiq no CT-e?"
/regra C17-10
/campo vTPrestLiq CT-e
/calendario CT-e
```

### Resumo do fluxo

```
  /atualizar-fontes          ← O que falta?
       |
       v
  Baixar e colar em entrada/ ← Download manual
       |
       v
  /catalogar-atualizar       ← Organiza automaticamente
       |
       v
  /ingerir-nt <arquivo>      ← Extrai JSON, cataloga
       |
       v
  /gerar-md <nt>             ← IA gera o MD a partir do JSON
       |
       v
  /impacto <nt>              ← Checklist para dev
       |
       v
  /consultar <pergunta>      ← Uso diario
```

## Como Funciona a Extracao de Cores

As NTs usam marcações visuais no PDF:

| Marcação | Significado |
|---|---|
| Fundo amarelo | Alterado na versao atual |
| Fundo verde | Alterado em versao posterior |
| Texto vermelho riscado | Excluido |
| Sem marcação | Inalterado ou novo inteiro |

O script `extrair_nt.py` (Python/PyMuPDF) detecta:
1. Retangulos de fundo (cor do fundo)
2. Linhas horizontais (riscado)
3. Cor do texto
4. Cruzamento com secao "Descricao das alteracoes"

**IMPORTANTE:** A cor nunca prova sozinha. Sempre cruza com o texto
da secao de alteracoes do proprio documento.

---

## Portais Oficiais

| Portal | URL |
|---|---|
| NF-e (Fazenda) | https://www.nfe.fazenda.gov.br |
| CT-e (Fazenda) | https://www.cte.fazenda.gov.br |
| NF-e (SVRS) | https://dfe-portal.svrs.rs.gov.br/NFe/Documentos |
| CT-e (SVRS) | https://dfe-portal.svrs.rs.gov.br/Cte/Documentos |
| MDF-e (SVRS) | https://dfe-portal.svrs.rs.gov.br/Mdfe/Documentos |
| NFS-e (RTC) | https://www.gov.br/nfse/pt-br/biblioteca/documentacao-tecnica |

**REGRA:** Sempre consultar AMBOS os portais (fazenda.gov + dfe-portal.svrs).

---

## Instalacao

```bash
# Dependencias Python
python -m venv venv
pip install -r requirements.txt

# Dependencias Node.js
npm install
```

---

## Status do Projeto

O projeto esta em fase de planejamento e organizacao inicial.
Consulte `docs/REFERENCIA.md` para o roadmap completo.

**Fases:**
1. fase-0-setup - Estrutura base
2. fase-0.5-organizacao - Mover entrada/ para fontes/
3. fase-1-extrator-nt - Extracao de PDFs
4. fase-2-calendario - Calendario de vigencias
5. fase-3-docs-fiscais - Documentacao por documento
6. fase-4-xsd-moc - Catalogo de XSDs e MOCs
7. fase-5-commands-skills - Commands e skills
8. fase-6-qualidade - Testes golden
9. fase-7-fontes-externas - Automacao de portais

---

## Limitacoes

- Extracao de PDF depende de Python (PyMuPDF)
- XSDs precisam de lxml (Python) para parsing completo
- Portais podem bloquear scraping (captcha)
- MOCs e NTs precisam ser baixados manualmente

---

## Documentacao

- `docs/REFERENCIA.md` - Contexto completo, roadmap, adaptacoes
- `docs/ARQUIVOS_NECESSARIOS.md` - Status de downloads
- `AGENTS.md` - Regras permanentes da IA
- `docs/legenda-cores.md` - Algoritmo de deteccao de cor