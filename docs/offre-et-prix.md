# Offre, prix, SEO et coûts — décisions au 11/11/2026

Remplace la grille Basique / Plus / Premium du 10/11/2026 (voir « Changements de direction » dans `docs/roadmap-projet.md`).

## Formules
| | **Base** | **Plus** |
|---|---|---|
| Création (une fois) | **350 €** | **450 €** |
| Site vitrine 1 page, mobile, rapide | oui | oui |
| Photos (fournies par le commerçant, jamais de photos Google) | oui | oui |
| Menu / carte / tarifs | oui | oui |
| Avis Google (note, nb d'avis, extraits, lien vers la fiche) | oui | oui |
| Contact : appel, email, adresse, bouton itinéraire, réseaux | oui | oui |
| **SEO local de départ** (détail plus bas) | oui | oui |
| Moteur de réservation intégré (Planity, Zenchef, TheFork — jamais recodé) | — | oui |
| Version anglaise | — | oui |
| Formulaire de demande de devis | — | oui |
| Carte d'accès intégrée (OpenStreetMap, sans cookies) | — | oui |

**Maintenance : 20 €/mois** (les deux formules) : modifications, ajouts, debug, hébergement, nom de domaine, HTTPS, suivi SEO.

Hors offre : e-commerce, click & collect, logo, photos pro, blog, application.

### Contenu de la maintenance (proposé, à valider)
- Modifications et ajouts de contenu (horaires, menu, photos, textes) : **jusqu'à 1 h de travail par mois**, au-delà sur devis.
- Debug, mises à jour, hébergement, domaine et certificat HTTPS inclus.
- Fiche Google tenue à jour (horaires, fermetures exceptionnelles) et vérification mensuelle de la Search Console.
- Rapport trimestriel : visites (Umami), recherches qui amènent sur le site (Search Console), appels et itinéraires (fiche Google).

Pourquoi un plafond : 20 €/mois = 240 €/an, soit ≈ 173 € nets après cotisations. Sans limite, 2 h de travail par mois font tomber à environ 7 €/h net.

## SEO local (argument de vente clé)
### Inclus à la création (Base et Plus)
- Site statique rapide, objectif PageSpeed mobile ≥ 90.
- Titres et descriptions « métier + quartier » (ex. « Fleuriste à Montmartre, Paris 18e »), données structurées schema.org, `sitemap.xml` et `robots.txt`.
- Google Search Console : propriété validée, sitemap envoyé, demande d'indexation.
- Fiche Google (Business Profile) : lien vers le site, catégories, description, horaires, photos du commerçant. Création et validation si elle n'existe pas.
- Mêmes nom, adresse et téléphone sur Bing Places, Apple Business Connect et PagesJaunes.
- QR code « Laissez-nous un avis » à poser en caisse.
- Plus : version anglaise, qui capte aussi les recherches des touristes.

### Arguments chiffrés (sourcés)
- 97 % des consommateurs lisent les avis avant de choisir un commerce local ([BrightLocal, Local Consumer Review Survey 2026](https://www.brightlocal.com/research/local-consumer-review-survey/), échantillon américain).
- 47 % n'iraient pas dans un commerce qui a moins de 20 avis (même étude, chiffre repris par [PinMeTo](https://www.pinmeto.com/news/brightlocal-local-consumer-review-survey-2026/), à vérifier sur le rapport complet).
- À compléter par une stat française sourcée avant de l'utiliser sur un one-pager.

### Coûts SEO
| Poste | Coût | Quand |
|---|---|---|
| Search Console, Business Profile, Bing Places, Apple Business Connect, PageSpeed | 0 € | toujours |
| Inscription de base PagesJaunes | 0 € | toujours |
| QR code avis (impression autocollant) | quelques € par client (estimation) | à la création |
| Suivi de positions local (Local Falcon Starter) | 24,99 $/mois pour tous les clients ([agrégateur, sept. 2026](https://hackceleration.com/fr/labs/meilleur/logiciel-suivi-positions-seo-local)) | à partir d'environ 10 clients (≈ 2,50 $/client/mois) |
| Alternative : BrightLocal | ≈ 31 à 41 $/mois (non confirmé) | idem |
| **Ton temps** : mise en place SEO | ≈ 2 à 3 h par client (estimation à mesurer en phase 0) | à la création |
| **Ton temps** : suivi | ≈ 15 à 30 min par client et par mois (estimation) | inclus dans les 20 €/mois |

Avant 10 clients, pas d'outil payant : la Search Console donne déjà les positions moyennes et les recherches, gratuitement.

## Paiement
- **Création** : payée à la mise en ligne (option à décider : acompte de 30 % à la signature).
- **Maintenance** : 20 €/mois par prélèvement SEPA (GoCardless : 1 % + 0,20 € par prélèvement + TVA non récupérable ≈ 0,48 €, soit ≈ 5,80 €/an), ou 240 €/an payés d'avance (≈ 2,40 € de frais).
- Engagement de 12 mois sur la maintenance, écrit au contrat.

## Rentabilité par client
| | Base | Plus |
|---|---|---|
| CA 1ère année (création + 12 × 20 €) | 590 € | 690 € |
| Cotisations + impôt (27,8 %) | − 164 € | − 192 € |
| Domaine (1ère année) + SEPA mensuel + QR code | ≈ − 15 € | ≈ − 15 € |
| **Net 1ère année** | **≈ 411 €** (≈ 449 € avec l'ACRE) | **≈ 483 €** (≈ 527 € avec l'ACRE) |
| **Net les années suivantes** (240 € de maintenance) | **≈ 158 €/an** | **≈ 158 €/an** |

Le vrai coût est ton temps : création + SEO de départ, puis maintenance plafonnée.

**Clients à gagner pour rembourser le site** = prix 1ère année ÷ (panier moyen × marge). Exemple : restaurant en Base, panier 25 €, marge 30 % → 590 ÷ 7,50 ≈ 79 couverts sur l'année, soit 1 à 2 par semaine. En Plus : 690 ÷ 7,50 ≈ 92 couverts, soit ~2 par semaine.

## Cibles par métier (estimations, à valider en phase 0)
| Métier | Volonté de payer | Formule conseillée |
|---|---|---|
| Artisans (plombier, électricien, menuisier) | haute | Plus : formulaire de devis |
| Restaurants | moyenne à haute | Base (menu) ou Plus (réservation + anglais) |
| Boutiques (fleuriste, caviste, épicerie fine) | moyenne | Base, ou Plus si devis (mariages, événements) |
| Coiffeurs, barbiers, instituts | faible à moyenne | Base ; Plus si bouton Planity intégré |
| Cafés, boulangeries, tabacs, snacks | faible | Base, priorité basse au scanner |

## Coûts de l'activité
### Avant le premier client
| Poste | Coût | Obligatoire ? |
|---|---|---|
| Création micro-entreprise (formalites.entreprises.gouv.fr) + demande d'ACRE | 0 € | oui |
| Domaine .fr pour les démos (OVHcloud) | ≈ 6 € TTC la 1ère année, puis ≈ 9,35 €/an | oui en pratique |
| Hébergement Cloudflare Pages (500 builds/mois gratuits) | 0 € | — |
| Google Places + PageSpeed (1 000 Text Search Enterprise gratuits/mois, puis 35 $ les 1 000) | 0 € — alerte budget et plafond de quota obligatoires | — |
| Plateforme de facturation électronique (réception obligatoire depuis le 01/09/2026, émission au 01/09/2027) | 0 € possible (offres gratuites) | oui |
| Compte bancaire séparé (2nd compte courant gratuit) | 0 € | après 2 ans > 10 000 € de CA, conseillé dès le début |
| Brevo (prospection, 300 emails/jour, désabonnement géré) | 0 € | — |
| Contrat + CGV | 0 à quelques centaines d'€ (estimation) | oui avant de signer |
| RC Pro | ≈ 200 à 400 €/an | non, conseillée |
| Impression one-pagers | ≈ 10 à 20 € (estimation) | — |
| Email pro (Google Workspace Business Starter) | 6,80 €/mois en annuel | non |

Minimum : ≈ 6 à 10 €. Conseillé : ≈ 300 à 450 € la 1ère année.

### Coûts fixes ensuite (par an)
Domaine ≈ 9,35 € · email pro ≈ 82 € · RC Pro ≈ 200 à 400 € · CFE : 0 € la 1ère année, puis 0 € tant que le CA N-2 ≤ 5 000 € · serveur Umami (quelques €/mois, à chiffrer) · outil de suivi SEO à partir de ~10 clients ≈ 300 $/an. **Total ≈ 300 à 900 €/an selon le nombre de clients.**

### Coûts par client (par an)
Domaine ≈ 6 € puis 9,35 € · hébergement 0 € · formulaire de devis Web3Forms 0 € (250 envois/mois) · SEPA ≈ 5,80 € · analytics Umami auto-hébergé ≈ 0 € (Plausible exclu : 9 $/mois par site, trop cher face à 20 €/mois).

## Fiscalité
Micro-entreprise BNC : 25,6 % + versement libératoire 2,2 % ≈ 27,8 % du CA (ACRE 1ère année : 19,2 % + 2,2 %). Plafond 83 600 €. Franchise de TVA jusqu'à 37 500 € de CA (seuil majoré 41 250 €) : mention « TVA non applicable, art. 293 B du CGI ». Chèque numérique Île-de-France clos : ne pas l'utiliser comme argument.

## Questions ouvertes
- La maintenance à 20 €/mois est-elle obligatoire ? (recommandé : oui, elle couvre hébergement, domaine et SEO)
- Plafond de 1 h/mois de modifications : à confirmer.
- Acompte à la signature ou tout à la mise en ligne ?
- Combien de pages en Plus ? (la v1 du template est une page unique)

## Liens
- README : https://claude.ai/artifact/Rb8bC8JQEKxUmfuZW7nb2s
- Feuille coûts & rentabilité (encore sur l'ancienne grille 490/990/1 790 €) : https://claude.ai/artifact/WfG364p47uLk3AsARAe32U
