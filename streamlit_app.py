import os
import streamlit as st
import pandas as pd
from datetime import date
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
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
    # Créer un nouveau PDF
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)

    # Dessiner le logo CNGE FORMATION
    can.setFillColorRGB(0.8, 0.8, 0.8)  # Gris
    can.rect(20, 700, 30, 30, fill=1)  # Carré gris
    can.setStrokeColorRGB(245/255, 166/255, 35/255)  # Orange
    can.setLineWidth(3)
    can.line(50, 715, 90, 695)  # Ligne orange diagonale

    # Texte CNGE en rouge
    can.setFillColorRGB(192/255, 57/255, 43/255)  # Rouge
    can.setFont("Helvetica-Bold", 14)
    can.drawString(25, 660, "CNGE")

    # Fond orange pour FORMATION
    can.setFillColorRGB(245/255, 166/255, 35/255)  # Orange
    can.rect(15, 640, 40, 10, fill=1)

    # Texte FORMATION en blanc
    can.setFillColorRGB(1, 1, 1)  # Blanc
    can.setFont("Helvetica-Bold", 10)
    can.drawString(20, 642, "FORMATION")

    # Texte du diplôme
    can.setFillColorRGB(0, 0, 0)  # Noir
    can.setFont("Helvetica", 12)
    can.drawString(100, 600, "Hereby Certifies that")

    can.setFont("Helvetica-Bold", 16)
    can.drawString(100, 570, nom_complet)

    can.setFont("Helvetica", 12)
    can.drawString(100, 540, "has completed the e-learning course")

    can.setFont("Helvetica-Bold", 14)
    can.drawString(100, 510, "RECHERCHE EN SOINS PREMIERS")
    can.setFont("Helvetica", 12)
    can.drawString(100, 490, "Formation aux bonnes pratiques cliniques")
    can.drawString(100, 470, "(ICH E6 (R3))")

    # Score
    can.drawString(100, 440, f"with a score of {int(score*100)}%")

    # Date
    can.drawString(100, 420, f"On {date_str}")

    # Texte de reconnaissance
    can.setFont("Helvetica-Oblique", 10)
    can.drawString(100, 380, "This e-learning course has been formally recognised for its quality and content by:")
    can.drawString(100, 360, "the following organisations and institutions")
    can.drawString(100, 340, "Collège National des Généralistes Enseignants Formation")
    can.drawString(100, 320, "https://www.cnge-formation.fr/")

    # Encadré TransCelerate
    can.setFont("Helvetica", 8)
    can.rect(50, 280, 120, 30, stroke=1, fill=0)
    text = can.beginText(55, 290)
    text.textLine("This ICH E6 GCP Investigator Site Training meets the Minimum Criteria for")
    text.textLine("ICH GCP Investigator Site Personnel Training identified by TransCelerate BioPharma")
    text.textLine("as necessary to enable mutual recognition of GCP training among trial sponsors.")
    can.drawText(text)

    # Version
    can.setFont("Helvetica-Oblique", 8)
    can.drawString(100, 250, "Version number 1-2025")

    can.save()
    packet.seek(0)
    return packet.getvalue()

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


