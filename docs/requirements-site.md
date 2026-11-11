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
| `accueil` | Nom, accroche, boutons Appeler / Itinéraire, visuel | toutes |
| `apropos` | Présentation du commerce, points forts | toutes |
| `produits` | Produits / services détaillés | Plus, Premium |
| `tarifs` | Module métier : grille de prix | module |
| `galerie` | Visuels (15 max Basique, 30 max Plus) | toutes |
| `avis` | Note Google, nb d'avis, 2-3 avis, lien vers la fiche | toutes |
| `horaires` | Horaires de la semaine, jour courant surligné | toutes |
| `devis` | Module métier : formulaire de demande de devis | module |
| `reservation` | Module métier : bouton Planity / Zenchef / TheFork (intégration, pas de recodage) | module |
| `acces` | Carte OpenStreetMap (sans cookies) + lien itinéraire | toutes |
| `contact` | Téléphone, email, adresse, réseaux sociaux | toutes |

Modules métier autorisés : 1 en Basique, 2 en Plus, tous en Premium. **Le build échoue si la config dépasse sa formule.**

## 4. Règles de conformité (contrôlées au build quand c'est possible)
- **Photos Google interdites** : le build refuse toute image venant d'un domaine Google (`googleusercontent`, `maps.googleapis`, `ggpht`…). On utilise les visuels génériques par métier (`public/visuels/<metier>/`) ou les photos fournies par le client.
- **Données Places** (nom, note, avis, horaires) : copiées dans la config au moment de générer la démo, puis rafraîchies avant la mise en ligne. Seul `placeId` est conservé durablement côté CRM.
- **Avis d'exemple** : dans une démo sans données réelles, chaque avis porte `"exemple": true` et s'affiche avec la mention « Avis d'exemple ». On n'affiche jamais un faux avis comme un vrai.
- **Démo non indexée** : `noindex, nofollow` quand `demo.actif` est vrai, et un bandeau « Démo » visible.
- **Sans cookies** : pas de Google Maps intégré, pas de Google Fonts, analytics Plausible/Umami seulement en production.
- **Mentions légales** : page `/mentions-legales` générée depuis la config (éditeur, SIRET, hébergeur).
- **Formulaires** : désactivés en démo (message explicatif), branchés sur `formulaire.action` en production.

## 5. Qualité attendue
- PageSpeed mobile ≥ 90 (site statique, pas de framework JS côté client, images SVG/optimisées).
- Lisible sur mobile dès 360 px, barre d'action fixe en bas (Appeler / Itinéraire).
- Accessibilité de base : contrastes suffisants, textes alternatifs, libellés de formulaire, navigation clavier.
- Données structurées schema.org (`Florist`, `Restaurant`, `HairSalon`… selon `metier`) pour le SEO local.

## 6. Critères d'acceptation d'une démo
- [ ] `npm run build` passe sans erreur avec la config du commerce
- [ ] Nom, adresse, téléphone, horaires, note et nb d'avis conformes à la fiche du commerce
- [ ] Aucune photo Google, bandeau démo présent, page non indexée
- [ ] Sections cohérentes avec la formule proposée dans le one-pager
- [ ] Vérifiée sur mobile (bouton Appeler fonctionnel)
- [ ] Publiée sur `demo.<domaine>/<slug>`

## 7. Commandes
```bash
cd site-template
npm install
SITE_CONFIG=configs/fleuriste-atelier-petale.json npm run dev     # aperçu local
SITE_CONFIG=configs/fleuriste-atelier-petale.json npm run build   # sortie dans dist/<slug>/ (démo) ou dist/ (production)
npm run check-config -- configs/fleuriste-atelier-petale.json    # valide une config sans builder
```
