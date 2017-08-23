#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
=====
libsne
=====
Librairie gérant les échanges synchrones avec le Système National
d'Enregistrement (SNE) des demandes de logements sociaux.
--------

4 classes la composent:

GestionDemande
    Cette classe permet de récupérer une demande de logement social sous forme
    de chaîne de caractères représentant le fichier XML. Elle s'occupe aussi
    de vérifier que le XML est bien formé et valide. Si c'est le cas, elle
    stocke la demande sous forme d'élément lxml. Sinon, si l'erreur provient
    de la librairie lxml (l'arbre XML est mal formé), l'exception est propagée
    et l'utilisateur voit directement cette erreur. Sinon l'erreur provient de
    la librairie SNE (l'arbre XML n'est pas valide, c'est-à-dire que les
    balises obligatoires ne contiennent pas de données), l'exception est
    construite par la librairie SNE et est levée.
ConstructionMessage
    Cette classe gère la construction du message XOP/MTOM à envoyer au serveur
    SNE. Étant donné qu'aucune librairie Python parmi celles que j'ai étudiées
    n'était compatible avec les exigences exposées dans le cahier des charges
    du SNE, la construction des messages envoyés vers SNE se fait à la main,
    grâce notamment à la librairie jinja2.
ConnexionServeur
    Cette classe met en place la connexion HTTPS avec le serveur SNE. Une
    seule méthode statique la compose, https, qui prend en entrée le nom du
    service web du serveur SNE, le nom du fichier contenant la chaîne de
    certificats et le nom du fichier contenant la clé privée, et retourne la
    réponse du serveur au format httplib.HTTPResponse. Elle utilise aussi une
    constante définie au début de la librairie, représentant le nom d'hôte et
    le port du serveur SNE. C'est la classe httplib.HTTPSConnection qui est
    utilisée pour mettre en place la connexion avec le serveur.
AnalyseReponse
    Cette classe analyse la réponse du serveur SNE et effectue les actions
    adéquates. Elle est instanciée grâce au nom du service web du serveur SNE,
    ainsi que la réponse du serveur, qui sont attributs de classe. La méthode
    anomalies effectue l'analyse en tant que telle en testant si la réponse du
    serveur SNE contient des anomalies. Si tel est le cas, elle raise une
    exception correspondant à l'anomalie en question avec le message
    d'excpetion dans un format lisible. Si aucune anomalie se trouve dans la
    réponse du serveur, à la valeur de l'attribut demande de la classe est
    attribuée cette réponse.
"""

import os
import sys
import time

from jinja2 import Template
from lxml import etree
import six
import six.moves.http_client as httplib

import Constantes



BOUNDARIES = "MIME_BOUNDARY"
LISTE_SERVICES_DISPONIBLES = [
    "declarationNouveauDalo", "demandeLogement", "demandesRadieesDepuisLe",
    "doublons", "nouveauxDaloDepuisLe", "numUnique"
]
PREFIXE_BALISES = "http://nuu.application.i2/"
SOAP_ROOT = "soaproot"

HOSTNAME = "nuu-ws.ecole.application.developpement-durable.gouv.fr"
PORT = "443"
XSD = os.path.dirname(
    os.path.abspath(__file__)
) + "/../ressources/InterfaceNuu_v0201.xsd"





class GestionDemande:
    """
    | Récupère la demande et permet le formatage XML.
    | Seule la récupération via une chaîne de caractères représentant le
      fichier XML est possible pour le moment.
    | **Améliorations bienvenues** :)
    """

    def __init__(self, xml=None):
        """
        | Constructeur de la classe GestionDemande.
        | Instancie le parser à partir de la constante XSD et set l'attribut
          interface_nuu si le xml est donné en entrée.

        Entrée:

        xml
            Chaîne de caractères représentant le XML de la demande.
            Attribut optionnellement initialisé à l'instanciation de la classe.
            Si cet attribut n'est pas donné ici, sa valeur devra
            obligatoirement être attribuée plus tard via la méthode
            set_interface_nuu (objet lxml.etree) ou remplir_interface_nuu_xml
            (chaîne de caractères représentant le XML).
        """
        self.parser = etree.XMLParser(schema=etree.XMLSchema(etree.parse(XSD)))
        if xml:
            self.verifier_infos_demande(etree.fromstring(xml))
            self.interface_nuu = etree.fromstring(xml, self.parser)



    @staticmethod
    def _formater_tns(template):
        """
        | Méthode privée statique permettant de rajouter le préfixe tns aux
          balises xml.
        | Cette méthode est appelée par _remplir_attributs_none et
          _verifier_attributs_obligatoires_set.

        Entrée:

        template
            Chaîne de caractères représentant un ou plusieurs balise(s) XML au
            format lxml.etree composée(s) de {} en lieu et place du préfixe
            des balises SNE.

        Sortie:
            Chaîne de caractères avec les préfixes au niveau des balises XML.
        """
        return template.replace("{}", "{{{0}}}").format(PREFIXE_BALISES)



    def set_interface_nuu(self, interface_nuu): # pragma: no cover
        """
        | Setter de l'attribut interface SNE.
        | L'argument en entrée est au format ``lxml.etree``.
        | La vérification du parser est automatiquement faite.
        """
        self.verifier_infos_demande(interface_nuu)
        self.interface_nuu = etree.fromstring(
            interface_nuu.toxml(), self.parser
        )



    def get_interface_nuu(self): # pragma: no cover
        """
        Getter de l'attribut interface SNE.
        """
        return self.interface_nuu



    def _remplir_attributs_none(self, interface_nuu):
        """
        | Méthode privée retournant l'ensemble des attributs obligatoires dont
          la valeur est None.
        | Cette méthode est appelée par _verifier_attributs_obligatoires_set.
        | Elle est basée sur le cahier des charges des interfaces SNE.

        Entrée:

        interface_nuu
            Objet ``lxml.etree`` représentant la structure XML de la demande.

        Sortie:
            Tableau des noms des attributs dont la valeur est None sous formes
            de chaînes de caractères.
        """
        ensemble_attributs_none = []

        #versionInterface
        if ("versionInterface" not in interface_nuu.attrib\
            or interface_nuu.attrib["versionInterface"] != "02.00"\
            and interface_nuu.attrib["versionInterface"] != "02.01"):
            ensemble_attributs_none.append("versionInterface")

        #typeFichier
        if interface_nuu.find(
            self._formater_tns("{}entete/{}typeFichier")
        ) is None or interface_nuu.findtext(
            self._formater_tns("{}entete/{}typeFichier")
        ) not in six.iterkeys(Constantes.LISTE_CODES["ListeTypeFichier"]):
            ensemble_attributs_none.append("typeFichier")

        #dateFichier
        if interface_nuu.find(
            self._formater_tns("{}entete/{}dateFichier")
        ) is None or interface_nuu.findtext(
            self._formater_tns("{}entete/{}dateFichier")
        ) in ["None", ""]:
            ensemble_attributs_none.append("dateFichier")

        #numGuichet
        if interface_nuu.find(
            self._formater_tns("{}demande/{}demandeLogement/{}numGuichet")
        ) is None or interface_nuu.findtext(
            self._formater_tns("{}demande/{}demandeLogement/{}numGuichet")
        ) in ["None", ""]:
            ensemble_attributs_none.append("numGuichet")

        #dateCreationDemande
        if interface_nuu.find(self._formater_tns(
            "{}demande/{}demandeLogement/{}dateCreationDemande"
        )) is None or interface_nuu.findtext(self._formater_tns(
            "{}demande/{}demandeLogement/{}dateCreationDemande"
        )) in ["None", ""]:
            ensemble_attributs_none.append("dateCreationDemande")

        #demandeElargie
        if interface_nuu.find(self._formater_tns(
            "{}demande/{}demandeLogement/{}logementRecherche/"
            "{}demandeElargie"
        )) is None or interface_nuu.findtext(self._formater_tns(
            "{}demande/{}demandeLogement/{}logementRecherche/"
            "{}demandeElargie"
        )) not in ["true", "false"]:
            ensemble_attributs_none.append("demandeElargie")

        #typeLogement
        if len(interface_nuu.findall(self._formater_tns(
            "{}demande/{}demandeLogement/{}logementRecherche/"
            "{}listeTypeLogement/{}typeLogement"
        ))) < 1:
            ensemble_attributs_none.append("typeLogement")
        else:
            for element in interface_nuu.findall(self._formater_tns(
                "{}demande/{}demandeLogement/{}logementRecherche/"
                "{}listeTypeLogement/{}typeLogement"
            )):
                if "code" not in element.attrib\
                    or element.attrib["code"] not in six.iterkeys(
                        Constantes.LISTE_CODES["ListeTypeLogement"]
                    ):
                    ensemble_attributs_none.append("typeLogement")
                    break

        #commune
        for element in interface_nuu.findall(self._formater_tns(
            "{}demande/{}demandeLogement/{}logementRecherche/"
            "{}listeLocalisationSouhaite/{}localisationSouhaite"
        )):
            if element.find(
                self._formater_tns("{}commune")
            ) is None or "code" not in element.find(
                self._formater_tns("{}commune")
            ).attrib or not element.find(
                self._formater_tns("{}commune")
            ).attrib["code"].isdigit():
                ensemble_attributs_none.append("commune")
                break

        return ensemble_attributs_none



    def _verifier_attributs_obligatoires_set(self, interface_nuu):
        """
        | Méthode privée vérifiant que l'ensemble des attributs obligatoires
          du XML sont bien définis : bien présents et ont une valeur.
        | Cette méthode est appelée par verifier_infos_demande.

        Entrée:

        interface_nuu
            Arbre ``lxml.etree`` représentant le XML.

        Sortie:
            Tableau contenant les attributs obligatoires qui ne sont pas
            définis.
        """
        if not isinstance(interface_nuu, type(etree.Element("racine")))\
            or self._formater_tns("{}interfaceNuu") != interface_nuu.tag:
            raise TypeError(
                "L'entrée donnée n'est pas un arbre xml contenant comme "
                "racine 'tns:interfaceNuu' (avec tns="
                "\"http://nuu.application.i2/\")."
            )

        elif interface_nuu.find(
            self._formater_tns("{}entete")
        ) is None or not isinstance(
            interface_nuu.find(self._formater_tns("{}entete")),
            type(etree.Element("racine"))
        ) or interface_nuu.find(
            self._formater_tns("{}demande")
        ) is None or not isinstance(
            interface_nuu.find(self._formater_tns("{}demande")),
            type(etree.Element("racine"))
        ):
            raise Exception(
                "L'interface doit contenir une entête et une demande."
            )

        elif interface_nuu.find(
            self._formater_tns("{}demande/{}demandeLogement")
        ) is None or interface_nuu.find(self._formater_tns(
            "{}demande/{}demandeLogement/{}logementRecherche"
        )) is None or interface_nuu.find(self._formater_tns(
            "{}demande/{}demandeLogement/{}logementRecherche/"
            "{}listeTypeLogement"
        )) is None or interface_nuu.find(self._formater_tns(
            "{}demande/{}demandeLogement/{}logementRecherche/"
            "{}listeLocalisationSouhaite"
        )) is None or len(interface_nuu.findall(self._formater_tns(
            "{}demande/{}demandeLogement/{}logementRecherche/"
            "{}listeLocalisationSouhaite/{}localisationSouhaite"
        ))) < 1:
            raise Exception(
                "La demande doit contenir une demande de logement, lui-même "
                "contenant un logement recherché, contenant une liste de "
                "types de logement et une liste de localisation souhaitées, "
                "lui-même contenant un attribut localisationSouhaite. "
                "Exemple :\n" + """{
"interface_nuu":{
    "versionInterface": None,
    "xmlns": "http://nuu.application.i2/",
    "entete":{
        "typeFichier": None,
        "dateFichier": None
        },
    "demande":{
        "demandeLogement":{
            "numGuichet": None,
            "dateCreationDemande": None,
            "logementRecherche":{
                "demandeElargie": None,
                "listeTypeLogement":{
                    "typeLogement": [None]
                    },
                "listeLocalisationSouhaite":{
                    "localisationSouhaite":[{"commune": None}]
                    }
                }
            }
        }
    }
}""")
        else:
            return self._remplir_attributs_none(interface_nuu)



    def verifier_infos_demande(self, interface_nuu):
        """
        | Méthode vérifiant que la demande contient les bonnes informations :
          s'il en manque, si le format est bon, ...
        | Appelle la méthode _verifier_attributs_obligatoires_set. Si le
          tableau renvoyé par cette méthode n'est pas vide, lève une
          exception, sinon ne fait rien.

        Entrée:

        interface_nuu
            Arbre ``lxml.etree`` représentant le XML.
        """
        ensemble_attributs_none = self._verifier_attributs_obligatoires_set(
            interface_nuu
        )
        if ensemble_attributs_none:
            raise Exception(
                "Certains attributs doivent être définis obligatoirement "
                "quelle que soit la demande : " + str(ensemble_attributs_none)
            )



    def export_xml(self):
        """
        Méthode exportant l'attribut XML de la demande en une chaîne de
        caractères.
        """
        return etree.tostring(self.interface_nuu)



    def remplir_interface_nuu_xml(self, xml):
        """
        | Méthode effectuant le remplissage de l'objet XML en récupérant les
          données d'une demande de logement en format xml.
        | La vérification du parser est automatiquement faite.

        Entrée:

        xml
            XML sous forme de chaîne de caractères.
        """
        self.verifier_infos_demande(etree.fromstring(xml))
        self.interface_nuu = etree.fromstring(xml, self.parser)





class ConstructionMessage:
    """
    | Gère la construction du message XOP/MTOM à envoyer au serveur SNE.
    | Les templates mériteraient un petit nettoyage car ils ne sont pas très
      faciles à lire... Attention tout de même à bien garder les contraintes
      exigeantes et peu logiques ni explicites de SNE dans le SOAP et le XML
      (certaines balises doivent obligatoirement se trouver à la suite ou à la
      ligne de la précédente par exemple).
    """
    def __init__(self):
        pass



    @staticmethod
    def _message_xopmtom(liste_contenus):
        """
        | Méthode privée statique construisant le squelette du message
          XOP/MTOM.
        | Cette méthode est appelée par get_message_xopmtom.

        Entrée:

        liste_contenus
            La liste des contenus à intégrer au message XOP/MTOM. Les valeurs
            possibles sont "cert" et "xml".

        Sortie:
            Chaine de caractères représentant le message XOP/MTOM templaté.
        """
        if not isinstance(liste_contenus, type([])):
            raise TypeError("La liste de contenus doit être un tableau.")

        message_xopmtom = ("""--{{ boundary }}
Content-Type: application/xop+xml; charset=UTF-8; """
"""type="application/soap+xml"; action="get{{ service }}"
Content-Transfer-Encoding: 8bit
Content-ID: <{{ soaproot }}>

{{ soap }}
""")
        for contenu in liste_contenus:
            if contenu == "cert":
                message_xopmtom += """--{{ boundary }}
Content-Type: application/octet-stream
Content-ID: <{{ cert_id }}>
Content-Transfer-Encoding: BASE64
Content-Disposition: attachment

{{ cert }}
"""
            elif contenu == "xml":
                message_xopmtom += """--{{ boundary }}
Content-Type: text/xml; charset=us-ascii
Content-Transfer-Encoding: 7bit
Content-ID: <{{ xml_id }}>
Content-Disposition: attachment; name="{{ xml_id }}"

{{ xml }}
"""
            else:
                raise Exception(
                    "Le contenu du message doit être un XML ou un certificat."
                )

        return message_xopmtom + """--{{ boundary }}--"""



    @staticmethod
    def _message_soap(liste_contenus):
        """
        | Méthode privée statique construisant le squelette du message SOAP.
        | Cette méthode est appelée par get_message_soap.

        Entrée:

        liste_contenus
            La liste des contenus à intégrer au message XOP/MTOM. Les valeurs
            possibles sont "fichierDemande", "certificat", "numUnique",
            "dateNouveauDaloDepuisLe" et "dateRadiationDepuisLe".

        Sortie:
            Chaine de caractères représentant le squelette du message SOAP.
        """
        if not isinstance(liste_contenus, type([])):
            raise TypeError("La liste de contenus doit être un tableau.")

        parametres = ""
        for contenu in liste_contenus:
            if contenu == "fichierDemande":
                #Attention à bien laisser la balise xop:Include sur la même
                #ligne que la balise fichierDemande !
                parametres += ("""      <nomFichierDemande>"""
                    """DEMG1226-{{ date_maintenant }}-000000.xml"""
                    """</nomFichierDemande>
      <fichierDemande ws:contentType="text/xml"><xop:Include """
        """href="cid:{{ xml_id }}" """
        """xmlns:xop="http://www.w3.org/2004/08/xop/include"/></fichierDemande>
""")
            elif contenu == "certificat":
                parametres += ("""      <nomCertificat>"""
                    """CERG1226-{{ date_maintenant }}.pem"""
                    """</nomCertificat>
      <certificat ws:contentType="application/x-x509-ca-cert"><xop:Include """
        """href="cid:{{ certificate }}" """
        """xmlns:xop="http://www.w3.org/2004/08/xop/include"/></certificat>
""")
            elif contenu == "numUnique":
                parametres += """      <numUnique>{{ num_unique }}</numUnique>
"""
            elif contenu == "dateNouveauDaloDepuisLe":
                parametres += ("""      <dateNouveauDaloDepuisLe>"""
                    """{{ date }}"""
                    """</dateNouveauDaloDepuisLe>
""")
            elif contenu == "dateRadiationDepuisLe":
                parametres += ("""      <dateRadiationDepuisLe>"""
                    """{{ date }}"""
                    """</dateRadiationDepuisLe>
""")
            else:
                raise Exception("Les paramètres SOAP fournis sont incorrects.")

        return parametres



    @staticmethod
    def get_message_xml(interface_nuu):
        """
        | Méthode statique créant le template XML à partie d'un objet
          ``lxml.etree``.
        | Cette méthode est appelée par get_message_soap.

        Entrée:

        interface_nuu
            Arbre au format lxml etree.

        Sortie:
            Chaine de caractères représentant le message XML.
        """
        message_xml = etree.tostring(interface_nuu)
        if sys.version_info[0] == 3:
            message_xml = message_xml.decode()
        return message_xml



    def get_message_xopmtom(self, cert, service, **kwargs):
        """
        | Méthode principale de la classe. C'est cette méthode qui doit être
          appelée de l'extérieur si l'on veut construire un message XOP/MTOM
          complet.

        Cette méthode utilise quelques constantes du module :
        :SOAP_ROOT:
            Chaine de caractères (censée être unique) qui sera le nom de
            la racine SOAP dans le message XOP/MTOM (voir
            https://www.w3.org/Submission/soap11mtom10/#serialization).
        :BOUNDARIES:
            Chaine de caractères (censée être unique) qui sera ajoutée aux
            frontières de chaque partie du message XOP/MTOM (voir
            https://www.w3.org/Protocols/rfc1341/7_2_Multipart.html)

        Entrées:

        cert
            Le certificat de chiffrement à intégrer au message (Peut être une
            chaîne vide).
        service
            Le nom du service web du message XOP/MTOM pour le serveur SNE.
        kwargs
            Arguments variables en fonction du service:

            interface_nuu ("numUnique" et "doublons")
                Objet lxml.etree représentant le fichier XML de la demande.
            num_unique ("demandeLogement")
                Numéro unique SNE
            date ("nouveauxDaloDepuisLe" et "demandesRadieesDepuisLe")
                Date paramètre du service

        Sortie:
            Chaine de caractères représentant le message XOP/MTOM à envoyer au
            serveur SNE.
        """

        content_id = "certificate"
        xml_id = "xml_id"

        if service == "numUnique":
            message_xopmtom = self._message_xopmtom(["cert", "xml"])
            return Template(message_xopmtom).render(
                boundary=BOUNDARIES,
                service=service[0].upper() + service[1:],
                soaproot=SOAP_ROOT,
                soap=self.get_message_soap(
                    service, content_id, xml_id, **kwargs
                ),
                cert_id=content_id,
                cert=cert,
                xml_id=xml_id,
                xml=self.get_message_xml(kwargs["interface_nuu"])
            )

        elif service == "demandeLogement":
            message_xopmtom = self._message_xopmtom(["cert"])
            return Template(message_xopmtom).render(
                boundary=BOUNDARIES,
                service=service[0].upper() + service[1:],
                soaproot=SOAP_ROOT,
                soap=self.get_message_soap(
                    service, content_id, xml_id, **kwargs
                ),
                cert_id=content_id,
                cert=cert,
                xml_id=xml_id
            )

        elif service == "doublons":
            message_xopmtom = self._message_xopmtom(["xml"])
            return Template(message_xopmtom).render(
                boundary=BOUNDARIES,
                service=service[0].upper() + service[1:],
                soaproot=SOAP_ROOT,
                soap=self.get_message_soap(
                    service, content_id, xml_id, **kwargs
                ),
                cert_id=content_id,
                cert=cert,
                xml_id=xml_id,
                xml=self.get_message_xml(kwargs["interface_nuu"])
            )

        elif service == "nouveauxDaloDepuisLe"\
            or service == "demandesRadieesDepuisLe":
            message_xopmtom = self._message_xopmtom(["cert"])
            return Template(message_xopmtom).render(
                boundary=BOUNDARIES,
                service=service[0].upper() + service[1:],
                soaproot=SOAP_ROOT,
                soap=self.get_message_soap(
                    service, content_id, xml_id, **kwargs
                ),
                cert_id=content_id,
                cert=cert,
                xml_id=xml_id
            )



    def get_message_soap(self, service, content_id, xml_id, **kwargs):
        """
        | Méthode créant et complètant le message SOAP.
        | Cette méthode est appelée par get_message_xopmtom.
        | Pour les cids, voir
          http://stackoverflow.com/questions/215741/how-does-mtom-work
          ou https://www.w3.org/Submission/soap11mtom10/#example.

        Entrées:

        service
            Le nom du service web du message pour le serveur SNE.
        content_id
            cid permettant de pointer vers le contenu du message XML dans le
            message XOP/MTOM.
        xml_id
            cid permettant de pointer vers le certificat de chiffrement dans
            le message XOP/MTOM.

        Sortie :
            Chaine de caractères représentant le message SOAP à intégrer au
            message XOP/MTOM.
        """
        soap = ("""<soap:Envelope """
        """xmlns:soap="http://www.w3.org/2003/05/soap-envelope" """
        """xmlns:ws="http://ws.metier.nuu.application.i2/">
  <soap:Header/>
  <soap:Body>
    {{ body }}
  </soap:Body>
</soap:Envelope>""")

        if service == "numUnique":
            body = "<ws:numUniqueParametres>\n"\
                + self._message_soap(["fichierDemande", "certificat"])\
                + "    </ws:numUniqueParametres>"
        elif service == "demandeLogement":
            body = "<ws:demandeLogementParametres>\n"\
                + self._message_soap(["numUnique", "certificat"])\
                + "    </ws:demandeLogementParametres>"
        elif service == "doublons":
            body = "<ws:rechercheDoublonsParametres>\n"\
                + self._message_soap(["fichierDemande"])\
                + "    </ws:rechercheDoublonsParametres>"
        elif service == "nouveauxDaloDepuisLe":
            body = "<ws:nouveauxDaloDepuisLeParametres>\n"\
                + self._message_soap(
                    ["dateNouveauDaloDepuisLe", "certificat"]
                ) + "    </ws:nouveauxDaloDepuisLeParametres>"
        elif service == "demandesRadieesDepuisLe":
            body = "<ws:demandesRadieesDepuisLeParametres>\n"\
                + self._message_soap(["dateRadiationDepuisLe", "certificat"])\
                + "    </ws:demandesRadieesDepuisLeParametres>"

        return Template(soap).render(
            body=Template(body).render(
                date_maintenant=time.strftime("%Y%m%d%H%M"),
                xml_id=xml_id,
                certificate=content_id,
                num_unique=kwargs.get("num_unique", None),
                date=kwargs.get("date", None)
            )
        )





class ConnexionServeur:
    """
    Met en place la connexion HTTPS avec le serveur SNE.
    """
    def __init__(self):
        pass

    @staticmethod
    def https(service, cert_file, key_file, hostname, **kwargs):
        """
        | Méthode statique permettant d'échanger avec l'application SNE.
        | Cette méthode est la méthode principale du module, car c'est elle
          qui effectue l'interfaçage désiré avec SNE.

        Entrées:

        service
            Le nom du service à interroger.
        cert_file
            Le chemin vers le fichier contenant la chaîne publique de
            certification.
        key_file
            Le chemin vers le fichier contenant la clé privée de certification.
        hostname
            Le nom d'hôte du serveur SNE. Doit se trouver dans le fichier de
            configuration (sinon, en constante au début du module).
        kwargs
            Arguments variables en fonction du service:

            xml
                Pour les services "getNumUnique" et "getDoublons", chaîne de
                caractères représentant le XML de la demande.
            num_unique
                Pour le service "getDemandeLogement", numéro unique SNE de la
                demande de logement.
            date
                Pour les services "getNouveauxDaloDepuisLe" et
                "getDemandesRadieesDepuisLe", date paramètre du service.

        Sortie:
            Réponse du serveur SNE au format HTTPResponse.
        """

        if service in ["numUnique", "doublons"]:
            if "xml" not in kwargs:
                raise TypeError(
                    "L'argument 'xml' doit être fourni dans les kwargs."
                )
            gestion_demande = GestionDemande(kwargs["xml"])
            construction_message = ConstructionMessage()
            message_xopmtom = construction_message.get_message_xopmtom(
                "",
                service,
                interface_nuu=gestion_demande.get_interface_nuu()
            ).replace("\n", "\r\n")
        elif service == "demandeLogement":
            if "num_unique" not in kwargs:
                raise TypeError(
                    "L'argument 'num_unique' doit être fourni dans les kwargs."
                )
            construction_message = ConstructionMessage()
            message_xopmtom = construction_message.get_message_xopmtom(
                "",
                service,
                num_unique=kwargs["num_unique"]
            ).replace("\n", "\r\n")
        elif service in ["demandesRadieesDepuisLe", "nouveauxDaloDepuisLe"]:
            if "date" not in kwargs:
                raise TypeError(
                    "L'argument 'date' doit être fourni dans les kwargs."
                )
            construction_message = ConstructionMessage()
            message_xopmtom = construction_message.get_message_xopmtom(
                "",
                service,
                date=kwargs["date"]
            ).replace("\n", "\r\n")

        connexion = httplib.HTTPSConnection(
            hostname, cert_file=cert_file, key_file=key_file
        )

        headers = {
            "MIME-Version": "1.0",
            "Accept-Encoding": "deflate",
            "Content-Type":
                ('multipart/related; type="application/xop+xml"; start="%s"; '
                'start-info="application/soap+xml"; boundary="%s"; '
                'action="http://ws.metier.nuu.application.i2/get%s"')\
                % (SOAP_ROOT, BOUNDARIES, service[0].upper() + service[1:]),
            "Host": "nuu-ws.ecole.application.developpement-durable.gouv.fr",
            "Connection": "Keep-Alive",
            "User-Agent": "Apache-HttpClient/4.1.1 (java 1.5)"
        }

        connexion.request(
            'POST',
            "/services/DemandeLogementImplService/",
            body=message_xopmtom,
            headers=headers
        )

        return connexion.getresponse()







class AnomaliesException(Exception):
    """
    | Exception générique pour les anomalies provenant de la réponse du serveur
      SNE.
    | Cette exception ne doit pas être levée mais doit être héritée par
      d'autres exceptions qui seront elles levées.
    """

    def __init__(self, message):
        """
        | Constructeur de l'exception.
        | Appelle le super et set l'attribut message.
        """

        super(AnomaliesException, self).__init__(message)
        self.message = message



class ErreurInattendueTraitementReponse(AnomaliesException):
    """
    Exception levée si la réponse du serveur SNE contient le message "Une
    erreur inattendue est survenue lors du traitement de la demande.".
    """

    def __init__(self, service):
        """
        | Constructeur de l'exception.
        | Appelle le super et set l'attribut message selon le service.

        Entrée:

        service
            Le nom du service SNE qui permet de construire le message d'erreur.
        """

        if service == "doublons":
            message = ("Le serveur SNE a renvoyé l'erreur : 'Une erreur "
            "inattendue est survenue lors du traitement de la demande.'\n"
            "Cette erreur connue est due au serveur SNE et apparaît lorsque "
            "que la recherche de doublon concerne une association.\nSi tel "
            "est le cas, veuillez effectuer une recherche de doublon sur une "
            "personne physique.\nSinon, il s'agit probablement d'une erreur "
            "dans la structure XML.")
        else:
            message = ("Le serveur SNE a renvoyé l'erreur : 'Une erreur "
            "inattendue est survenue lors du traitement de la demande.'\nIl "
            "s'agit probablement d'une erreur dans la structure XML ou dans "
            "la librairie libsne.")
        super(ErreurInattendueTraitementReponse, self).__init__(message)
        self.message = message



class AnomaliesDansReponse(AnomaliesException):
    """
    | Exception levée si la réponse du serveur SNE contient des anomalies.
    | Celles-ci sont affichées dans le message de l'exception.
    """

    def __init__(self, reponse_xml):
        """
        | Constructeur de l'exception.
        | Appelle le super et set l'attribut message selon les anomalies
          renvoyées par le serveur SNE.

        Entrée:

        reponse_xml
            La réponse du serveur SNE contenant les anomalies.
        """

        message = ("Des anomalies ont été détectées par le serveur SNE :\n"
            "++++++++++++++++++++++Anomalies++++++++++++++++++++++++++")
        for anomalie in reponse_xml.find(
            ("{http://nuu.application.i2/}demande/"
            "{http://nuu.application.i2/}demandeLogement/"
            "{http://nuu.application.i2/}listeAnomalie")
        ).getchildren():
            unicode_str = anomalie.getchildren()[0].text
            if sys.version_info[0] == 2:
                unicode_str = unicode_str.encode("utf-8")
            message += "\n" + anomalie.attrib["code"] + " : " + unicode_str
        message += """
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++
"""
        super(AnomaliesDansReponse, self).__init__(message)
        self.message = message





class AnalyseReponse:
    """
    Analyse la réponse de l'application SNE et effectue les actions adéquates.
    """

    def __init__(self, service, reponse=None):
        """
        | Constructeur de la classe.
        | Set l'attribut reponse selon sa valeur en entrée.

        Entrées:

        service
            Nom du service web pour le serveur SNE.
        reponse
            Objet HTTPResponse représentant la réponse du serveur SNE. Défaut
            None. L'attribut final sera une chaîne de caractères représentant
            le contenu de la réponse.
        """
        if reponse is None or isinstance(reponse, type("")):
            self.reponse = reponse
        elif isinstance(reponse, httplib.HTTPResponse):# pragma: no cover
            self.reponse = reponse.read()
            if sys.version_info[0] == 3:
                self.reponse = self.reponse.decode()
        else:
            raise TypeError("La réponse n'est pas du bon type.")
        self.service = service
        self.demande = None



    def get_service(self): # pragma: no cover
        """
        Getter sur l'attribut service.
        """
        return self.service



    def set_service(self, service): # pragma: no cover
        """
        Setter sur l'attribut service.
        """
        self.service = service



    def get_demande(self): # pragma: no cover
        """
        Getter sur l'attribut demande.
        """
        return self.demande



    def set_demande(self, demande): # pragma: no cover
        """
        Setter sur l'attribut demande.
        """
        self.demande = demande



    def get_reponse(self): # pragma: no cover
        """
        Getter sur l'attribut reponse.
        """
        return self.reponse



    def set_reponse(self, reponse):
        """
        Setter sur l'attribut reponse selon sa valeur en entrée.
        """
        if isinstance(reponse, type("")):# pragma: no cover
            self.reponse = reponse
        elif isinstance(reponse, httplib.HTTPResponse):# pragma: no cover
            self.reponse = reponse.read()
            if sys.version_info[0] == 3:
                self.reponse = self.reponse.decode()
        else:
            raise TypeError("La réponse n'est pas du bon type.")



    def anomalies(self):
        """
        | Méthode testant si la réponse du serveur SNE contient des anomalies.
        | Si tel est le cas, raise une AnomaliesException contenant les
          anomalies dans un format lisible.
        | Il est possible que ce qui est écrit ne corresponde pas à ce qui est
          attendu en termes d'anomalies. Il s'agit dans ce cas d'erreur
          retournée par le serveur dans l'enveloppe SOAP.
        | S'il n'y a pas d'anomalie, la valeur de l'attribut demande devient le
          contenu de la réponse du serveur SNE.
        """
        if ("Une erreur inattendue est survenue lors du traitement de la "
            "demande.") in self.reponse:
            raise ErreurInattendueTraitementReponse(self.get_service())
        try:
            if self.service == "doublons":
                contenu_xml = self.reponse[
                    self.reponse.find(
                        ":listeDoublons"
                    )-4:self.reponse.find(
                        ":listeDoublons>"
                    )
                ] + ":listeDoublons>"
            else:
                contenu_xml = self.reponse[
                    self.reponse.find(
                        ":interfaceNuu"
                    )-4:self.reponse.find(
                        ":interfaceNuu>"
                    )
                ] + ":interfaceNuu>"
            reponse_xml = etree.fromstring(contenu_xml)
            if reponse_xml.find(
                ("{http://nuu.application.i2/}demande/"
                "{http://nuu.application.i2/}demandeLogement/"
                "{http://nuu.application.i2/}listeAnomalie")
            ) is not None:
                raise AnomaliesDansReponse(reponse_xml)
            else:
                self.set_demande(contenu_xml)

        except etree.XMLSyntaxError as xmlse:
            raise Exception(
                "XMLSyntaxError: " + str(xmlse)\
                + "\n\nRéponse serveur : \n" + self.reponse
            )





def echanger(
    service, cert_file, key_file, hostname=":".join([HOSTNAME, PORT]), **kwargs
):
    """
    | Fonction principale de la librairie. Permet de gérer les échanges SNE.
    | Les services getNouveauxDaloDepuisLe et getDemandesRadieesDepuisLe ne
      fonctionnent pas car le serveur renvoie l'erreur "Le nom du certificat
      associé [] n’est pas conforme." bien que ce soit le même nom utilisé
      pour les autres services...

    Entrées:

    service
        Nom du service web pour le serveur SNE.
    cert_file
        Le chemin vers le fichier contenant la chaîne publique de
        certification.
    key_file
        Le chemin vers le fichier contenant la clé privée de certification.
    hostname
        Le nom d'hôte du serveur SNE. Défaut aux valeurs du nom d'hôte et du
        port définies en constante.
    kwargs
            Arguments variables en fonction du service:

            xml
                Pour les services "getNumUnique" et "getDoublons", chaîne de
                caractères représentant le XML de la demande.
            num_unique
                Pour le service "getDemandeLogement", numéro unique SNE de la
                demande de logement.
            date
                Pour les services "getNouveauxDaloDepuisLe" et
                "getDemandesRadieesDepuisLe", date paramètre du service.

    Sortie:
        Chaîne de caractères représentant la réponse XML du serveur si aucune
        erreur et aucune anomalie n'est apparue, lève une exception sinon.
    """
    if service not in LISTE_SERVICES_DISPONIBLES:
        raise NameError(
            ("Erreur sur le nom du service : le nom du service donné n'est pas"
            " conforme. Les services disponibles sont ")
            + str(LISTE_SERVICES_DISPONIBLES)
        )
    elif service == "declarationNouveauDalo":
        raise NotImplementedError(
            "Erreur sur le nom du service : ce service n'est pas implémenté."
        )
    elif service == "demandeLogement" and "num_unique" not in kwargs:
        raise IOError(
            ("Si le service est 'demandeLogement', il faut founir le numéro "
            "unique SNE (argument 'numUnique').")
        )
    elif service in ["numUnique", "doublons"] and "xml" not in kwargs:
        raise IOError(
            ("Si le service est 'numUnique' ou 'doublons', il faut founir une "
            "chaîne de caractères représentant le XML (argument 'xml').")
        )
    elif service in [
        "nouveauxDaloDepuisLe", "demandesRadieesDepuisLe"
    ] and "date" not in kwargs:
        raise IOError(
            ("Si le service est 'nouveauxDaloDepuisLe' ou "
            "'demandesRadieesDepuisLe', il faut founir une date (format "
            "'aaaa-mm-jjTHH:MM:SS.s+hh:mm' (décalage par rapport à UTC)) "
            "(argument 'date').")
        )
    else:
        analyse_reponse = AnalyseReponse(
            service, ConnexionServeur.https(
                service, cert_file, key_file, hostname, **kwargs
            )
        )
        analyse_reponse.anomalies()
        return analyse_reponse.get_demande()



def main(args):
    """
    | Fonction main de la librairie utilisée en lignes de commandes (pour le
      dev notamment).
    | Vérifie si le nombre d'arguments donnés en args est bon.
    | Appelle la fonction echanger si c'est le cas.
    """
    if len(args) != 5:
        raise IOError(
            ("Erreur sur le nombre d'arguments en entrée : il faut donner le "
            "nom du service, l'argument du service, le nom du fichier "
            "contenant la chaîne de certificats et le nom du fichier "
            "contenant la clé privée en arguments.\nLes services disponibles "
            "sont " + str(LISTE_SERVICES_DISPONIBLES) + ".\nSi le service "
            "est 'demandeLogement', l'argument du service est le numéro "
            "unique SNE de la demande.\nSi le service est "
            "'demandesRadieesDepuisLe' ou 'nouveauxDaloDepuisLe', l'argument "
            "du service est une date (format 'aaaa-mm-jjTHH:MM:SS.s+hh:mm' "
            "(décalage par rapport à UTC)).\nSinon l'argument du service est "
            "une chaîne de caractères représentant le XML.\nExemples :\n\t"
            "./libsne.py numUnique [xml] certificats.pem cle.pem\n\t"
            "./libsne.py demandeLogement [numunique] certificats.pem cle.pem"
            "\n\t./libsne.py demandesRadieesDepuisLe "
            "2017-08-31T15:30:00.0+02:00 certificats.pem cle.pem")
        )
    if args[1] == "demandeLogement":
        print(echanger(args[1], args[3], args[4], num_unique=args[2]))
    elif args[1] in ["demandesRadieesDepuisLe", "nouveauxDaloDepuisLe"]:
        print(echanger(args[1], args[3], args[4], date=args[2]))
    else:
        print(echanger(args[1], args[3], args[4], xml=args[2]))



if __name__ == "__main__": # pragma: no cover
    main(sys.argv)
