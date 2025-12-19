import os
import streamlit as st
import pandas as pd
from datetime import date
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
from io import BytesIO

# Configuration de base
st.set_page_config(page_title="QCM Formation", layout="centered")
st.title("QCM - Recherche en Soins Premiers")

RESULT_FILE = "resultats_quiz.csv"
ADMINS = [("bayen", "marc"), ("steen", "johanna")]

# Initialisation du fichier CSV
if not os.path.exists(RESULT_FILE):
    pd.DataFrame(columns=["Nom", "Prénom", "Email", "Score", "Résultat", "Date"]).to_csv(RESULT_FILE, index=False)

def creer_pdf(nom_complet, score, date_str):
    """Crée un PDF avec le diplôme complet et tout centré"""
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)

    # Largeur de la page
    page_width, _ = letter
    center_x = page_width / 2

    # Dessiner le logo CNGE FORMATION (centré en haut)
    dessiner_logo_cnge(can, center_x)

    # Texte du diplôme (tout centré)
    can.setFillColorRGB(0, 0, 0)

    # Hereby Certifies that
    can.setFont("Helvetica", 12)
    can.drawCentredString(center_x, 600, "Hereby Certifies that")

    # Nom du participant
    can.setFont("Helvetica-Bold", 16)
    can.drawCentredString(center_x, 570, nom_complet)

    # Texte du cours
    can.setFont("Helvetica", 12)
    can.drawCentredString(center_x, 540, "has completed the e-learning course")

    can.setFont("Helvetica-Bold", 14)
    can.drawCentredString(center_x, 510, "RECHERCHE EN SOINS PREMIERS")

    can.setFont("Helvetica", 12)
    can.drawCentredString(center_x, 490, "Formation aux bonnes pratiques cliniques")
    can.drawCentredString(center_x, 470, "(ICH E6 (R3))")

    # Score
    can.drawCentredString(center_x, 440, f"with a score of {int(score*100)}%")

    # Date
    can.drawCentredString(center_x, 420, f"On {date_str}")

    # Texte de reconnaissance
    can.setFont("Helvetica-Oblique", 10)
    can.drawCentredString(center_x, 380, "This e-learning course has been formally recognised for its quality and content by:")
    can.drawCentredString(center_x, 360, "the following organisations and institutions")
    can.drawCentredString(center_x, 340, "Collège National des Généralistes Enseignants Formation")
    can.drawCentredString(center_x, 320, "https://www.cnge-formation.fr/")

    # Encadré TransCelerate avec bordure fine (centré)
    can.setFont("Helvetica", 8)
    can.setLineWidth(0.2)
    can.rect(center_x - 90, 280, 180, 40, stroke=1, fill=0)  # Encadré plus large

    # Texte dans l'encadré (centré et justifié)
    text = can.beginText(center_x - 85, 310)  # Positionné en haut de l'encadré
    text.setFont("Helvetica", 8)
    text.textLine("This ICH E6 GCP Investigator Site Training meets the Minimum Criteria for")
    text.textLine("ICH GCP Investigator Site Personnel Training identified by TransCelerate BioPharma")
    text.textLine("as necessary to enable mutual recognition of GCP training among trial sponsors.")
    can.drawText(text)

    # Version (centrée)
    can.setFont("Helvetica-Oblique", 8)
    can.drawCentredString(center_x, 230, "Version number 1-2025")

    can.save()
    packet.seek(0)
    return packet.getvalue()

def dessiner_logo_cnge(can, center_x):
    """Dessine le logo CNGE FORMATION centré"""
    # Position du logo (centré en haut)
    logo_x = center_x - 50

    # Carré gris
    can.setFillColor(HexColor('#cccccc'))
    can.rect(logo_x, 720, 40, 40, fill=1, stroke=0)

    # Ligne orange diagonale (au-dessus du carré)
    can.setStrokeColor(HexColor('#F5A623'))
    can.setLineWidth(3)
    can.line(logo_x + 10, 760, logo_x + 90, 730)  # Position ajustée pour être au-dessus

    # Texte CNGE en rouge
    can.setFillColor(HexColor('#C0392B'))
    can.setFont("Helvetica-Bold", 16)
    can.drawString(logo_x + 5, 670, "CNGE")

    # Fond orange pour FORMATION
    can.setFillColor(HexColor('#F5A623'))
    can.rect(logo_x - 5, 650, 50, 15, fill=1)

    # Texte FORMATION en blanc
    can.setFillColor(HexColor('#ffffff'))
    can.setFont("Helvetica-Bold", 10)
    can.drawString(logo_x, 653, "FORMATION")

# Gestion de la session
if "step" not in st.session_state:
    st.session_state.step = "login"

# Page de login
if st.session_state.step == "login":
    for key in ["nom_input", "prenom_input", "email_input"]:
        if key not in st.session_state:
            st.session_state[key] = ""

    nom = st.text_input("Nom", value=st.session_state.nom_input)
    prenom = st.text_input("Prénom", value=st.session_state.prenom_input)
    is_admin = (nom.lower(), prenom.lower()) in [(a[0].lower(), a[1].lower()) for a in ADMINS]
    email = st.text_input("Email", value=st.session_state.email_input) if not is_admin else ""

    if st.button("Continuer"):
        st.session_state.nom_input = nom.strip()
        st.session_state.prenom_input = prenom.strip()
        st.session_state.email_input = email.strip()

        if not st.session_state.nom_input or not st.session_state.prenom_input:
            st.warning("Merci de remplir le nom et le prénom")
        elif not is_admin and not st.session_state.email_input:
            st.warning("Merci de renseigner votre email")
        else:
            st.session_state.nom = st.session_state.nom_input
            st.session_state.prenom = st.session_state.prenom_input
            st.session_state.email = st.session_state.email_input
            st.session_state.is_admin = is_admin
            st.session_state.step = "admin" if is_admin else "quiz"

# Page admin
if st.session_state.step == "admin":
    st.subheader("Résultats des participants")
    df = pd.read_csv(RESULT_FILE)
    st.dataframe(df)

    if st.button("Réinitialiser la liste"):
        df.iloc[0:0].to_csv(RESULT_FILE, index=False)
        st.success("Liste effacée")

# Page quiz avec questions Oui/Non
if st.session_state.step == "quiz":
    st.subheader(f"Bienvenue {st.session_state.prenom} {st.session_state.nom}")

    questions = [
        ("Les Bonnes Pratiques Cliniques visent-elles à protéger les sujets de recherche ?", ["Oui", "Non"], 0),
        ("L'investigateur principal est-il responsable de la conduite de l'essai sur un lieu précis ?", ["Oui", "Non"], 0),
        ("Le promoteur est-il responsable de la gestion de l'essai ?", ["Oui", "Non"], 0),
        ("Le protocole de recherche doit-il décrire le rationnel scientifique ?", ["Oui", "Non"], 0),
        ("Les données sources doivent-elles être attribuables ?", ["Oui", "Non"], 0)
    ]

    if "reponses_quiz" not in st.session_state:
        st.session_state.reponses_quiz = [None] * len(questions)

    for i, (q, options, bonne) in enumerate(questions):
        st.session_state.reponses_quiz[i] = st.radio(
            q,
            options=options,
            index=None if st.session_state.reponses_quiz[i] is None else options.index(st.session_state.reponses_quiz[i]),
            key=f"q{i}"
        )

    if st.button("Valider le QCM"):
        score = 0
        corrections = []

        for i, (q, options, bonne) in enumerate(questions):
            user_rep = st.session_state.reponses_quiz[i]
            bonne_rep = options[bonne]
            if user_rep == bonne_rep:
                score += 1
            corrections.append((q, user_rep, bonne_rep, user_rep == bonne_rep))

        resultat = "Réussi" if score >= 3 else "Échoué"

        # Enregistrement CSV
        new_row = {
            "Nom": st.session_state.nom,
            "Prénom": st.session_state.prenom,
            "Email": st.session_state.email,
            "Score": f"{score}/{len(questions)}",
            "Résultat": resultat,
            "Date": date.today().strftime("%d/%m/%Y")
        }

        new_row_df = pd.DataFrame([new_row])
        new_row_df.to_csv(RESULT_FILE, mode='a', header=False, index=False)

        st.markdown("---")
        st.subheader(f"Score : {score}/{len(questions)} — {resultat}")

        st.markdown("### Correction détaillée")
        for q, user, bonne, ok in corrections:
            if ok:
                st.success(f"{q} → Bonne réponse : {bonne}")
            else:
                st.error(f"{q} → Ta réponse : {user} | Bonne réponse : {bonne}")

        # Générer le PDF
        nom_complet = f"{st.session_state.prenom} {st.session_state.nom}"
        date_str = date.today().strftime("%d/%m/%Y")
        pdf_bytes = creer_pdf(nom_complet, score/len(questions), date_str)

        if pdf_bytes:
            st.download_button(
                "Télécharger le diplôme PDF",
                pdf_bytes,
                file_name=f"diplome_{st.session_state.nom}_{st.session_state.prenom}.pdf",
                mime="application/pdf"
            )

    if st.button("🔁 Refaire le QCM"):
        st.session_state.reponses_quiz = [None] * len(questions)
        st.rerun()


