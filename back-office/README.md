# Back-office — scanner de prospects + CRM

Phases 1 et 2 de `docs/roadmap-projet.md`. Python + Streamlit + SQLite.
Réécrit à partir du prototype prospect-automation (scanner de site et suivi de quota repris, Supabase et NLU retirés).

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
2. Active « Places API (New) » et « PageSpeed Insights API ».
3. Crée une clé API **restreinte à ces deux API**.
4. Mets une **alerte budget** à 1 € et, dans Quotas, un plafond journalier sur Text Search.

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
PLACES_FAKE_FILE=tests/fixtures/places_test.json streamlit run Scanner.py
```
Le second lance l'interface avec 6 lieux fictifs, sans aucune requête Google.

## Pas encore fait
- Génération démo + one-pager depuis le CRM (phases 3-4, puis 6).
- Envoi d'emails : le module du prototype (SMTP + validation) sera repris en phase 6, avec un message conforme CNIL (lien avec l'activité + désabonnement).
