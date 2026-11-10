// Usage : npm run check-config -- configs/<slug>.json
import { loadConfig, cheminConfig } from '../src/lib/load-config.mjs';

const fichier = process.argv[2];
try {
  const cfg = loadConfig(fichier);
  const actives = cfg.ordre.filter((k) => cfg.sections[k]?.actif);
  console.log(`OK ${cheminConfig(fichier)}`);
  console.log(`  ${cfg.commerce.nom} — formule ${cfg.formule} — ${cfg.demo?.actif ? 'DÉMO' : 'production'}`);
  console.log(`  Sections : ${actives.join(', ')}`);
} catch (err) {
  console.error(err.message);
  process.exit(1);
}
