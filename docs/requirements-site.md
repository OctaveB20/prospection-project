# Exigences — Template Astro (sites clients et démos)

Concerne la **phase 0** (démos rapides faites à la main) et prépare la **phase 3** (génération automatique de démo depuis le CRM).

## 1. Prérequis techniques
| Outil | Version | Usage |
|---|---|---|
| Node.js | 22 LTS (≥ 20.19 minimum) | Build Astro |
| npm | ≥ 10 | Dépendances |
| Astro | 7.x (verrouillé par `package-lock.json`) | Générateur de site statique |
| Git + compte GitHub | — | Versionnement, déclenche le déploiement |
| Cloudflare Pages ou Netlify | — | Hébergement statique gratuit |

Aucune clé API n'est nécessaire pour construire un site : toutes les données sont dans le `config.json`.

## 2. Principe
- **Un seul template** (`site-template/`), **un `config.json` par commerce** (`site-template/configs/<slug>.json`).
- On choisit la config au build : `SITE_CONFIG=configs/<slug>.json npm run build`.
- Toute nouvelle fonctionnalité = une **section activable** dans la config (`"actif": true/false`). Aucun code spécifique à un client.
- La même config sert à la démo (`"demo.actif": true`) puis au site de production (`false`) après signature.

## 3. Sections disponibles
| Clé | Contenu | Formules |
|---|---|---|
| `accueil` | Nom, accroche, boutons Appeler / Itinéraire, visuel | Base, Plus |
| `apropos` | Présentation du commerce, points forts | Base, Plus |
| `produits` | Produits / services | Base, Plus |
| `tarifs` | Menu, carte ou grille de prix | Base, Plus |
| `galerie` | Photos du commerçant (visuels génériques en démo) | Base, Plus |
| `avis` | Note Google, nb d'avis, 2-3 avis, lien vers la fiche | Base, Plus |
| `horaires` | Horaires de la semaine, jour courant surligné | Base, Plus |
| `contact` | Téléphone, email, adresse, réseaux sociaux | Base, Plus |
| `reservation` | Bouton Planity / Zenchef / TheFork (intégration, pas de recodage) | **Plus** |
| `devis` | Formulaire de demande de devis | **Plus** |
| `acces` | Carte OpenStreetMap (sans cookies) + lien itinéraire | **Plus** |
| `evenements` | Événements à venir (dégustations, ateliers, soirées) : les dates passées disparaissent seules, données schema.org Event pour Google ; inscription par billetterie externe, téléphone ou devis | à placer dans l'offre (voir offre-et-prix.md) |
| *(à faire)* version anglaise | Pages en anglais + `hreflang` | **Plus** |

Offre : Base 350 €, Plus 450 €, maintenance 20 €/mois (`docs/offre-et-prix.md`). **Le build échoue si une config `base` active une section réservée à Plus.**

## 4. Règles de conformité (contrôlées au build quand c'est possible)
- **Photos Google interdites** : le build refuse toute image venant d'un domaine Google (`googleusercontent`, `maps.googleapis`, `ggpht`…). On utilise les visuels génériques par métier (`public/visuels/<metier>/`) ou les photos fournies par le client.
- **Données Places** (nom, note, avis, horaires) : copiées dans la config au moment de générer la démo, puis rafraîchies avant la mise en ligne. Seul `placeId` est conservé durablement côté CRM.
- **Avis d'exemple** : dans une démo sans données réelles, chaque avis porte `"exemple": true` et s'affiche avec la mention « Avis d'exemple ». On n'affiche jamais un faux avis comme un vrai.
- **Démo non indexée** : `noindex, nofollow` quand `demo.actif` est vrai, et un bandeau « Démo » visible.
- **Sans cookies** : pas de Google Maps intégré, pas de Google Fonts, analytics Plausible/Umami seulement en production.
- **Mentions légales** : page `/mentions-legales` générée depuis la config (éditeur, SIRET, hébergeur).
- **Formulaires** : désactivés en démo (message explicatif), branchés sur `formulaire.action` en production.

**Mentions obligatoires par métier** : `commerce.avertissements` s'affiche en pied de page. Pour un caviste (vente d'alcool, loi Évin), le build échoue sans « L'abus d'alcool est dangereux pour la santé, à consommer avec modération. » ; ajouter aussi « La vente d'alcool aux mineurs est interdite. »

## 5. SEO local (inclus dans toutes les formules)
- Généré par le template : `<title>` et description « métier + quartier » (`seo` dans la config), données structurées schema.org, `sitemap.xml`, `robots.txt` (démo : `Disallow: /`).
- À faire à la mise en ligne : Search Console (sitemap envoyé), fiche Google optimisée et liée au site, Bing Places, Apple Business Connect, PagesJaunes, QR code avis.

## 6. Qualité attendue
- PageSpeed mobile ≥ 90 (site statique, pas de framework JS côté client, images SVG/optimisées).
- Lisible sur mobile dès 360 px, barre d'action fixe en bas (Appeler / Itinéraire).
- Accessibilité de base : contrastes suffisants, textes alternatifs, libellés de formulaire, navigation clavier.
- Données structurées schema.org (`Florist`, `Restaurant`, `HairSalon`… selon `metier`) pour le SEO local.

## 7. Critères d'acceptation d'une démo
- [ ] `npm run build` passe sans erreur avec la config du commerce
- [ ] Nom, adresse, téléphone, horaires, note et nb d'avis conformes à la fiche du commerce
- [ ] Aucune photo Google, bandeau démo présent, page non indexée
- [ ] Sections cohérentes avec la formule proposée dans le one-pager
- [ ] Vérifiée sur mobile (bouton Appeler fonctionnel)
- [ ] Publiée sur `demo.<domaine>/<slug>`

## 8. Commandes
```bash
cd site-template
npm install
SITE_CONFIG=configs/fleuriste-atelier-petale.json npm run dev     # aperçu local
SITE_CONFIG=configs/fleuriste-atelier-petale.json npm run build   # sortie dans dist/<slug>/ (démo) ou dist/ (production)
npm run check-config -- configs/fleuriste-atelier-petale.json    # valide une config sans builder
```
