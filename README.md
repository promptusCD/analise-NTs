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
  scripts/python/extrair_nt.py
  scripts/python/catalogar_xsd.py
        |
        v  (JSON / arquivos)
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
  /ingerir-nt, /impacto, /atualizar-fontes
```

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
├── entrada/                     # Area de recebimento (antes de organizar)
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
- Extrai marcações de cor (Python)
- Atualiza catalogo, calendario e docs-fiscais
- Lista duvidas encontradas

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
Atualizar o CATALOGO_ARQUIVOS.md com todos os arquivos do projeto.

---

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