## Context

O projeto tem 9 NTs e 9 MOCs organizados em `fontes/`, mas nenhum script de extracao existe. A arquitetura e hibrida: Python (PyMuPDF) para extracao de PDF, Node.js para orquestracao. O `extrair_nt.py` e o ponto de entrada -- sem ele, o catalogo fica vazio e nenhum command funciona.

Ver `proposal.md` para motivacao e `specs/` para requisitos comportamentais.

## Goals / Non-Goals

**Goals:**
- Extrair NTs de PDF com marcações de cor (AMARELO, VERDE, EXCLUIDO)
- Extrair MOCs de PDF/DOCX (estrutura, regras, campos)
- Gerar JSON estruturado + MD legivel para cada documento
- Gerar legendas cor -> versao por documento fiscal
- Atualizar manifest.yaml automaticamente

**Non-Goals:**
- Catalogar XSDs (fase 4, script separado `catalogar_xsd.py`)
- Gerar calendario de vigencias (fase 2)
- Gerar docs-fiscais (fase 3)
- Implementar commands do opencode (fase 5)
- RAG ou embeddings (futuro)

## Decisions

### Decisao 1: Um script para NTs, um para MOCs

**Escolha:** Dois scripts separados (`extrair_nt.py` e `extrair_moc.py`) com modulos compartilhados em `utils/`.

**Alternativas consideradas:**
- **Um script unico com flag `--tipo nt|moc`**: Mais simples, mas NTs e MOCs tem logica muito diferente (marcacoes de cor vs estrutura de secoes). Misturaria responsabilidades.
- **Um script por documento fiscal** (`extrair_nfe.py`, `extrair_cte.py`): Muita duplicacao. A logica de deteccao de cor e a mesma para todos.

**Justificativa:** Dois scripts com utils compartilhados equilibra separacao de responsabilidades com reuso de codigo. A deteccao de cor fica em `utils/cores.py`, o parsing em `utils/parsing.py`, e cada script principal orquestra sua propria logica.

### Decisao 2: Granularidade de item individual com contexto de secao

**Escolha:** Cada regra/campo/evento e um item individual no JSON, mas com referencia a secao pai.

**Alternativas consideradas:**
- **Por pagina**: Perde contexto -- uma pagina pode ter itens de secoes diferentes.
- **Por secao**: Granularidade grossa -- dificulta busca por regra especifica (`/regra C17-10`).
- **Por paragrafo**: Granularidade fina demais -- muitos itens sem significado proprio.

**Justificativa:** O item individual (regra C17-10, campo vTPrestLiq, evento e211110) e a unidade de consulta mais comum. A secao fornece contexto (e uma regra de validacao? um campo? um evento?). O formato `itens[]` com `secao` e `secao_titulo` atende ambos.

### Decisao 3: Deteccao de cor com fallback pixmap

**Escolha:** Primario via `page.get_drawings()` + `get_text("dict")`, fallback via pixmap sampling.

**Alternativas consideradas:**
- **So pixmap sampling**: Lento (renderiza pagina inteira como imagem), impreciso para texto pequeno.
- **So get_drawings()**: Alguns PDFs nao tem retangulos vetoriais (fundos sao imagens).
- **OCR com Tesseract**: Overkill, lento, e nao detecta cores.

**Justificativa:** `get_drawings()` e rapido e preciso para a maioria dos PDFs fiscais. O fallback pixmap cobre os casos edge (PDFs gerados por ferramentas que rasterizam o fundo).

### Decisao 4: Strikethrough via tres metodos

**Escolha:** Detectar strikethrough por (1) flag `FZ_STEXT_STRIKEOUT`, (2) annotations de strikeout, (3) linhas vetoriais horizontais cruzando texto.

**Alternativas consideradas:**
- **So flag FZ_STEXT_STRIKEOUT**: Funciona apenas com PyMuPDF >= 1.24 e PDFs com strikethrough codificado como atributo de texto.
- **So deteccao vetorial**: Complexo, falsos positivos com linhas de tabela.

**Justificativa:** NTs fiscais brasileiras usam strikethrough de formas variadas. Os tres metodos cobrem diferentes encoding de PDF. A uniao dos tres maximiza recall.

### Decisao 5: Formato JSON conforme REFERENCIA.md secao 5.1

**Escolha:** Seguir exatamente o formato JSON definido em REFERENCIA.md secao 5.1, com campos `nt`, `versao`, `documento`, `titulo`, `sha256`, `extraido_em`, `cronograma[]`, `itens[]`.

**Justificativa:** O REFERENCIA.md ja definiu o contrato de saida. Segui-lo garante compatibilidade com os commands que serao implementados nas fases seguintes.

### Decisao 6: Manifest update como script separado

**Escolha:** `atualizar_manifest.py` como script separado, chamado pelo `extrair_nt.py` apos extracao bem-sucedida.

**Alternativas consideradas:**
- **Logica embutida no extrair_nt.py**: Acoplamento desnecessario. O manifest e compartilhado entre NTs e MOCs.

**Justificativa:** Separar permite reuso (extrair_moc.py tambem atualiza manifest) e testabilidade.

### Decisao 7: Estatisticas obrigatorias no JSON

**Escolha:** O JSON de saida DEVE incluir `estatisticas` com contagem por marcacao (AMARELO, VERDE, EXCLUIDO, SEM_MARCA) e total de itens.

**Justificativa:** Permite validacao rapida (se SEM_MARCA = 100%, algo errado na deteccao) e diagnostico. Conforme REFERENCIA.md secao 5.1.

### Decisao 8: Logs em arquivo dedicado

**Escolha:** Logs de erros e avisos sao salvos em `catalogo/nt/<doc>/stdout/<nt>_v<ver>.log`, alem de aparecerem no stdout.

**Alternativas consideradas:**
- **So stdout**: A IA captura, mas nao fica persistido para revisao posterior.
- **So arquivo**: Dificulta acompanhamento em tempo real.

**Justificativa:** Dupla saida (stdout + arquivo) atende tanto o acompanhamento em tempo real quanto a revisao posterior. O diretorio `stdout/` separa logs do conteudo extraido (JSON/MD).

## Riscos / Trade-offs

| Risco | Probabilidade | Impacto | Mitigacao |
|-------|---------------|---------|-----------|
| PyMuPDF nao detecta fundo em algum PDF | Media | Alto | Fallback pixmap sampling; logar PDFs problematicos |
| Strikethrough nao detectado em NT especifica | Baixa | Medio | Tres metodos de deteccao; revisao manual para casos edge |
| NTs com estrutura diferente do esperado | Media | Medio | Parsing flexivel com logging de erros; nao falhar silenciosamente |
| DOCX de MOC dificil de extrair | Baixa | Baixo | python-docx ja testado; fallback para extrair texto puro |
| Performance em PDFs grandes (>50 pag) | Baixa | Baixo | Processar pagina por pagina; nao carregar tudo em memoria |
| Cor de tabela confundida com fundo colorido | Media | Medio | Filtrar por dimensao (width < 5 && height > 50 = linha de tabela) |
| Regra nova inteira sem marcacao de cor | Alta | Medio | Detectar SEM_MARCA + cruzar com secao "Descricao das alteracoes" |
| PDF sem camada de texto (imagem escaneada) | Baixa | Alto | Detectar e reportar; nao tentar OCR (out of scope) |

## Migration Plan

Nao aplicavel -- e uma implementacao nova, nao ha dados existentes para migrar.

Passos de implantacao:
1. Criar `scripts/python/utils/` com modulos compartilhados
2. Implementar `extrair_nt.py` e testar com NF-e 2026.007 (mais simples)
3. Validar com CT-e 2026.004 (mais complexa, 3 blocos de cronograma)
4. Implementar `extrair_moc.py` e testar com MOC CT-e v4.00
5. Executar em todas as 9 NTs e 9 MOCs
6. Verificar catalogo gerado e manifest atualizado

## Open Questions

Nenhuma -- todas as decisoes foram resolvidas.