---
name: fiscal-responder-regras
description: Tirar dúvidas e responder qualquer pergunta sobre regras, campos, cStat, obrigatoriedade e novidades de implementação das NTs e MOCs de NF-e, CT-e e MDF-e. Cruza catálogo, calendário, leitura profunda dos PDFs/XSDs ingeridos e pesquisa em fontes oficiais; termina sempre com o calendário de homologação e produção. Use para "quando passa a valer", "o que muda para o emissor", "essa regra rejeita?", "o que preciso implementar".
allowed-tools: Read, Grep, Glob, Bash(python3:*), Bash(node:*), Bash(date), Bash(shasum:*), WebSearch, WebFetch
---

# Skill: Responder regras e novidades das NTs/MOCs

## Quando usar
- Dúvida sobre regra de validação, campo, grupo, cStat, rejeição ou quem aplica
- "Quando isso entra em produção?" / "o que preciso implementar até X?"
- Comparar versões de NT, ou NT x MOC, ou NT x XSD
- Conferir se uma regra está em vigor hoje
- Qualquer dúvida de implementação sobre NF-e, CT-e ou MDF-e

## Regras que valem sempre (AGENTS.md)
1. **Data de hoje**: rode `date` antes de qualquer vigência. Nunca assuma a data.
2. **Não invente** regra, cStat, tag, versão ou data. Se não achar nas fontes, responda `NAO ENCONTRADO NAS FONTES` e sugira `/fiscal-atualizar-fontes`.
3. **Hierarquia**: oficial (NT/MOC/XSD) > fornecedor > fórum/blog. Tudo que não for oficial leva o selo **não oficial**.
4. **Cor não prova nada sozinha**: cruze a marcação com "Descrição das alterações". Texto vermelho riscado = EXCLUÍDO. Cor de tabela ou de exemplo é dado, não revisão.
5. **Contradição entre fontes**: mostre as duas, prevaleça a oficial, registre com `/fiscal-duvidas --registrar`.
6. **Nunca edite `fontes/`**: é só leitura para esta skill. Não faça commit.
7. **`docs-fiscais` = `fontes/`**: é aí que estão os documentos fiscais de fato (NTs, MOCs, XSDs, tabelas). Quando o AGENTS.md mandar ler `docs-fiscais/<DOC>.md` ou "a fonte", leia o documento correspondente em `fontes/<doc>/`. `catalogo/` é a camada extraída e indexada desses documentos; use-a primeiro, mas confirme no arquivo em `fontes/` quando a resposta depender de detalhe.

## Ordem de consulta (siga nesta ordem, para e cite a fonte de cada achado)

### 1. Catálogo gerado (`catalogo/`)
- NT: `catalogo/nt/<doc>/<NT>.json` (cronograma, seções, regras, marcações) e `.md` quando existir.
- MOC: `catalogo/moc/<doc>/<MOC>.json`.
- Leitura: `python3` com `json`. Percorra `secoes` recursivamente; cada item tem `texto`, `marcacao` e `pagina` quando a extração capturou.
- Procure a regra pelo id (ex.: `B09-20`, `C17-11`), cStat ou campo (ex.: `tpRegimeIBSCBS`).
- Use `/ler-catalogo-xsd` e `/consultar-moc` quando a dúvida for de campo ou de versão de MOC.

### 2. Calendário (`calendario/`)
- Verifique se `calendario/calendario.yaml` existe. **Hoje ele não existe**, só o README. Se faltar:
  - use o `cronograma` de cada NT no catálogo (cada item tem `versao`, `homologacao`, `producao`, `descricao`);
  - avise a pessoa que o calendário gerado está ausente e sugira a skill `atualizar-calendario` e, depois, `/fiscal-calendario`.
- Datas "Até dd/mm/aaaa" ou texto como "Já implantado" são literais da NT. Reporte como estão e aponte se já passaram.

### 3. Leitura profunda dos arquivos ingeridos (`fontes/`)
Use quando o catálogo não bastar, quando a dúvida for sobre tabela, exemplo, nota de rodapé ou ocorrência, ou quando houver conflito.
- **PDF da NT/MOC**: `python3` com `fitz` (PyMuPDF). Extraia a página exata e leia o trecho. Ex.: `fitz.open(arq)[pagina-1].get_text()`. Não confie só na extração do JSON.
- **XSD**: `grep`/`python3` com regex nos `*.xsd` de `fontes/<doc>/xsd/<pacote>/`. Confirme `minOccurs`/`maxOccurs`, `type`, `pattern` e enumerações. Ex.: `<xs:element name="tpRegimeIBSCBS" ... minOccurs="0">`.
- Se o XSD diz opcional e a NT diz "DEVE", a NT vale para a regra de negócio; o XSD vale para a validação de schema. Diga as duas coisas.
- Não use `grep` com regex complexa em XSD grande sem `-F` ou `python3`; o `ugrep` estoura o limite em alguns arquivos.

### 4. Pesquisa externa (só para confirmar, atualizar ou quando o acervo não responder)
Use `WebSearch` (modo `standard`; `extended` só se a primeira busca vier fraca). Use `WebFetch` para abrir a página oficial encontrada. Rotule cada fonte como **oficial** ou **não oficial**.

**Oficiais (primeira escolha)**
- Portal Nacional da NF-e: `https://www.nfe.fazenda.gov.br` (NF-e e NFC-e; NTs e MOCs)
- Portal Nacional do CT-e: `https://cte.fazenda.gov.br`
- Portal SVRS (MDF-e e leiautes da reforma, com IBS/CBS): `https://dfe-portal.svrs.rs.gov.br` e `https://mdfe-portal.sefaz.rs.gov.br`
- Portal SEFAZ do seu estado (avisos próprios): ex. SEFAZ-PE, SEFAZ-RJ
- Diário Oficial da União: `https://www.in.gov.br` (atos que alterem prazo ou obrigatoriedade; confirme publicação antes de afirmar)

**Não oficiais (comentário e impacto, nunca a regra)**
- Portal SPED / fórum Portal SPED Brasil: `https://portalspedbrasil.com.br` (publica avisos de implantação de NTs)
- Fórum ACBr: `https://www.projetoacbr.com.br/forum` (discussão técnica de CT-e, GTVe)
- Portal da Reforma Tributária: `https://www.reformatributaria.com` (painel de monitoramento das NTs)
- Blogs de análise de NT: AmdJus, Inventti, Systax, Coad, Portal Tributário e NotaGateway

**Reddit**: a busca desta data não retornou threads úteis. Não cite Reddit como fonte até que uma thread específica seja confirmada.

**Sempre** cheque se a NT citada foi substituída ou complementada por versão mais nova. O painel da Reforma Tributária e os portais oficiais listam as versões.

### 5. Faltou documento
- Se a NT, MOC ou XSD necessário não estiver em `fontes/`, responda `NAO ENCONTRADO NAS FONTES` e sugira **`/fiscal-atualizar-fontes`** (busca nos portais oficiais e registra em `docs/ARQUIVOS_NECESSARIOS.md`; só propõe, não ingere).
- Para ingerir o documento depois, use `/fiscal-ingerir-nt`.

## Formato da resposta (obrigatório)

1. **Resumo** (2 a 3 linhas): a resposta direta, com o que muda e quando.
2. **Detalhe**:
   - Campo/regra: `<nome>`
   - cStat: `<código>` ou `NAO ENCONTRADO NAS FONTES`
   - Quem aplica: SEFAZ / todas / CRT específico
   - NT de origem: `<NT> v<versão>`, pág. `<N>` (ou "pág. não capturada")
   - Marcação: AMARELO / VERDE / EXCLUÍDO / SEM_MARCA
   - Situação na data de hoje: futura / em homologação / em produção / excluída
3. **Impacto no emissor**: o que precisa mudar no sistema, em tópicos.
4. **Calendário de implementação**: **sempre**, para qualquer regra ou campo. Tabela com as linhas do cronograma da NT que se aplicam:

   | Versão | Homologação | Produção | Situação em `<data de hoje>` | Escopo |
   |---|---|---|---|---|

   Se a data já passou, diga "passou". Se for "Até dd/mm", reporte o texto literal. Se houver mais de uma linha (campos e regras com datas diferentes), liste todas.
5. **Fontes**: uma linha por fonte, com documento, NT/MOC/XSD, versão, página ou seção, marcação e selo **oficial** ou **não oficial**.

## Dúvida que não fecha
- Contradição entre fontes ou falha de extração: registre com `/fiscal-duvidas --registrar`, com a fonte oficial prevalecendo.
- Pergunta que depende de decisão do usuário (ex.: estratégia de implantação): diga a recomendação e pergunte uma vez, no fim.

## Exemplo de pergunta e onde buscar
- "Vai rejeitar se o SN não mandar `gTribSN`?" → catálogo (regras da NT 2026.005) + XSD (`minOccurs`) + calendário (regras em produção em 14/12/2026). Se o cStat não estiver na NT, responda `NAO ENCONTRADO NAS FONTES` e não chute.
- "O que muda no DANFE?" → catálogo da NT 2026.010 + MOC NF-e Anexo II (DANFE) + calendário da NT.
- "Quando entra o split payment?" → NT 2026.001 (CT-e) e IT 2026.001 em `fontes/externas/tabelas/`.
