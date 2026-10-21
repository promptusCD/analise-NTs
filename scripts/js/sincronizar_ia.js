#!/usr/bin/env node
/**
 * sincronizar_ia.js - Espelha skills e commands fiscais de .claude/ para .opencode/.
 *
 * .claude/ e a fonte; .opencode/ e copia (OpenCode). Os fluxos OpenSpec
 * (openspec-*, opsx-*) sao gerados por `openspec init/update` e NAO sao tocados.
 *
 * Uso:
 *   node scripts/js/sincronizar_ia.js           # copia
 *   node scripts/js/sincronizar_ia.js --check   # so verifica (exit 1 se divergente)
 */

const fs = require("fs");
const path = require("path");

const RAIZ = path.resolve(__dirname, "..", "..");
const CHECK = process.argv.includes("--check");

function lerSeExiste(p) {
  return fs.existsSync(p) ? fs.readFileSync(p) : null;
}

function pares() {
  const lista = [];
  const skills = path.join(RAIZ, ".claude", "skills");
  for (const nome of fs.readdirSync(skills)) {
    if (nome.startsWith("openspec-")) continue;
    lista.push([
      path.join(skills, nome, "SKILL.md"),
      path.join(RAIZ, ".opencode", "skills", nome, "SKILL.md"),
    ]);
  }
  const cmds = path.join(RAIZ, ".claude", "commands");
  for (const nome of fs.readdirSync(cmds)) {
    if (!/^fiscal-.*\.md$/.test(nome)) continue;
    lista.push([path.join(cmds, nome), path.join(RAIZ, ".opencode", "commands", nome)]);
  }
  return lista;
}

let divergentes = 0;
for (const [origem, destino] of pares()) {
  const a = fs.readFileSync(origem);
  const b = lerSeExiste(destino);
  if (b && a.equals(b)) continue;
  divergentes++;
  const rel = path.relative(RAIZ, destino);
  if (CHECK) {
    console.log(`DIVERGENTE: ${rel}`);
  } else {
    fs.mkdirSync(path.dirname(destino), { recursive: true });
    fs.writeFileSync(destino, a);
    console.log(`ATUALIZADO: ${rel}`);
  }
}

console.log(divergentes === 0 ? "Tudo sincronizado." : `${divergentes} arquivo(s) ${CHECK ? "divergente(s)" : "atualizado(s)"}.`);
process.exit(CHECK && divergentes ? 1 : 0);
