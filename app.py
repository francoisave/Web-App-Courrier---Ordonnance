import streamlit as st
from docxtpl import DocxTemplate
from datetime import datetime
import io

# ============================================================
# CONFIGURATION DE LA PAGE
# ============================================================
st.set_page_config(
    page_title="Documents médicaux – Dr AVENEL",
    page_icon="📋",
    layout="centered"
)
st.title("📋 Documents médicaux – Dr AVENEL")

# ============================================================
# BASE DE DONNÉES DES TEXTES TYPES
# ============================================================
# Pour AJOUTER un nouveau courrier : ajoutez une entrée dans le dictionnaire
# correspondant, en utilisant {nom_salarie} comme placeholder si besoin.
# ============================================================

# --- Courriers Médecin Traitant (3 variantes) ---
COURRIERS_MEDECIN_TRAITANT = {

    "Vierge":
        "Cher confrère, chère consœur,\n\n\n\nConfraternellement,",

    "Prolonger arrêt – inaptitude probable": (
        "Cher confrère, chère consœur,\n\n"
        "J'ai revu en visite de pré-reprise {nom_salarie} que vous suivez dans un contexte de \n\n"
        "{nom_salarie} me rapporte \n\n"
        "Une reprise à son poste de travail de … n'est pas envisageable et une situation "
        "d'inaptitude à la reprise est très probable.\n\n"
        "Pourriez-vous lui prolonger son arrêt de travail si vous êtes d'accord le temps que "
        "je rassemble les documents nécessaires à l'inaptitude (fiche entreprise, étude de poste, "
        "échange avec l'employeur) ?\n\n"
        "Confraternellement,"
    ),

    "Pas d'inaptitude indiquée": (
        "Cher confrère, chère consœur,\n\n"
        "J'ai revu ce jour en visite de pré-reprise {nom_salarie}.\n\n"
        "{nom_salarie} me rapporte \n\n"
        "L'inaptitude n'est pas indiquée. Je vous laisse le soin de lui prolonger son arrêt "
        "de travail si vous l'estimez nécessaire.\n\n"
        "Restant à votre disposition pour tout renseignement complémentaire.\n\n"
        "Confraternellement,"
    ),
}

# --- Courriers vers d'autres médecins ---
# Pour ajouter un médecin spécialiste : ajoutez une entrée ici.
COURRIERS_AUTRES_MEDECINS = {

    "Médecin Conseil – invalidité probable": (
        "Cher confrère,\n\n"
        "J'ai reçu en consultation de pré-reprise {nom_salarie}.\n\n"
        "[Compléter : pathologie, limitations fonctionnelles, éléments cliniques]\n\n"
        "La reprise de son poste de travail ne semble pas compatible avec son état de santé "
        "actuel, une situation d'inaptitude à son poste est probable.\n"
        "Une invalidité à l'issue de son arrêt serait justifiée à mon sens.\n\n"
        "Confraternellement,"
    ),

    "Médecin ORL – bilan auditif": (
        "Cher confrère,\n\n"
        "J'ai vu en consultation {nom_salarie}, employé(e) en tant que [POSTE].\n\n"
        "{nom_salarie} présente une altération notable de son audition de manière bilatérale. "
        "Il/Elle est exposé(e) de manière chronique aux bruits dans le cadre de son activité "
        "professionnelle, avec port de protections auditives.\n\n"
        "Je sollicite votre expertise pour une évaluation approfondie de l'état auditif "
        "et voir si un appareillage est nécessaire.\n\n"
        "Je vous prie de recevoir l'expression de mes salutations distinguées.\n\n"
        "Confraternellement,"
    ),

    "Psychiatre – avis pré-reprise": (
        "Cher confrère, chère consœur,\n\n"
        "J'ai vu en consultation de pré-reprise {nom_salarie} qui présente [PATHOLOGIE], "
        "en arrêt depuis [DATE].\n\n"
        "{nom_salarie} ne se sent pas capable de reprendre son poste ce jour "
        "et présente [SYMPTÔMES].\n\n"
        "Une inaptitude à son poste est probable à la reprise.\n\n"
        "Pourriez-vous me donner votre avis sur la nature de la pathologie, sa sévérité, "
        "son évolution / traitement, éventuellement son pronostic ?\n\n"
        "Confraternellement,"
    ),

    "Demande certificat Maladie Professionnelle": (
        "Cher confrère, Chère Consœur,\n\n"
        "Je vois ce jour {nom_salarie} à sa demande en visite de préreprise.\n\n"
        "Sa pathologie entre à mon avis dans le cadre du tableau de maladie professionnelle "
        "n° [N°] (avec une date de 1ère constatation à celle de l'imagerie réalisée).\n\n"
        "Qu'en pensez-vous ? Pouvez-vous lui rédiger le certificat médical initial ?\n\n"
        "J'envoie des préconisations à l'employeur en vue de la reprise.\n\n"
        "Merci par avance de ce que vous ferez pour lui.\n\n"
        "Bien confraternellement,"
    ),
}

# --- Courriers destinés aux salariés ---
# Pour ajouter un nouveau courrier salarié : ajoutez une entrée ici.
COURRIERS_SALARIES = {

    "Résultats Amiante – Normaux": (
        "Objet : Suivi professionnel post-exposition aux poussières d'amiante\n\n"
        "Madame, Monsieur,\n\n"
        "À la suite de votre dernière consultation de médecine du travail, veuillez trouver "
        "en copie vos résultats dans le cadre de votre suivi professionnel post-exposition "
        "aux poussières d'amiante.\n\n"
        "Les résultats sont normaux, aucune anomalie significative n'a été décelée.\n\n"
        "Cordialement,"
    ),

    "Résultats Amiante – Anormaux": (
        "Objet : Suivi professionnel post-exposition aux poussières d'amiante\n\n"
        "Madame, Monsieur,\n\n"
        "À la suite de votre dernière consultation de médecine du travail, veuillez trouver "
        "en copie vos résultats de scanner thoracique dans le cadre de votre suivi professionnel "
        "post-exposition à l'amiante.\n\n"
        "[Compléter avec les résultats spécifiques du patient]\n\n"
        "L'exposition à l'amiante peut amener à développer des plaques pleurales dans les "
        "poumons.\n\n"
        "Cordialement,"
    ),

    "Résultats Silice – Normaux": (
        "Objet : Suivi professionnel post-exposition aux poussières de silice\n\n"
        "Madame, Monsieur,\n\n"
        "À la suite de votre dernière consultation de médecine du travail, veuillez trouver "
        "en copie vos résultats dans le cadre de votre suivi professionnel post-exposition "
        "aux poussières de silice.\n\n"
        "Les résultats sont normaux, aucune anomalie significative n'a été décelée.\n\n"
        "Cordialement,"
    ),

    "Suggestion visite pré-reprise": (
        "Madame, Monsieur,\n\n"
        "J'ai récemment été en contact avec votre employeur et nous en sommes venus à discuter "
        "de votre absence pour maladie.\n\n"
        "Il me paraît important que je vous voie en visite de pré-reprise (consultation de "
        "médecine du travail pendant l'arrêt) afin de faire le point sur votre situation "
        "médicale / professionnelle et ainsi anticiper la fin de l'arrêt pour éviter la "
        "récidive, la pérennisation ou l'aggravation de votre problème de santé :\n\n"
        "- Reprise sans mesure particulière ?\n"
        "- Aménagement de poste ?\n"
        "- Reclassement au sein de l'entreprise ?\n"
        "- Reconversion extérieure à l'entreprise ?\n\n"
        "Il n'y aura pas d'avis d'aptitude ou d'inaptitude, il s'agit simplement de préparer "
        "l'avenir et sécuriser votre parcours professionnel.\n\n"
        "Je vous incite donc à appeler mon assistante au 02 35 71 85 90 pour demander une "
        "visite de pré-reprise.\n\n"
        "Merci d'apporter le jour de la consultation tout document médical utile "
        "(comptes-rendus, ordonnances etc.).\n\n"
        "Cordialement,"
    ),

    "Reconversion professionnelle – Accord": (
        "Objet : Reconversion professionnelle\n\n"
        "Madame, Monsieur,\n\n"
        "J'ai reçu en consultation {nom_salarie}, au vu de son état de santé actuel "
        "une reconversion professionnelle est souhaitable.\n\n"
        "Il n'y aura pas à priori de contre-indication médicale pour effectuer le métier "
        "et la formation de [METIER].\n\n"
        "Cordialement,"
    ),
}

# --- Ordonnances ---
# Pour ajouter une ordonnance : ajoutez une entrée ici.
ORDONNANCES = {

    "Plombémie": (
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

    # === AJOUTER ICI : "Amiante – Scanner", "Amiante – Radio", "Silice" ===
}

# ============================================================
# FONCTIONS UTILITAIRES
# ============================================================

def injecter_nom(texte_template: str, nom_salarie: str) -> str:
    """Remplace {nom_salarie} dans le texte type par le nom saisi."""
    nom = nom_salarie.strip() if nom_salarie and nom_salarie.strip() else "[NOM SALARIÉ]"
    try:
        return texte_template.format(nom_salarie=nom)
    except (KeyError, ValueError):
        return texte_template


def generer_docx(date_du_jour: str, destinataire: str, corps_du_texte: str) -> io.BytesIO:
    """Injecte les données dans le template Word et retourne un BytesIO."""
    doc = DocxTemplate("master_template.docx")
    doc.render({
        "date_du_jour": date_du_jour,
        "destinataire": destinataire,
        "corps_du_texte": corps_du_texte,
    })
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio


# ============================================================
# SESSION STATE – initialisation
# ============================================================
if "last_type_key" not in st.session_state:
    st.session_state["last_type_key"] = ""
if "corps_texte" not in st.session_state:
    st.session_state["corps_texte"] = ""
if "date_saisie" not in st.session_state:
    st.session_state["date_saisie"] = datetime.today().strftime('%d/%m/%Y')


# ============================================================
# CALLBACKS – pour les boutons qui modifient le corps du texte
# ============================================================

def cb_recharger(template_dict: dict, sous_type_key: str, nom_key: str):
    """Recharge le corps du texte avec le nom du salarié courant."""
    nom = st.session_state.get(nom_key, "")
    st.session_state["corps_texte"] = injecter_nom(template_dict[sous_type_key], nom)


# ============================================================
# VARIABLES DE SORTIE (réinitialisées à chaque render)
# ============================================================
destinataire = ""
corps_du_texte = ""
nom_fichier_prefix = "Document"
can_generate = False

# ============================================================
# CHOIX PRINCIPAL : COURRIER OU ORDONNANCE
# ============================================================
choix_principal = st.radio(
    "Que voulez-vous rédiger ?",
    ["Courrier", "Ordonnance"],
    horizontal=True
)
st.markdown("---")

# ===========================================================
#  BLOC COURRIER
# ===========================================================
if choix_principal == "Courrier":

    categorie = st.selectbox(
        "Catégorie :",
        [
            "Courrier vierge",
            "Médecin traitant",
            "Autre médecin",
            "Courrier pour salarié",
        ],
        key="categorie_courrier"
    )

    # --------------------------------------------------------
    # COURRIER VIERGE
    # --------------------------------------------------------
    if categorie == "Courrier vierge":
        type_key = "vierge"
        if st.session_state["last_type_key"] != type_key:
            st.session_state["last_type_key"] = type_key
            st.session_state["corps_texte"] = ""

        date_du_jour    = st.text_input("Date", key="date_saisie")
        destinataire    = st.text_area("A l'attention de :", placeholder="Nom, adresse du destinataire...", key="dest_vierge")
        objet           = st.text_input("Objet :", placeholder="Ex : Suivi de M. X", key="objet_vierge")
        corps_msg       = st.text_area("Corps du message :", height=250, key="corps_texte")

        corps_du_texte  = f"Objet : {objet}\n\n{corps_msg}" if objet.strip() else corps_msg
        nom_fichier_prefix = "Courrier"
        can_generate    = bool(destinataire.strip())

    # --------------------------------------------------------
    # MÉDECIN TRAITANT
    # --------------------------------------------------------
    elif categorie == "Médecin traitant":
        sous_type = st.selectbox(
            "Type de courrier :",
            list(COURRIERS_MEDECIN_TRAITANT.keys()),
            key="sous_type_mt"
        )
        type_key = f"mt_{sous_type}"

        # Reset automatique du corps quand le type de courrier change
        if st.session_state["last_type_key"] != type_key:
            st.session_state["last_type_key"] = type_key
            nom_courant = st.session_state.get("nom_salarie_mt", "")
            st.session_state["corps_texte"] = injecter_nom(
                COURRIERS_MEDECIN_TRAITANT[sous_type], nom_courant
            )

        date_du_jour = st.text_input("Date", key="date_saisie")
        nom_salarie  = st.text_input(
            "Concernant :",
            placeholder="Nom et Prénom du salarié",
            key="nom_salarie_mt"
        )
        destinataire = st.text_area(
            "A l'attention de :",
            placeholder="Dr [Nom], [Adresse]...",
            key="dest_mt"
        )

        # Bouton pour insérer le nom dans le texte type
        st.button(
            "🔄 Insérer le nom dans le texte",
            on_click=cb_recharger,
            args=(COURRIERS_MEDECIN_TRAITANT, sous_type, "nom_salarie_mt"),
            key="btn_reload_mt",
            help="Remplace [NOM SALARIÉ] par le nom saisi ci-dessus"
        )

        corps_msg = st.text_area("Corps du message :", height=300, key="corps_texte")

        # Le "Concernant" s'ajoute en tête du corps injecté dans le Word
        if nom_salarie.strip():
            corps_du_texte = f"Concernant : {nom_salarie}\n\n{corps_msg}"
        else:
            corps_du_texte = corps_msg

        nom_fichier_prefix = f"Courrier_MT_{sous_type[:25].replace(' ', '_')}"
        can_generate = bool(destinataire.strip() or nom_salarie.strip())

    # --------------------------------------------------------
    # AUTRE MÉDECIN (Conseil, ORL, Psychiatre, MP...)
    # --------------------------------------------------------
    elif categorie == "Autre médecin":
        sous_type = st.selectbox(
            "Spécialité / type :",
            list(COURRIERS_AUTRES_MEDECINS.keys()),
            key="sous_type_am"
        )
        type_key = f"am_{sous_type}"

        if st.session_state["last_type_key"] != type_key:
            st.session_state["last_type_key"] = type_key
            nom_courant = st.session_state.get("nom_salarie_am", "")
            st.session_state["corps_texte"] = injecter_nom(
                COURRIERS_AUTRES_MEDECINS[sous_type], nom_courant
            )

        date_du_jour = st.text_input("Date", key="date_saisie")
        nom_salarie  = st.text_input(
            "Concernant :",
            placeholder="Nom et Prénom du salarié",
            key="nom_salarie_am"
        )
        destinataire = st.text_area(
            "A l'attention de :",
            placeholder="Dr [Nom], Spécialité, Adresse...",
            key="dest_am"
        )

        st.button(
            "🔄 Insérer le nom dans le texte",
            on_click=cb_recharger,
            args=(COURRIERS_AUTRES_MEDECINS, sous_type, "nom_salarie_am"),
            key="btn_reload_am",
            help="Remplace [NOM SALARIÉ] par le nom saisi ci-dessus"
        )

        corps_msg = st.text_area("Corps du message :", height=300, key="corps_texte")

        if nom_salarie.strip():
            corps_du_texte = f"Concernant : {nom_salarie}\n\n{corps_msg}"
        else:
            corps_du_texte = corps_msg

        nom_fichier_prefix = f"Courrier_{sous_type[:25].replace(' ', '_')}"
        can_generate = bool(destinataire.strip() or nom_salarie.strip())

    # --------------------------------------------------------
    # COURRIER POUR SALARIÉ
    # --------------------------------------------------------
    elif categorie == "Courrier pour salarié":
        sous_type = st.selectbox(
            "Type de courrier :",
            list(COURRIERS_SALARIES.keys()),
            key="sous_type_sal"
        )
        type_key = f"sal_{sous_type}"

        if st.session_state["last_type_key"] != type_key:
            st.session_state["last_type_key"] = type_key
            nom_courant = st.session_state.get("nom_salarie_sal", "")
            st.session_state["corps_texte"] = injecter_nom(
                COURRIERS_SALARIES[sous_type], nom_courant
            )

        date_du_jour = st.text_input("Date", key="date_saisie")
        nom_salarie  = st.text_input(
            "Concernant :",
            placeholder="Nom et Prénom du salarié",
            key="nom_salarie_sal"
        )
        destinataire = st.text_area(
            "A l'attention de :",
            placeholder="Nom et adresse du salarié...",
            key="dest_sal"
        )

        st.button(
            "🔄 Insérer le nom dans le texte",
            on_click=cb_recharger,
            args=(COURRIERS_SALARIES, sous_type, "nom_salarie_sal"),
            key="btn_reload_sal",
            help="Remplace [NOM SALARIÉ] par le nom saisi ci-dessus"
        )

        corps_msg = st.text_area("Corps du message :", height=300, key="corps_texte")

        corps_du_texte = corps_msg
        nom_fichier_prefix = (
            f"Courrier_{sous_type[:25].replace(' ', '_').replace('–', '-')}"
        )
        can_generate = bool(destinataire.strip())

# ===========================================================
#  BLOC ORDONNANCE
# ===========================================================
elif choix_principal == "Ordonnance":

    options_ordo = list(ORDONNANCES.keys()) + ["Amiante (À venir)", "Silice (À venir)"]
    sous_type = st.selectbox("Type d'ordonnance :", options_ordo, key="sous_type_ordo")

    if sous_type in ["Amiante (À venir)", "Silice (À venir)"]:
        st.info("🚧 Cette ordonnance type sera disponible prochainement.")
    else:
        date_du_jour   = st.text_input("Date", key="date_saisie")
        nom_salarie    = st.text_input("Nom et Prénom du salarié :", key="nom_salarie_ordo")
        date_naissance = st.text_input("Date de naissance (optionnel) :", key="ddn_ordo")

        if nom_salarie.strip():
            if date_naissance.strip():
                destinataire = f"M. / Mme {nom_salarie}\nNé(e) le {date_naissance}"
            else:
                destinataire = f"M. / Mme {nom_salarie}"

        corps_du_texte     = ORDONNANCES[sous_type]
        nom_fichier_prefix = f"Ordonnance_{sous_type.replace(' ', '_')}"
        can_generate       = bool(nom_salarie.strip())

# ===========================================================
#  GÉNÉRATION DU DOCUMENT WORD
# ===========================================================
st.markdown("---")

if can_generate:
    if st.button("📄 Générer le document Word", type="primary"):
        try:
            bio = generer_docx(
                st.session_state.get("date_saisie", datetime.today().strftime('%d/%m/%Y')),
                destinataire,
                corps_du_texte
            )
            date_str   = st.session_state.get("date_saisie", "").replace("/", "-")
            nom_fichier = f"{nom_fichier_prefix}_{date_str}.docx"
            st.download_button(
                label="📥 Télécharger le document",
                data=bio,
                file_name=nom_fichier,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            st.success("✅ Document prêt au téléchargement !")
        except FileNotFoundError:
            st.error(
                "❌ Fichier 'master_template.docx' introuvable. "
                "Assurez-vous qu'il est dans le même dossier que app.py."
            )
        except Exception as e:
            st.error(f"❌ Erreur lors de la génération : {e}")
else:
    st.info("ℹ️ Remplissez les champs obligatoires pour activer la génération.")
