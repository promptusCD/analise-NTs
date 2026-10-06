## Context

O projeto fiscal-dfe-knowledge ja tem toda a documentacao de referencia
definida em `docs/REFERENCIA.md` (arquitetura, estrutura de diretorios,
mapeamento de fontes, roadmap). Os arquivos brutos estao todos em `entrada/`
sem organizacao. A fase-0-setup e responsavel por criar a estrutura base
e organizar os arquivos antes de qualquer funcionalidade ser implementada.

Ver `docs/REFERENCIA.md` secoes 3, 11 e 18 para detalhes completos.

## Goals / Non-Goals

**Goals:**
- Criar toda a arvore de diretorios do projeto
- Configurar dependencias (Python + Node.js)
- Mover arquivos de `entrada/` para `fontes/` organizados por documento
- Criar manifest.yaml como registro central
- Verificar integridade dos arquivos movidos
- Atualizar CATALOGO_ARQUIVOS.md

**Non-Goals:**
- Implementar scripts de extracao (fase-1)
- Implementar calendario (fase-2)
- Implementar docs-fiscais (fase-3)
- Implementar commands (fase-5)

## Decisions

### D1: Estrutura de diretorios conforme REFERENCIA.md secao 3

A estrutura ja foi definida e validada na fase de planejamento. Seguir
exatamente o que esta documentado.

**Alternativa considerada:** Estrutura mais simples (tudo em uma pasta).
Rejeitada porque o projeto precisa de separacao clara entre fontes originais
e catalogo gerado.

### D2: Organizar entrada/ antes de criar scripts

Mover os arquivos de `entrada/` para `fontes/` como primeiro passo, antes
de criar qualquer script. Isso garante que os scripts ja nascom com os
arquivos no lugar correto.

**Alternativa considerada:** Deixar arquivos em `entrada/` e mover depois.
Rejeitada porque geraria confusao sobre onde buscar os arquivos.

### D3: SHA256 para verificacao de integridade

Calcular hash SHA256 de cada arquivo antes e depois de mover para garantir
que nenhum arquivo se perdeu ou corrompeu.

**Alternativa considerada:** Verificar apenas tamanho de arquivo.
Rejeitada porque nao detecta corrupcao de conteudo.

### D4: package.json com dependencias minimas

Incluir apenas dependencias essenciais: js-yaml, ejs, node-fetch.
Outras dependencias serao adicionadas conforme necessario nas fases seguintes.

### D5: requirements.txt com dependencias do prompt original

Manter as bibliotecas especificadas no prompt: pymupdf, python-docx, lxml,
pyyaml, pytest, jinja2.

## Risks / Trade-offs

**[Risco] Arquivos duplicados em entrada/**
Alguns arquivos podem existir em duplicata (ex: MOC_CTe_Anexo_I em 2 copias).
→ Mitigacao: Verificar hash SHA256 para identificar duplicatas. Manter apenas
uma copia em `fontes/` e registrar a duplicata em `docs/duvidas-abertas.md`.

**[Risco] XSDs com nomes de pasta inconsistentes**
Os nomes das pastas de XSDs em `entrada/XSDs/` nao seguem padrao.
→ Mitigacao: Renomear conforme convencao definida em REFERENCIA.md secao 18.

**[Risco] Arquivo corrompido durante movimentacao**
→ Mitigacao: Calcular SHA256 antes e depois. Se hash divergir, restaurar original.