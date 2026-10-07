## Why

O projeto tem 9 NTs e 9 MOCs em `fontes/`, mas nenhuma foi processada. Sem o extrator, o catalogo fica vazio e nenhum command funciona (`/consultar`, `/regra`, `/campo`, `/calendario`, `/impacto`). O `extrair_nt.py` e o coracao do projeto -- sem ele, a IA nao tem dados para consultar.

Agora e o momento certo porque:
- Todas as fontes ja estao baixadas e organizadas em `fontes/` (ciclo v1 concluido)
- A estrutura de diretorios esta definida (REFERENCIA.md secao 3)
- O manifest.yaml registra as 9 NTs com status `pendente`
- A arquitetura Python+JS esta definida e as dependencias estao em requirements.txt

## What Changes

- **Novo** `scripts/python/extrair_nt.py` -- extrai PDFs de NTs com marcações de cor (PyMuPDF)
- **Novo** `scripts/python/extrair_moc.py` -- extrai PDFs/DOCXs de MOCs (estrutura de secoes, regras)
- **Novo** `scripts/python/utils/` -- modulos compartilhados (cores.py, parsing.py, saida.py, manifest.py)
- **Novo** `scripts/python/atualizar_manifest.py` -- atualiza status de ingestao no manifest.yaml
- **Novo** `catalogo/nt/<doc>/` -- JSON + MD gerados por NT (diretorio criado pelo script)
- **Novo** `catalogo/nt/<doc>/stdout/` -- logs de extracao por NT (`<nt>_v<ver>.log`)
- **Novo** `catalogo/moc/<doc>/` -- JSON + MD gerados por MOC (diretorio criado pelo script)
- **Novo** `catalogo/legendas/<doc>.yaml` -- mapa cor -> versao de cada NT
- **Atualizado** `manifest.yaml` -- status `pendente` -> `extraida` apos extracao

## Capabilities

### New Capabilities

- `extrair-nt`: Extracao de PDFs de NTs fiscais com marcações de cor usando PyMuPDF. Gera JSON estruturado com itens, marcacoes, cronograma, e MD legivel. Detecta fundo colorido (amarelo/verde), texto vermelho, strikethrough, com fallback pixmap.
- `extrair-moc`: Extracao de PDFs/DOCXs de MOCs. Gera JSON com estrutura de secoes, regras de validacao, campos do leiaute. O MOC e o consolidado base que as NTs incrementam.
- `legenda-cores`: Gerenciamento do mapa cor -> versao por documento fiscal. YAML que associa cada marcacao visual (AMARELO, VERDE, EXCLUIDO) a uma versao especifica da NT.
- `gerenciar-manifest`: Atualizacao do status de ingestao no manifest.yaml. Transicoes: `pendente` -> `extraida` -> `revisada`.

### Modified Capabilities

Nenhuma capability existente e modificada (o projeto esta comecando).

## Impact

### Arquivos criados:
- `scripts/python/extrair_nt.py`
- `scripts/python/extrair_moc.py`
- `scripts/python/atualizar_manifest.py`
- `scripts/python/utils/__init__.py`
- `scripts/python/utils/cores.py`
- `scripts/python/utils/parsing.py`
- `scripts/python/utils/saida.py`
- `scripts/python/utils/manifest.py`
- `catalogo/nt/<doc>/` (diretorios gerados)
- `catalogo/moc/<doc>/` (diretorios gerados)
- `catalogo/legendas/<doc>.yaml` (arquivos gerados)

### Arquivos atualizados:
- `manifest.yaml` -- status das 9 NTs muda de `pendente` para `extraida`

### Dependencias (ja em requirements.txt):
- `pymupdf>=1.24.0` -- extracao de PDF com deteccao de cor
- `pyyaml>=6.0` -- leitura/escrita de YAML (legendas, manifest)
- `python-docx>=1.1.0` -- extracao de MOCs em DOCX

### Referencia:
- docs/REFERENCIA.md -- contexto completo, roadmap (secao 9), estrutura de diretorios (secao 3), catalogo (secao 5)