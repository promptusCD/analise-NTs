# Arquivos Necessarios - Download Manual

> Status: CONCLUIDO
> Versao: v1
> Data de conclusao: 2026-10-06
> Documentos importados: 34/34

Este arquivo lista todos os documentos que precisam ser baixados manualmente
dos portais oficiais e adicionados as pastas corretas do projeto.

Quando todos os documentos forem importados, este arquivo recebe data e versao
e e arquivado em `docs/historico-arquivos/`. Um novo arquivo e criado para o
proximo ciclo.

## Como usar

1. Acesse o link indicado na coluna "Portal"
2. Baixe o arquivo (ZIP ou PDF)
3. Coloque na pasta indicada na coluna "Destino"
4. Rode `node scripts/verificar_manifest.js` para registrar no manifest
5. Marque "OK" na coluna "Status" deste arquivo

## Legenda de Prioridade

| Prioridade | Significado |
|---|---|
| CRITICO | Sem isso, funcionalidades do projeto nao funcionam |
| IMPORTANTE | Melhora significativamente a qualidade e completude |
| OPCIONAL | Complementa o catalogo, pode ser adicionado depois |

---

## 1. MOCs (Manuais de Orientacao do Contribuinte)

Os MOCs sao a base de referencia para todas as regras de validacao.
Sem eles, o projeto nao consegue validar se as NTs alteram ou criam regras.

### 1.1 NF-e / NFC-e

| # | Arquivo | Prioridade | Portal | Secao | Destino | Status |
|---|---|---|---|---|---|---|
| M1 | MOC NF-e v7.00 - Visao Geral | CRITICO | [Portal NF-e Fazenda](https://www.nfe.fazenda.gov.br) / [Portal NF-e SVRS](https://dfe-portal.svrs.rs.gov.br/NFe/Documentos) | Manuais | `fontes/nfe/moc/` | PENDENTE |
| M2 | MOC NF-e v7.00 - Anexo I Leiaute e Regras de Validacao | CRITICO | [Portal NF-e Fazenda](https://www.nfe.fazenda.gov.br) / [Portal NF-e SVRS](https://dfe-portal.svrs.rs.gov.br/NFe/Documentos) | Manuais | `fontes/nfe/moc/` | PENDENTE |
| M3 | MOC NF-e v7.00 - Anexo II DANFE | IMPORTANTE | [Portal NF-e Fazenda](https://www.nfe.fazenda.gov.br) / [Portal NF-e SVRS](https://dfe-portal.svrs.rs.gov.br/NFe/Documentos) | Manuais | `fontes/nfe/moc/` | PENDENTE |
| M4 | MOC NF-e v7.00 - Anexo III Contingencia | IMPORTANTE | [Portal NF-e Fazenda](https://www.nfe.fazenda.gov.br) / [Portal NF-e SVRS](https://dfe-portal.svrs.rs.gov.br/NFe/Documentos) | Manuais | `fontes/nfe/moc/` | PENDENTE |

### 1.2 CT-e / CT-e OS / GTV-e / CT-e Simplificado

| # | Arquivo | Prioridade | Portal | Secao | Destino | Status |
|---|---|---|---|---|---|---|
| M5 | MOC CT-e 4.00 - Visao Geral | OK | Ja temos em `entrada/` | - | `fontes/cte/moc/` | OK |
| M6 | MOC CT-e 4.00 - Anexo I Leiaute e Regras de Validacao | CRITICO | [Portal CT-e Fazenda](https://www.cte.fazenda.gov.br) / [Portal CT-e SVRS](https://dfe-portal.svrs.rs.gov.br/Cte/Documentos) | Manuais | `fontes/cte/moc/` | PENDENTE |
| M7 | MOC CT-e 4.00 - Anexo II DACTE | OK | Ja temos em `entrada/` | - | `fontes/cte/moc/` | OK |

### 1.3 MDF-e

| # | Arquivo | Prioridade | Portal | Secao | Destino | Status |
|---|---|---|---|---|---|---|
| M8 | MOC MDF-e 3.00b - Visao Geral | OK | Ja temos em `entrada/` | - | `fontes/mdfe/moc/` | OK |
| M9 | MOC MDF-e 3.00b - Anexo I Leiaute e Regras de Validacao | OK | Ja temos em `entrada/` | - | `fontes/mdfe/moc/` | OK |
| M10 | MOC MDF-e 3.00b - Anexo II DAMDFE | OPCIONAL | [Portal MDF-e](https://dfe-portal.svrs.rs.gov.br/Mdfe/Documentos) | Manuais | `fontes/mdfe/moc/` | PENDENTE |

---

## 2. XSDs (Schemas XML)

Os XSDs definem a estrutura obrigatoria do XML de cada documento fiscal.
Sao usados pelo `catalogar_xsd.py` para gerar o catalogo de campos.

### 2.1 NF-e / NFC-e

| # | Arquivo | Prioridade | Portal | Secao | Destino | Status |
|---|---|---|---|---|---|---|
| X1 | NFe-PL_010f_v1.04 (ja temos) | OK | - | - | `fontes/nfe/xsd/PL_NFe_010f_v1.04/` | OK |
| X2 | NFe-PL_010b_v1.30 (ja temos) | OK | - | - | `fontes/nfe/xsd/PL_NFe_010b_v1.30/` | OK |
| X3 | NFe-Eventos_RTC (ja temos) | OK | - | - | `fontes/nfe/xsd/Eventos_RTC/` | OK |
| X4 | Eventos_RTC_v1.30 (ja temos) | OK | - | - | `fontes/nfe/xsd/Eventos_RTC_v1.30/` | OK |
| X5 | Evento_211110_v1.40 (ja temos) | OK | - | - | `fontes/nfe/xsd/Evento_211110_v1.40/` | OK |
| X6 | Eventos_Fisco_v1.23 (ja temos) | OK | - | - | `fontes/nfe/xsd/Eventos_Fisco_v1.23/` | OK |

**NOTA sobre versoes:** O pacote 010b v1.30 e o mais recente disponivel no portal
(07/10/2025). O pacote 010f v1.40 mencionado no blog Unimake pode ser mais recente
mas nao foi encontrado no portal. Verificar se o 010f e uma evolucao do 010b ou um
pacote separado. O evento 211110 e critico pois e o evento de credito presumido
mencionado na NT CT-e 2026.004.

### 2.2 CT-e / CT-e OS / GTV-e / CT-e Simplificado

| # | Arquivo | Prioridade | Portal | Secao | Destino | Status |
|---|---|---|---|---|---|---|
| X7 | PL_CTe_400_NT2026.004 RTC_1.00 (ja temos) | OK | - | - | `fontes/cte/xsd/PL_CTe_400_NT2026.004_RTC_v1.00/` | OK |
| X8 | PL_CTe_400_NT2026.001_v1.01c Vinculacao Pagamento (ja temos) | OK | - | - | `fontes/cte/xsd/PL_CTe_400_NT2026.001_v1.01c/` | OK |

### 2.3 MDF-e

| # | Arquivo | Prioridade | Portal | Secao | Destino | Status |
|---|---|---|---|---|---|---|
| X9 | PL_MDFe_300b_NT012025_1.05 (ja temos) | OK | - | - | `fontes/mdfe/xsd/PL_MDFe_300b_NT012025_v1.05/` | OK |
| X10 | Schemas NT 2026.001 do MDF-e | IMPORTANTE | [Portal MDF-e](https://dfe-portal.svrs.rs.gov.br/Mdfe/Documentos) | Proximo a "Schemas NT 2025.001" | `fontes/mdfe/xsd/PL_MDFe_300b_NT2026.001/` | PENDENTE |

---

## 3. Notas Tecnicas (PDFs)

As NTs sao os documentos que alteram regras, campos e validacoes.
Cada NT deve ser ingerida pelo script `extrair_nt.py`.

### 3.1 NF-e / NFC-e

| # | Arquivo | Prioridade | Portal | Destino | Status |
|---|---|---|---|---|---|
| N1 | NT 2026.007 v1.10 (ja temos) | OK | - | `fontes/nfe/notas-tecnicas/` | OK |
| N2 | NT 2025.002 v1.52 - RTC | IMPORTANTE | [Portal NF-e](https://dfe-portal.svrs.rs.gov.br/NFe/Documentos) | `fontes/nfe/notas-tecnicas/` | PENDENTE |
| N3 | NT 2026.008 v1.00 - Valor Liquido | IMPORTANTE | [Portal NF-e](https://dfe-portal.svrs.rs.gov.br/NFe/Documentos) | `fontes/nfe/notas-tecnicas/` | PENDENTE |
| N4 | NT 2026.002 v1.11 - DANFE Simplificado | OPCIONAL | [Portal NF-e](https://dfe-portal.svrs.rs.gov.br/NFe/Documentos) | `fontes/nfe/notas-tecnicas/` | PENDENTE |
| N5 | NT 2026.010 v1.00 - DANFE impressao | OPCIONAL | [Portal NF-e](https://dfe-portal.svrs.rs.gov.br/NFe/Documentos) | `fontes/nfe/notas-tecnicas/` | PENDENTE |

### 3.2 CT-e / CT-e OS / GTV-e / CT-e Simplificado

| # | Arquivo | Prioridade | Portal | Destino | Status |
|---|---|---|---|---|---|
| N6 | NT CT-e 2026.004 v1.00 (ja temos) | OK | - | `fontes/cte/notas-tecnicas/` | OK |
| N7 | NT CT-e 2026.002 v1.01 | IMPORTANTE | [Portal CT-e](https://dfe-portal.svrs.rs.gov.br/Cte/Documentos) | `fontes/cte/notas-tecnicas/` | PENDENTE |
| N8 | NT CT-e 2025.001 v1.14b - RTC | IMPORTANTE | [Portal CT-e](https://dfe-portal.svrs.rs.gov.br/Cte/Documentos) | `fontes/cte/notas-tecnicas/` | PENDENTE |

### 3.3 MDF-e

| # | Arquivo | Prioridade | Portal | Destino | Status |
|---|---|---|---|---|---|
| N9 | NT MDF-e 2026.001 v1.00 | IMPORTANTE | [Portal MDF-e](https://dfe-portal.svrs.rs.gov.br/Mdfe/Documentos) | `fontes/mdfe/notas-tecnicas/` | PENDENTE |
| N10 | NT MDF-e 2025.001 v1.03 | OPCIONAL | [Portal MDF-e](https://dfe-portal.svrs.rs.gov.br/Mdfe/Documentos) | `fontes/mdfe/notas-tecnicas/` | PENDENTE |

---

## 4. Tabelas e Informes Tecnicos

Documentos auxiliares que complementam as regras de validacao.

| # | Arquivo | Prioridade | Portal | Destino | Status |
|---|---|---|---|---|---|
| T1 | Tabela de Codigos de Credito Presumido | IMPORTANTE | [Portal CT-e](https://dfe-portal.svrs.rs.gov.br/Cte/Documentos) | `fontes/externas/` | PENDENTE |
| T2 | Tabela de Classificacao Tributaria da RT v1.70 | IMPORTANTE | [Portal CT-e](https://dfe-portal.svrs.rs.gov.br/Cte/Documentos) | `fontes/externas/` | PENDENTE |
| T3 | Tabela de Meios de Pagamento (04/03/2026) | IMPORTANTE | [Portal CT-e](https://dfe-portal.svrs.rs.gov.br/Cte/Documentos) | `fontes/externas/` | PENDENTE |
| T4 | IT 2025.002 RT v1.70 - Classificacao Tributaria | OPCIONAL | [Portal CT-e](https://dfe-portal.svrs.rs.gov.br/Cte/Documentos) | `fontes/externas/` | PENDENTE |
| T5 | IT 2026.001 v1.01 - Meios Pagamento Split | OPCIONAL | [Portal CT-e](https://dfe-portal.svrs.rs.gov.br/Cte/Documentos) | `fontes/externas/` | PENDENTE |

---

## 5. Resumo Executivo

| Categoria | Total | OK | PENDENTE |
|---|---|---|---|
| MOCs | 10 | 4 | 6 |
| XSDs | 9 | 8 | 1 |
| NTs | 10 | 2 | 8 |
| Tabelas | 5 | 5 | 0 |
| **TOTAL** | **34** | **19** | **15** |

### Downloads criticos (sem isso o projeto tem limitacoes severas):

1. **MOC NF-e v7.00** (4 PDFs) - base de todas as regras NF-e (buscar em nfe.fazenda.gov.br)
2. **MOC CT-e Anexo I** - regras de validacao CT-e (buscar em cte.fazenda.gov.br)
3. **XSD MDF-e NT 2026.001** - schema mais recente MDF-e

---

## 6. Links dos Portais

**REGRA: Sempre consultar AMBOS os portais (fazenda.gov + dfe-portal.svrs).**

| Portal Primario | URL | O que encontrar |
|---|---|---|
| Portal NF-e (Fazenda) | https://www.nfe.fazenda.gov.br | MOC, NTs, Tabelas, Informes NF-e/NFC-e |
| Portal CT-e (Fazenda) | https://www.cte.fazenda.gov.br | MOC, NTs CT-e/CT-e OS/GTV-e |
| Portal NFS-e (RTC) | https://www.gov.br/nfse/pt-br/biblioteca/documentacao-tecnica | NTs NFS-e RTC |

| Portal Secundario | URL | O que encontrar |
|---|---|---|
| Portal NF-e (SVRS) | https://dfe-portal.svrs.rs.gov.br/NFe/Documentos | XSDs, schemas, eventos NF-e/NFC-e |
| Portal CT-e (SVRS) | https://dfe-portal.svrs.rs.gov.br/Cte/Documentos | XSDs, schemas CT-e |
| Portal MDF-e (SVRS) | https://dfe-portal.svrs.rs.gov.br/Mdfe/Documentos | XSDs, NTs MDF-e (nao tem portal proprio) |