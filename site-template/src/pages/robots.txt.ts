import type { APIRoute } from 'astro';
import { config, estDemo, url } from '../lib/config';

// Démo : rien n'est indexé. Production : tout est indexable + lien vers le sitemap.
export const GET: APIRoute = () => {
  const lignes = estDemo
    ? ['User-agent: *', 'Disallow: /']
    : ['User-agent: *', 'Allow: /', `Sitemap: ${new URL(url('sitemap.xml'), import.meta.env.SITE ?? config.site?.url).href}`];
  return new Response(lignes.join('\n') + '\n', { headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
};
