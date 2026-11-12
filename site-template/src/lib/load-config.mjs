// Chargement + validation du config.json d'un commerce.
// Utilisé par astro.config.mjs, src/lib/config.ts et scripts/check-config.mjs.
import fs from 'node:fs';
import path from 'node:path';

export const CONFIG_PAR_DEFAUT = 'configs/fleuriste-atelier-petale.json';

// Offre au 11/11/2026 (docs/offre-et-prix.md) : sections réservées à la formule Plus.
const FORMULES = { base: {}, plus: {} };
const SECTIONS_PLUS = ['reservation', 'devis', 'acces'];

// Règle Google : aucune photo issue de Google dans les sites ou démos.
const DOMAINES_INTERDITS = [
  'googleusercontent.com',
  'maps.googleapis.com',
  'places.googleapis.com',
  'ggpht.com',
  'gstatic.com',
];

export function cheminConfig(fichier) {
  return path.resolve(process.cwd(), fichier ?? process.env.SITE_CONFIG ?? CONFIG_PAR_DEFAUT);
}

export function loadConfig(fichier) {
  const chemin = cheminConfig(fichier);
  if (!fs.existsSync(chemin)) {
    throw new Error(`[config] Fichier introuvable : ${chemin}`);
  }
  let cfg;
  try {
    cfg = JSON.parse(fs.readFileSync(chemin, 'utf-8'));
  } catch (e) {
    throw new Error(`[config] JSON invalide dans ${chemin} : ${e.message}`);
  }
  const erreurs = validerConfig(cfg);
  if (erreurs.length) {
    throw new Error(`[config] ${path.basename(chemin)} invalide :\n  - ${erreurs.join('\n  - ')}`);
  }
  return cfg;
}

export function validerConfig(cfg) {
  const e = [];
  const requis = (val, nom) => {
    if (val === undefined || val === null || val === '') e.push(`champ requis manquant : ${nom}`);
  };

  requis(cfg.slug, 'slug');
  if (cfg.slug && !/^[a-z0-9-]+$/.test(cfg.slug)) e.push('slug : minuscules, chiffres et tirets uniquement');
  requis(cfg.metier, 'metier');
  requis(cfg.formule, 'formule');
  if (cfg.formule && !FORMULES[cfg.formule]) e.push(`formule inconnue : ${cfg.formule} (base, plus)`);
  requis(cfg.commerce?.nom, 'commerce.nom');
  requis(cfg.commerce?.telephone, 'commerce.telephone');
  requis(cfg.commerce?.adresse?.rue, 'commerce.adresse.rue');
  requis(cfg.commerce?.adresse?.codePostal, 'commerce.adresse.codePostal');
  requis(cfg.commerce?.adresse?.ville, 'commerce.adresse.ville');
  requis(cfg.seo?.titre, 'seo.titre');
  requis(cfg.seo?.description, 'seo.description');

  if (!Array.isArray(cfg.ordre) || cfg.ordre.length === 0) {
    e.push('ordre : liste des sections à afficher requise');
  } else {
    for (const cle of cfg.ordre) {
      if (!cfg.sections?.[cle]) e.push(`ordre contient « ${cle} » mais sections.${cle} n'existe pas`);
    }
  }

  if (cfg.formule === 'base' && cfg.sections) {
    const enTrop = SECTIONS_PLUS.filter((m) => cfg.sections[m]?.actif);
    if (enTrop.length) {
      e.push(`formule base : ${enTrop.join(', ')} réservé(s) à la formule Plus`);
    }
  }

  const texte = JSON.stringify(cfg);
  for (const d of DOMAINES_INTERDITS) {
    if (texte.includes(d)) e.push(`image ou ressource Google interdite (${d}) : utiliser les visuels génériques`);
  }

  for (const [i, avis] of (cfg.sections?.avis?.liste ?? []).entries()) {
    if (cfg.demo?.actif !== true && avis.exemple) {
      e.push(`avis n°${i + 1} marqué « exemple » : interdit hors démo, remplacer par un vrai avis`);
    }
  }

  return e;
}
