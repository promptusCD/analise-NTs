# Dúvidas abertas

> Registro de inconsistências e contradições encontradas nas fontes (regras 8 e 9 do AGENTS.md).
> Use `/fiscal-duvidas --registrar` para acrescentar. Não reescreva entradas existentes.

## Formato de cada entrada

```
### [#NNN] <título curto>
- Data: AAAA-MM-DD
- Documento: NF-e | CT-e | MDF-e
- NT/MOC: <referência e versão>
- Página: <N>
- Trecho: <trecho problematico, curto>
- O que parece errado: <descrição>
- Fontes em conflito: <oficial vs outra, se houver>
- Prioridade: ALTA | MEDIA | BAIXA
- Impacto: <por que>
- Status: pendente | resolvida (fonte: ...)
```

## Entradas

### [#001] MOC CT-e Visão Geral: cStat 890 não vira regra
- Data: 2026-10-20
- Documento: CT-e
- NT/MOC: MOC CT-e v4.00 - Visão Geral
- Página: 71
- Trecho: "O06 Rejeitar se o CTe de valores informado possuir GTVe informadas Obrig. 890 Rej. Rejeição: Evento GTV não é permitido para CTe OS que relaciona GTVe"
- O que parece errado: o PDF imprime a aplicação e o cStat 890, mas nenhuma regra com cStat 890 sai em `regras_validacao` (a linha parece não ser reconhecida como início de regra).
- Fontes em conflito: nenhuma (falha do extrator)
- Prioridade: MEDIA
- Impacto: 1 regra de 165 ausente; `/fiscal-regra 890` responderia "NAO ENCONTRADO NAS FONTES" mesmo existindo no MOC.
- Status: pendente (listada em LACUNAS_CONHECIDAS de `tests/python/test_moc.py`)

### [#002] MOC NF-e Visão Geral: cStat 831 não vira regra
- Data: 2026-10-20
- Documento: NF-e
- NT/MOC: MOC NF-e v7.00 - Visão Geral
- Página: 122
- Trecho: "... Evento atual com CNPJ/CPF Autor (tag:CNPJ, id:P10) diferente do Emitente ou Destinatário da NF-e Obrig. 831 Rejeição: Transportador Contratado não autorizado a ..."
- O que parece errado: regra sem o token "Rej." (só "Obrig. 831 Rejeição:") dentro de um span longo; não é reconhecida.
- Fontes em conflito: nenhuma (falha do extrator)
- Prioridade: MEDIA
- Impacto: 1 regra de 226 ausente.
- Status: pendente (listada em LACUNAS_CONHECIDAS de `tests/python/test_moc.py`)

### [#003] CT-e NT 2026.004 pág. 7: cabeçalho amarelo da tabela de ALC é dado, mas sai como AMARELO
- Data: 2026-10-20
- Documento: CT-e
- NT/MOC: NT CT-e 2026.004 v1.00
- Página: 7
- Trecho: tabela "ALC | Município Início | Município Fim" dentro da regra cStat 326
- O que parece errado: a cor (amarelo, verde, laranja) da tabela de ALC é DADO (quais municípios pertencem à mesma área), não revisão (regra 7 do AGENTS.md; skill `interpretar-nota-tecnica`, categoria DADO). O extrator marca o cabeçalho "ALC" / "Município Início Município Fim" como `AMARELO`, o que infla a contagem de alterações e pode ser lido como revisão.
- Fontes em conflito: nenhuma
- Prioridade: BAIXA
- Impacto: ruído nas estatísticas por marcação; risco de interpretar o cabeçalho como alteração de regra.
- Status: pendente (fora do escopo da change fase-2b)

### [#004] Portal NF-e Fazenda sem lista de NTs (2026-11-12)
- Data: 2026-11-12
- Documento: NF-e
- NT/MOC: portal `https://www.nfe.fazenda.gov.br` (página "Documentos")
- Página: n/a
- Trecho: a página retornou só o título "Portal Nacional da Nota Fiscal Eletrônica", sem NTs, MOCs ou XSDs. Em execução anterior, `listaConteudo.aspx` deu "Too many redirects" (3 tentativas).
- O que parece errado: a fonte oficial Fazenda da NF-e não foi listada em nenhuma execução, então a verificação de NF-e depende só do SVRS.
- Fontes em conflito: nenhuma (fonte não consultada com sucesso)
- Prioridade: MEDIA
- Impacto: uma NT NF-e publicada só na Fazenda não aparece nos relatórios de `/fiscal-atualizar-fontes`.
- Status: pendente (ERRO_PORTAL_INDISPONIVEL parcial; informar a URL exata da página de Notas técnicas da NF-e para tentar de novo)

### [#005] MDF-e NT 2022.002 v1.02: título vazio no JSON (capa sem título)
- Data: 2026-11-12
- Documento: MDF-e
- NT/MOC: NT MDF-e 2022.002 v1.02 (`fontes/mdfe/notas-tecnicas/MDFe_NT_2022_002_PAA_v1.02.pdf`)
- Página: 1 (capa); título aparece na pág. 2 ("NT 2022.002 PAA")
- Trecho: capa diz só "Projeto Manifesto Eletrônico de Documentos Fiscais / Nota Técnica 2022.002 / Versão 1.02 – abril 2026"
- O que parece errado: `verificar_extracao.py` marca TITULO_SUSPEITO (`titulo: ''`). Pela pág. 2 e pelo sumário, o assunto é "Provedor de Assinatura e Autorização (PAA)". Não editei o JSON gerado.
- Fontes em conflito: nenhuma (falha de extração de metadados)
- Prioridade: MEDIA
- Impacto: bloqueia o verificador (exit 1) até o título ser resolvido ou a dúvida aceita; manifest já usa "Nota Tecnica 2022.002 (PAA)".
- Status: pendente (corrigir título no extrator ou confirmar "Provedor de Assinatura e Autorização (PAA)")

### [#006] NTs com `arquivo_origem` absoluto e títulos de cabeçalho ("Projeto ...") no JSON
- Data: 2026-11-12
- Documento: CT-e, NF-e, MDF-e
- NT/MOC: NT CT-e 2025.001 v1.14b, CT-e 2026.002 v1.01, CT-e 2026.004 v1.00, NF-e 2026.002 v1.11, NF-e 2026.007 v1.10, NF-e 2026.008 v1.00, NF-e 2026.010 v1.00, MDF-e 2025.001 v1.03, MDF-e 2026.001 v1.00
- Página: n/a
- Trecho: `arquivo_origem: /Users/.../fontes/...` (absoluto); `titulo: 'Projeto Conhecimento de'` / `'Projeto Nota Fiscal'` / `'Projeto Manifesto'`
- O que parece errado: JSONs gerados antes da correção do extrator guardam caminho absoluto (viola a regra de origem relativa do verificador) e pegam a linha do cabeçalho da capa como título. Os JSONs de 2026-11 (CT-e 2025.001 v1.14a, CT-e 2026.001, CT-e 2026.004 v1.01, CT-e 2026.005, MDF-e 2022.002) saíram corretos.
- Fontes em conflito: nenhuma (artefato de extração antiga)
- Prioridade: MEDIA
- Impacto: 9 NTs reprovam no verificador (ORIGEM_ABSOLUTA / SCHEMA / TITULO_SUSPEITO); bloqueia `/fiscal-gerar-md` e calendário para elas.
- Status: pendente (solução: reextrair cada NT com `extrair_nt.py`; o script não tem `--forcar` — confirmar o comportamento de reextração antes; decidir com o usuário, pois reprocessa NTs já extraídas)

### [#007] NTs com regras ausentes ou mensagens cortadas no JSON
- Data: 2026-11-12
- Documento: NF-e, CT-e
- NT/MOC: NF-e NT 2026.002 v1.11 (0 regras; 99 IDs do PDF fora do JSON); NF-e NT 2026.008 v1.00 (0 regras; 11 IDs fora); NF-e NT 2026.007 v1.10 (17 de 38 mensagens cortadas); CT-e NT 2025.001 v1.14b (23 de 68 mensagens cortadas); CT-e NT 2026.002 v1.01 (0 regras); CT-e NT 2026.004 v1.00 (0 regras, superada por v1.01)
- Página: n/a
- Trecho: IDs do PDF que não viram regra, ex.: `5E17-65`, `B09-20`, `B09-40`, `NB01-10`, `VB01-10`; mensagens cortadas, ex.: `C17-11`, `I08-191`, `004`, `006`
- O que parece errado: o extrator não captura regras de tabelas/blocos e corta mensagens de validação. O verificador acusa REGRAS_AUSENTES e MENSAGEM_TRUNCADA.
- Fontes em conflito: nenhuma (falha de extração)
- Prioridade: ALTA
- Impacto: `/fiscal-regra` pode responder "NAO ENCONTRADO NAS FONTES" para regras que existem no PDF. Afeta resposta confiável sobre rejeições.
- Status: pendente (corrigir extrator e reextrair; ver `revisar-extracao` para ERRO_MUDANCA_SEM_MARCACAO)

### [#008] Cronogramas inválidos ou vazios em NT NF-e 2026.010 e MDF-e 2025.001
- Data: 2026-11-12
- Documento: NF-e, MDF-e
- NT/MOC: NF-e NT 2026.010 v1.00 (`NT_2026_010_v1.00_DANFE_impressao.pdf`); MDF-e NT 2025.001 v1.03
- Página: n/a
- Trecho: NF-e 2026.010: `versao: '.'`, homologação e produção `00/00/0000`; MDF-e 2025.001: cronograma vazio (ERRO_DATA_NAO_ENCONTRADA)
- O que parece errado: a extração não achou datas de vigência nessas NTs. Sem data, o calendário não pode calcular situação.
- Fontes em conflito: nenhuma (falha de extração). Conferir no PDF se a tabela existe em outro formato.
- Prioridade: MEDIA
- Impacto: essas NTs ficam sem vigência no `calendario/calendario.yaml`; consultas de "quando vale" não têm resposta.
- Status: pendente (conferir o cronograma no PDF e registrar a data ou confirmar que não existe)
