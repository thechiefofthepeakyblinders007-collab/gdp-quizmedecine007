import os
import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import date

# ================= CONFIG =================
st.set_page_config(page_title="QCM Formation", layout="centered")
st.title("QCM – Recherche en Soins Premiers")

RESULT_FILE = "resultats_quiz.csv"
ADMINS = [("bayen", "marc"), ("steen", "johanna")]

# ================= CSV =================
if not os.path.exists(RESULT_FILE):
    pd.DataFrame(columns=["Nom", "Prénom", "Email", "Score", "Résultat", "Date"]).to_csv(RESULT_FILE, index=False)

# ================= PDF DIPLOME =================
def creer_diplome(nom, prenom, score):
    pdf = FPDF()
    pdf.add_page()

    # Logo CNGE FORMATION
    pdf.image("logo_cnge_formation.png", x=85, y=10, w=40)

    # Texte du diplôme
    pdf.set_font("Arial", "B", 16)
    pdf.ln(30)
    pdf.cell(0, 10, "CNGE FORMATION", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, "Hereby Certifies that", ln=True, align="C")
    pdf.ln(8)
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 10, f"{prenom} {nom}", ln=True, align="C")
    pdf.ln(8)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(
        0, 8,
        "has completed the e-learning course\n\n"
        "RECHERCHE EN SOINS PREMIERS\n"
        "Formation aux bonnes pratiques cliniques\n"
        "(ICH E6 (R3))",
        align="C"
    )
    pdf.ln(6)
    pdf.cell(0, 8, f"with a score of {score*10} %", ln=True, align="C")
    pdf.ln(6)
    today = date.today().strftime("%d/%m/%Y")
    pdf.cell(0, 8, f"On {today}", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "I", 10)
    pdf.multi_cell(
        0, 6,
        "This e-learning course has been formally recognised for its quality and content by:\n\n"
        "the following organisations and institutions\n\n"
        "Collège National des Généralistes Enseignants Formation\n"
        "https://www.cnge-formation.fr/",
        align="C"
    )
    pdf.ln(4)
    pdf.set_font("Arial", "", 10)
    pdf.set_fill_color(230, 230, 230)
    txt = ("This ICH E6 GCP Investigator Site Training meets the Minimum Criteria for "
           "ICH GCP Investigator Site Personnel Training identified by TransCelerate BioPharma "
           "as necessary to enable mutual recognition of GCP training among trial sponsors.")
    pdf.multi_cell(0, 6, txt, border=1, align="C", fill=True)
    pdf.ln(10)
    pdf.set_font("Arial", "I", 8)
    pdf.cell(0, 5, "Version number 1-2025", ln=True, align="C")

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
        ("Buts des BPC. Quels sont les buts principaux des Bonnes Pratiques Cliniques (BPC) selon l'ICH E6 (R3) ?",
         ["La protection des sujets de recherche", "Le conditionnement optimal des médicaments",
          "La crédibilité des résultats", "La confidentialité des données personnelles",
          "La communication optimale avec les instances réglementaires"], [0, 2, 3]),

        ("Investigateur Principal. Qu'est-ce qu'un investigateur principal selon l'ICH E6 (R3) ?",
         ["La personne qui réalise les recherches bibliographiques",
          "La personne responsable de la conduite de l'essai sur un lieu précis",
          "La personne en charge du respect des règles éthiques d'un essai",
          "La personne qui finance un essai"], 1),

        ("Responsabilité du Promoteur. Quelle est la responsabilité du promoteur selon l'ICH E6 (R3) ?",
         ["La promotion des résultats de l'essai", "La gestion de l'essai",
          "Le financement de l'essai", "L'initiative d'un essai"], 1),

        ("Principes BPC Avant Début. Avant de débuter un essai clinique, le promoteur doit vérifier que la recherche remplit les principes suivants des BPC (ICH E6 (R3))",
         ["Les soins sont placés sous la responsabilité d'une personne compétente",
          "Le consentement libre et éclairé est recueilli",
          "Le médicament est efficace",
          "La confidentialité des informations les concernant est protégée"], [0, 1, 3]),

        ("Principes BPC pour les Sujets. Quels principes des BPC s'appliquent aux sujets de recherche selon l'ICH E6 (R3) ?",
         ["Les soins sont placés sous la responsabilité d'une personne compétente",
          "Le consentement libre et éclairé est recueilli",
          "Le médicament est efficace",
          "La confidentialité des informations les concernant est protégée"], [0, 1, 3]),

        ("Validation des Compétences. Comment valide-t-on la compétence d'un professionnel impliqué dans un essai clinique selon l'ICH E6 (R3)?",
         ["Par l'obtention d'un diplôme",
          "Par la validation d'un module de formation aux BPC",
          "Par le suivi d'une formation continue",
          "Par l'exercice de son activité professionnelle",
          "Par la participation régulière à des groupes de pairs"], [1, 2, 4]),

        ("Inclusion Sans Consentement. Peut-on inclure un sujet dont il est impossible de recueillir le consentement éclairé ?",
         ["Non", "Oui, en disposant de l'attestation d'un tiers indépendant",
          "Oui, en disposant de l'avis express du comité d'éthique"], 2),

        ("Protocole de Recherche. Concernant le protocole de recherche, quels principes ci-dessous doit-il respecter selon l'ICH E6 (R3)?",
         ["Il n'est pas indispensable dans le cadre des BPC",
          "Il décrit le rationnel scientifique de façon claire et détaillée",
          "Il doit avoir reçu l'avis favorable d'un comité d'éthique",
          "Il doit avoir reçu l'avis favorable de l'autorité réglementaire (ex. ANSM)",
          "Il décrit l'usage des médicaments étudiés"], [1, 2, 3, 4]),

        ("Suivi de la Recherche. Concernant le suivi de la recherche, quel(s) principe(s) ci-dessous doit-il respecter selon l'ICH E6 (R3)?",
         ["Seules les données concernant les médicaments sont à consigner",
          "Toutes les données sont à consigner",
          "Des procédures doivent être mises en place pour assurer la qualité de chaque aspect"], [1, 2]),

        ("Principes ALCOA+. Quels sont les principes ALCOA+ applicables aux données sources selon l'ICH E6 (R3)?",
         ["Attribuable", "Lisible", "Contemporain", "Original", "Exact",
          "Complet", "Consistant", "Durable"], [0, 1, 2, 3, 4, 5, 6, 7])
    ]

    if "reponses_quiz" not in st.session_state:
        st.session_state.reponses_quiz = [None] * len(questions)

    for i, (q, options, bonne) in enumerate(questions):
        if isinstance(bonne, list):
            st.session_state.reponses_quiz[i] = st.multiselect(
                q,
                options=options,
                default=[] if st.session_state.reponses_quiz[i] is None else st.session_state.reponses_quiz[i],
                key=f"q{i}"
            )
        else:
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
            if isinstance(bonne, list):
                if set(user_rep) == set([options[j] for j in bonne]):
                    score += 1
                    corrections.append((q, user_rep, [options[j] for j in bonne], True))
                else:
                    corrections.append((q, user_rep, [options[j] for j in bonne], False))
            else:
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
                file_name="diplome_CNGE.pdf"
            )

    if st.button("🔁 Refaire le QCM"):
        st.session_state.reponses_quiz = [None] * len(questions)
        st.experimental_rerun()
