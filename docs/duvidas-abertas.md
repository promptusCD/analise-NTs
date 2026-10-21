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
