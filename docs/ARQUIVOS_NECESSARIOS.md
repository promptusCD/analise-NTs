# Arquivos Necessarios - Download Manual

> Status: ATIVO (em andamento)
> Ciclo: v2
> Última verificação: 2026-11-12 16:12 (/fiscal-atualizar-fontes)
> Documentos pendentes: 27 (NOVO/ATUALIZADO/VERIFICAR, aguardando download para `entrada/`)

Ciclo v2: a versão anterior deste arquivo dizia "todos os documentos foram baixados" e não tinha lista
de itens. Esta versão passa a ser o registro vivo: `/fiscal-atualizar-fontes` grava aqui a cada execução.
Os itens do Ciclo v1 continuam em `docs/historico-arquivos/ARQUIVOS_NECESSARIOS_v1_2026-10-06.md`.

## Proximos passos
1. Baixar os itens PENDENTES (links na tabela) e colocar em `entrada/`
2. Rodar `/fiscal-processar` (organiza em `fontes/`, extrai e verifica)
3. Verificar integridade (SHA256) e atualizar `manifest.yaml`
4. Marcar o item como OK nesta tabela (só o usuário muda o status)

## Itens

Legenda: **NOVO** = no portal, ausente do manifest e deste arquivo · **ATUALIZADO** = versão maior que a local ·
**VERIFICAR** = registrado localmente, sem versão no portal · **Sem mudança** = versão igual à local.
Link "(página geral)" = o portal não expõe href do item; a URL leva à página onde ele aparece.

| Doc | Tipo | Nº | Versão | Data publicação | Ação | Status | Link |
|---|---|---|---|---|---|---|---|
| CT-e | NT | 2026.005 (Simples Nacional) | v1.00 | 30/10/2026 | NOVO em 12/11/2026 · arquivo já em `entrada/` | PENDENTE | https://www.cte.fazenda.gov.br/portal/exibirArquivo.aspx?conteudo=AtaVevRXCIQ= |
| CT-e | NT | 2026.004 (leiautes CT-e, CT-eOS, GTV-e) | v1.00 → v1.01 | 30/10/2026 | ATUALIZADO em 12/11/2026 · arquivo já em `entrada/` | PENDENTE | https://www.cte.fazenda.gov.br/portal/exibirArquivo.aspx?conteudo=urai6j7wfLM= |
| CT-e | NT | 2026.001 (RTC Vinculação Pagamento) | v1.01 | 02/03/2026 | NOVO em 12/11/2026 · arquivo já em `entrada/` | PENDENTE | https://www.cte.fazenda.gov.br/portal/exibirArquivo.aspx?conteudo=9qjN8INgSkA= |
| CT-e | XSD | Schemas NT 2026.004 RTC | v1.01 | 11/11/2026 | NOVO em 12/11/2026 | PENDENTE | https://dfe-portal.svrs.rs.gov.br/Cte/Documentos (página geral) |
| CT-e | XSD | Schemas NT 2026.005 SN | não informada | 11/11/2026 | NOVO em 12/11/2026 | PENDENTE | https://dfe-portal.svrs.rs.gov.br/Cte/Documentos (página geral) |
| CT-e | XSD | Schemas NT 2026.002 correção 2 | v1.01 | 21/08/2026 | NOVO em 12/11/2026 | PENDENTE | https://dfe-portal.svrs.rs.gov.br/Cte/Documentos (página geral) |
| CT-e | XSD | Schemas NT 2025.001 RTC 1.14a correção | v1.14a | 12/05/2026 | NOVO em 12/11/2026 | PENDENTE | https://dfe-portal.svrs.rs.gov.br/Cte/Documentos (página geral) |
| NF-e | NT | 2025.002 (RTC) | v1.53 | 30/10/2026 | NOVO em 12/11/2026 | PENDENTE | https://dfe-portal.svrs.rs.gov.br/NFe/Documentos (página geral) |
| NF-e | NT | 2026.005 (RTC Simples Nacional) | v1.00 | 30/10/2026 | NOVO em 12/11/2026 | PENDENTE | https://dfe-portal.svrs.rs.gov.br/NFe/Documentos (página geral) |
| NF-e | NT | 2026.006 (RTC Vinculação Pagamento) | v1.01 | 30/10/2026 | NOVO em 12/11/2026 | PENDENTE | https://dfe-portal.svrs.rs.gov.br/NFe/Documentos (página geral) |
| NF-e | NT | 2026.009 (correção de regra de validação) | v1.00 | 09/09/2026 | NOVO em 12/11/2026 | PENDENTE | https://dfe-portal.svrs.rs.gov.br/NFe/Documentos (página geral) |
| NF-e | NT | 2026.001 (PAA) | v1.02b | 29/07/2026 | NOVO em 12/11/2026 | PENDENTE | https://dfe-portal.svrs.rs.gov.br/NFe/Documentos (página geral) |
| NF-e | NT | 2026.004 (Schema CNPJ Alfa) | v1.01 | 08/06/2026 | NOVO em 12/11/2026 | PENDENTE | https://dfe-portal.svrs.rs.gov.br/NFe/Documentos (página geral) |
| NF-e | NT | 2026.003 (DANFE Simplificado Tipo 2) | v1.0 | 22/05/2026 | NOVO em 12/11/2026 | PENDENTE | https://dfe-portal.svrs.rs.gov.br/NFe/Documentos (página geral) |
| NF-e | NT | 2022.002 (Equiparação à Exportação) | v1.30 | 09/03/2026 | NOVO em 12/11/2026 | PENDENTE | https://dfe-portal.svrs.rs.gov.br/NFe/Documentos (página geral) |
| NF-e | NT | 2023.003 (Validação NFC-e, AM) | v1.4 | 24/09/2026 | NOVO em 12/11/2026 | PENDENTE | https://dfe-portal.svrs.rs.gov.br/NFe/Documentos (página geral) |
| NF-e | NT | 2021.003 (GTIN, construção civil) | v1.50 | 25/09/2026 | NOVO em 12/11/2026 | PENDENTE | https://dfe-portal.svrs.rs.gov.br/NFe/Documentos (página geral) |
| NF-e | NT | 2023.002 (extingue emissão assíncrona) | v1.02 | 26/10/2026 | NOVO em 12/11/2026 | PENDENTE | https://dfe-portal.svrs.rs.gov.br/NFe/Documentos (página geral) |
| NF-e | NT | 2014.001 (EPEC) | v1.41 | 04/08/2026 | NOVO em 12/11/2026 | PENDENTE | https://dfe-portal.svrs.rs.gov.br/NFe/Documentos (página geral) |
| NF-e | NT | 2026.007 (Emissão por Contribuinte exclusivo IBS/CBS) | v1.10 → v1.11 | 30/10/2026 | ATUALIZADO em 12/11/2026 | PENDENTE | https://dfe-portal.svrs.rs.gov.br/NFe/Documentos (página geral) |
| NF-e | NT | 2026.008 (Valor Líquido do Produto) | v1.00 → v1.01 | 30/10/2026 | ATUALIZADO em 12/11/2026 | PENDENTE | https://dfe-portal.svrs.rs.gov.br/NFe/Documentos (página geral) |
| NF-e | XSD | Evento 211110 (NT 2025.002) | v1.40 | 23/07/2026 | NOVO em 12/11/2026 | PENDENTE | https://dfe-portal.svrs.rs.gov.br/NFe/Documentos (página geral) |
| NF-e | XSD | Pacote de schemas NT 2022.002 | v1.30 | 20/03/2026 | NOVO em 12/11/2026 | PENDENTE | https://dfe-portal.svrs.rs.gov.br/NFe/Documentos (página geral) |
| NF-e | XSD | Pacote de schemas NT 2025.002 | v1.30 | 07/10/2025 | NOVO em 12/11/2026 | PENDENTE | https://dfe-portal.svrs.rs.gov.br/NFe/Documentos (página geral) |
| MDF-e | NT | 2026.001 | não indicada no portal | 29/05/2026 | VERIFICAR em 12/11/2026 | PENDENTE | https://dfe-portal.svrs.rs.gov.br/Mdfe/Documentos (página geral) |
| MDF-e | NT | 2022.002 (PAA) | v1.02 | 25/04/2026 | NOVO em 12/11/2026 | PENDENTE | https://dfe-portal.svrs.rs.gov.br/Mdfe/Documentos (página geral) |
| MDF-e | XSD | Schemas NT 2025.001 | v1.04 | 25/04/2026 | NOVO em 12/11/2026 | PENDENTE | https://dfe-portal.svrs.rs.gov.br/Mdfe/Documentos (página geral) |

Sem mudança (confirmado): CT-e NT 2025.001 v1.14b; CT-e NT 2026.002 v1.01; CT-e NT 2026.004 v1.00 (01/10/2026, também no portal);
CT-e MOC 4.00; CT-e schema PL_CTe_400_NT2026.001 v1.01c (já em `fontes/cte/xsd/`); NF-e NT 2026.002 v1.11;
NF-e NT 2026.010 v1.00; NF-e MOC v7.00; MDF-e NT 2025.001 v1.03; MDF-e MOC 3.00b.

Observações desta execução:
- Schemas NF-e e CT-e de anos anteriores (2019–2025) estão no portal e não foram listados linha a linha: são
  histórico, não entram aqui até alguém pedir.
- Os três PDFs de CT-e (2026.001, 2026.004, 2026.005) estão em `entrada/`, ainda não processados. Não foram lidos
  neste ambiente (sem leitor de PDF). Versão e data vêm da listagem da Fazenda e batem com a listagem do SVRS.
- NF-e Fazenda (`www.nfe.fazenda.gov.br`): ERRO_PORTAL_INDISPONIVEL parcial. A página retorna só o título, sem
  lista de NTs; uma busca na web não achou a listagem oficial (só sites de terceiros, não usados). Ver
  `docs/duvidas-abertas.md` #004. Nenhum item NF-e veio dessa fonte, só do SVRS.

## Histórico de atualizações
- 2026-11-12 16:12 — /fiscal-atualizar-fontes (2ª execução): sem novidades em relação à 1ª execução (mesmos 27 pendentes).
  Hrefs de CT-e confirmados na listagem da Fazenda; SVRS sem href (link para página geral). NF-e Fazenda sem listagem.
- 2026-11-12 16:05 — /fiscal-atualizar-fontes (1ª execução): 15 NT novas (CT-e 2, NF-e 12, MDF-e 1), 3 NT atualizadas
  (CT-e 2026.004; NF-e 2026.007 e 2026.008), 1 para verificar (MDF-e 2026.001), 8 schemas novos listados.

## Documentos ja importados (Ciclo v1)
Ver `docs/historico-arquivos/ARQUIVOS_NECESSARIOS_v1_2026-10-06.md`
