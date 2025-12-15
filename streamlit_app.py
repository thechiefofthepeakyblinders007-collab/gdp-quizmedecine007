import streamlit as st
import pandas as pd
from fpdf import FPDF
from io import BytesIO
import os
from datetime import date

# ================= CONFIG =================
st.set_page_config(page_title="QCM Formation", layout="centered")
st.title("QCM – Recherche en Soins Premiers")

RESULT_FILE = "resultats_quiz.csv"

ADMINS = [
    ("bayen", "marc"),
    ("steen", "johanna")
]

# ================= CSV =================
if not os.path.exists(RESULT_FILE):
    pd.DataFrame(
        columns=["Nom", "Prénom", "Email", "Score", "Résultat"]
    ).to_csv(RESULT_FILE, index=False)

# ================= PDF DIPLOME =================
def creer_diplome(nom, prenom, score):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "CNGE FORMATION", ln=True, align="C")

    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, "Hereby certifies that", ln=True, align="C")

    pdf.ln(8)
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 10, f"{prenom} {nom}", ln=True, align="C")

    pdf.ln(8)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(
        0,
        8,
        "has completed the e-learning course\n\n"
        "RECHERCHE EN SOINS PREMIERS\n"
        "Formation aux bonnes pratiques cliniques\n"
        "(ICH E6 (R3))",
        align="C"
    )

    pdf.ln(6)
    pdf.cell(0, 8, f"with a score of {score * 10} %", ln=True, align="C")

    pdf.ln(6)
    today = date.today().strftime("%d/%m/%Y")
    pdf.cell(0, 8, f"On {today}", ln=True, align="C")

    pdf.ln(10)
    pdf.set_font("Arial", "I", 10)
    pdf.multi_cell(
        0,
        6,
        "This e-learning course has been formally recognised for its quality and content by:\n\n"
        "Collège National des Généralistes Enseignants Formation\n"
        "https://www.cnge-formation.fr/",
        align="C"
    )

    buffer = BytesIO()
    buffer.write(pdf.output(dest="S").encode("latin-1"))
    buffer.seek(0)
    return buffer

# ================= SESSION =================
if "step" not in st.session_state:
    st.session_state.step = "login"

# ================= LOGIN =================
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

# ================= ADMIN =================
if st.session_state.step == "admin":
    st.subheader("Résultats des participants")
    df = pd.read_csv(RESULT_FILE)
    st.dataframe(df)

    if st.button("Réinitialiser la liste"):
        df.iloc[0:0].to_csv(RESULT_FILE, index=False)
        st.success("Liste effacée")

# ================= QUIZ =================
if st.session_state.step == "quiz":
    st.subheader(f"Bienvenue {st.session_state.prenom} {st.session_state.nom}")

    questions = [
        ("ICH signifie :", ["International Council for Harmonisation", "Internal Clinical Health"], 0),
        ("Les BPC concernent :", ["Les essais cliniques", "La comptabilité médicale"], 0),
        ("Objectif principal des BPC ?", ["Protection des sujets", "Marketing"], 0),
        ("ICH E6 traite de :", ["Bonnes pratiques cliniques", "Pharmacologie"], 0),
        ("Consentement éclairé est :", ["Obligatoire", "Optionnel"], 0),
        ("Les données doivent être :", ["Traçables", "Orales"], 0),
        ("Le promoteur est responsable :", ["De l'étude", "Du patient"], 0),
        ("ICH E6 R3 est :", ["Une mise à jour", "Un protocole local"], 0),
        ("Audit sert à :", ["Vérifier la conformité", "Sanctionner"], 0),
        ("Le respect éthique est :", ["Essentiel", "Secondaire"], 0),
    ]

    reponses = []
    for i, (q, options, _) in enumerate(questions):
        reponses.append(st.radio(q, options, key=i))

    if st.button("Valider le QCM"):
        score = 0
        corrections = []

        for i, (q, options, bonne) in enumerate(questions):
            bonne_rep = options[bonne]
            user_rep = reponses[i]
            ok = user_rep == bonne_rep
            if ok:
                score += 1
            corrections.append((q, user_rep, bonne_rep, ok))

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

        st.markdown("---")
        st.subheader(f"Score : {score}/10 — {resultat}")

        # -------- CORRECTION --------
        st.markdown("### Correction détaillée")
        for q, user, bonne, ok in corrections:
            if ok:
                st.success(f"{q} → Bonne réponse : {bonne}")
            else:
                st.error(f"{q} → Ta réponse : {user} | Bonne réponse : {bonne}")

        # -------- DIPLOME --------
        if resultat == "Réussi":
            pdf = creer_diplome(
                st.session_state.nom,
                st.session_state.prenom,
                score
            )
            st.download_button(
                "Télécharger le diplôme PDF",
                pdf,
                file_name="diplome_CNGE.pdf"
            )

        if st.button("🔁 Refaire le QCM"):
            st.session_state.step = "quiz"
            st.experimental_rerun()
