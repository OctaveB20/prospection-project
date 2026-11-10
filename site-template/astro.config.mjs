import { defineConfig } from 'astro/config';
import { loadConfig } from './src/lib/load-config.mjs';

// La config du commerce est choisie avec SITE_CONFIG=configs/<slug>.json
const cfg = loadConfig();
const estDemo = cfg.demo?.actif === true;

export default defineConfig({
  // Production : domaine du client. Démo : demo.<domaine>/<slug>
  site: estDemo ? cfg.demo.urlBase : cfg.site?.url,
  base: estDemo ? `/${cfg.slug}` : '/',
  // En démo, chaque commerce sort dans dist/<slug>/ : plusieurs démos peuvent
  // être déployées ensemble sur demo.<domaine>.
  outDir: estDemo ? `./dist/${cfg.slug}` : './dist',
  trailingSlash: 'ignore',
  build: { format: 'directory' },
});
