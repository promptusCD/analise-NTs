## Purpose

Extrair informacoes de PDFs de Notas Tecnicas fiscais (NF-e, CT-e, MDF-e) mantendo as marcações visuais de cor (amarelo, verde, vermelho riscado) e gerando JSON estruturado e MD legivel. E o coracao do projeto -- sem ele, o catalogo fica vazio.

## ADDED Requirements

### Requirement: Extrair texto com marcações de cor de fundo
O sistema SHALL extrair cada span de texto de uma NT em PDF, detectando se tem cor de fundo amarela ou verde, e classificando como AMARELO, VERDE ou SEM_MARCA.

#### Scenario: NT com fundo amarelo em trecho alterado
- **WHEN** o PDF contem um retangulo de fundo amarelo (#FFFF00) sobre texto
- **THEN** o item extraido tem marcacao `AMARELO` e o hex do fundo e `#FFFF00`

#### Scenario: NT com fundo verde em trecho alterado em versao posterior
- **WHEN** o PDF contem um retangulo de fundo verde (#00FF00) sobre texto
- **THEN** o item extraido tem marcacao `VERDE` e o hex do fundo e `#00FF00`

#### Scenario: Trecho sem marcação de fundo
- **WHEN** o texto nao esta sobre nenhum retangulo colorido
- **THEN** o item extraido tem marcacao `SEM_MARCA`

### Requirement: Detectar texto vermelho riscado como exclusao
O sistema SHALL detectar texto com cor vermelha E strikethrough (riscado) e classificar como EXCLUIDO.

#### Scenario: Texto vermelho com strikethrough
- **WHEN** o span tem cor de texto vermelha E flag strikethrough ativa
- **THEN** o item extraido tem marcacao `EXCLUIDO`

#### Scenario: Texto vermelho sem strikethrough
- **WHEN** o span tem cor de texto vermelha mas NAO tem strikethrough
- **THEN** o item extraido tem marcacao `VERMELHO_TEXTO` (nao EXCLUIDO)

### Requirement: Gerar JSON estruturado por item com contexto de secao
O sistema SHALL gerar um arquivo JSON com a extracao completa, usando granularidade de item individual com contexto de secao.

#### Scenario: JSON com itens e secoes
- **WHEN** a NT e processada com sucesso
- **THEN** o JSON contem `nt`, `versao`, `documento`, `titulo`, `sha256`, `extraido_em`, `cronograma[]`, `itens[]` com `id`, `tipo`, `secao`, `secao_titulo`, `pagina`, `texto`, `marcacoes[]`, `classificacao_cor`

#### Scenario: Item com multiplas marcacoes
- **WHEN** um item tem fundo amarelo E texto vermelho riscado
- **THEN** o array `marcacoes` contem duas entradas: uma AMARELO e uma EXCLUIDO

### Requirement: Extrair cronograma de vigencia
O sistema SHALL extrair as datas de homologacao e producao do cronograma da NT, mantendo literais como "Ate 05/10/2026".

#### Scenario: Cronograma com multiplas versoes
- **WHEN** a NT tem secao de cronograma com datas por versao
- **THEN** o JSON contem array `cronograma` com objetos `{versao, homologacao, producao}`

#### Scenario: Data literal com "Ate"
- **WHEN** o cronograma contem "Ate 05/10/2026"
- **THEN** o valor e armazenado literalmente como string, nao convertido para data

### Requirement: Gerar MD legivel por humano
O sistema SHALL gerar um arquivo .MD com a extracao em formato legivel, destacando itens por marcacao.

#### Scenario: MD com secoes e marcacoes
- **WHEN** a NT e processada
- **THEN** o MD contem cabecalho com metadados, secoes com itens, e cada item mostra sua marcacao (AMARELO/VERDE/EXCLUIDO/SEM_MARCA)

### Requirement: Calcular SHA256 do arquivo original
O sistema SHALL calcular o hash SHA256 do PDF original e incluir no JSON de saida.

#### Scenario: Hash incluido na saida
- **WHEN** o PDF e processado
- **THEN** o JSON contem `sha256` com o hash hexadecimal do arquivo

### Requirement: Suportar os tres documentos fiscais
O sistema SHALL processar PDFs de NF-e, CT-e e MDF-e, detectando automaticamente o tipo pelo nome do arquivo ou conteudo.

#### Scenario: NF-e detectada
- **WHEN** o arquivo segue nomenclatura `NT_2026_007_v1.10.pdf` ou contem "NF-e" no conteudo
- **THEN** o campo `documento` no JSON e `NF-e`

#### Scenario: CT-e detectada
- **WHEN** o arquivo segue nomenclatura `CTe_NT_2026_004_v1.00.pdf`
- **THEN** o campo `documento` no JSON e `CT-e`

#### Scenario: MDF-e detectada
- **WHEN** o arquivo segue nomenclatura `MDFe_NT_2025_001_v1.03.pdf`
- **THEN** o campo `documento` no JSON e `MDF-e`

### Requirement: Fallback pixmap para cor de fundo
O sistema SHALL usar pixmap sampling como fallback quando `page.get_drawings()` nao retorna retangulos de fundo.

#### Scenario: PDF sem retangulos vetoriais
- **WHEN** `get_drawings()` retorna lista vazia mas o PDF tem fundo colorido (renderizado como imagem)
- **THEN** o sistema renderiza a area do bbox e amostra o pixel para detectar a cor

### Requirement: Gerar estatisticas de extracao
O sistema SHALL incluir no JSON de saida um bloco `estatisticas` com `total_itens` e `por_marcacao` (contagem de AMARELO, VERDE, EXCLUIDO, SEM_MARCA).

#### Scenario: JSON com estatisticas
- **WHEN** a NT e processada com sucesso
- **THEN** o JSON contem `estatisticas.total_itens` (inteiro) e `estatisticas.por_marcacao` (objeto com chaves AMARELO, VERDE, EXCLUIDO, SEM_MARCA e valores inteiros)

#### Scenario: Estatisticas para diagnostico
- **WHEN** `por_marcacao.SEM_MARCA` = `total_itens` (100% dos itens sem marcacao)
- **THEN** isso indica possivel falha na deteccao de cor (WARN no log)

### Requirement: Gerar log file de extracao
O sistema SHALL gerar arquivo de log em `catalogo/nt/<doc>/stdout/<nt>_v<ver>.log` contendo erros, avisos e diagnostico da extracao.

#### Scenario: Log file criado
- **WHEN** a NT e processada (com sucesso ou com erros)
- **THEN** e criado `catalogo/nt/<doc>/stdout/<nt>_v<ver>.log` com timestamp, nivel (INFO/WARN/ERROR) e mensagem

#### Scenario: Log de item problematico
- **WHEN** um item esta em secao de alteracoes mas tem marcacao SEM_MARCA
- **THEN** o log registra WARN: "Item X na secao Y.sem marcacao (possivel regra nova inteira)"