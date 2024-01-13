from collections import Counter
import unicodedata
import csv
import openpyxl
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import tkinter as tk
from tkinter import ttk,filedialog, messagebox, PhotoImage
import tktabl

# Librairie pour la création des PDF
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Spacer, SimpleDocTemplate, Table, TableStyle, Image, PageBreak
from reportlab.lib import colors
from reportlab.lib.units import cm

# -*- coding: UTF-8 -*-

class Analyse:
    """Class avec toutes les fonctionnalités pour extraire et analyser le code d'une page HTML
    """

    def __init__(self):
        self.fichier_csv = "Liste_de_mots_parasites.csv"
        self.occurrences = 5
        

    def extraire_code_html(self, url):
        """Envoye une requête pour récupérer le contenu de la page

        Args:
            url (_type_): _description_

        Returns:
            _type_: _description_
        """
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
        texte_sans_balises = self.supprimer_caracteres_speciaux(texte_sans_balises)

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
    
    def href(self, valeurs_href):
        """Fonction qui permet d'analyser les liens entrants et sortants

        Args:
            valeurs_href (list): Valeurs des alt

        Returns:
            Dictionnaire: Retourne un dictionnaire avec les 2 types de liens
        """

        # Dictionnaire avec le nombre des 2 types de liens
        liens = [['Liens entrants',0],['Liens sortants',0]]

        # Boucle pour analyser le contenu des alt et compter les 2 types de liens
        for valeur in valeurs_href:
            # Si il y a une chaine de caratère evec un 'http' ou un https' alors le lien est sortant
            if isinstance(valeur, str) and ("http" in valeur or "https" in valeur):
                liens[1][1] += 1
            else:
                liens[0][1] += 1

        # Renvoie une liste des miens
        return liens


    def extraire_nom_domaine(self, url):
        """Utiliser urlparse pour extraire les composants de l'URL

        Returns:
            str: Nom de domaine
        """
        # Utiliser urlparse pour extraire les composants de l'URL
        parsed_url = urlparse(url)

        # Extraire le nom de domaine
        nom_domaine = parsed_url.netloc

        return nom_domaine




############## TKinter

# Classe principale qui crée la fenêtre
class Application():

    def __init__(self):
        """Class Application
        """
        self.matk = tk.Tk()
        self.url = tk.StringVar()
        self.url.set("https://loic-ledoher.fr")

        self.mots = tk.StringVar()
        self.mots.set("Vos mots")


        # titre de la fenetre
        self.matk.title("Ma Fenêtre de référencement")
        # taille de la fenetre
        self.matk.geometry("800x500")
        # couleur du fond de la fenetre
        self.matk.configure(bg="light blue", cursor="pirate", relief="groove")
        # Charger l'image et la définir comme icône de la fenêtre
        logo = PhotoImage(file='logo.png')
        self.matk.iconphoto(True, logo)

        # Menu
        menu_bar = tk.Menu(self.matk)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Charger Excel", command=lambda:Parasites())
        menu_bar.add_cascade(label="Mots Parasites", menu=file_menu)
        self.matk.config(menu=menu_bar)

        # Appel des fonctions
        self.TitrePageWeb()
        self.quitter()
        self.zone_url()
        self.zone_occurrence()


        self.matk.mainloop()


    def TitrePageWeb(self):
        """Fonction pour le titre
        """
        # création de la frame
        self.frame_titre = tk.Frame(self.matk, width=1000, height=100, bg='light blue')

        # création d'un label pour affichage du texte
        self.Label_titre = tk.Label(self.frame_titre, text="Welcome", font=("Helvetica", 25, "bold"), fg="red", bg="light blue")

        # positionnement du label sur l'ecran
        self.Label_titre.pack(side="top", fill="both", expand=True)
        self.frame_titre.pack(side="top")


    def quitter(self):
        """Fonction pour le bouton quitter
        """
        # création de la frame
        self.frame_quitter = tk.Frame(self.matk, width=1000, height=50, bg='light blue')
        # Fontion qui créer un bouton pour quitter l'application
        self.bouton_quitter = tk.Button(self.frame_quitter, text="Quitter", command=self.matk.destroy)

        # On pack
        self.bouton_quitter.pack()
        self.frame_quitter.pack(side="bottom")


    def zone_url(self):
        """Fonction pour la zone pour saisir l'url
        """
        # création de la frame
        self.frame_url = tk.Frame(self.matk, width=500, height=100, bg='light blue')

        # Création d'une Entry (zone de texte)
        self.zone_texte = tk.Entry(self.frame_url, width=100, textvariable=self.url)
        self.instruc = tk.Label(self.frame_url, text="Renseignez l'url du site web que vous souhaitez analyser", font=("Helvetica", 11), fg="black", bg="light blue")

        # Positionnement de la zone de texte sur l'écran
        self.zone_texte.pack(pady=10)
        self.instruc.pack()

        # On pack
        self.frame_url.pack(side="top")


    def zone_occurrence(self):
        """Fonction pour la zone pour saisir l'url
        """
        # création de la frame
        self.frame_reccurrence = tk.Frame(self.matk, width=500, height=100, bg='light blue')

        # Création d'une Entry (zone de texte)
        self.zone_texte = tk.Entry(self.frame_reccurrence, width=100, textvariable=self.mots)
        self.instruc = tk.Label(self.frame_reccurrence, text="Renseignez les mots que vous voulez voir (séparé(s) d'une virgule). Vous pouvez laisser vide pour voir tous les mots", font=("Helvetica", 11), fg="black", bg="light blue")

        # Positionnement de la zone de texte sur l'écran
        self.zone_texte.pack(pady=10)
        self.instruc.pack()
        
        # Création d'un bouton pour déclencher une action (optionnel)
        self.bouton_valider = tk.Button(self.frame_reccurrence, text="Valider", command=lambda:self.recuperation())

        # On pack
        self.bouton_valider.pack(pady=10)
        self.frame_reccurrence.pack(side="top")

    
    
    def recuperation(self):
        """Fonction pour récupérer les valeurs renseignées dans la première page et les transférer vers la deuxième page
        """
        valeur = self.url.get()
        valeur2 = self.mots.get()
        
        resul = Resultats(valeur, valeur2)




class Resultats():
    """Class qui afficher le résultat de l'analyse
    """
    def __init__(self,url, mots):

        self.matk2 = tk.Toplevel()

        self.url = url
        self.mots = mots

        # Nombre de liens
        self.liens = (['Liens entrants',0],['Liens sortants',0])
        # Nombre de balise <img>
        self.img = (['Balise(s) avec un alt',0],['Balise(s) sans alt',0])
        # Occurrences du site web
        self.occurrences = ()
        # Occurrences de l'utilisateur
        self.liste_tableau = []
        # 3 premères occurrences
        self.trois_occurrences = []

        # titre de la fenetre
        self.matk2.title("Ma Fenêtre de référencement - Résultat")
        # taille de la fenetre
        self.matk2.geometry("800x500")
        # Charger l'image et la définir comme icône de la fenêtre
        logo = PhotoImage(file='logo.png')
        self.matk2.iconphoto(True, logo)

        # Ajustement de la taille de la page
        self.matk2.pack_propagate(False)

        # couleur du fond de la fenetre
        self.matk2.configure(bg="light blue", cursor="pirate", relief="groove")

        # Menu
        menu_bar = tk.Menu(self.matk2)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        # Menu pour les mots parasites
        parasite_menu = tk.Menu(menu_bar, tearoff=0)
        parasite_menu.add_command(label="Charger Excel", command=lambda: self.Parasites())
        menu_bar.add_cascade(label="Mots Parasites", menu=parasite_menu)

        # Menu pour exporter
        export_menu = tk.Menu(menu_bar, tearoff=0)
        export_menu.add_command(label="PDF", command=lambda: self.exporter_en_pdf())
        menu_bar.add_cascade(label="Exporter", menu=export_menu)

        # Configuration de la barre de menu
        self.matk2.config(menu=menu_bar)


        # Ajout d'un Canvas pour rendre la fenêtre scrollable
        self.canvas = tk.Canvas(self.matk2, bg='light blue')
        self.canvas.pack(side="left", fill="both", expand=True)
        # Ajout d'une barre de défilement verticale
        scrollbar = tk.Scrollbar(self.matk2, command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        # Ajout d'un frame pour contenir tous les éléments
        self.frame_conteneur = tk.Frame(self.canvas, bg='light blue')
        self.canvas.create_window((0, 0), window=self.frame_conteneur, anchor="nw")

        # Appel des fonctions
        self.TitrePageWeb()
        self.afficher_resultats()
        self.exporter()
        self.quitter()

        # Mettez à jour la taille du Canvas après avoir ajouté tous les éléments
        self.frame_conteneur.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

        self.matk2.mainloop()


    def TitrePageWeb(self):
        """Fonction pour le titre
        """
        # création de la frame
        self.frame_titre = tk.Frame(self.frame_conteneur, width=1000, height=100, bg='light blue')

        # création d'un label pour affichage du texte
        self.Label_titre = tk.Label(self.frame_titre, text="Résultat de l'analyse SEO", font=("Helvetica", 25, "bold"), fg="red", bg="light blue")

        # positionnement du label sur l'ecran
        self.Label_titre.pack(side="top",anchor="center", fill="both", expand=True,padx=90)
        self.frame_titre.pack(side="top",anchor="center", fill="both", expand=True,padx=90)

    def afficher_resultats(self):
        """Fonction qui affiche tous les résultats de l'analyse
        """
        analyses = Analyse()
        print(self.url)
        self.frame_url = tk.Frame(self.frame_conteneur, width=1000, height=100, bg='light blue')
        self.Label_url = tk.Label(self.frame_url, text=Analyse.extraire_nom_domaine(analyses, self.url), font=("Helvetica", 25, "bold"), fg="red", bg="light blue")

        # positionnement du label sur l'ecran
        self.Label_url.pack(side="top", fill="both", expand=True)
        self.frame_url.pack(side="top")


        # Lancement de la Class
        Analyser = Analyse()
        # Extraire le code html du site web défini sur la première page
        code_html = Analyser.extraire_code_html(self.url)
        # Suppression des balises du code
        texte_sans_balises = Analyser.extraire_text(code_html)
        # Suppression des mots parasites (ex : un, une, ...)
        texte_sans_parasites = Analyser.enlever_parasites(texte_sans_balises)
        # Création de la listes des occurrences
        self.occurrences = Analyser.occurrence(texte_sans_parasites)

        # Récupérer tous les href des balises a
        valeurs_href,nombre_balises_sans_href = Analyser.extraire_valeurs_balises(code_html, 'a', 'href')
        # Séparation des liens entrants et sortants
        self.liens = Analyser.href(valeurs_href)

        # Récupérer les valeurs des attributs alt des balises img
        valeurs_alt,self.img[1][1] = Analyser.extraire_valeurs_balises(code_html, 'img', 'alt')
        self.img[0][1] = len(valeurs_alt)

        # Appel de la fonction pour afficher les occurreces demandées
        self.afficher_occurrences()
        # Appel de la fonction pour afficher les liens entrants et sortants
        self.afficher_liens()
        # Appel de la fonction pour afficher le pourcentage de balise <img> avec alt
        self.afficher_alt()

            

    def afficher_occurrences(self):
        """Fonction qui permet l'affichage des occurrences demandées par l'utilisateur

        Args:
            liste_occurrences (list): liste des mots avec leur occurrences, trouvés dans le site web
        """
        # Split des mots pour l'analyse SEO via les virgules
        # Suppression des espaces pour la bonne compréhension des mots
        liste_mots = [mot.strip() for mot in self.mots.split(',')]

        # Comparaisons des occurrences et des mots renseignés
        for mot_a_comparer in liste_mots:
            for occurrence in self.occurrences:

                # Si l'occurrence correspond aux mots donnés par l'utilisateur alors ...
                if occurrence['Le mot'].lower() == mot_a_comparer.lower():
                    # Ajout dans le tableau du mots et de son occurrence
                    self.liste_tableau.append(occurrence)

        trois_premier = "Vos mots sélectionnés ne figurent pas dans les 3 premiers de votre site web."
        for i in range (len(self.liste_tableau)):
            for j in range (3):
                if self.liste_tableau[i] == self.occurrences[j]:
                    trois_premier = "Au moin un de vos mots sélectionnés figure parmis les 3 premiers."

        # Si aucunes correspondances alors un message s'affiche pour informer l'utilisateur
        if len(self.liste_tableau) == 0 and self.mots != "":
            self.frame_occurrences = tk.Frame(self.frame_conteneur, width=1000, height=100, bg='light blue')
            self.label_occurrences = tk.Label(self.frame_occurrences, text=f"Aucun(s) résultat(s) pour votre recherche : {self.mots}", font=("Helvetica", 20), fg="black", bg="light blue")
            self.label_occurrences.pack(side="bottom", fill="both", expand=True)
            self.frame_occurrences.pack(side="top")
        elif len(self.liste_tableau) == 0 and self.mots == "":
            self.frame_occurrences = tk.Frame(self.frame_conteneur, width=1000, height=100, bg='light blue')
            self.label_occurrences = tk.Label(self.frame_occurrences, text=f"Recherche de tous les mots de votre site web", font=("Helvetica", 20), fg="black", bg="light blue")
            self.label_occurrences.pack(side="bottom", fill="both", expand=True)
            self.frame_occurrences.pack(side="top")

            # Création d'un cadre pour le tableau
            cadre_tableau = tk.Frame(self.frame_conteneur)
            table = tktabl.Table(cadre_tableau , data=self.occurrences)
            cadre_tableau.pack(expand=True)
            table.pack()
        else:
            self.frame_occurrences = tk.Frame(self.frame_conteneur, width=1000, height=100, bg='light blue')
            self.label_occurrences = tk.Label(self.frame_occurrences, text=f"{trois_premier}", font=("Helvetica", 14), fg="black", bg="light blue")
            self.label_occurrences.pack(side="bottom", fill="both", expand=True)
            self.frame_occurrences.pack(side="top")
            table = tktabl.Table(self.frame_conteneur , data=self.liste_tableau)
            table.pack()


    def afficher_liens(self):
        """Fonction qui affiche les liens entrant(s) et sortant(s)

        Args:
            nombre_liens (list): liste avec les nombres de liens
        """
        # Création de la frame
        self.frame_liens = tk.Frame(self.frame_conteneur, width=100, height=50, bg='light blue')

        # Affichage du nombre des liens
        self.label_liens = tk.Label(self.frame_liens, text=f"Nombre de liens entrant(s) : {self.liens[0][1]}\nNombre de liens sortant(s) : {self.liens[1][1]}\n")

        # Pack
        self.label_liens.pack(side="top", expand=True, pady=10)
        self.frame_liens.pack(side="top")


    def afficher_alt(self):
        """Fonction qui permet d'afficher le pourcentage de balise <img> avec des alt par rapport au balise sans alt

        Args:
            nombre_balise_alt (int): Nombre de balise <img> avec des alt
            nombre_balise_sans_alt (int): Nombre de balise <img> sans alt
        """
        if self.img[1][1] != 0:
            Pourcentage = (self.img[0][1] / (self.img[0][1] + self.img[1][1])) * 100
        else:
            Pourcentage = 100

        # Création de la frame
        self.frame_alt = tk.Frame(self.frame_conteneur, width=100, height=50, bg='light blue')

        # Afficher le pourcentage de balise <img> avec alt
        self.label_alt = tk.Label(self.frame_alt, text=f"Pourcentage de balise <img> avec des alt : {Pourcentage}%")
                                  
        # Pack
        self.label_alt.pack(side="top", expand=True, pady=10)
        self.frame_alt.pack(side="top")


    def exporter(self):
        """Fonction qui créer le bouton pour exporter la page
        """
        # Création de la frame
        self.frame_exporter = tk.Frame(self.frame_conteneur, width=1000, height=50, bg='light blue')
        # Fontion qui créer un bouton pour quitter l'application
        self.bouton_exporter = tk.Button(self.frame_exporter, text="Exporter", command=lambda:self.exporter_en_pdf())

        # On pack
        self.bouton_exporter.pack()
        self.frame_exporter.pack(side="top", expand=True)


    def header_footer(self, canvas, doc):
        """En-tête et pied de page de mon fichier PDF

        Args:
            canvas (_type_): _description_
            doc (_type_): _description_
        """
        canvas.saveState()
        # Ajout du logo dans l'en-tête
        logo_path = "logo.png"
        canvas.drawImage(logo_path, 2.54 * cm, 24.3 * cm, width=2.54 * cm, height=2.54 * cm)

        # Ajout du pied de page
        canvas.setFont('Helvetica', 9)
        canvas.drawString(2.54 * cm, 2 * cm, "TKinter SEO - Page %d" % doc.page)
        canvas.restoreState()


    def exporter_en_pdf(self):
        """Fonction qui permet d'exporter toute la page de résultats en pdf
        """
        # Permet de fermer la page avec les résultats
        self.matk2.destroy()

        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not file_path:
            return

        doc = SimpleDocTemplate(file_path, pagesize=LETTER)
        story = []
        styles = getSampleStyleSheet()

        # Définir des styles personnalisés
        titre_style = styles["Title"]
        titre_style.fontName = "Helvetica-Bold"
        titre_style.fontSize = 24
        titre_style.leading = 36
        titre_style.alignment = 1
        titre_style.textColor = "#0052CC"

        titre2_style = styles["Heading2"]
        titre2_style.fontName = "Helvetica-Bold"
        titre2_style.fontSize = 18
        titre2_style.leading = 24
        titre2_style.alignment = 0
        titre2_style.textColor = "#0052CC"

        info_style = styles["Normal"]
        info_style.fontName = "Helvetica"
        info_style.fontSize = 14
        info_style.leading = 20
        info_style.alignment = 0

        # Titre
        story.append(Paragraph("Rapport d'Audit SEO", titre_style))

        # URL analysée
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"URL analysée: ", titre2_style))
        story.append(Paragraph(f"{self.url}", info_style))

        # Mots clés utilisateur
        story.append(Spacer(1, 12))
        story.append(Paragraph("Mots clés utilisateur:", titre2_style))
        # Condition pour savoir dans quelle liste aller chercher les occurrences
        if len(self.mots) > 0:
            if len(self.liste_tableau) > 0:
                # Créer des en-têtes de colonnes
                table_data = [['Mot', 'Occurrence']]

                # Ajout de chaque occurrence dans une nouvelle ligne du tableau
                for occurrence in self.occurrences:
                    row = [occurrence['Le mot'], occurrence['occurrence']]
                    table_data.append(row)
                table = Table(table_data)

                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), "#F2F2F2"),
                    ('TEXTCOLOR', (0, 0), (-1, 0), "#0052CC"),
                    ('FONTNAME', (0, 0), (-1, 0), "Helvetica-Bold"),
                    ('FONTSIZE', (0, 0), (-1, 0), 14),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), "#FFFFFF"),
                    ('GRID', (0, 0), (-1, -1), 1, "#CCCCCC"),
                ]))
                story.append(table)
            else:
                story.append(Paragraph("N/A", info_style))
        elif len(self.occurrences) > 0:
            # Créer des en-têtes de colonnes
            table_data = [['Mot', 'Occurrence']]

            # Ajouter chaque occurrence dans une nouvelle ligne du tableau
            for occurrence in self.occurrences:
                row = [occurrence['Le mot'], occurrence['occurrence']]
                table_data.append(row)

            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), "#F2F2F2"),
                ('TEXTCOLOR', (0, 0), (-1, 0), "#0052CC"),
                ('FONTNAME', (0, 0), (-1, 0), "Helvetica-Bold"),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), "#FFFFFF"),
                ('GRID', (0, 0), (-1, -1), 1, "#CCCCCC"),
            ]))
            story.append(table)
        else:
            story.append(Paragraph("N/A", info_style))


        # Top mots clés
        # Création de la liste des trois premières occurrences du site web
        for i in range (3):
            self.trois_occurrences.append(self.occurrences[i])

        story.append(Spacer(1, 12))
        story.append(Paragraph("Top mots clés:", titre2_style))

        # Créer des en-têtes de colonnes
        table_data = [['Mot', 'Occurrence']]
        # Ajouter chaque occurrence dans une nouvelle ligne du tableau
        for occurrence in self.trois_occurrences:
            row = [occurrence['Le mot'], occurrence['occurrence']]
            table_data.append(row)

        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), "#F2F2F2"),
            ('TEXTCOLOR', (0, 0), (-1, 0), "#0052CC"),
            ('FONTNAME', (0, 0), (-1, 0), "Helvetica-Bold"),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), "#FFFFFF"),
            ('GRID', (0, 0), (-1, -1), 1, "#CCCCCC"),
        ]))
        story.append(table)

        # Liens entrants
        story.append(Spacer(1, 12))
        story.append(Paragraph("Liens entrants:", titre2_style))
        story.append(Paragraph(f"{self.liens[0][1]}", info_style))

        # Liens sortants
        story.append(Spacer(1, 12))
        story.append(Paragraph("Liens sortants:", titre2_style))
        story.append(Paragraph(f"{self.liens[1][1]}", info_style))
            
        # Balises alt manquantes
        story.append(Paragraph("Nombre de balises alt manquantes:", titre2_style))
        if self.img[1][1] > 0:
            story.append(Paragraph(f"{self.img[1][1]}", info_style))
        else:
            story.append(Paragraph("Aucune balise alt manquantes !", info_style))


        doc.build(story, onFirstPage=self.header_footer, onLaterPages=self.header_footer)
        messagebox.showinfo("Sauvegarde Réussie", "Le rapport a été sauvegardé avec succès en format PDF.")


            
    def quitter(self):
        """Fonction pour le bouton quitter
        """
        # création de la frame
        self.frame_quitter = tk.Frame(self.frame_conteneur, width=1000, height=50, bg='light blue')
        # Fontion qui créer un bouton pour quitter l'application
        self.bouton_quitter = tk.Button(self.frame_quitter, text="Quitter", command=self.matk2.destroy)

        # On pack
        self.bouton_quitter.pack()
        self.frame_quitter.pack(side="bottom")


class Parasites():
    """Class qui gère la page pour les mots parasites
    """
    def __init__(self) -> None:
        self.matk3 = tk.Toplevel()

        # titre de la fenetre
        self.matk3.title("Ma Fenêtre de référencement - Parasites")
        # taille de la fenetre
        self.matk3.geometry("800x500")
        # Charger l'image et la définir comme icône de la fenêtre
        logo = PhotoImage(file='logo.png')
        self.matk3.iconphoto(True, logo)

        # Ajustement de la taille de la page
        self.matk3.pack_propagate(False)

        # couleur du fond de la fenetre
        self.matk3.configure(bg="light blue", cursor="pirate", relief="groove")

        # lien vers le fichier Excel des mots parasites
        self.fichier_excel = "Liste_de_mots_parasites.csv"


        self.page()
        self.charger_excel()

        self.matk3.mainloop()


    def charger_excel(self):
        """Ouvrir le fichier excel avec tous les mots parasites
        """
        try:
            with open(self.fichier_excel, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                self.tree.delete(*self.tree.get_children())
                for row in reader:
                    self.tree.insert('', tk.END, values=row)
        except Exception as e:
            print("Erreur lors du chargement du fichier:", e)


    def ajout_mot(self):
        """Ajouter un mot parasite au fichier excel
        """
        nouveau_mot = self.add_mot.get()
        if nouveau_mot:
            self.tree.insert('', tk.END, values=(nouveau_mot,))
            self.add_mot.delete(0, tk.END)


    def supprimer_mot(self):
        """Fonction pour supprimer le mot selectionné
        """
        mot_selectionne = self.tree.selection()
        if mot_selectionne:
            self.tree.delete(mot_selectionne)
    

    def sauvegarde(self):
        """Fonction pour sauvegarder les modifications
        """
        with open(self.fichier_excel, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            for child in self.tree.get_children():
                writer.writerow(self.tree.item(child)['values'])

        messagebox.showinfo("Information", "Modifications sauvegardées avec succès.")
        self.matk3.destroy

    def page(self):
        """Fonction avec toute la mis en page de la fenetre avec les mots parasites
        """
        # Frame pour l'ajout
        self.ajout = tk.Frame(self.matk3,bg='light blue')
        # Entrée pour ajouter un nouveau mot
        self.add_mot = tk.Entry(self.ajout)
        # Boutons pour ajouter ou supprimer des mots
        self.add_button = tk.Button(self.ajout, text="Ajouter Mot", command=self.ajout_mot)

        # Pack
        self.add_mot.pack(side="left")
        self.add_button.pack(side="right")
        self.ajout.pack(side="top")

        # bouton pour supprimer le mot séléctionné
        remove_button = tk.Button(self.matk3, text="Supprimer Mot Sélectionné", command=self.supprimer_mot)
        remove_button.pack()

        # Treeview = widget pour afficher les mots parasites
        self.tree = ttk.Treeview(self.matk3, columns=("Word",), show="headings")
        self.tree.heading("Word", text="Mot")
        self.tree.pack(expand=True, fill='both')


        # Frame pour charger et sauvegarder le fichier CSV
        self.fin = tk.Frame (self.matk3, bg='light blue')

        # Bouton pour load le fichier
        charger_button = tk.Button(self.fin, text="Re-charger le fichier Excel", command=self.charger_excel)
        # Bouton pour sauvegarde le fichier
        sauvegarder_button = tk.Button(self.fin, text="Sauvegarder les modifications", command=self.sauvegarde)

        # Pack
        charger_button.pack(side="left")
        sauvegarder_button.pack(side="right")
        self.fin.pack()


        # création de la frame
        self.frame_quitter = tk.Frame(self.matk3, width=1000, height=50, bg='light blue')
        # Fontion qui créer un bouton pour quitter l'application
        self.bouton_quitter = tk.Button(self.frame_quitter, text="Quitter", command=self.matk3.destroy)

        # On pack
        self.bouton_quitter.pack()
        self.frame_quitter.pack(side="bottom")


app = Application()