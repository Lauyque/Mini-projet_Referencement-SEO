from collections import Counter
import unicodedata
import csv

def supprimer_caracteres_speciaux(texte):
    # Supprimer la ponctuation et les caractères spéciaux, y compris le "-"
    texte = ''.join(c for c in unicodedata.normalize('NFD', texte) if (unicodedata.category(c) != 'Mn' and c != '-'))
    return texte

def compter_mots_fichier(Liste_de_mots_SEO):
    # Ouvrir le fichier text SEO
    with open(Liste_de_mots_SEO, 'r', encoding='utf-8') as fichier:
        # Lire le texte, supprimer la ponctuation, le "-" et les caractères spéciaux
        texte_SEO = supprimer_caracteres_speciaux(fichier.read())

    Mots_SEO = texte_SEO.split()

    # Fermer le fichier SEO
    fichier.close()

    return Mots_SEO



def enlever_parasites(Mots_SEO, fichier_csv):
    # Charger les mots parasites depuis un fichier CSV
    with open(fichier_csv, 'r', encoding='utf-8') as fichier:
        lecteur_csv = csv.reader(fichier)
        mots_parasites = [ligne[0] for ligne in lecteur_csv]

    # Fermer le fichier des mots parasites
    fichier.close()

    print(mots_parasites)
    mots_SEO_propres = [mot for mot in Mots_SEO if mot not in mots_parasites]
    return mots_SEO_propres


def occurrence (Mots_SEO):
    # Occurences
    occurrences = Counter(Mots_SEO)

    liste_occurrences = [{"Le mot": mot, "occurrence": occurrences[mot]} for mot in occurrences]

    # Tri par nombre d'occurrences
    liste_occurrences = sorted(liste_occurrences, key=lambda x: x["occurrence"], reverse=True)

    return liste_occurrences



# utilisation avec un fichier texte
Liste_de_mots_SEO = "SEO.txt"
Liste_de_mots_parasites = "Liste_de_mots_parasites.csv"

Liste_Mots = compter_mots_fichier(Liste_de_mots_SEO)
mots_SEO_propre = enlever_parasites(Liste_Mots,Liste_de_mots_parasites)
resultat = occurrence (mots_SEO_propre)
print(resultat)