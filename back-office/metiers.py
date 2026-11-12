"""Métiers ciblés, alignés sur docs/offre-et-prix.md (cibles par métier).

- requete : mots ajoutés à la recherche texte (« fleuriste Paris 18e »)
- type_google : includedType de Places API (New), None si aucun type fiable
- bonus : priorité commerciale (volonté de payer) utilisée dans le score
- formule : formule conseillée
"""

METIERS = {
    # Artisans : volonté de payer haute
    "Plombier": {"groupe": "Artisans", "requete": "plombier", "type_google": "plumber", "bonus": 3.0, "formule": "Plus (devis)"},
    "Électricien": {"groupe": "Artisans", "requete": "électricien", "type_google": "electrician", "bonus": 3.0, "formule": "Plus (devis)"},
    "Serrurier": {"groupe": "Artisans", "requete": "serrurier", "type_google": "locksmith", "bonus": 3.0, "formule": "Plus (devis)"},
    "Menuisier": {"groupe": "Artisans", "requete": "menuisier", "type_google": None, "bonus": 3.0, "formule": "Plus (devis)"},
    "Peintre en bâtiment": {"groupe": "Artisans", "requete": "peintre en bâtiment", "type_google": "painter", "bonus": 3.0, "formule": "Plus (devis)"},
    "Couvreur": {"groupe": "Artisans", "requete": "couvreur", "type_google": "roofing_contractor", "bonus": 3.0, "formule": "Plus (devis)"},
    # Restaurants : moyenne à haute
    "Restaurant": {"groupe": "Restaurants", "requete": "restaurant", "type_google": "restaurant", "bonus": 2.0, "formule": "Base (menu) ou Plus (réservation + anglais)"},
    # Boutiques : moyenne
    "Fleuriste": {"groupe": "Boutiques", "requete": "fleuriste", "type_google": "florist", "bonus": 1.5, "formule": "Base, ou Plus si devis"},
    "Caviste": {"groupe": "Boutiques", "requete": "caviste", "type_google": "liquor_store", "bonus": 1.5, "formule": "Base"},
    "Épicerie fine": {"groupe": "Boutiques", "requete": "épicerie fine", "type_google": None, "bonus": 1.5, "formule": "Base"},
    # Coiffeurs, barbiers, instituts : faible à moyenne
    "Coiffeur": {"groupe": "Beauté", "requete": "coiffeur", "type_google": "hair_salon", "bonus": 1.0, "formule": "Base ; Plus si Planity"},
    "Barbier": {"groupe": "Beauté", "requete": "barbier", "type_google": "barber_shop", "bonus": 1.0, "formule": "Base ; Plus si Planity"},
    "Institut de beauté": {"groupe": "Beauté", "requete": "institut de beauté", "type_google": "beauty_salon", "bonus": 1.0, "formule": "Base ; Plus si Planity"},
    # Cafés, boulangeries : faible, priorité basse
    "Boulangerie": {"groupe": "Cafés & boulangeries", "requete": "boulangerie", "type_google": "bakery", "bonus": 0.5, "formule": "Base"},
    "Café": {"groupe": "Cafés & boulangeries", "requete": "café", "type_google": "cafe", "bonus": 0.5, "formule": "Base"},
}

NOMS = list(METIERS)
