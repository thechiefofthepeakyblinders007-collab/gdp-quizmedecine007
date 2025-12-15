import os
import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import date
from io import BytesIO
import base64
import requests

# ================= CONFIG =================
st.set_page_config(page_title="QCM Formation", layout="centered")
st.title("QCM – Recherche en Soins Premiers")

RESULT_FILE = "resultats_quiz.csv"
ADMINS = [("bayen", "marc"), ("steen", "johanna")]

# URL de l'image du logo
LOGO_URL = "https://mistralaichatupprodswe.blob.core.windows.net/chat-images/f4/26/d1/f426d13e-875f-4fd9-899f-49c94b257c5b/38758a3a-e4b5-4132-b44c-65dd45256afa/8c637623-b200-4d1f-b714-899adac55ed7?sv=2025-01-05&st=2025-12-15T17%3A59%3A20Z&se=2025-12-15T18%3A59%3A20Z&sr=b&sp=rade&sig=eqPN%2FR3sxFUbUpif9XBZ8dVMhoVwLdBvVeLXhIQH2Ps%3D"

# ================= CSV =================
if not os.path.exists(RESULT_FILE):
    pd.DataFrame(columns=["Nom", "Prénom", "Email", "Score", "Résultat", "Date"]).to_csv(RESULT_FILE, index=False)

# ================= PDF DIPLOME =================
def creer_diplome(nom, prenom, score):
    pdf = FPDF()
    pdf.add_page()

    # Télécharger l'image depuis l'URL
    response = requests.get(LOGO_URL)
    with open("logo_temp.png", "wb") as f:
        f.write(response.content)

    # Ajout du logo en haut du diplôme
    pdf.image("logo_temp.png", x=85, y=10, w=40)

    # Texte du diplôme
    pdf.set_font("Arial", "B", 16)
    pdf.ln(30)
    pdf.cell(0, 10, "CNGE FORMATION", ln=True, align="C")
    pdf.ln(5)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, "Hereby certifies that", ln=True, align="C")
    pdf.ln(5)
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 10, f"{prenom} {nom}", ln=True, align="C")
    pdf.ln(5)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(
        0, 6,
        "has completed the e-learning course\n\n"
        "RECHERCHE EN SOINS PREMIERS\n"
        "Formation aux bonnes pratiques cliniques\n"
        "(ICH E6 (R3))",
        align="C"
    )
    pdf.ln(5)
    pdf.cell(0, 8, f"with a score of {score*10} %", ln=True, align="C")
    pdf.ln(5)
    today = date.today().strftime("%d/%m/%Y")
    pdf.cell(0, 8, f"On {today}", ln=True, align="C")
    pdf.ln(5)
    pdf.set_font("Arial", "I", 10)
    pdf.multi_cell(
        0, 5,
        "This e-learning course has been formally recognised for its quality and content by:\n\n"
        "Collège National des Généralistes Enseignants Formation\n"
        "https://www.cnge-formation.fr/",
        align="C"
    )
    pdf.ln(5)
    pdf.set_font("Arial", "", 10)
    pdf.set_fill_color(230, 230, 230)
    txt = ("This ICH E6 GCP Investigator Site Training meets the Minimum Criteria for "
           "ICH GCP Investigator Site Personnel Training identified by TransCelerate BioPharma "
           "as necessary to enable mutual recognition of GCP training among trial sponsors.")
    pdf.multi_cell(0, 5, txt, border=1, align="C", fill=True)

    # Suppression du fichier temporaire
    os.remove("logo_temp.png")

    return pdf.output(dest="S").encode("latin-1")

# ================= SESSION / LOGIN / QUIZ =================
if "step" not in st.session_state:
    st.session_state.step = "login"

# ================= LOGIN =================
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

    if "reponses_quiz" not in st.session_state:
        st.session_state.reponses_quiz = [None] * len(questions)

    for i, (q, options, _) in enumerate(questions):
        st.session_state.reponses_quiz[i] = st.radio(
            q,
            options,
            index=0 if st.session_state.reponses_quiz[i] is None else options.index(st.session_state.reponses_quiz[i]),
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

        resultat = "Réussi" if score >= 7 else "Échoué"

        # Enregistrement CSV (ajout d'une nouvelle ligne)
        new_row = {
            "Nom": st.session_state.nom,
            "Prénom": st.session_state.prenom,
            "Email": st.session_state.email,
            "Score": f"{score}/10",
            "Résultat": resultat,
            "Date": date.today().strftime("%d/%m/%Y")
        }

        new_row_df = pd.DataFrame([new_row])
        new_row_df.to_csv(RESULT_FILE, mode='a', header=False, index=False)

        st.markdown("---")
        st.subheader(f"Score : {score}/10 — {resultat}")

        st.markdown("### Correction détaillée")
        for q, user, bonne, ok in corrections:
            if ok:
                st.success(f"{q} → Bonne réponse : {bonne}")
            else:
                st.error(f"{q} → Ta réponse : {user} | Bonne réponse : {bonne}")

        if resultat == "Réussi":
            pdf_bytes = creer_diplome(st.session_state.nom, st.session_state.prenom, score)
            if pdf_bytes:
                st.download_button(
                    "Télécharger le diplôme PDF",
                    pdf_bytes,
                    file_name="diplome_CNGE.pdf"
                )

    if st.button("🔁 Refaire le QCM"):
        st.session_state.reponses_quiz = [None] * len(questions)
        st.experimental_rerun()
