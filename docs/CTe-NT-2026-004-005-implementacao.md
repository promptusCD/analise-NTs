# CT-e: Plano de implementação das NT 2026.004 v1.01 e NT 2026.005 v1.00

**Status:** RASCUNHO para análise. Ainda não virou tarefa para desenvolvedores.
**Data de referência:** 12/11/2026
**Written for:** equipe de produto/analista que vai revisar o escopo e, depois, o time de desenvolvimento.

Este documento segue três etapas:
1. **Seção 2:** pré-tarefas. Perguntas e premissas que precisam de resposta antes de codar.
2. **Seções 3 a 6:** o que muda (campos, regras, eventos) e o que o sistema deve enviar.
3. **Seções 7 a 9:** ordem sugerida, tarefas para desenvolvedores e cuidados.

Fonte de verdade: as NTs em PDF (`fontes/cte/notas-tecnicas/`) e os XSDs em `fontes/cte/xsd/`. O catálogo (`catalogo/nt/cte/`) é um índice. Em caso de dúvida, o PDF e o XSD prevalecem.

---

## 1. Prazos

| # | NT / bloco | Homologação | Produção | Situação em 12/11/2026 |
|---|---|---|---|---|
| A | 2026.005: campos IBS/CBS no Simples Nacional | 26/10/2026 | **16/11/2026** | Homologação passou. Produção em 4 dias |
| B | 2026.005: regras de validação | **16/11/2026** | 14/12/2026 | Homologação em 4 dias |
| C | 2026.004 v1.01: valor líquido, Multa e Juros, emissão, CTe Simplificado, crédito presumido | "Até 26/10/2026" | 14/12/2026 | Homologação passou. Produção em 32 dias |
| D | 2026.004 v1.01: ICMS previsto no pagamento antecipado | 01/02/2027 | 01/03/2027 | Futura |
| E | 2026.005: evento de Tributação do SN (412140) | Implementação futura pela Administração Tributária | Implementação futura | Sem prazo definido |

Observação: na 2026.004 v1.00 o bloco principal tinha produção em 16/11/2026. A v1.01 moveu para 14/12/2026. A comparação é minha, feita entre os dois cronogramas.

**Risco principal:** os blocos A e B estão com prazo muito curto. Se a equipe não tiver as tarefas de A e B em andamento até a semana que vem, o bloco A entra em produção sem o campo implementado.

---

## 2. Pré-tarefas (para análise antes de codar)

Cada item tem uma **recomendação** (o que eu faria se ninguém responder). Você pode aceitar ou corrigir. Os itens marcados como **BLOQUEANTE** impedem o início da tarefa indicada.

### 2.1 Escopo e produto

| ID | Pergunta | Recomendação padrão | Status |
|---|---|---|---|
| P01 | **BLOQUEANTE para T08.** Qual é o pai correto de `vPrestLiq` no CT-e normal? O texto da NT (seção 1) diz `vPrest`. A tabela da seção 2 diz `vTPrestLiq` dentro de `vPrest`. O XSD mostra `vPrestLiq` em `det/vPrest` (CT-e Simplificado) e `vTPrestLiq` em `total` e em `vPrest`. | Seguir o XSD, confirmar com o PDF pág. 4 a 5 | Em aberto |
| P02 | **BLOQUEANTE para T01.** O pacote XSD `PL_CTe_400_NT2026.005 RTC SN_1.00` já contém as alterações da 2026.004 v1.01 (`vPrestLiq`, `gMultaJuros`, `gICMSPrevistoPagtoAntecip`)? A pasta da 2026.004 só tem a v1.00, e o `ARQUIVOS_NECESSARIOS.md` marca o XSD v1.01 como pendente. | Usar o pacote 2026.005 como base e pedir o XSD oficial da 2026.004 v1.01 para comparar | Em aberto |
| P03 | Quais tipos de emissão o sistema usa hoje? Normal (1), offline (2), EPEC (4), FS-DA (5), NFF (3)? A NT remove EPEC e FS-DA da autorização. | Mapear uso real antes de remover código | Em aberto |
| P04 | O sistema emite **CT-e de Multa e Juros** (`gMultaJuros`)? Emite **pagamento antecipado** (`gPagAntecipado`, `tpPagAnt`)? | Se não emite, T11 e T12 viram só validação de recebimento | Em aberto |
| P05 | O sistema atende **TAC, MEI ou PAA** (`procEmi=4`)? Isso ativa o evento de Apropriação de Crédito Presumido (211110) e as regras 1060 a 1071. | Ativar T14 apenas se atender esses perfis | Em aberto |
| P06 | Quais **CRT** os clientes usam? Quais têm opção pendente pelo Simples (CRT 3 com `tpRegimeIBSCBS` 2, 3 ou 4)? | Mapear base de clientes com o comercial | Em aberto |
| P07 | Há clientes com **compra governamental** (`gCompraGov`, `tpEnteGov`)? Isso ativa as regras 1108 e 1109 (IBS SN zero em 2027 e 2028 para a União). | Implementar as regras sem depender de cliente | Em aberto |
| P08 | Há operações em **Zona Franca de Manaus ou ALC** (alíquota zero de CBS)? | Só implementar se houver operação real | Em aberto |
| P09 | **BLOQUEANTE para T06.** As alíquotas de 2026 e 2027 em homologação (`tpAmb=2`) devem ser aceitas em produção? A NT diz que não. | Não aceitar fora de `tpAmb=2` | Em aberto |
| P10 | O IBS e a CBS são **calculados pelo CT-e** ou **recebidos de outro sistema** (ERP, calculadora)? | Confirmar, porque muda o escopo de T06 a T09 | Em aberto |
| P11 | Quem gera a **Tributação do SN (412140)**? A NT diz que é a Administração Tributária. O sistema precisa só consultar ou tratar retorno? | Não implementar envio. Só tratar consulta, se houver | Em aberto |

### 2.2 Dúvidas de extração (texto da NT)

| ID | Item | Ação |
|---|---|---|
| P12 | Regra 909 (CT-e complementar, mesmo ano e mês): a condição está truncada na extração. | Ler o PDF, pág. 12, e registrar a condição completa |
| P13 | Regra 1083: a mensagem está quebrada na extração. | Ler o PDF, pág. 7, e corrigir o texto |
| P14 | Regras 1051 e 1052: a mensagem está idêntica nas duas. | Ler o PDF, pág. 5, e confirmar qual é a mensagem de cada uma |

### 2.3 Informações que você precisa me enviar

Se você tiver estes itens, me passe. Sem eles, a tarefa fica com a recomendação da seção 2.1.

- [ ] Lista de **produtos de serviço** (cClassTrib) usados pelos clientes.
- [ ] Regra de **alíquota de IBS e CBS** que a empresa aplica hoje (se o sistema calcula).
- [ ] Ambientes: quais CNPJs/UFs estão em homologação e quais em produção.
- [ ] Lista de **tarefas já abertas** para a 2026.004 v1.00 (Jira, planilha ou outro). Eu comparo com este plano e marco o que já está coberto.
- [ ] Versão do **layout** (`versao`) que o sistema envia hoje.

---

## 3. O que muda na NT 2026.004 v1.01

### 3.1 Campos novos

| Campo (NT) | Onde fica | Tipo / tamanho | Ocorrência | Quando enviar | Fonte |
|---|---|---|---|---|---|
| `vPrestLiq` | `det/vPrest` (CT-e Simplificado) | N, 13v2 | 0-1 | Quando o sistema quiser informar o valor líquido do item, sem tributos | NT pág. 4 a 5; XSD `cteTiposBasico` |
| `vTPrestLiq` | `total` (CT-e Simplificado) e `vPrest` (CT-e) | N, 13v2 | 0-1 | Valor líquido total da prestação, sem tributos. Tem de bater com a soma dos itens (regra 1054) | NT pág. 4 a 5; XSD |
| `vICMSPrevisto` | `gICMSPrevistoPagtoAntecip` | N, 13v2 | **1-1 (obrigatório no grupo)** | Só em pagamento antecipado de compra governamental (ver 3.3) | NT pág. 5; XSD |
| `gICMSPrevistoPagtoAntecip` | Dentro do grupo ICMS (`ICMSSN`/`CST`/`indSN` no XSD) | Grupo | 0-1 | Mesma condição do `vICMSPrevisto` | NT pág. 5; XSD |
| `gMultaJuros` | Dentro de `Ide`, pela NT. No XSD aparece perto de `gPagAntecipado` | Grupo | 0-1 | Ver 3.4. **P01 e P04 precisam confirmar o pai** | NT pág. 6; XSD |
| `chCTeRef` | Dentro de `gMultaJuros` | Chave, 44 | 1-1 | Chave do CT-e que sofre multa ou juros | NT pág. 6; XSD `TChDFe` |
| `IBSCBSTot` | `total` (CT-e Simplificado) | Grupo | 0-1 | Totais de IBS e CBS (ver 3.5) | NT pág. 12 a 13; XSD |

### 3.2 Regras novas e alteradas

| cStat | Efeito | Aplicação | Regra resumida | Situação na NT |
|---|---|---|---|---|
| 1054 | Rej | Obrig. | `vTPrestLiq` (total) deve ser igual à soma de `vPrestLiq` dos itens | Nova |
| 1051 | Rej | Obrig. | Grupo ICMS previsto informado indevidamente (fora de compra governamental ou pagamento antecipado) | Nova. P14 |
| 1052 | Rej | Obrig. | Grupo ICMS previsto informado indevidamente (`tpPagAnt` ou `tpOperGov` fora da condição) | Nova. P14 |
| 1053 | Rej | Obrig. | Grupo ICMS previsto **deve** ser informado (`tpPagAnt` = 1 e `tpOperGov` = 4) | Nova |
| 1072 | Rej | Obrig. | CT-e de Multa e Juros não pode ser tributado pelo ICMS. O CST deve ser 41 | Nova |
| 1073 | Rej | Obrig. | Chave de acesso do CT-e referenciado inválida (CNPJ zerado, ano, mês) | Nova |
| 1074 | Rej | Facult. | CT-e referenciado inexistente na base da SEFAZ | Nova. **Facultativa** |
| 1075 | Rej | Facult. | CT-e referenciado com diferença de chave de acesso | Nova. **Facultativa** |
| 1076 | Rej | Facult. | CT-e referenciado cancelado | Nova. **Facultativa** |
| 1077 | Rej | Facult. | CT-e referenciado substituído | Nova. **Facultativa** |
| 1078 | Rej | Obrig. | Emitente do CT-e referenciado diferente do emitente do CT-e de Multa e Juros | Nova |
| 1079 | Rej | Obrig. | Tomador do CT-e referenciado diferente do tomador do CT-e de Multa e Juros | Nova |
| 1080 | Rej | Obrig. | UF de início e fim da prestação devem ser iguais | Nova |
| 1081 | Rej | Obrig. | CST e cClassTrib do IBS/CBS devem ser iguais (não se aplica ao CT-e Simplificado) | Nova |
| 1082 | Rej | Obrig. | Tipo de CT-e (`tpCTe`) deve ser igual | Nova |
| 1083 | Rej | Obrig. | Tipo de serviço (`tpServ`) deve ser igual. **P13** | Nova |
| 316 | Rej | Obrig. | Alíquota de IBS UF inválida. 0,1% em 2026, 0,05% em 2027 e 2028. Em 2026 e 2027, aceita as alíquotas de 2026 e 2027 só com `tpAmb=2` | Alterada (exceção de homologação) |
| 321 | Rej | Obrig. | Alíquota de IBS Município inválida. 0% em 2026, 0,05% em 2027 e 2028. Mesma exceção de homologação | Alterada (exceção de homologação) |
| 326 | Rej | Obrig. | Alíquota de CBS inválida. 0,90% em 2026 | Alterada (exceção de homologação) |
| 365 | Rej | Obrig. | `vTotDFe`: em 2026, repete `vTPrest`. A partir de 2027, `vPrest + IBS + CBS` | Alterada |
| 228 | Rej | Obrig. | Data de emissão atrasada (168 horas). **Não se aplica** se houver `gMultaJuros` ou `gPagAntecipado`. Retorno de fora de prazo: cStat 150 | Alterada |
| 853 | Rej | Obrig. | Parâmetro `sign` não informado no QR Code em contingência offline | Alterada (inclui offline e EPEC; EPEC sai) |
| 855 | Rej | Obrig. | Assinatura do QR Code difere da calculada | Alterada (inclui offline e EPEC) |
| 586 | Rej | Obrig. | **Excluída.** Relacionada ao FS-DA | Excluída |
| 928 | Rej | Obrig. | **Excluída.** Tipo de emissão FS-DA não permitido | Excluída |
| 530 | Rej | Obrig. | **Excluída.** Rejeição de eventos em SVC | Excluída |
| 370 | Rej | Obrig. | **Excluída.** Município de fim de prestação único no CT-e Simplificado | Excluída |
| 1055 | Rej | Obrig. | Doação com CNPJ/CPF do emitente igual ao do tomador | Sem marcação de alteração. Conferir se já existe |
| 1056 | Rej | Obrig. | cClassTrib incompatível com indicador de doação | Sem marcação de alteração. Conferir se já existe |
| 1057 | Rej | Obrig. | cClassTrib exige indicador de doação | Sem marcação de alteração. Conferir se já existe |

**Regra 1051 a 1053:** as três são do mesmo grupo. A pré-tarefa P14 é confirmar a redação de cada uma no PDF.

### 3.3 ICMS previsto no pagamento antecipado (2027)

- Quando informar: `tpPagAnt = 1` (pagamento antecipado) **e** `tpOperGov = 4` (recebimento com fornecimento posterior).
- Não informar em outros casos (regra 1051 e 1052).
- Se não houver ICMS devido, informar `0`.
- **Prazo:** homologação 01/02/2027, produção 01/03/2027.

### 3.4 Multa e Juros (`gMultaJuros`)

- Usado para CT-e que cobra multa ou juros de outro CT-e já emitido.
- O CT-e referenciado (`chCTeRef`) deve ter o **mesmo** emitente, tomador, UF de início e fim, CST e cClassTrib, tipo de CT-e e tipo de serviço.
- O CST do ICMS deve ser **41** (ICMS45), porque multa e juros não podem ser tributados pelo ICMS.
- Validações da chave (1073) são obrigatórias. Validações contra a base da SEFAZ (1074 a 1077) são **facultativas**.

### 3.5 Totais do CT-e Simplificado (`IBSCBSTot`)

- `vBCIBSCBS` (1-1, 13,2).
- Grupos `gIBS` (com `gIBSUF` e `gIBSMun`) e `gCBS`, com diferimento, devolução e estorno.
- Regras 348 a 359, 305 e 306: cada total deve ser a soma dos itens. O total do IBS deve ser a soma de IBS UF e IBS Município.

### 3.6 Emissão

- **EPEC:** deixa de ser aceita pelo ambiente de autorização. CT-e com `tpEmis=4` continua sendo recebido, para conciliar eventos já registrados. O código da SVC EPEC (4) está em desativação.
- **FS-DA (`tpEmis=5`):** excluída. Regras 586, 928 e 530 saem.
- **Offline (`tpEmis=2`):** continua. QR Code com `sign` (regras 853 e 855). Regra 228 com exceção para Multa e Juros e pagamento antecipado.

### 3.7 Evento de Apropriação de Crédito Presumido (211110)

- **Autor:** o tomador do serviço. Só vale para CT-e emitido por TAC (com `tpEmis=3` ou `procEmi=4`) ou MEI (`CRT=4`).
- **Autorização:** exclusiva na SVRS.
- **Campos:** `cCredPres` (tabela do Anexo IV), `vBCCredPres`, `gIBSCredPres` (`pCredPres`, `vCredPres`), `gCBSCredPres`, `xDecPag` quando exigido.
- **Regras:** 1060 a 1071. Mais importantes: 1060 (quem pode apropriar), 1066 e 1069 (valor difere do calculado, tolerância de 0,01), 1070 e 1071 (`xDecPag` obrigatório ou proibido conforme `cCredPres`).
- **Retorno:** evento homologado retorna cStat 135.

---

## 4. O que muda na NT 2026.005 v1.00 (Simples Nacional)

### 4.1 Campo novo

| Campo | Onde fica | Tipo | Ocorrência | Quando enviar |
|---|---|---|---|---|
| `tpRegimeIBSCBS` | `emit` | C, 1 | 0-1 | Só nas situações abaixo |

Valores:
- **1:** CRT 1 ou 2 com opção pelo regime regular do IBS/CBS.
- **2:** CRT 3 com opção pendente pelo CRT 1 (Simples), sem regime regular.
- **3:** CRT 3 com opção pendente pelo CRT 2 (Simples, excesso de sublimite), sem regime regular.
- **4:** CRT 3 com opção pendente pelo Simples (CRT 1 ou 2), com regime regular.

Não informar nos demais casos. Regras 1090 (CRT 1 ou 2 com valor diferente de 1), 1091 (CRT 3 com valor fora de 2, 3 ou 4) e 1092 (MEI não deve informar).

### 4.2 Matriz: o que enviar por situação

| Situação do emitente | `tpRegimeIBSCBS` | `gIBSCBS` | `gTribSN` |
|---|---|---|---|
| Simples (CRT 1 ou 2), regime regular | 1 | Sim: `gIBSUF`, `gIBSMun`, `gCBS` | Não |
| Simples (CRT 1), sem regime regular | Não informar | **Não** (regra 1100) | **Sim**, com `gIBSSN` e `gCBSSN` (regra 1101) |
| Simples (CRT 2), excesso de sublimite, sem regime regular | Não informar | Sim, com `gIBSUF`, `gIBSMun`, `gCBS` (alíquota zero) | Sim, só com `gCBSSN` (regras 1103 e 1104) |
| Regime normal (CRT 3), opção pendente CRT 1, sem regime regular | 2 | Sim | Sim, com `gIBSSN` e `gCBSSN` (regra 1105) |
| Regime normal (CRT 3), opção pendente CRT 2, sem regime regular | 3 | Sim | Sim, só com `gCBSSN` (regra 1106) |
| Regime normal (CRT 3), opção pendente Simples, com regime regular | 4 | Sim | **Não** (regra 1102) |
| MEI (CRT 4) | Não informar | **Não** (regra 1107) | **Não** (regra 1107) |

Fonte: NT 2026.005 pág. 4 a 9. Esta tabela é resumo. A NT tem os detalhes completos, e a implementação deve seguir a NT, não este resumo.

### 4.3 Grupo `gTribSN` (composição do SN)

| Campo | Pai | Tipo | Ocorrência | Observação |
|---|---|---|---|---|
| `gTribSN` | `IBSCBS` | Grupo | 0-1 | Composição do IBS e CBS para o SN |
| `gIBSSN` | `gTribSN` | Grupo | 0-1 | IBS do SN |
| `pIBSSN` | `gIBSSN` | N, 3v2-4 | 1-1 | Alíquota efetiva do IBS. Zero para compra governamental da União em 2027 e 2028 |
| `vIBSSN` | `gIBSSN` | N, 13v2 | 1-1 | Valor do IBS do SN. Zero para compra governamental da União em 2027 e 2028 |
| `gCBSSN` | `gTribSN` | Grupo | 0-1 | CBS do SN |
| `pCBSSN` | `gCBSSN` | N, 3v2-4 | 1-1 | Alíquota efetiva da CBS. Na União em 2027 e 2028, é a soma de IBS e CBS do SN |
| `vCBSSN` | `gCBSSN` | N, 13v2 | 1-1 | Valor da CBS do SN |

### 4.4 Totais do DFe (CT-e Simplificado)

Dentro de `IBSCBSTot/gTribSN`:
- `vIBSSN`: soma dos `vIBSSN` dos itens (regra 1111).
- `vCBSSN`: soma dos `vCBSSN` dos itens (regra 1112).
- O grupo total é obrigatório se pelo menos um item tiver `gTribSN` (regra 1110).

### 4.5 Regras de alíquota (CBS)

- **2026:** CBS de 0,90% (regra 316). Alíquota zero só para área incentivada específica (ZFM ou ALC), com regras próprias da NT.
- **Área incentivada:** a NT lista municípios de ZFM (Manaus, Rio Preto da Eva, Itacoatiara) e pares de municípios de ALC (Tabatinga, Guajará-Mirim, Boa Vista, Bonfim, Macapá, Santana, Brasileia, Epitaciolândia, Cruzeiro do Sul). **Não hardcodar a lista no código.** Se for implementar, usar tabela de parâmetros. Só serviços presenciais se beneficiam.
- **2027 em diante:** `pCBS` deve ser a alíquota vigente para o período (regra 316, parte 2027). Consultar a tabela de alíquotas da CBS.
- **Homologação:** até a alíquota de 2027 ser publicada, usar a de 2026. Depois da publicação, aceitar também a de 2027 em homologação.

### 4.6 Evento de Tributação do SN (412140)

- **Quem gera:** Administração Tributária, com base nos DFe recebidos e emitidos por contribuintes do Simples.
- **Tipo:** `tpEvent = 412140`. Schema `evTributacaoSN_v1.00.xsd`.
- **Cancelamento:** evento 412141 (`evCancTributacaoSN_v1.00.xsd`). Só para DFe autorizado.
- **O que o emissor precisa:** provavelmente nada no envio. Ver pré-tarefa P11.
- **Conteúdo do evento (para referência):** `gTribItemSN` por item (`vRBSNitem`, `tpRBSN`, `pIBSSN`, `vIBSSN`, `pCBSSN`, `vCBSSN`, `vIBSPendSusp`, `vCBSPendSusp`). `gTotalSN` com totais.

### 4.7 Regra 909 (CT-e complementar)

- Se o CT-e é complementar (Tipo = 1) e o emitente é CRT 1, CRT 2 ou CRT 3 com opção pendente, as chaves dos CT-e complementados devem ser do mesmo ano e mês.
- A condição completa está truncada na extração. **P12.**

---

## 5. O que o sistema deve enviar (resumo por tipo de documento)

| Documento | Campos novos a enviar | Regras a respeitar |
|---|---|---|
| CT-e normal | `vPrestLiq`/`vTPrestLiq` (opcional). `gMultaJuros` (se aplicável). `gICMSPrevistoPagtoAntecip` (se aplicável). `tpRegimeIBSCBS` (se optante ou pendente). | 1054, 1051 a 1053, 1072 a 1083, 365, 326, 316, 321, 228, 853, 855, 1090 a 1092, 1100 a 1107 |
| CT-e Simplificado | `det/vPrest/vPrestLiq`. `total/vTPrestLiq`. `IBSCBSTot` (com `gTribSN`). `tpRegimeIBSCBS` (se aplicável). | Regras 348 a 359, 305, 306, 1110 a 1112, 1054 |
| CT-e de Multa e Juros | `gMultaJuros` com `chCTeRef`. CST ICMS 41. | 1072 a 1083 |
| Pagamento antecipado | `gICMSPrevistoPagtoAntecip` com `vICMSPrevisto`. | 1051 a 1053 (vigente em 01/03/2027) |
| Evento 211110 (crédito presumido) | Enviado pelo tomador, no ambiente da SVRS. | 1060 a 1071 |
| Evento 412140 e 412141 | Não enviado pelo emissor. Só consultar, se houver. | Ver 4.6 |
| Eventos de EPEC (`tpEmis=4`) | Sem novos envios. Conciliação de eventos já registrados. | Ver 3.6 |

---

## 6. Cuidados (lista para o time)

1. **Alíquotas de homologação:** as alíquotas de 2026 e 2027 só podem ser aceitas com `tpAmb=2`. Em produção, rejeitar (regras 316, 321).
2. **`vTotDFe` muda em 2027.** Em 2026, o total é `vTPrest`. A partir de 2027, `vPrest + IBS + CBS`. Não misturar as duas fórmulas no mesmo código sem controle por data de emissão.
3. **Data de emissão decide a alíquota.** Usar sempre a data de emissão do DFe, não a data do sistema.
4. **Remover EPEC e FS-DA com cuidado.** O CT-e com `tpEmis=4` continua sendo recebido. O código de emissão precisa aceitar o retorno, mas não gerar novos EPEC. Confirmar com P03.
5. **Offline e regra 228:** o CT-e offline que chega depois de 168 horas não deve ser rejeitado se tiver `gMultaJuros` ou `gPagAntecipado`. Retorno esperado: cStat 150.
6. **Não hardcodar a lista de ZFM e ALC.** Usar tabela de parâmetros atualizável.
7. **Multa e Juros:** o CT-e referenciado precisa existir e ter a mesma estrutura. Validar antes de enviar, para não gerar rejeição de cStat 1078 a 1083.
8. **Cor não prova nada:** a seção "Descrição das alterações" da NT é a referência, não a cor do texto. A NT 2026.004 v1.01 tem texto AMARELO e VERDE nas alterações. A cor sozinha não indica revisão.
9. **Schema primeiro:** antes de qualquer regra, gerar o XML e validar contra o XSD novo. Se o XSD não validar, nenhuma regra funciona.
10. **Homologação antes de produção:** cada bloco (A a E) precisa de teste no ambiente de homologação com o prazo da seção 1.
11. **Arquivos da NT:** não alterar nada em `fontes/`. Os arquivos são somente leitura.

---

## 7. Ordem sugerida de implementação

Os prazos estão na seção 1. Esta ordem prioriza o que vence primeiro.

**Fase 0: análise (até 13/11/2026)**
1. Responder P01 a P11 (seção 2.1). Bloqueantes: P01, P02, P09.
2. Confirmar pré-tarefas de extração P12 a P14.
3. Comparar com as tarefas já abertas (2.3).

**Fase 1: bloco A (2026.005 campos), produção 16/11/2026**
4. T01: base de XSD (2026.005 com 2026.004).
5. T02: campo `tpRegimeIBSCBS` e validação 1090 a 1092.
6. T03: grupo `gTribSN` (`gIBSSN`, `gCBSSN`) e validações 1100 a 1107 e 315.

**Fase 2: bloco B (2026.005 regras), homologação 16/11, produção 14/12/2026**
7. T04: alíquotas 316, 321, 326 (com exceção de `tpAmb=2`).
8. T05: totais SN (1110 a 1112).
9. T06: regras de compra governamental (1108, 1109). Só se P07 confirmar.

**Fase 3: bloco C (2026.004 v1.01), produção 14/12/2026**
10. T07: `vPrestLiq`/`vTPrestLiq` e regra 1054 (depois de P01).
11. T08: `vTotDFe` (regra 365) e retirada da orientação de incluir IBS/CBS no `vPrest`.
12. T09: `gMultaJuros` e regras 1072 a 1083 (se P04 confirmar).
13. T10: emissão: EPEC, FS-DA, offline, regra 228 e QR Code (853, 855).
14. T11: evento 211110 (crédito presumido), se P05 confirmar.

**Fase 4: bloco D (ICMS previsto), produção 01/03/2027**
15. T12: `gICMSPrevistoPagtoAntecip` e regras 1051 a 1053.

**Fase 5: eventos e fechamento**
16. T13: evento 412140 e 412141, se P11 confirmar consulta.
17. T14: CT-e complementar (regra 909), depois de P12.
18. T15: regressão completa e testes de homologação.

---

## 8. Tarefas para desenvolvedores

Cada tarefa tem: **escopo**, **critério de aceite** (o que precisa estar verdadeiro para dar como pronta) e **depende de** (pré-tarefa ou outra tarefa).

**T01: base de XSD**
- Escopo: gerar o schema novo a partir do pacote 2026.005 (e 2026.004 v1.01, quando o XSD oficial chegar).
- Aceite: XML de exemplo valida contra o XSD sem erros.
- Depende de: P02.

**T02: `tpRegimeIBSCBS`**
- Escopo: campo `emit/tpRegimeIBSCBS`, com valores 1 a 4. Validação de CRT vs valor (1090, 1091, 1092).
- Aceite: envio correto para cada situação da matriz 4.2. Testes unitários para CRT 1, 2, 3 e 4 com cada valor.
- Depende de: T01, P06.

**T03: `gTribSN` e validações SN**
- Escopo: grupo `gTribSN` com `gIBSSN` e `gCBSSN`. Validações 315, 1100 a 1107.
- Aceite: cada combinação da matriz 4.2 gera XML válido. Rejeições corretas em homologação.
- Depende de: T02.

**T04: alíquotas (316, 321, 326)**
- Escopo: tabela de alíquotas por data de emissão (2026, 2027, 2028, pós-2028). Exceção de `tpAmb=2`.
- Aceite: teste de alíquota fora da tabela rejeita em produção e aceita em homologação (quando a exceção se aplica).
- Depende de: P09, P10.

**T05: totais SN (1110 a 1112)**
- Escopo: `IBSCBSTot/gTribSN` com `vIBSSN` e `vCBSSN`, somados a partir dos itens.
- Aceite: total igual à soma dos itens em todos os casos de teste. Rejeição quando diferente.
- Depende de: T03.

**T06: compra governamental (1108, 1109)**
- Escopo: IBS SN zero para compra da União em 2027 e 2028.
- Aceite: caso de teste com `tpEnteGov=1` em 2027 e 2028.
- Depende de: P07.

**T07: valor líquido**
- Escopo: `vPrestLiq` (item) e `vTPrestLiq` (total). Validação 1054.
- Aceite: total igual à soma dos itens. Rejeição quando diferente.
- Depende de: P01.

**T08: `vTotDFe` (regra 365)**
- Escopo: em 2026, `vTotDFe = vTPrest`. A partir de 2027, `vTPrest + IBS + CBS`. Retirar a orientação de incluir IBS/CBS no `vPrest`.
- Aceite: teste com data de emissão em 2026 e em 2027.
- Depende de: P10.

**T09: Multa e Juros (`gMultaJuros`)**
- Escopo: grupo, `chCTeRef` e validações 1072 a 1083.
- Aceite: caso de teste para cada cStat. Validação 1074 a 1077 só se a consulta à base for implementada.
- Depende de: P04, P12, P13.

**T10: emissão (EPEC, FS-DA, offline)**
- Escopo: remover geração de EPEC e FS-DA. Manter recebimento de CT-e com `tpEmis=4`. QR Code (853, 855) para offline. Regra 228 com exceções.
- Aceite: FS-DA e EPEC não geradas. Offline com QR Code válido. Retorno 150 para atraso com Multa e Juros.
- Depende de: P03.

**T11: evento de crédito presumido (211110)**
- Escopo: evento do tomador, com regras 1060 a 1071 e envio à SVRS.
- Aceite: caso de teste para TAC e MEI. Retorno 135 em homologação.
- Depende de: P05.

**T12: ICMS previsto (1051 a 1053)**
- Escopo: grupo `gICMSPrevistoPagtoAntecip` com `vICMSPrevisto`.
- Aceite: caso de teste para cada cStat. Prazo: produção em 01/03/2027.
- Depende de: P04, P14.

**T13: eventos 412140 e 412141**
- Escopo: depende de P11. Pode ser só leitura ou nada.
- Aceite: conforme decisão de P11.

**T14: CT-e complementar (909)**
- Escopo: validação de mesmo ano e mês.
- Aceite: casos de teste com mesmo mês, mês diferente e ano diferente.
- Depende de: P12.

**T15: regressão e homologação**
- Escopo: rodar todos os casos acima em homologação, por bloco, antes do prazo de produção.
- Aceite: relatório de homologação com todos os cStat esperados.
- Depende de: todas as anteriores.

---

## 9. Dúvidas em aberto (registrar em `docs/duvidas-abertas.md` depois de respondidas)

- P01: pai de `vPrestLiq` e `vTPrestLiq`.
- P02: pacote XSD da 2026.004 v1.01.
- P03: tipos de emissão usados hoje.
- P04: CT-e de Multa e Juros e pagamento antecipado.
- P05: TAC, MEI e PAA.
- P06: CRT e opção pendente da base de clientes.
- P07: compra governamental.
- P08: ZFM e ALC.
- P09: alíquotas de homologação.
- P10: cálculo de IBS e CBS (sistema ou externo).
- P11: evento 412140.
- P12: regra 909 (texto completo).
- P13: regra 1083 (texto).
- P14: regras 1051 e 1052 (texto).

---

## Fontes

- **Oficial** · CT-e NT 2026.004 v1.01 · `fontes/cte/notas-tecnicas/CTe_NT_2026_004_v1.01.pdf` · págs. 3 (cronograma), 4 a 5 (campos e ICMS previsto), 6 a 7 (Multa e Juros e alíquotas), 8 a 9 (regras de emissão), 9 a 10 (EPEC e FS-DA), 12 a 13 (CT-e Simplificado), 14 a 16 (crédito presumido).
- **Oficial** · CT-e NT 2026.004 v1.00 · `fontes/cte/notas-tecnicas/CTe_NT_2026_004_v1.00.pdf` · págs. 3 (cronograma), 6 (ICMS previsto, 01/02/2027 e 01/03/2027).
- **Oficial** · CT-e NT 2026.005 v1.00 · `fontes/cte/notas-tecnicas/CTe_NT_2026_005_SN_v1.00.pdf` · págs. 3 (cronograma), 4 a 5 (`tpRegimeIBSCBS` e `gIBSCBS` por situação), 5 a 9 (grupo `gTribSN` e regras 315 a 1112), 9 (totais), 10 a 12 (eventos 412140 e 412141), 12 (regra 909).
- **Oficial (XSD)** · `fontes/cte/xsd/PL_CTe_400_NT2026.005 RTC SN_1.00/` · `cteTiposBasico_v4.00.xsd`, `DFeTiposBasicos_v1.00.xsd`, `evTributacaoSN_v1.00.xsd`, `evCancTributacaoSN_v1.00.xsd`, `evApropriaCredPres_v4.00.xsd`.
- Catálogo: `catalogo/nt/cte/CTe_NT_2026_004_v1.01.json` e `catalogo/nt/cte/CTe_NT_2026_005_SN_v1.00.json`. Índice, não fonte primária.
