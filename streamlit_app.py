import streamlit as st
import pandas as pd
from fpdf import FPDF
from io import BytesIO
import os

# ---------------- CONFIG ----------------
st.set_page_config(page_title="QCM Médecine", layout="centered")
st.title("QCM Médecine")

RESULT_FILE = "resultats_quiz.csv"

ADMINS = [
    ("bayen", "marc"),
    ("steen", "johanna")
]

# ---------------- CSV ----------------
if not os.path.exists(RESULT_FILE):
    pd.DataFrame(
        columns=["Nom", "Prénom", "Email", "Score", "Résultat"]
    ).to_csv(RESULT_FILE, index=False)

# ---------------- PDF ----------------
def creer_pdf(nom, prenom, score):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 26)
    pdf.cell(0, 20, "Diplôme de Réussite", ln=True, align="C")

    pdf.ln(15)
    pdf.set_font("Arial", "", 18)
    pdf.multi_cell(
        0, 10,
        f"Ceci certifie que\n\n{prenom} {nom}\n\n"
        f"a réussi le QCM.\n\nScore : {score}/10",
        align="C"
    )

    pdf.ln(20)
    pdf.set_font("Arial", "I", 14)
    pdf.cell(0, 10, "Signature :", ln=True)
    pdf.cell(0, 10, "Date :", ln=True, align="R")

    buffer = BytesIO()
    buffer.write(pdf.output(dest="S").encode("latin-1"))
    buffer.seek(0)
    return buffer

# ---------------- SESSION ----------------
if "step" not in st.session_state:
    st.session_state.step = "login"

# ---------------- LOGIN ----------------
if st.session_state.step == "login":
    nom = st.text_input("Nom")
    prenom = st.text_input("Prénom")

    is_admin = (nom.lower(), prenom.lower()) in ADMINS

    email = ""
    if not is_admin:
        email = st.text_input("Email")

   if st.button("Continuer"):
    nom = nom.strip()
    prenom = prenom.strip()
    email = email.strip()

    if nom == "" or prenom == "":
        st.warning("Merci de remplir le nom et le prénom")
    elif not is_admin and email == "":
        st.warning("Merci de renseigner votre email")
    else:
        st.session_state.nom = nom
        st.session_state.prenom = prenom
        st.session_state.email = email
        st.session_state.is_admin = is_admin
        st.session_state.step = "admin" if is_admin else "quiz"

# ---------------- ADMIN ----------------
if st.session_state.step == "admin":
    st.subheader("📊 Résultats du QCM")

    df = pd.read_csv(RESULT_FILE)
    st.dataframe(df)

    if st.button("🔄 Réinitialiser les résultats"):
        pd.DataFrame(
            columns=["Nom", "Prénom", "Email", "Score", "Résultat"]
        ).to_csv(RESULT_FILE, index=False)
        st.success("Résultats effacés")

# ---------------- QUIZ ----------------
if st.session_state.step == "quiz":
    st.subheader(
        f"Bonjour {st.session_state.prenom} {st.session_state.nom}"
    )

    questions = [
        ("Capitale de la France ?", ["Paris", "Lyon", "Nice"], "Paris"),
        ("2 + 2 ?", ["3", "4", "5"], "4"),
        ("Couleur du ciel ?", ["Bleu", "Vert", "Rouge"], "Bleu"),
        ("Triangle = combien de côtés ?", ["3", "4", "5"], "3"),
        ("Plus grand océan ?", ["Pacifique", "Atlantique"], "Pacifique"),
        ("Langue du Brésil ?", ["Espagnol", "Portugais"], "Portugais"),
        ("Nombre de continents ?", ["5", "7"], "7"),
        ("Auteur de Hamlet ?", ["Shakespeare", "Molière"], "Shakespeare"),
        ("Planète la plus proche du Soleil ?", ["Mercure", "Mars"], "Mercure"),
        ("Secondes dans une minute ?", ["60", "100"], "60")
    ]

    reponses = []
    for q, options, _ in questions:
        reponses.append(st.radio(q, options))

    if st.button("Valider le QCM"):
        score = 0
        for i, (_, _, bonne) in enumerate(questions):
            if reponses[i] == bonne:
                score += 1

        resultat = "Réussi" if score >= 7 else "Échoué"

        df = pd.read_csv(RESULT_FILE)
        df.loc[len(df)] = [
            st.session_state.nom,
            st.session_state.prenom,
            st.session_state.email,
            f"{score}/10",
            resultat
        ]
        df.to_csv(RESULT_FILE, index=False)

        st.success(f"Score : {score}/10")

        if resultat == "Réussi":
            pdf = creer_pdf(
                st.session_state.nom,
                st.session_state.prenom,
                score
            )
            st.download_button(
                "Télécharger le diplôme",
                pdf,
                file_name="diplome.pdf"
            )
        else:
            st.error("Score insuffisant (70% requis)")
