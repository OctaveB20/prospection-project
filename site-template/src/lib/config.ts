import { loadConfig } from './load-config.mjs';
import type { SiteConfig } from './types';

export const config = loadConfig() as SiteConfig;

export const estDemo = config.demo?.actif === true;

/** Préfixe un chemin avec la base du site (utile en démo : /<slug>/...). */
export function url(chemin: string): string {
  const base = import.meta.env.BASE_URL.replace(/\/$/, '');
  return `${base}/${chemin.replace(/^\//, '')}`;
}

/** "01 99 00 12 34" -> "+33199001234" pour les liens tel: */
export function telLien(tel: string): string {
  const chiffres = tel.replace(/[^\d+]/g, '');
  return chiffres.startsWith('0') ? `+33${chiffres.slice(1)}` : chiffres;
}

export function adresseComplete(): string {
  const a = config.commerce.adresse;
  return `${a.rue}, ${a.codePostal} ${a.ville}`;
}

export function lienItineraire(): string {
  const g = config.commerce.geo;
  const destination = g ? `${g.lat},${g.lng}` : encodeURIComponent(adresseComplete());
  return `https://www.google.com/maps/dir/?api=1&destination=${destination}`;
}

export function lienAvisGoogle(): string | null {
  const id = config.commerce.placeId;
  return id ? `https://search.google.com/local/reviews?placeid=${encodeURIComponent(id)}` : null;
}

/** Sections actives, dans l'ordre de la config. */
export function sectionsActives(): string[] {
  return config.ordre.filter((cle) => (config.sections[cle] as { actif?: boolean } | undefined)?.actif);
}
