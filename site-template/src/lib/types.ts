export type Formule = 'base' | 'plus';

export interface Image {
  src: string;
  alt: string;
  legende?: string;
}

export interface Section {
  actif: boolean;
  menu?: string;
  titre?: string;
  intro?: string;
}

export interface Horaire {
  jour: string;
  plages: string[];
}

export interface Avis {
  auteur: string;
  note: number;
  texte: string;
  date?: string;
  exemple?: boolean;
}

export interface Evenement {
  titre: string;
  /** AAAA-MM-JJ : l'événement disparaît automatiquement le lendemain. */
  date: string;
  heure?: string;
  duree?: string;
  prix?: string;
  places?: string;
  description?: string;
  /** Inscription : lien externe (billetterie), téléphone, ou formulaire de devis du site. */
  inscription?: { type: 'lien' | 'telephone' | 'devis'; url?: string; libelle?: string };
}

export interface SiteConfig {
  slug: string;
  metier: string;
  formule: Formule;
  demo?: { actif: boolean; urlBase?: string; message?: string };
  site?: { url?: string };
  commerce: {
    nom: string;
    slogan?: string;
    adresse: { rue: string; codePostal: string; ville: string; quartier?: string };
    geo?: { lat: number; lng: number };
    telephone: string;
    email?: string;
    placeId?: string | null;
    reseaux?: { instagram?: string | null; facebook?: string | null; tiktok?: string | null };
    /** Mentions légales obligatoires du métier, affichées en pied de page (ex. loi Évin pour l'alcool). */
    avertissements?: string[];
  };
  theme: { principale: string; accent: string; fond: string; texte: string; clair: string };
  seo: { titre: string; description: string; typeSchema?: string };
  analytics?: { plausibleDomaine?: string | null; umamiId?: string | null; umamiSrc?: string | null };
  ordre: string[];
  sections: {
    accueil?: Section & { accroche?: string; image?: Image; boutonPrincipal?: string; /** Section visée par le bouton principal */ boutonCible?: string };
    apropos?: Section & { texte: string[]; pointsForts?: { titre: string; texte: string }[] };
    produits?: Section & { items: { titre: string; texte: string; image?: Image }[] };
    tarifs?: Section & { lignes: { libelle: string; prix: string; detail?: string }[]; note?: string };
    galerie?: Section & { images: Image[] };
    avis?: Section & { note: number; nombre: number; liste: Avis[] };
    horaires?: Section & { semaine: Horaire[]; note?: string };
    devis?: Section & {
      types: string[];
      formulaire?: { action?: string | null };
      merci?: string;
    };
    reservation?: Section & { fournisseur: string; url: string; texte?: string };
    evenements?: Section & {
      liste: Evenement[];
      /** Affiché quand aucun événement n'est à venir. */
      aucun?: string;
    };
    acces?: Section & { indications?: string[] };
    contact?: Section;
    [cle: string]: unknown;
  };
  mentionsLegales: {
    editeur: string;
    statut: string;
    siret: string;
    responsable: string;
    hebergeur: { nom: string; adresse: string; site: string };
  };
}
