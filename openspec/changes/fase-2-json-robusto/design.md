## Context

O projeto tem 9 NTs e 9 MOCs extraidos, mas o JSON e muito pobre (lista plana de itens) e o MD gerado por Python e ilegivel. A solucao e redesenhar o JSON para ser robusto e ter a IA gerar o MD.

Ver `proposal.md` para motivacao e `specs/` para requisitos comportamentais.

## Goals / Non-Goals

**Goals:**
- JSON robusto com secoes tipificadas (tabela, regras, texto)
- Tabelas com cabecalho e linhas estruturadas
- Regras de validacao identificadas com campos estruturados
- IA gera MD a partir do JSON (formatacao inteligente)
- Fluxo de trabalho claro para o usuario

**Non-Goals:**
- Alterar extracao de cores (ja funciona)
- Alterar deteccao de strikethrough (ja funciona)
- Alterar cronograma (ja funciona)
- Alterar manifest (ja funciona)

## Decisions

### Decisao 1: Separar extracao de formatacao

**Escolha:** Python extrai dados brutos para JSON, IA formata para MD.

**Alternativas consideradas:**
- **Python gera MD**: Nao funciona bem, regex nao entende contexto
- **Python gera HTML**: Overkill, MD e suficiente

**Justificativa:** A IA e muito melhor entendendo contexto e formatando texto legivel. Python e bom em extrair dados de PDFs.

### Decisao 2: JSON com secoes tipificadas

**Escolha:** Cada secao tem um `tipo` (tabela, regras, texto) que indica como deve ser processada.

**Alternativas consideradas:**
- **Lista plana de itens**: Atual, nao funciona
- **Arvore hierarquica**: Complexo demais

**Justificativa:** Secoes tipificadas permitem que a IA saiba como formatar cada parte (tabela como bullets, regras com destaque, texto como paragrafos).

### Decisao 3: Tabelas com cabecalho estruturado

**Escolha:** Tabelas tem `cabecalho[]` e `linhas[]` onde cada linha e um objeto com campos correspondentes ao cabecalho.

**Alternativas consideradas:**
- **Linhas como strings**: Nao permite acesso a campos especificos
- **HTML table**: Overkill

**Justificativa:** Cabecalho estruturado permite que a IA formate cada campo adequadamente (ex: campo em destaque, tipo em parenteses).

### Decisao 4: Regras com campos estruturados

**Escolha:** Regras tem `id`, `aplicacao`, `cStat`, `efeito`, `mensagem`, `condicao`.

**Alternativas consideradas:**
- **Texto livre**: Nao permite busca por ID ou cStat
- **JSON Schema completo**: Complexo demais

**Justificativa:** Campos estruturados permitem busca por ID (`/regra 001`) e por cStat (`/regra 311`).

### Decisao 5: Command `/gerar-md`

**Escolha:** Command separado para regenerar MD a partir do JSON.

**Alternativas consideradas:**
- **So no `/ingerir-nt`**: Nao permite regenerar sem re-extrair
- **Automatico sempre**: Pode ser lento

**Justificativa:** Command separado permite regenerar MD sem re-extrair o PDF (util para ajustar formatacao).

## Risks / Trade-offs

| Risco | Probabilidade | Impacto | Mitigacao |
|-------|---------------|---------|-----------|
| JSON fica muito grande | Media | Baixo | Paginacao ou compressao |
| IA nao entende o JSON | Baixa | Alto | Schema bem documentado |
| Extracao de tabelas falha | Media | Medio | Fallback para texto corrido |
| Regras nao identificadas | Baixa | Medio | Fallback para texto livre |

## Migration Plan

1. Atualizar `utils/saida.py` para nova estrutura JSON
2. Atualizar `extrair_nt.py` para gerar JSON robusto (sem MD)
3. Atualizar `extrair_moc.py` para gerar JSON robusto (sem MD)
4. Criar command `/gerar-md`
5. Atualizar documentacao (README.md, REFERENCIA.md)
6. Re-extrair todas as NTs e MOCs

## Open Questions

Nenhuma -- todas as decisoes foram resolvidas.