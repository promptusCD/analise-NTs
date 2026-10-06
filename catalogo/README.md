# Catalogo - Camada "Mastigada"

Este diretorio contem a versao estruturada e consultavel dos documentos
fiscais brutos (NTs, MOCs, XSDs) que estao em `fontes/`. Aqui voce
encontra JSON e MD prontos para consulta, sem precisar abrir PDFs.

---

## Estrutura

```
catalogo/
├── nt/<doc>/              # NTs extraidas com marcacoes de cor
│   ├── nfe/               # NF-e (modelo 55)
│   ├── cte/               # CT-e (modelo 57)
│   └── mdfe/              # MDF-e (modelo 58)
│
├── moc/<doc>/             # MOCs extraidos (estrutura, regras, campos)
│   ├── nfe/
│   ├── cte/
│   └── mdfe/
│
├── regras/<doc>.json      # Indice consolidado de regras de validacao
├── campos/<doc>.json      # Tags do leiaute (XSD + NT)
└── legendas/<doc>.yaml    # Mapa cor -> versao de cada NT
```

---

## O Que Cada Arquivo Contem

### catalogo/nt/<doc>/<nt>_v<ver>.json

Extracao completa de uma Nota Tecnica com marcacoes de cor interpretadas.

**Campos principais:**
- `nt` / `versao` -- identificacao da NT
- `documento` -- NF-e, CT-e ou MDF-e
- `cronograma[]` -- datas de homologacao e producao
- `itens[]` -- cada regra, campo ou evento extraido
  - `id` -- identificador (ex: C17-10, vTPrestLiq)
  - `tipo` -- regra, campo, evento, item
  - `secao` -- secao do documento (ex: 3.2)
  - `marcacao` -- AMARELO, VERDE, EXCLUIDO, SEM_MARCA
  - `texto` -- conteudo do item
- `estatisticas` -- contagem por marcacao

**Exemplo de uso:**
```bash
# Ver todas as regras excluidas de uma NT
python -c "import json; d=json.load(open('catalogo/nt/cte/CTe_NT_2026_004_v1.00.json')); [print(i['id'], i['texto'][:80]) for i in d['itens'] if 'EXCLUIDO' in str(i.get('marcacoes', []))]"
```

### catalogo/nt/<doc>/<nt>_v<ver>.md

Versao legivel por humano do JSON acima. Use para:
- Leitura rapida sem precisar abrir o PDF original
- Verificar marcacoes de cor (AMARELO, VERDE, EXCLUIDO)
- Consultar cronograma de vigencia

### catalogo/nt/<doc>/stdout/<nt>_v<ver>.log

Log de erros e avisos da extracao. Use para:
- Diagnosticar problemas na deteccao de cor
- Verificar itens que ficaram SEM_MARCA em secoes de alteracoes
- Auditar a qualidade da extracao

### catalogo/moc/<doc>/MOC_<doc>_v<ver>.json

Extracao de um Manual de Orientacao do Contribuinte.

**Campos principais:**
- `documento` / `versao` -- identificacao do MOC
- `secoes[]` -- hierarquia de secoes do documento
- `regras[]` -- regras de validacao extraidas (id, cStat, descricao)
- `campos[]` -- campos do leiaute (tag, tipo, ocorrencia)

### catalogo/legendas/<doc>.yaml

Mapa cor -> versao de cada NT. Use para:
- Saber qual versao cada cor representa
- Cruzar marcacoes com versoes especificas

**Exemplo:**
```yaml
documento: NF-e
nt: "2026.007"
legenda:
  AMARELO:
    versao: "1.00"
    confianca: ALTA
  VERDE:
    versao: "1.10"
    confianca: ALTA
```

---

## Como o Analista Pode Usar

### 1. Consultar uma regra especifica

```bash
# Ver todas as regras de validacao do CT-e
cat catalogo/nt/cte/CTe_NT_2026_004_v1.00.json | python -c "
import json, sys
d = json.load(sys.stdin)
for i in d['itens']:
    if i.get('tipo') == 'regra':
        print(f\"{i['id']}: {i['texto'][:100]}\")
"
```

### 2. Verificar vigencia

```bash
# Ver cronograma de uma NT
cat catalogo/nt/cte/CTe_NT_2026_004_v1.00.json | python -c "
import json, sys
d = json.load(sys.stdin)
for c in d['cronograma']:
    print(f\"v{c['versao']}: homologacao={c['homologacao']}, producao={c['producao']}\")
"
```

### 3. Listar itens excluidos

```bash
# Ver itens excluidos (vermelho riscado)
cat catalogo/nt/nfe/NT_2026_007_v1.10.json | python -c "
import json, sys
d = json.load(sys.stdin)
for i in d['itens']:
    if any(m.get('tipo') == 'EXCLUIDO' for m in i.get('marcacoes', [])):
        print(f\"EXCLUIDO: {i['id']} - {i['texto'][:80]}\")
"
```

### 4. Auditar extracao

```bash
# Ver estatisticas de marcacao
cat catalogo/nt/cte/CTe_NT_2026_004_v1.00.json | python -c "
import json, sys
d = json.load(sys.stdin)
print(f\"Total: {d['estatisticas']['total_itens']}\")
for k, v in d['estatisticas']['por_marcacao'].items():
    print(f\"  {k}: {v}\")
"
```

### 5. Consultar log de avisos

```bash
# Ver avisos de uma extracao
cat catalogo/nt/cte/stdout/CTe_NT_2026_004_v1.00.log | grep WARN
```

---

## Marcacoes de Cor

| Marcacao | Significado | O que procurar |
|----------|-------------|----------------|
| AMARELO | Alterado na versao atual | Itens com fundo amarelo no PDF |
| VERDE | Alterado em versao posterior | Itens com fundo verde no PDF |
| EXCLUIDO | Regra/texto excluido | Texto vermelho riscado |
| SEM_MARCA | Inalterado ou novo inteiro | Sem marcação visual |

**IMPORTANTE:** A cor nunca prova sozinha. Cruze com a secao
"Descricao das alteracoes" do proprio documento.

---

## Gerado Por

- `scripts/python/extrair_nt.py` -- extrai NTs com marcacoes de cor
- `scripts/python/extrair_moc.py` -- extrai MOCs (PDF + DOCX)
- `scripts/python/atualizar_manifest.py` -- gerencia manifest.yaml

Para regenerar, rode o script correspondente ou use o command `/ingerir-nt`.