import type { APIRoute } from 'astro';
import { config, url } from '../lib/config';

// Pages du site (une entrée par page Astro de src/pages).
const PAGES = ['/', '/mentions-legales/'];

export const GET: APIRoute = () => {
  const base = import.meta.env.SITE ?? config.site?.url ?? 'https://example.com';
  const urls = PAGES.map((p) => `  <url><loc>${new URL(url(p), base).href}</loc></url>`).join('\n');
  const xml = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls}\n</urlset>\n`;
  return new Response(xml, { headers: { 'Content-Type': 'application/xml; charset=utf-8' } });
};
