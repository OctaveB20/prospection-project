# CLAUDE.md — Sites clés en main pour petits commerces

## Contexte
Activité de création de sites vitrines clés en main pour petits commerces locaux (Paris pour commencer).
Circuit : Scanner (Google Places + PageSpeed) → Score → CRM → Génération démo Astro + one-pager → Envoi → Relance → Signature → Mise en ligne (même config.json).

Documents de référence, à lire avant de proposer une étape :
- `docs/roadmap-projet.md` : phases 0 à 6. Indique toujours dans quelle phase on se situe.
- `docs/offre-et-prix.md` : formules Base (350 €) / Plus (450 €) + maintenance 20 €/mois, SEO local inclus, paiement, coûts, cibles par métier, fiscalité. Ces décisions sont prises : ne propose pas d'autre grille sauf demande explicite, et signale toute idée qui les contredit.

## Stack (décidée — ne pas proposer d'alternatives sauf demande)
- Back-office interne : Python + Streamlit (scanner, scoring, CRM, génération) ; base SQLite en local, Postgres Supabase en ligne (Streamlit Community Cloud), via `DATABASE_URL`
- Données : Google Places API (New) avec field masks stricts + PageSpeed Insights API
- Sites clients et démos : Astro, UN seul template, un `config.json` par client
- Déploiement : GitHub → Cloudflare Pages ou Netlify
- SEO : Google Search Console + Google Business Profile (SEO local inclus dans toutes les formules : argument de vente clé)
- Analytics : Umami auto-hébergé (sans cookies) ; Plausible écarté, trop cher par client
- Carte : OpenStreetMap intégrée (sans cookies) + lien itinéraire Google Maps ; pas d'iframe Google Maps
- Formulaires : Web3Forms (offre gratuite)
- Réservation : intégrer Planity, Zenchef, TheFork — ne jamais recoder

## Règles pour le code
- Code complet et exécutable, jamais de fragments avec "..." ; indique le fichier et l'emplacement de chaque modification.
- Itératif : livrer une version qui marche, puis améliorer.
- Coûts API :
  - field masks minimaux sur chaque appel Places ;
  - cache systématique, ne jamais rescanner une zone scannée récemment (stocker `place_id` + date du dernier scan) ;
  - signaler l'impact quota de toute nouvelle fonctionnalité (Text Search Enterprise : 1 000 appels gratuits/mois, ~20 lieux par appel).
- Conditions Google :
  - seul le `place_id` est stockable durablement (nom, note, avis, horaires = données à rafraîchir, pas à archiver) ;
  - aucune photo Google réutilisée dans les sites ou démos (visuels génériques par catégorie).
- Template Astro piloté par `config.json` : toute nouvelle fonctionnalité = une section activable dans la config, jamais de code spécifique à un client.
- Clés API dans des variables d'environnement / `st.secrets`, jamais en dur, jamais commitées (`.env` et `.streamlit/secrets.toml` dans `.gitignore`).

## Règles pour les contenus commerciaux (argumentaires, one-pagers, emails)
- Concrets, chiffrés, personnalisés avec les données du commerce (note, nb d'avis, concurrents à 500 m avec site, score mobile PageSpeed).
- Toute statistique générale est sourcée (source + année). En cas de doute sur un chiffre : le chercher ou le dire, ne jamais l'inventer.
- Ton professionnel, simple, sans jargon technique pour un commerçant.
- Adapter au métier (artisan, restaurant, boutique, coiffeur, café) — voir les cibles dans `docs/offre-et-prix.md`.
- Comparer le prix à ce que le commerce paie déjà (Planity, TheFork…), jamais à une agence.
- Toujours inclure le calcul « clients à gagner pour rembourser le site » :
  `prix 1ère année ÷ (panier moyen × marge)`, avec les chiffres du commerce (prix 1ère année = création + 12 × 20 €).
  Exemple : formule Base = 350 + 240 = 590 € la 1ère année ; restaurant avec panier moyen 25 € et marge 30 % → 590 ÷ (25 × 0,30) ≈ 79 couverts sur l'année, soit 1 à 2 par semaine.
- Ne jamais mentionner le chèque numérique Île-de-France (aide close).
- Prospection email B2B conforme CNIL : message en lien avec l'activité du destinataire + lien de désabonnement dans chaque envoi.

## Façon de travailler
- Répondre en français, de façon directe et actionnable.
- Exemples ancrés dans des cas réels (vrais types de commerces, vrais quartiers parisiens), pas de génériques.
- Si une idée pose problème (coût, juridique, technique, commercial) : le dire franchement et proposer mieux.

## Source de vérité
Ce dépôt est la référence pour la stack et les règles de code. Si `docs/offre-et-prix.md` ou `docs/roadmap-projet.md` change ici, le reporter aussi dans le Projet claude.ai « construction site petit commerce » (et inversement).
