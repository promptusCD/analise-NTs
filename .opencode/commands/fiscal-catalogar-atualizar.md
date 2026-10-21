---
description: Organizar entrada/ em fontes/ (identifica tipo e documento), atualizar manifest e ARQUIVOS_NECESSARIOS
argument-hint: [--dry-run]
---

# /fiscal-catalogar-atualizar

**Argumentos**: $ARGUMENTS (`--dry-run` = só mostrar o que faria)

**Regra 11: a IA nunca edita, cria ou copia nada em `fontes/` — só MOVE (`mv`) o que o usuário colocou em `entrada/`, sem sobrescrever.**
Este command é a **fonte única das regras de classificação** de `entrada/`; `/fiscal-processar`
(etapa 1) usa as mesmas regras. Preserve sempre `entrada/README.md`. Sem commit (regra 12).

## 0. Organizar entrada/

1. Liste: `ls -R entrada/` (ou `Get-ChildItem entrada -Recurse -File`). Vazio → pule para o passo 1.
2. **ZIP**: extraia para um subdiretório **novo e vazio** dentro de `entrada/` (nunca rode scripts de
   dentro dele) e reclassifique o conteúdo.
3. **Classificar** cada arquivo (por extensão e nome, sem diferenciar maiúsculas):

| Critério | Classe | Destino |
|---|---|---|
| `.xsd` / pasta de pacote `PL_*` | XSD | `fontes/<doc>/xsd/<pacote>/` |
| nome com `MOC`/`Manual`/`Anexo`/`VisaoGeral` | MOC (`.pdf`/`.docx`) | `fontes/<doc>/moc/` |
| nome com `NT`/`Nota_Tecnica`/`Nota Tecnica` | NT | `fontes/<doc>/notas-tecnicas/` |
| `.xlsx`/`.xls` ou `IT `/`Tabela` | Tabela | `fontes/externas/tabelas/` |
| nome com `ABI` | Externa | `fontes/externas/` |

   Documento: `NFe`/`NF-e`/`NT_`sem prefixo/`NT2026.007` → nfe · `CTe`/`CT-e`/`PL_CTe` → cte ·
   `MDFe`/`MDF-e`/`PL_MDFe` → mdfe. Se o nome contiver mais de um doc ou nenhum:
   `ERRO_DOCUMENTO_NAO_IDENTIFICADO` → **não mova**, pergunte.
4. **Nomenclatura**: NT `<DOC>_NT_<AAAA>_<NNN>_v<versão>.pdf` (NF-e sem prefixo `NFe_`, como já existe) ·
   MOC `MOC_<DOC>_<seção>_<versão>.pdf` · XSD/Tabela mantêm o nome original.
5. **Duplicata**: SHA256 (`sha256sum`) contra **todo** `fontes/` (não só o destino; não confie no
   manifest: shas truncados). Idêntico → duplicata; remover de `entrada/` (o `rm` pede confirmação).
   Mesmo nome e hash diferente → `ERRO_DUPLICATA_HASH_DIVERGENTE`, alertar, manter ambos.
6. Mover com `mv` (Bash). Em `--dry-run`, apenas imprima a tabela origem → destino.
7. Confirme que `entrada/` só contém o README.

## 1. Atualizar `manifest.yaml`
Uma entrada por arquivo (id, documento, tipo, nt, versao, titulo, arquivo, sha256, status_ingestao,
confianca). NTs/MOCs ainda não extraídos entram como `pendente`.

## 2. Atualizar `docs/ARQUIVOS_NECESSARIOS.md`
- Marque como OK os itens atendidos e atualize "Documentos pendentes: N".
- `Status: ATIVO` = ciclo em andamento. Se **todos** OK: marque CONCLUIDO (versão, data, contagem),
  copie para `docs/historico-arquivos/ARQUIVOS_NECESSARIOS_vN_AAAA-MM-DD.md` e abra novo ciclo ATIVO.
  Detalhes em `docs/REFERENCIA.md` seção 15.
- `CATALOGO_ARQUIVOS.md` (seção 16 da REFERENCIA): se o arquivo existir, atualize; senão avise.

## 3. Relatório
```
ORGANIZAÇÃO CONCLUÍDA - <data>
Processados N · NTs N · MOCs N · XSDs N · Tabelas N · Duplicatas N · Não identificados N
Manifest atualizado: sim/não · Pendentes em ARQUIVOS_NECESSARIOS: N (lista)
Próximo passo: /fiscal-processar --etapa 2
```

## Erros
| Erro | Ação |
|---|---|
| `ERRO_DOCUMENTO_NAO_IDENTIFICADO` | Não mover; perguntar |
| `ERRO_TIPO_NAO_IDENTIFICADO` | Não é NT/MOC/XSD → alertar, perguntar (padrão: `fontes/externas/`) |
| `ERRO_DUPLICATA_HASH_DIVERGENTE` | Alertar, manter ambos |
| `ERRO_ARQUIVO_CORROMPIDO` | SHA256 falhou → alertar, não mover |
