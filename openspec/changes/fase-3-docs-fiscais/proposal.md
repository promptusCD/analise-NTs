# Proposal

## Why

O `AGENTS.md` (regra 1) manda a IA ler `docs-fiscais/<DOC>.md` e `docs-fiscais/_COMUM.md` antes de responder, mas a pasta `docs-fiscais/` não existe e o script `atualizar_docs_fiscais.js` (referenciado no `package.json` e em `docs/REFERENCIA.md`, seção 7 e fase-3) também não. Hoje o fluxo de consulta quebra na primeira regra. A fase-1 e as correções de fidelidade (fase-2/2b) já entregaram `catalogo/nt/` e `catalogo/moc/` confiáveis, então há dado suficiente para gerar o documento por fiscal. O `calendario/` (fase-2 original) continua vazio; esta change não espera por ele e deriva a vigência diretamente do `cronograma` de cada NT.

## What Changes

- Criar `docs-fiscais/NFE.md`, `CTE.md`, `MDFE.md`, `_COMUM.md` e `_GLOSSARIO.md` seguindo o template da seção 7.1 do `docs/REFERENCIA.md` (9 seções; manuais + blocos AUTO).
- Criar `scripts/js/atualizar_docs_fiscais.js` (já exposto como `npm run docs-fiscais`) que regenera somente o conteúdo entre `<!-- AUTO:BEGIN <nome> -->` e `<!-- AUTO:END <nome> -->`: `fontes_vigentes`, `grupos`, `eventos`, `regras`, `em_andamento`, `linha_do_tempo`, `duvidas`.
- Criar um módulo JS compartilhado e exportado de vigência (`scripts/js/lib/vigencia.js`) que calcula a situação (futura / em_homologacao / prazo_homologacao_encerrado / em_producao / excluida) a partir da data de hoje e do `cronograma` literal da NT, sem inventar data. O futuro `gerar_calendario.js` deve reutilizá-lo.
- Preencher as partes manuais com conteúdo já conhecido (identificação, armadilhas da seção 7.2) e marcar como limitação o que depende de fontes ainda não catalogadas (XSD, fase-4).
- Criar os commands `/fiscal-docs-gerar` e `/fiscal-docs-validar` em `.claude/commands/` (espelhados em `.opencode/` por `npm run sincronizar-ia`) para a IA regenerar os documentos e validá-los.
- Criar uma validação minuciosa, somente leitura, que confere cada documento gerado contra o JSON do catálogo e contra os originais (NTs, MOCs) em `fontes/`, e executá-la ao final dos testes.
- Declarar em cada documento, num bloco AUTO `cobertura` (seção 2), o que ainda falta: NTs e MOCs ingeridos, fontes pendentes, ausência de XSD, de legendas revisadas e de calendário, e os modelos sem conteúdo específico no catálogo.
- Falhar de forma explícita se um marcador AUTO estiver ausente, duplicado ou desbalanceado, sem escrever nada fora dos marcadores.
- Fora de escopo: `calendario.yaml` e `gerar_calendario.js`, `catalogar_xsd.py`, alterar o pipeline `/fiscal-processar` para chamar o script (os commands novos rodam o script manualmente; a integração fica para change seguinte), commits.

## Capabilities

### New Capabilities
- `docs-fiscais-estrutura`: estrutura e conteúdo manual dos documentos por fiscal (template de 9 seções, `_COMUM`, `_GLOSSARIO`, armadilhas conhecidas, lacunas e cobertura declaradas).
- `docs-fiscais-blocos-auto`: geração determinística dos blocos AUTO a partir de `catalogo/`, `manifest.yaml` e `docs/duvidas-abertas.md`, com proteção do conteúdo manual.
- `vigencia-por-cronograma`: cálculo da situação de vigência de um item a partir da data de hoje e do cronograma literal da NT, num módulo compartilhado.
- `docs-fiscais-commands`: commands de IA para regenerar e validar os documentos fiscais.
- `docs-fiscais-verificacao`: validação minuciosa do documento gerado contra o JSON e contra os originais em `fontes/`.

### Modified Capabilities

(nenhuma; os specs existentes não mudam de requisito)

## Impact

- Novos: `docs-fiscais/*.md`, `scripts/js/atualizar_docs_fiscais.js`, `scripts/js/verificar_docs_fiscais.js`, `scripts/python/verificar_docs_vs_fontes.py`, módulo de vigência em `scripts/js/lib/`, commands em `.claude/commands/` (e espelho em `.opencode/`), testes em `tests/js/` e `tests/python/`, ajuste de `docs/REFERENCIA.md` se algo divergir do implementado.
- Dependências: `js-yaml` (já no `package.json`) e PyMuPDF (já em `requirements.txt`); nenhuma nova.
- Leitura apenas de `catalogo/`, `manifest.yaml`, `docs/duvidas-abertas.md` e, na validação, dos originais em `fontes/`. Nada é escrito em `fontes/` (regra 11) nem em projetos do usuário (regra 13).
- Risco principal: a seção 3 (mapa do leiaute) e a 4 (eventos) dependem do MOC Anexo I, sem XSD; ficam marcadas como parciais. Dados com acentuação corrompida em alguns JSONs (ex.: `cronograma.descricao`) exigem que o gerador não "conserte" texto e apenas reproduza o literal.
- Referência de contexto: `docs/REFERENCIA.md` (seções 3, 4.4, 7 e fase-3).
