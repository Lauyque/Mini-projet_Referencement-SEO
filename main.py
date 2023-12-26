from collections import Counter
import unicodedata
import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def supprimer_caracteres_speciaux(texte):
    # Supprimer la ponctuation et les caractères spéciaux, y compris le "-"
    texte = ''.join(c for c in unicodedata.normalize('NFD', texte) if (unicodedata.category(c) != 'Mn' and c != '-'))
    return texte

def extraire_text(Liste_de_mots_SEO):
    # Utiliser BeautifulSoup pour extraire le texte des balises HTML
    soup = BeautifulSoup(Liste_de_mots_SEO, 'html.parser')
    texte_sans_balises = soup.get_text(separator=' ')

    # Supprimer les caractères spéciaux et la ponctuation
    texte_sans_balises = supprimer_caracteres_speciaux(texte_sans_balises)

    return texte_sans_balises.split()


def  extraire_valeurs_balises(Liste_de_mots_SEO,nom_balise,nom_attribut):

    # Utiliser BeautifulSoup pour extraire le texte des balises HTML
    soup = BeautifulSoup(Liste_de_mots_SEO, 'html.parser')

    # Trouver toutes les balises correspondantes
    balises = soup.find_all(nom_balise)

    # Extraire les valeurs de l'attribut spécifié
    valeurs = [balise.get(nom_attribut) for balise in balises if balise.get(nom_attribut) is not None]

    # Compter le nombre de balises sans attribut alt
    balises_sans_alt = [balise for balise in balises if balise.get(nom_attribut) is None]
    nombre_balises_sans_alt = len(balises_sans_alt)
    return valeurs,nombre_balises_sans_alt 


def enlever_parasites(Mots_SEO, fichier_csv):
    # Charger les mots parasites depuis un fichier CSV
    with open(fichier_csv, 'r', encoding='utf-8') as fichier:
        lecteur_csv = csv.reader(fichier)
        mots_parasites = [ligne[0] for ligne in lecteur_csv]

    # Fermer le fichier des mots parasites
    fichier.close()

    mots_SEO_propres = [mot for mot in Mots_SEO if mot not in mots_parasites]
    return mots_SEO_propres


def occurrence (Mots_SEO):
    # Occurences
    occurrences = Counter(Mots_SEO)

    liste_occurrences = [{"Le mot": mot, "occurrence": occurrences[mot]} for mot in occurrences]

    # Tri par nombre d'occurrences
    liste_occurrences = sorted(liste_occurrences, key=lambda x: x["occurrence"], reverse=True)

    return liste_occurrences


def extraire_nom_domaine(url):
    # Utiliser urlparse pour extraire les composants de l'URL
    parsed_url = urlparse(url)

    # Extraire le nom de domaine
    nom_domaine = parsed_url.netloc

    return nom_domaine

def extraire_code_html(url):
    # Envoyer une requête pour récupérer le contenu de la page
    reponse = requests.get(url)

    # Vérifier si la requête a réussi (code 200)
    if reponse.status_code == 200:
        # Utiliser BeautifulSoup pour analyser le HTML
        soup = BeautifulSoup(reponse.content, 'html.parser')

        # Extraire le code HTML
        code_html = str(soup)

        return code_html
    else:
        print("La requête a échoué avec le code :", reponse.status_code)
        return None


def href(valeurs_href, nombre_liens_sortant, nombre_liens_entrant):
    for valeur in valeurs_href:
        if isinstance(valeur, str) and "http" in valeur:
            nombre_liens_sortant += 1
        else:
            nombre_liens_entrant += 1

    return nombre_liens_sortant, nombre_liens_entrant




# Debut du script
print("Bienvenue sur l'outil pour effectuer un audit SEO simple sur une page web.")
url = input("Quel URL voulez-vous analyser :")
Liste_de_mots_parasites = input("Quel est le chemin du fichier (.csv) avec les mots parasites :")
nombre_occurrences = int(input("Combien d'occurrences voulez-vous analyser :"))

# Obtenir le nom de domaine d'une URL
#url = "https://loic-ledoher.fr"
nom_domaine = extraire_nom_domaine(url)
print("\nNom de domaine :", nom_domaine,"\n")

# Récupération du code du site
code_html = extraire_code_html(url)

# Chemin du documents avec les mots parasites
#Liste_de_mots_parasites = "Liste_de_mots_parasites.csv"

# Extraire le text des balises
Liste_Mots = extraire_text(code_html)

# Supprimé tous les mots parasites
mots_SEO_propre = enlever_parasites(Liste_Mots,Liste_de_mots_parasites)

#Compter les occurrences et mettre en forme le dictionnaire
resultat = occurrence (mots_SEO_propre)

# Afficher les mots clés avec les occurrences
for i in range(len(resultat)):
    if nombre_occurrences > 0:
        print(resultat[i])
        nombre_occurrences -= 1
print()

# Récupérer tous les href des balises a
valeurs_href,nombre_balises_sans_href = extraire_valeurs_balises(code_html, 'a', 'href')
#print("Valeurs des attributs href des balises a :", valeurs_href,"\n")
# Séparation des liens entrants et sortants
nombre = href(valeurs_href,0,0)
print("Nombre de liens entrant(s) :",nombre[1],"\nNombre de liens sortant(s) :",nombre[0])

# Récupérer les valeurs des attributs alt des balises img
valeurs_alt,nombre_balises_sans_alt = extraire_valeurs_balises(code_html, 'img', 'alt')
#print("Valeurs des attributs alt des balises img :", valeurs_alt,"\n")
print("Nombre de balises img sans attribut alt :", nombre_balises_sans_alt,"\n")



