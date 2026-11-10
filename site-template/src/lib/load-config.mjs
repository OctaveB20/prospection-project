// Chargement + validation du config.json d'un commerce.
// Utilisé par astro.config.mjs, src/lib/config.ts et scripts/check-config.mjs.
import fs from 'node:fs';
import path from 'node:path';

export const CONFIG_PAR_DEFAUT = 'configs/fleuriste-atelier-petale.json';

const FORMULES = {
  basique: { modules: 1, galerie: 15 },
  plus: { modules: 2, galerie: 30 },
  premium: { modules: Infinity, galerie: Infinity },
};

// Sections qui comptent comme « module métier » dans l'offre.
const MODULES_METIER = ['tarifs', 'devis', 'reservation', 'menu'];

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
  if (cfg.formule && !FORMULES[cfg.formule]) e.push(`formule inconnue : ${cfg.formule} (basique, plus, premium)`);
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

  const regles = FORMULES[cfg.formule];
  if (regles && cfg.sections) {
    const actifs = MODULES_METIER.filter((m) => cfg.sections[m]?.actif);
    if (actifs.length > regles.modules) {
      e.push(`formule ${cfg.formule} : ${regles.modules} module(s) métier max, ${actifs.length} actifs (${actifs.join(', ')})`);
    }
    const nbImages = cfg.sections.galerie?.images?.length ?? 0;
    if (cfg.sections.galerie?.actif && nbImages > regles.galerie) {
      e.push(`formule ${cfg.formule} : galerie limitée à ${regles.galerie} visuels (${nbImages} fournis)`);
    }
    if (cfg.formule === 'basique' && cfg.sections.produits?.actif) {
      e.push('formule basique : la section produits détaillés n\'est pas incluse');
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
