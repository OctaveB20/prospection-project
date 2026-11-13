# Back-office — scanner de prospects + CRM

Phases 1 et 2 de `docs/roadmap-projet.md`. Python + Streamlit, base SQLite en local ou Postgres (Supabase) en ligne.
Réécrit à partir du prototype prospect-automation (scanner de site et suivi de quota repris, NLU et modèle d'email retirés).

## Ce que ça fait
1. **Recherche** Google Places (New) par métier + zone (« fleuriste Paris 18e »), avec un field mask minimal.
2. **Présence en ligne** de chaque commerce, à partir du lien que Google affiche :

| Type | Exemple | Priorité |
|---|---|---|
| aucun site | pas de lien sur la fiche | très haute |
| réseau social | Facebook, Instagram, Linktree… | très haute |
| site inaccessible | le domaine ne répond plus | très haute |
| annuaire / plateforme | PagesJaunes, TheFork, Planity, Interflora… | haute |
| site gratuit / faible | business.site, Wix gratuit, Google Sites… | moyenne |
| site | vrai domaine (option : vitesse mobile PageSpeed) | basse, sauf site lent ou sans HTTPS |

3. **Filtres** sans nouvelle requête : note minimum, nombre d'avis (min et max), types de présence.
4. **Score** = note × log(nb avis) + bonus métier + bonus présence + bonus concurrents à 500 m avec site, et un malus au-delà de 1 500 avis.
5. **CRM** : statut (repéré → contacté → démo vue → relancé → signé / refus), date de relance, notes, vue « à relancer aujourd'hui ».

Métiers : artisans (plombier, électricien, serrurier, menuisier, peintre, couvreur), restaurant, fleuriste, caviste, épicerie fine, coiffeur, barbier, institut, boulangerie, café. On en ajoute dans `metiers.py`.

## Installation
```bash
cd back-office
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # puis mettre ta clé Google
streamlit run Scanner.py
```

Clé Google :
1. Ouvre console.cloud.google.com, crée un projet et active la facturation (obligatoire, même pour rester dans le gratuit).
2. Active « Places API (New) » et crée une clé : restriction d'application **Aucune** (le scanner appelle Google depuis Python, une restriction « Sites Web » bloquerait tout), restriction d'API **Places API (New) uniquement**.
3. Mets une **alerte budget** à 1 € et, dans Quotas, un plafond journalier sur Text Search.
4. PageSpeed : rien à faire (marche sans clé), ou une 2e clé restreinte à « PageSpeed Insights API » dans `PAGESPEED_API_KEY`.

## Mise en ligne (Streamlit Community Cloud + Supabase)
Sur Streamlit Cloud le disque est effacé à chaque redémarrage : la base doit être sur Supabase.

1. **Supabase** : crée un **nouveau** projet (pas celui de l'ancien prototype), note le mot de passe de la base.
   Puis Project Settings → Database → Connection string → **Transaction pooler** (port 6543) : copie l'URI et remplace `[YOUR-PASSWORD]`.
   Rien à créer à la main : les tables sont créées au premier lancement, avec RLS activé (l'API REST publique de Supabase n'y a pas accès).
2. **Streamlit Cloud** : New app → dépôt `prospection-project`, branche `main`, fichier `back-office/Scanner.py`.
3. **Settings → Secrets** :
   ```toml
   GOOGLE_PLACES_API_KEY = "ta-clé-google"
   DATABASE_URL = "postgresql://postgres.xxxx:MOT-DE-PASSE@aws-0-eu-west-3.pooler.supabase.com:6543/postgres"
   APP_PASSWORD = "un-mot-de-passe-long"
   PLACES_MONTHLY_LIMIT = "900"
   PLACES_DAILY_LIMIT = "60"
   ```
   L'URI exacte est celle copiée à l'étape 1. Les crochets autour du mot de passe et ses caractères spéciaux sont corrigés automatiquement ; tu peux aussi mettre le mot de passe à part dans `DATABASE_PASSWORD = "..."`. Sans `APP_PASSWORD`, l'app en ligne refuse de s'ouvrir.
4. **Settings → Sharing** : mets l'app en privé si ton offre Streamlit le permet. Le mot de passe protège dans tous les cas.

Ne jamais mettre ces valeurs dans le dépôt : `.env` et `.streamlit/secrets.toml` sont dans `.gitignore`.

## Coûts et quota
- 1 requête Text Search Enterprise = 20 lieux. 1 000 requêtes gratuites par mois, puis 35 $ les 1 000.
- Un scan de 3 métiers × 60 lieux = 9 requêtes. Garde-fous dans `.env` : `PLACES_MONTHLY_LIMIT=900`, `PLACES_DAILY_LIMIT=60`.
- Un même métier + zone n'est pas rescanné avant `RESCAN_DAYS` (30 jours) sauf case cochée : les résultats sont relus en base, pour 0 requête.
- PageSpeed : gratuit, mais lent (10 à 30 s par site). Désactivé par défaut.

## Conditions Google
- Seul le `place_id` est conservé durablement. Les données Google (nom, note, avis, téléphone, lien) sont en cache au plus `CACHE_DAYS` (30 jours), puis purgées. Le CRM propose de les rafraîchir (1 requête Place Details par fiche).
- Aucune photo Google n'est demandée (pas de champ `photos` dans le field mask).

## Tests sans clé
```bash
python -m pytest -q
TEST_DATABASE_URL=postgresql://postgres@localhost:5432/postgres python -m pytest -q   # mêmes tests sur Postgres
PLACES_FAKE_FILE=tests/fixtures/places_test.json streamlit run Scanner.py
```
Le second lance l'interface avec 6 lieux fictifs, sans aucune requête Google.

## Pas encore fait
- Génération démo + one-pager depuis le CRM (phases 3-4, puis 6).
- Envoi d'emails : le module du prototype (SMTP + validation) sera repris en phase 6, avec un message conforme CNIL (lien avec l'activité + désabonnement).
