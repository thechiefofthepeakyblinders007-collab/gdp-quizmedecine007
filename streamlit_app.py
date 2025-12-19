import os
import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import date

# Configuration de base
st.set_page_config(page_title="QCM Formation", layout="centered")
st.title("QCM Simplifié - Recherche en Soins Premiers")

RESULT_FILE = "resultats_quiz.csv"
ADMINS = [("bayen", "marc"), ("steen", "johanna")]

# Initialisation du fichier CSV
if not os.path.exists(RESULT_FILE):
    pd.DataFrame(columns=["Nom", "Prénom", "Email", "Score", "Résultat", "Date"]).to_csv(RESULT_FILE, index=False)

# Fonction pour créer le diplôme PDF
def creer_diplome(nom, prenom, score):
    pdf = FPDF()
    pdf.add_page()

    # Logo simplifié
    pdf.set_fill_color(255, 255, 255)
    pdf.rect(80, 10, 50, 30, 'DF')
    pdf.set_draw_color(245, 166, 35)
    pdf.set_line_width(2)
    pdf.line(80, 20, 130, 20)
    pdf.line(80, 20, 80, 40)
    pdf.line(130, 20, 130, 40)
    pdf.line(80, 40, 130, 40)
    pdf.set_text_color(192, 57, 43)
    pdf.set_font("Arial", "B", 14)
    pdf.text(90, 45, "CNGE")
    pdf.set_text_color(245, 166, 35)
    pdf.text(85, 55, "FORMATION")

    # Contenu du diplôme
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "", 12)
    pdf.ln(50)
    pdf.cell(0, 10, "Hereby Certifies that", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"{prenom} {nom}", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "has completed the e-learning course", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "RECHERCHE EN SOINS PREMIERS", ln=True, align="C")
    pdf.set_font("Arial", "", 14)
    pdf.cell(0, 10, "Formation aux bonnes pratiques cliniques", ln=True, align="C")
    pdf.cell(0, 10, "(ICH E6 (R3))", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"with a score of {int(score*100)}%", ln=True, align="C")
    pdf.ln(10)
    today = date.today().strftime("%d/%m/%Y")
    pdf.cell(0, 10, f"On {today}", ln=True, align="C")

    return pdf.output(dest="S").encode("latin-1")

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

        resultat = "Réussi" if score >= 3 else "Échoué"  # 3 bonnes réponses sur 5 pour réussir

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

        pdf_bytes = creer_diplome(st.session_state.nom, st.session_state.prenom, score/len(questions))
        if pdf_bytes:
            st.download_button(
                "Télécharger le diplôme PDF",
                pdf_bytes,
                file_name="diplome_CNGE.pdf",
                mime="application/pdf"
            )

    if st.button("🔁 Refaire le QCM"):
        st.session_state.reponses_quiz = [None] * len(questions)
        st.experimental_rerun()

