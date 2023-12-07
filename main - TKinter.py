from collections import Counter
import unicodedata
import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import tkinter as tk
from tkinter import messagebox

# -*- coding: UTF-8 -*-

class Analyse:
    """Class avec toutes les fonctionnalités pour extraire et analyser le code d'une page HTML
    """

    def __init__(self, url, occurrences):
        self.fichier_csv = "Liste_de_mots_parasites.csv"
        self.url = url
        self.occurrences = occurrences
        

    def extraire_code_html(self):
        """Envoye une requête pour récupérer le contenu de la page

        Args:
            url (_type_): _description_

        Returns:
            _type_: _description_
        """
        reponse = requests.get(self.url)

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

    
    def extraire_text(self,code_html):
        """Utiliser BeautifulSoup pour extraire le texte des balises HTML

        Args:
            code_html (_type_): _description_

        Returns:
            _type_: _description_
        """
        soup = BeautifulSoup(code_html, 'html.parser')
        texte_sans_balises = soup.get_text(separator=' ')

        # Supprimer les caractères spéciaux et la ponctuation
        texte_sans_balises = Analyser.supprimer_caracteres_speciaux(texte_sans_balises)

        return texte_sans_balises.split()


    def supprimer_caracteres_speciaux(self, texte_sans_balises):
        """Supprimer la ponctuation et les caractères spéciaux

        Args:
            texte (_type_): _description_

        Returns:
            _type_: _description_
        """
        # Supprimer la ponctuation et les caractères spéciaux, y compris le "-"
        texte_sans_balises = ''.join(c for c in unicodedata.normalize('NFD', texte_sans_balises) if (unicodedata.category(c) != 'Mn' and c != '-'))
        return texte_sans_balises


    def enlever_parasites(self, Mots_SEO):
        """Charger les mots parasites depuis un fichier CSV

        Args:
            Mots_SEO (_type_): _description_

        Returns:
            _type_: _description_
        """
        # Charger les mots parasites depuis un fichier CSV
        with open(self.fichier_csv, 'r', encoding='utf-8') as fichier:
            lecteur_csv = csv.reader(fichier)
            mots_parasites = [ligne[0] for ligne in lecteur_csv]

        # Fermer le fichier des mots parasites
        fichier.close()

        mots_SEO_propres = [mot for mot in Mots_SEO if mot not in mots_parasites]
        return mots_SEO_propres



    def occurrence (self, Mots_SEO):
        """En fonction du nombre d'occurrences voulu, la fonction recherchée les mots les plus utilisés sur le site

        Args:
            Mots_SEO (_type_): _description_

        Returns:
            _type_: _description_
        """
        # Occurences
        occurrences = Counter(Mots_SEO)

        liste_occurrences = [{"Le mot": mot, "occurrence": occurrences[mot]} for mot in occurrences]

        # Tri par nombre d'occurrences
        liste_occurrences = sorted(liste_occurrences, key=lambda x: x["occurrence"], reverse=True)

        return liste_occurrences


    def  extraire_valeurs_balises(self, Liste_de_mots_SEO,nom_balise,nom_attribut):
        """Utiliser BeautifulSoup pour extraire le texte des balises HTML

        Args:
            Liste_de_mots_SEO (_type_): _description_
            nom_balise (_type_): _description_
            nom_attribut (_type_): _description_

        Returns:
            _type_: _description_
        """
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
    
    def href(self, valeurs_href, nombre_liens_sortant, nombre_liens_entrant):
        """Fonction qui permet d'analyser les liens entrants et sortants

        Args:
            valeurs_href (_type_): _description_
            nombre_liens_sortant (_type_): _description_
            nombre_liens_entrant (_type_): _description_

        Returns:
            _type_: _description_
        """
        for valeur in valeurs_href:
            if isinstance(valeur, str) and "http" in valeur:
                nombre_liens_sortant += 1
            else:
                nombre_liens_entrant += 1

        return nombre_liens_sortant, nombre_liens_entrant


    def extraire_nom_domaine(self):
        """Utiliser urlparse pour extraire les composants de l'URL

        Returns:
            _type_: _description_
        """
        # Utiliser urlparse pour extraire les composants de l'URL
        parsed_url = urlparse(self.url)

        # Extraire le nom de domaine
        nom_domaine = parsed_url.netloc

        return nom_domaine








url = "https://loic-ledoher.fr"
nombre_occurrences = 5

Analyser = Analyse(url, nombre_occurrences)
code_html = Analyser.extraire_code_html()
texte_sans_balises = Analyser.extraire_text(code_html)
texte_sans_parasites = Analyser.enlever_parasites(texte_sans_balises)
liste_occurrences = Analyser.occurrence(texte_sans_parasites)

for i in range(len(liste_occurrences)):
    if nombre_occurrences > 0:
        print(liste_occurrences[i])
        nombre_occurrences -= 1
print()

# Debut du script
#print("Bienvenue sur l'outil pour effectuer un audit SEO simple sur une page web.")
#url = input("Quel URL voulez-vous analyser :")
#Liste_de_mots_parasites = input("Quel est le chemin du fichier (.csv) avec les mots parasites :")
#nombre_occurrences = int(input("Combien d'occurrences voulez-vous analyser :"))

# Obtenir le nom de domaine d'une URL
#url = "https://loic-ledoher.fr"
#nom_domaine = extraire_nom_domaine(url)
#print("\nNom de domaine :", nom_domaine,"\n")

# Récupération du code du site
#code_html = extraire_code_html(url)

# Chemin du documents avec les mots parasites
#Liste_de_mots_parasites = "Liste_de_mots_parasites.csv"

# Extraire le text des balises
#Liste_Mots = extraire_text(code_html)

# Supprimé tous les mots parasites
#mots_SEO_propre = enlever_parasites(Liste_Mots,Liste_de_mots_parasites)

#Compter les occurrences et mettre en forme le dictionnaire
#resultat = occurrence (mots_SEO_propre)

# Afficher les mots clés avec les occurrences
#for i in range(len(resultat)):
#    if nombre_occurrences > 0:
#        print(resultat[i])
#        nombre_occurrences -= 1
#print()

# Récupérer tous les href des balises a
#valeurs_href,nombre_balises_sans_href = extraire_valeurs_balises(code_html, 'a', 'href')
#print("Valeurs des attributs href des balises a :", valeurs_href,"\n")
# Séparation des liens entrants et sortants
#nombre = href(valeurs_href,0,0)
#print("Nombre de liens entrant(s) :",nombre[1],"\nNombre de liens sortant(s) :",nombre[0])

# Récupérer les valeurs des attributs alt des balises img
#valeurs_alt,nombre_balises_sans_alt = extraire_valeurs_balises(code_html, 'img', 'alt')
#print("Valeurs des attributs alt des balises img :", valeurs_alt,"\n")
#print("Nombre de balises img sans attribut alt :", nombre_balises_sans_alt,"\n")





# TKinter

# Classe principale qui crée la fenêtre
class Application(tk.Tk):
    def __init__(self):
        """Class Application
        """
        super().__init__()
        # titre de la fenetre
        self.title("Ma Fenêtre de référencement")
        # taille de la fenetre
        self.geometry("1000x700")
        # couleur du fond de la fenetre
        self.configure(bg="light blue", cursor="pirate", relief="groove")


        # Appel des fonctions
        self.TitrePageWeb()
        self.quitter()
        self.url()

    def TitrePageWeb(self):
        """Fonction pour le titre
        """
        # création de la frame
        self.frame_titre = tk.Frame(self, width=1000, height=100, bg='light blue')

        # création d'un label pour affichage du texte
        self.Label_titre = tk.Label(self.frame_titre, text="Titre Page Web", font=("Helvetica", 25, "bold"), fg="red", bg="light blue")

        # positionnement du label sur l'ecran
        self.Label_titre.pack(side="top", fill="both", expand=True)
        self.frame_titre.pack(side="top")


    def quitter(self):
        """Fonction pour le bouton quitter
        """
        # création de la frame
        self.frame_quitter = tk.Frame(self, width=1000, height=50, bg='light blue')
        # Fontion qui créer un bouton pour quitter l'application
        self.bouton_quitter = tk.Button(self.frame_quitter, text="Quitter", command=self.destroy)

        # On pack
        self.bouton_quitter.pack()
        self.frame_quitter.pack(side="bottom")

    def url(self):
        """Fonction pour la zone pour saisir l'url
        """
        # création de la frame
        self.frame_url = tk.Frame(self, width=1000, height=50, bg='light blue')

        # Création d'une Entry (zone de texte)
        self.zone_texte = tk.Entry(self.frame_url, width=300)

        # Positionnement de la zone de texte sur l'écran
        self.zone_texte.pack(pady=10)

        
        # Création d'un bouton pour déclencher une action (optionnel)
        self.bouton_valider = tk.Button(self.frame_url, text="Valider")#, command=self.afficher_texte)

        # On pack
        self.bouton_valider.pack()
        self.frame_url.pack(side="top")




# Fonction principale qui crée une instance de la classe Application et lance la boucle principale de Tkinter
def main():
    app = Application()
    app.mainloop()

# Appel de la fonction principale
if __name__ == "__main__":
    main()