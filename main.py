from collections import Counter

def compter_mots_fichier(Liste_de_mots_SEO, Liste_de_mots_parasites):
    # Ouvrir le fichier text SEO
    with open(Liste_de_mots_SEO, 'r', encoding='utf-8') as fichier:
        texte_SEO = fichier.read()
    Mots_SEO = texte_SEO.split()

    # Fermer le fichier SEO
    fichier.close()

    # Ouvrir le fichier mots parasites
    with open(Liste_de_mots_parasites, 'r', encoding='utf-8') as fichier:
        texte_parasites = fichier.read()
    Mots_parasites = texte_parasites.split()

    # Fermer le fichier des mots parasites
    fichier.close()

    Mots_SEO = enlever_parasites(Mots_SEO, Mots_parasites)

    # Occurences
    occurrencesS = Counter(Mots_SEO)

    liste_occurrences = [{"mot": mot, "occurrence": occurrencesS[mot]} for mot in occurrencesS]

    # Tri par nombre d'occurrences
    liste_occurrences = sorted(liste_occurrences, key=lambda x: x["occurrence"], reverse=True)

    return liste_occurrences

def enlever_parasites(Mots_SEO, Mots_parasites):
    print(Mots_parasites)
    mots_SEO_propres = [mot for mot in Mots_SEO if mot not in Mots_parasites]
    return mots_SEO_propres

# utilisation avec un fichier texte
Liste_de_mots_SEO = "SEO.txt"
Liste_de_mots_parasites = "Liste_de_mots_parasites.txt"
resultat = compter_mots_fichier(Liste_de_mots_SEO, Liste_de_mots_parasites)
print(resultat)