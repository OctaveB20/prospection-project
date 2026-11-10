# Roadmap — Sites clés en main pour petits commerces

## Vision
Repérer automatiquement des commerces locaux à fort potentiel, leur envoyer une démo de **leur** site déjà prête + un argumentaire chiffré personnalisé, puis transformer la démo vendue en site final, le tout avec un minimum de travail manuel.

**Circuit complet :**
Scanner (Google Places + PageSpeed) → Score → CRM → Génération démo Astro + one-pager → Envoi → Relance → Signature → Mise en ligne (même config)

---

## Architecture
| Brique | Techno | Rôle |
|---|---|---|
| Back-office interne | Python + Streamlit + SQLite | Scanner, scoring, CRM, génération démo/one-pager |
| Données lieux | Google Places API (New), field masks stricts | Note, nb d'avis, site web, horaires, catégorie |
| Qualité site existant | PageSpeed Insights API (gratuit) | Score mobile, vitesse, HTTPS |
| Sites clients + démos | Astro (template unique) + `config.json` par client | Site vitrine statique, rapide, SEO |
| Code / déploiement | GitHub → Cloudflare Pages ou Netlify | Déploiement auto à chaque push |
| SEO / visibilité | Google Search Console + Google Business Profile | Indexation, lien fiche Google |
| Audience | Plausible ou Umami (sans cookies) | KPI clients, pas de bandeau cookies |
| Réservation | Intégrations existantes (Planity, Zenchef, TheFork) | Pas de recodage |

---

## Phase 0 — Validation manuelle (avant toute automatisation)
- [ ] Choisir 1 quartier + 2-3 catégories cibles
- [ ] Repérer 15-20 commerces à la main
- [ ] Faire 3-5 démos rapides, envoyer, relancer
- [ ] Mesurer : taux de réponse, objections, prix acceptable
- **Critère de sortie :** au moins 1 intérêt sérieux / objections connues

## Phase 1 — Moteur de repérage (à partir du prototype existant)
- [ ] Recherche par zone + catégorie (Text Search, field masks minimaux)
- [ ] Détection « faux sites » : websiteUri vers Facebook / Instagram / Linktree / annuaires = pas de site
- [ ] Audit PageSpeed pour les commerces qui ont un site (mobile, vitesse, HTTPS)
- [ ] Score de priorité : note × log(nb avis) + bonus catégorie dépendante de la recherche + bonus si concurrents proches ont un site + bonus site absent/médiocre
- [ ] Cache : stocker `place_id` + date du dernier scan, ne jamais rescanner une zone récente
- [ ] Suivi du quota (1 000 appels Enterprise gratuits/mois, ~20 lieux par appel)

## Phase 2 — CRM minimal
- [ ] Table SQLite : commerce, score, contact, statut, date de relance, notes
- [ ] Statuts : repéré → contacté → démo vue → relancé → signé / refus
- [ ] Vue « à relancer aujourd'hui »

## Phase 3 — Template Astro + génération de démo
- [ ] Template unique, sections activables : accueil, services/menu, horaires, carte, avis, contact, réservation
- [ ] `config.json` par commerce rempli automatiquement depuis Places (nom, adresse, horaires, catégorie, 2-3 avis)
- [ ] Visuels génériques par catégorie (pas de photos Google)
- [ ] Démo publiée sur URL privée : `demo.<domaine>/<slug-commerce>`
- [ ] 3 variantes visibles = les 3 formules (vitrine / + réservation / + avis & contenu)

## Phase 4 — Argumentaire personnalisé
- [ ] One-pager généré par commerce : sa note, son nb d'avis, concurrents à 500 m avec site, son score mobile éventuel
- [ ] Bloc de stats générales **sourcées** (source citée pour chaque chiffre)
- [ ] Export PDF + lien vers la démo

## Phase 5 — Offre, juridique, livraison
- [ ] Offre : frais de création + abonnement mensuel (hébergement, domaine, petites modifs, fiche Google)
- [ ] Statut pour facturer (micro-entreprise)
- [ ] Contrat / CGV : propriété du site, durée, résiliation
- [ ] Mentions légales sur chaque site client
- [ ] Prospection email B2B : vérifier la doc CNIL (message lié à l'activité + désabonnement)
- [ ] Mise en ligne : domaine client, Search Console, lien Business Profile, analytics sans cookies

## Phase 6 — Automatisation de bout en bout
- [ ] Bouton « générer démo + one-pager » depuis le CRM
- [ ] Envoi + relance programmés
- [ ] Signature → la config de la démo devient le site de production

---

## Points de vigilance
- L'API Places ne donne pas l'affluence en temps réel : fréquentation estimée via nb d'avis, note, récence des avis
- Règles de cache Google : seul le `place_id` est stockable indéfiniment
- Un commerce bondé sans site n'en a pas forcément besoin : viser bonne note + volume moyen
