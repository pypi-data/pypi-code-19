#!/usr/bin/env python
# -*- coding: utf-8 -*-

LISTE_CODES = {
"ListeCivilite":
    {
    "1": "Monsieur",
    "2": "Madame",
    "3": "Mademoiselle"
    },
"ListeNationalite":
    {
    "1": "Française",
    "2": "Union Européenne",
    "3": "Hors union Européenne"
    },
"ListeSituationFamiliale":
    {
    "C": "Célibataire",
    "M": "Marié(e)",
    "D": "Divorcé(e)",
    "S": "Séparé(e)",
    "P": "Pacsé(e)",
    "U": "Concubin(e)",
    "V": "Veuf(ve)"
    },
"ListeLienDemandeur":
    {
    "M": "Conjoint",
    "P": "Pacsé(e)",
    "C": "Concubin(e)",
    "L": "Co-locataire"
    },
"ListeCategorieLogementRecherche":
    {
    "A": "Appartement",
    "M": "Maison",
    "I": "Indifférent"
    },
"ListeCategorieLogement":
    {
    "A": "Appartement",
    "M": "Maison"
    },
"ListeTypeLogement":
    {
    "C": "Chambre",
    "T1": "T1",
    "T2": "T2",
    "T3": "T3",
    "T4": "T4",
    "T5": "T5",
    "T6P": "T6 et plus"
    },
"ListeSexe":
    {
    "M": "Masculin",
    "F": "Féminin"
    },
"ListeLienParente":
    {
    "P": "Parent",
    "E": "Enfant",
    "A": "Autre"
    },
"ListeCoparentalite":
    {
    "G": "Garde alternée",
    "D": "Droit de visite"
    },
"ListeTypeContratTravail":
    {
    "CDI": "CDI (ou fonctionnaire)",
    "CDD": "CDD, Stage, intérim",
    "ART": "Artisan, commerçant, profession libérale",
    "CHO": "Chômage",
    "APP": "Apprenti",
    "ETU": "Etudiant",
    "RET": "Retraité",
    "AUT": "Autre"
    },
"ListeRessourceRecue":
    {
    "SAL": "Salaire ou revenu d’activité",
    "RET": "Retraite",
    "CHO": "Allocation chômage / indemnités",
    "PAR": "Pension alimentaire reçue",
    "PINV": "Pension invalidité",
    "AF": "Allocation familiales",
    "AAH": "Allocation d’adulte handicapé(AAH)",
    "AEEH": "Allocation d’éducation d’enfant handicapé (AEEH)",
    "AJPP": "Allocation journalière de présence parentale (AJPP)",
    "RSA": "Revenu de solidarité active (RSA)",
    "AMV": "Allocation de minimum vieillesse",
    "PAJE": "Allocation Jeune enfant (PAJE)",
    "BE": "Bourse étudiant",
    "AUT": "Autres (hors APL ou AL)"
    },
"ListeRessourceVersee":
    {
    "PAV": "Pension alimentaire versée"
    },
"ListeModeleLogement":
    {
    "HLM": "Logement HLM",
    "LP": "Locataire parc privé",
    "RS": "Résidence sociale ou foyer ou pension de famille",
    "RHVS": "Résidence hôtellerie à vocation sociale",
    "RE": "Résidence étudiant",
    "SLHT": "Sous-locataire ou hébergé dans un logement à titre temporaire",
    "SH": "Structure d’hébergement",
    "CDEFCM": "Centre départemental de l’enfance et de la famille ou centre maternel",
    "CPE": "Chez vos parents ou vos enfants",
    "CP": "Chez un particulier",
    "LTG": "Logé à titre gratuit",
    "FONC": "Logement de fonction",
    "POCC": "Propriétaire occupant",
    "CAMCAR": "Camping, Caravaning",
    "HOT": "Logé dans un hôtel",
    "SD": "Sans abri ou abri de fortune",
    "SQUAT": "Dans un squat"
    },
"ListeMotifDemande":
    {
    "01": "Sans logement ou hébergé ou en logement temporaire",
    "02": "Démolition",
    "03": "Logement non décent, insalubre ou dangereux ou local impropre à l’habitation "\
        "(cave, sous-sol, garage, combles, cabane...)",
    "04": "Logement repris ou mis en vente par son propriétaire",
    "05": "En procédure d’expulsion",
    "06": "Violences familiales",
    "07": "Handicap",
    "08": "Raisons de santé",
    "09": "Logement trop cher",
    "10": "Logement trop grand",
    "11": "Divorce, séparation",
    "12": "Décohabitation",
    "13": "Logement trop petit",
    "14": "Futur mariage, concubinage, PACS",
    "15": "Regroupement familial",
    "16": "Assistant(e) maternel(le) ou familiale",
    "17": "Problèmes d’environnement ou de voisinage",
    "18": "Mutation professionnelle",
    "19": "Rapprochement du lieu de travail",
    "20": "Rapprochement des équipements et services",
    "21": "Rapprochement de la famille",
    "22": "Accédant à la propriété en difficulté",
    "23": "Autre motif particulier (précisez)"
    },
"ListeEtatHandicap":
    {
    "STA": "Stabilisé",
    "EVO": "Evolutif"
    },
"ListeCapaciteMarcheHandicap":
    {
    "1": "Impossible",
    "2": "1 à 3 marches",
    "3": "1er étage",
    "4": "Plus d’un étage"
    },
"ListeNatureHandicapMoteur":
    {
    "MS": "Membre(s) supérieur(s)",
    "MI": "Membre(s) inférieur(s)"
    },
"ListeNatureHandicapSensoriel":
    {
    "DA": "Déficience auditive",
    "DV": "Déficience visuelle"
    },
"ListeAideTechniqueHandicap":
    {
    "1": "Aucune",
    "2": "Canne, Béquille",
    "3": "Déambulateur",
    "4": "Fauteuil roulant manuel",
    "5": "Fauteuil roulant électrique",
    "6": "Lève personne",
    "7": "Lit médicalisé"
    },
"ListeEquipementHandicap":
    {
    "1": "Baignoire adaptée",
    "2": "WC avec espace de transfert",
    "3": "Douche sans seuil",
    "4": "Ascenseur",
    "5": "Chambre avec une tierce personne (aide à domicile, aide soignante, veille de nuit)",
    "6": "Place de stationnement accessible et de largeur adaptée (3m30)"
    },
"ListeMotifsRadiation":
    {
    "RADABA": "Radiation pour abandon de la demande",
    "RADATT": "Radiation suite à attribution d'un logement",
    "RADIRR": "Radiation suite à irrecevabilité de la demande",
    "RADCON": "Radiation suite à impossibilité de contacter le demandeur",
    "RADREN": "Radiation pour cause de non renouvellement",
    "": "Déradiation"
    },
"ListeSousMotifRadiationIrrecevabilite":
    {
    "IRRSEJ": "Irrégularité de séjour",
    "IRRRES": "Ressources supérieures au plafond"
    },
"ListeTypeReservataire":
    {
    "COLTER": "Contingent des collectivités territoriales, de leurs établissements publics "\
        "et des EPCI",
    "COLACT": "Contingent employeurs et organismes collecteurs d'Action Logement",
    "PPRIOR": "Contingent préfet prioritaires (hors fonctionnaires et agents publics de "\
        "l'Etat)",
    "PFONCT": "Contingent préfet fonctionnaires et agents publics de l'Etat",
    "AUTRES": "Contingent autres réservataires",
    "AUCUN": "Hors contingent"
    },
"ListeZUS":
    {
    "ZUSOUI": "Oui",
    "ZUSNON": "Non",
    "ZUSNSP": "Ne sait pas"
    },
"ListeTypeFichier":
    {
    "CRE": "Création",
    "CRS": "Création suite à séparation du couple",
    "MOD": "Modification",
    "RAD": "Radiation",
    "REN": "Renouvellement",
    "SUP": "Suppression",
    "DIS": "Dispatching",
    "RET": "Retour",
    "COP": "Copie numérique"
    },
"ListeStatutDalo":
    {
    "NON": "Non",
    "ACTIF": "Actif",
    "CADUC": "Caduc",
    "ACTREL": "Actif relogé"
    },
"ListeTypologieLogementDalo":
    {
    "01": "T1",
    "02": "T2",
    "03": "T3",
    "04": "T4",
    "05": "T5",
    "06": "T6 et plus",
    "08": "Habitat individuel",
    "09": "A définir",
    "21": "T1 adapté",
    "22": "T2 adapté",
    "23": "T3 adapté",
    "24": "T4 adapté",
    "25": "T5 adapté",
    "26": "T6 et plus adapté",
    "28": "Habitat individuel adapté",
    "30": "Réorientation hébergement",
    "31": "A définir adapté",
    "99": "Autre",
    "40": "T1-T2",
    "41": "T2-T3",
    "42": "T3-T4",
    "43": "T4-T5",
    "44": "T5-T6",
    "45": "T1-T2 adapté",
    "46": "T2-T3 adapté",
    "47": "T3-T4 adapté",
    "48": "T4-T5 adapté",
    "49": "T5-T6 adapté",
    "50": "Sous-location"
    },
"ListeTypeLogementRPLS":
    {
    "T1": "1 pièce principale",
    "T2": "2 pièces principales",
    "T3": "3 pièces principales",
    "T4": "4 pièces principales",
    "T5": "5 pièces principales",
    "T6": "6 pièces principales",
    "T7": "7 pièces principales",
    "T8": "8 pièces principales",
    "T9P": "9 pièces principales et plus"
    },
"ListeBooleen":
    {
    "OUI": "Oui",
    "NON": "Non",
    "NONDOC": "Non renseigné"
    },
"ListeAccordCollectif":
    {
    "ACD": "Accord collectif départemental",
    "ACI": "Accord collectif intercommunal",
    "AUCUN": "Aucun",
    "NONDOC": "Non renseigné"
    }
}
