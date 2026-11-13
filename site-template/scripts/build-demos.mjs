// Construit toutes les démos (configs/*.json avec "demo.actif": true) dans dist/<slug>/,
// pour un seul projet Cloudflare Pages : <projet>.pages.dev/<slug>/
//
//   npm run build:demos                 -> toutes les démos
//   npm run build:demos -- caviste      -> seulement les configs dont le nom contient « caviste »
//
// La racine reçoit une page neutre qui NE liste PAS les démos (on n'expose pas ses prospects),
// un robots.txt et des en-têtes « noindex » : aucune démo n'est indexée par Google.
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { loadConfig } from '../src/lib/load-config.mjs';

const racine = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const dist = path.join(racine, 'dist');
const filtre = process.argv[2] ?? '';

const demos = [];
for (const fichier of fs.readdirSync(path.join(racine, 'configs')).filter((f) => f.endsWith('.json')).sort()) {
  if (filtre && !fichier.includes(filtre)) continue;
  const chemin = `configs/${fichier}`;
  const cfg = loadConfig(path.join(racine, chemin)); // échoue tout de suite si une config est invalide
  if (cfg.demo?.actif === true) demos.push({ chemin, cfg });
}
if (!demos.length) {
  console.error(`Aucune démo trouvée${filtre ? ` pour « ${filtre} »` : ''} (configs avec "demo": {"actif": true}).`);
  process.exit(1);
}
const slugs = demos.map((d) => d.cfg.slug);
const doublons = slugs.filter((s, i) => slugs.indexOf(s) !== i);
if (doublons.length) {
  console.error(`Slugs en double : ${[...new Set(doublons)].join(', ')}`);
  process.exit(1);
}

fs.rmSync(dist, { recursive: true, force: true });
for (const { chemin, cfg } of demos) {
  console.log(`\n▶ ${cfg.commerce.nom} -> dist/${cfg.slug}/`);
  const r = spawnSync('npx', ['astro', 'build', '--silent'], {
    cwd: racine,
    stdio: 'inherit',
    env: { ...process.env, SITE_CONFIG: chemin, ASTRO_TELEMETRY_DISABLED: '1' },
  });
  if (r.status !== 0) {
    console.error(`Échec du build pour ${chemin}`);
    process.exit(r.status ?? 1);
  }
}

const page = (titre, texte) => `<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow"><title>${titre}</title>
<style>body{margin:0;min-height:100vh;display:grid;place-items:center;font-family:system-ui,sans-serif;background:#faf7f2;color:#2b2224;padding:16px}
main{max-width:34rem;text-align:center}h1{font-family:Georgia,serif;font-weight:600}</style></head>
<body><main><h1>${titre}</h1><p>${texte}</p></main></body></html>
`;
fs.writeFileSync(path.join(dist, 'index.html'), page('Démos privées', 'Les démos sont accessibles uniquement par le lien personnel qui vous a été envoyé.'));
fs.writeFileSync(path.join(dist, '404.html'), page('Page introuvable', 'Vérifiez le lien qui vous a été envoyé.'));
fs.writeFileSync(path.join(dist, 'robots.txt'), 'User-agent: *\nDisallow: /\n');
// Cloudflare Pages : en-tête noindex sur tout le site, en plus de la balise meta de chaque démo.
fs.writeFileSync(path.join(dist, '_headers'), '/*\n  X-Robots-Tag: noindex, nofollow\n');

console.log(`\n✓ ${demos.length} démo(s) construite(s) :`);
for (const { cfg } of demos) console.log(`  /${cfg.slug}/  (${cfg.commerce.nom})`);
