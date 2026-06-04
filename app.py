import streamlit as st
from docxtpl import DocxTemplate
from datetime import datetime
import io

# Configuration de la page
st.set_page_config(page_title="Générateur de Documents - Santé BTP", layout="centered")
st.title("Saisie de documents - Dr AVENEL")

# --- ÉTAPE 2A : LA BASE DE DONNÉES DES TEXTES TYPES ---
# C'est ici que tu pourras ajouter tes futurs courriers types plus tard !
TEXTES_TYPES = {
    "Ordonnance Plombémie": (
        "ORDONNANCE MEDICALE\n\n"
        "Pratiquer dans un laboratoire d'analyses médicales avant le début du chantier plomb :\n"
        "- NFS plaquettes\n"
        "- créatininémie\n"
        "- plombémie\n\n"
        "Puis toutes les 5 semaines pendant la durée du chantier plomb :\n"
        "- Plombémie\n\n"
        "Puis 1 semaine après la fin du chantier plomb :\n"
        "- Plombémie"
    ),
    # Tu pourras ajouter tes futurs modèles ici sous cette forme :
    # "Nom du modèle": "Le texte complet...",
}

# --- ÉTAPE 2B : L'INTERFACE D'ACCUEIL ---
# Choix principal : Courrier ou Ordonnance
choix_principal = st.radio("Que voulez-vous rédiger ?", ["Courrier", "Ordonnance"], horizontal=True)

# Initialisation des variables du formulaire
destinataire = ""
objet = ""
corps_du_texte = ""
date_du_jour = datetime.today().strftime('%d/%m/%Y')

# --- ÉTAPE 2C : LOGIQUE DES SENS-OPTIONS ---
if choix_principal == "Courrier":
    # Option pour les courriers
    option_courrier = st.selectbox("Type de courrier :", ["Courrier vierge", "Courrier types (À venir)"])
    
    if option_courrier == "Courrier vierge":
        date_du_jour = st.text_input("Date du jour", value=date_du_jour)
        destinataire = st.text_area("A l'attention de :", placeholder="Nom du destinataire, Adresse...")
        objet = st.text_input("Objet :", placeholder="Ex: État de santé de M. X...")
        corps_du_message = st.text_area("Corps du message :", height=250)
        
        # On assemble l'objet et le corps pour le Word
        if objet:
            corps_du_texte = f"Objet : {objet}\n\n{corps_du_message}"
        else:
            corps_du_texte = corps_du_message

elif choix_principal == "Ordonnance":
    # Option pour les ordonnances
    option_ordonnance = st.selectbox("Type d'ordonnance :", ["Ordonnance Plombémie"])
    
    if option_ordonnance == "Ordonnance Plombémie":
        date_du_jour = st.text_input("Date du jour", value=date_du_jour)
        
        # Champs spécifiques pour le salarié
        nom_salarie = st.text_input("Nom et Prénom du salarié :")
        date_naissance = st.text_input("Date de naissance (optionnel) :")
        
        # Construction du bloc destinataire et du texte
        if date_naissance:
            destinataire = f"M. / Mme {nom_salarie}\nNé(e) le {date_naissance}"
        else:
            destinataire = f"M. / Mme {nom_salarie}"
            
        corps_du_texte = TEXTES_TYPES["Ordonnance Plombémie"]

# --- ÉTAPE 2D : LA GÉNÉRATION DU WORD ---
st.markdown("---")

# Bouton de génération (uniquement si un destinataire est saisi pour éviter les bêtises)
if destinataire:
    if st.button("Visualiser / Générer le document Word", type="primary"):
        try:
            # Chargement du template master
            doc = DocxTemplate("master_template.docx")
            
            # Dictionnaire des données à injecter
            context = {
                "destinataire": destinataire,
                "date_du_jour": date_du_jour,
                "corps_du_texte": corps_du_texte
            }
            
            # Injection des données
            doc.render(context)
            
            # Sauvegarde en mémoire pour le téléchargement sans stocker de fichier sur le serveur
            bio = io.BytesIO()
            doc.save(bio)
            bio.seek(0)
            
            # Bouton de téléchargement
            nom_fichier = f"{choix_principal}_{date_du_jour.replace('/', '-')}.docx"
            st.download_button(
                label="📥 Télécharger le document complété",
                data=bio,
                file_name=nom_fichier,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            st.success("Le document est prêt !")
            
        except FileNotFoundError:
            st.error("Erreur : Le fichier 'master_template.docx' est introuvable. Placez-le dans le même dossier que ce script.")
else:
    st.info("Veuillez remplir au moins le nom du salarié ou le destinataire pour pouvoir générer le document.")
