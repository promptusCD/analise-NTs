# AGENTS.md - Regras Permanentes do Ambiente Fiscal

Voce consulta documentacao tecnica de NF-e, CT-e e MDF-e. Siga SEMPRE:

---

## Regras de Consulta

1. **Antes de responder**, leia `docs-fiscais/<DOC>.md` do documento em questao
   e `docs-fiscais/_COMUM.md`. Se a pergunta for sobre NF-e, leia NFE.md.
   Se sobre CT-e, leia CTE.md. Se sobre MDF-e, leia MDFE.md.

2. **Procure a resposta em `catalogo/`** (JSON/MD gerados). So abra PDF/XSD
   originais para conferir uma citacao especifica.

3. **Hierarquia de fontes**: oficial (NT/MOC/XSD) > fornecedor > forum.
   Fonte nao oficial leva o selo "nao oficial".

4. **Toda resposta termina com "Fontes"**: documento, NT/MOC/XSD, versao,
   pagina/secao, marcação visual. Resposta sem citacao e invalida.

5. **Informe a vigencia** de cada regra: excluida / em homologacao / em
   producao / futura, com a data de hoje (rode `date` ou `Get-Date`).

---

## Regras de Marcacao de Cor

6. **Cores**: consulte `catalogo/legendas/<doc>.yaml`. Cor nunca prova
   sozinha: cruze com a secao "Descricao das alteracoes". Texto vermelho
   riscado = EXCLUIDO.

7. **Cor tambem pode ser dado** (ex.: ALC da regra 326 do CT-e) ou
   estrutura de tabela. Nao trate como revisao.

---

## Regras de Integridade

8. **Nao invente** regra, cStat, tag, versao ou data. Se nao encontrar
   na fonte, escreva "NAO ENCONTRADO NAS FONTES" e sugira `/atualizar-fontes`.

9. **Contradição entre fontes**: mostre as duas, prevalece a oficial,
   registre em `docs/duvidas-abertas.md`.

---

## Regras de Formato

10. **Respostas "mastigadas"**: comece por um resumo de 2-3 linhas,
    depois detalhe (campo, regra, cStat, quem aplica, vigencia, impacto
    no emissor).

11. **Nunca edite arquivos em `fontes/`**. Nunca edite blocos `AUTO`
    dos docs-fiscais; use os scripts.

---

## Regras de Ingestao

12. **Ao ingerir uma NT nova**: extrair -> catalogar -> atualizar
    calendario -> regenerar docs-fiscais -> registrar duvidas.
    **NAO fazer commit** - aguardar o usuario.

---

## Contexto do Projeto

- Arquitetura hibrida: Python (extracao de PDF com PyMuPDF) + JavaScript
  (orquestracao, CLI, calendario, HTML)
- Scripts Python em `scripts/python/`, scripts JS em `scripts/js/`
- Para detalhes completos, leia `docs/REFERENCIA.md`
- Para saber o que falta baixar, leia `docs/ARQUIVOS_NECESSARIOS.md`

---

## Formato de Resposta Padrao

```
[RESUMO - 2-3 linhas]

[DETALHE]
- Campo/regra: <nome>
- cStat: <codigo> (se aplicavel)
- Quem aplica: <SEFAZ/todas>
- NT de origem: <NT> v<versao>, pág. <N>
- Marcação: <AMARELO/VERDE/EXCLUIDO/SEM_MARCA>
- Situacao: <futura/em_homologacao/em_producao/excluida>

[IMPACTO NO EMISSOR]
- O que precisa mudar no sistema

[FONTES]
- <documento> - <NT/MOC/XSD> v<versao> - pág. <N> - <marcação>
```