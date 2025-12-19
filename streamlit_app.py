import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import date
import os

# ================= CONFIG =================
st.set_page_config(page_title="QCM CNGE – BPC ICH E6 R3", layout="centered")
st.title("QCM – Recherche en Soins Premiers")

RESULT_FILE = "resultats_quiz.csv"

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
    pdf.cell(0, 12, "CNGE FORMATION", ln=True, align="C")

    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, "Hereby Certifies that", ln=True, align="C")

    pdf.ln(10)
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 10, f"{prenom} {nom}", ln=True, align="C")

    pdf.ln(10)
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
    pdf.cell(0, 8, f"with a score of {score * 10} %", ln=True, align="C")

    pdf.ln(6)
    today = date.today().strftime("%d/%m/%Y")
    pdf.cell(0, 8, f"On {today}", ln=True, align="C")

    pdf.ln(12)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(
        0, 6,
        "This ICH E6 GCP Investigator Site Training meets the Minimum Criteria for "
        "ICH GCP Investigator Site Personnel Training identified by TransCelerate BioPharma "
        "as necessary to enable mutual recognition of GCP training among trial sponsors.",
        align="C"
    )

    pdf.ln(6)
    pdf.multi_cell(
        0, 6,
        "Collège National des Généralistes Enseignants Formation\n"
        "https://www.cnge-formation.fr/\n\n"
        "Version number 1-2025",
        align="C"
    )

    return pdf.output(dest="S").encode("latin-1")

# ================= SESSION =================
if "step" not in st.session_state:
    st.session_state.step = "login"

# ================= LOGIN =================
if st.session_state.step == "login":

    for key in ["nom", "prenom", "email"]:
        if key not in st.session_state:
            st.session_state[key] = ""

    st.session_state.nom = st.text_input("Nom", st.session_state.nom)
    st.session_state.prenom = st.text_input("Prénom", st.session_state.prenom)
    st.session_state.email = st.text_input("Email", st.session_state.email)

    if st.button("Commencer le QCM"):
        if st.session_state.nom == "" or st.session_state.prenom == "" or st.session_state.email == "":
            st.warning("Merci de remplir tous les champs")
        else:
            st.session_state.step = "quiz"

# ================= QUIZ =================
if st.session_state.step == "quiz":

    st.subheader(f"Participant : {st.session_state.prenom} {st.session_state.nom}")

    questions = [
        (
            "Buts des BPC – Quels sont les buts principaux des BPC (ICH E6 R3) ?",
            [
                "La protection des sujets de recherche",
                "Le conditionnement optimal des médicaments",
                "La crédibilité des résultats",
                "La confidentialité des données personnelles",
                "La communication avec les instances réglementaires"
            ],
            [0, 2, 3]
        ),
        (
            "Investigateur – Qui est l’investigateur ?",
            [
                "La personne qui réalise les recherches bibliographiques",
                "La personne responsable de la conduite de l’essai sur un lieu précis",
                "La personne en charge du respect des règles éthiques",
                "La personne qui finance l’essai"
            ],
            [1]
        ),
        (
            "Investigateur principal – Qu’est-ce qu’un investigateur principal ?",
            [
                "La promotion des résultats",
                "La gestion de l’essai",
                "Le financement de l’essai",
                "L’initiative de l’essai"
            ],
            [1]
        ),
        (
            "Responsabilité du promoteur – Quelle est sa responsabilité ?",
            [
                "Les principes éthiques sont conformes à la déclaration de Genève",
                "La balance bénéfice/risque est favorable",
                "Les intérêts de la société prévalent sur ceux des sujets",
                "L’expérimentation préclinique est suffisante"
            ],
            [1, 3]
        ),
        (
            "Principes BPC – Avant le début de l’essai",
            [
                "Les soins sont placés sous la responsabilité d’une personne compétente",
                "Le consentement libre et éclairé est recueilli",
                "Le médicament est efficace",
                "La confidentialité des informations est protégée"
            ],
            [0, 1, 3]
        ),
        (
            "Validation des compétences – Comment valide-t-on les compétences ?",
            [
                "Par l’obtention d’un diplôme",
                "Par la validation d’un module de formation BPC",
                "Par une formation continue",
                "Par l’exercice professionnel",
                "Par la participation à des groupes de pairs"
            ],
            [1]
        ),
        (
            "Inclusion sans consentement – Est-ce possible ?",
            [
                "Non",
                "Oui avec attestation d’un tiers indépendant",
                "Oui avec avis du comité d’éthique"
            ],
            [2]
        ),
        (
            "Protocole de recherche – Quelles obligations ?",
            [
                "Il n’est pas indispensable",
                "Il décrit le rationnel scientifique",
                "Avis favorable du comité d’éthique",
                "Avis favorable de l’autorité réglementaire",
                "Il décrit l’usage des médicaments"
            ],
            [1, 2, 3, 4]
        ),
        (
            "Suivi de la recherche – Quels principes ?",
            [
                "Seules les données médicaments sont consignées",
                "Toutes les données sont consignées",
                "Des procédures qualité sont mises en place"
            ],
            [1, 2]
        )
    ]

    if "reponses" not in st.session_state:
        st.session_state.reponses = [None] * len(questions)

    for i, (question, options, _) in enumerate(questions):
        st.session_state.reponses[i] = st.multiselect(
            question,
            options,
            default=[],
            key=f"q{i}"
        )

    if st.button("Valider le QCM"):
        score = 0

        for i, (_, options, bonnes) in enumerate(questions):
            bonnes_labels = [options[j] for j in bonnes]
            if set(st.session_state.reponses[i]) == set(bonnes_labels):
                score += 1

        resultat = "Réussi" if score >= 7 else "Échoué"

        df = pd.read_csv(RESULT_FILE)
        df.loc[len(df)] = [
            st.session_state.nom,
            st.session_state.prenom,
            st.session_state.email,
            f"{score}/9",
            resultat
        ]
        df.to_csv(RESULT_FILE, index=False)

        st.markdown("---")
        st.subheader(f"Score : {score}/9 — {resultat}")

        if resultat == "Réussi":
            pdf = creer_diplome(
                st.session_state.nom,
                st.session_state.prenom,
                score
            )
            st.download_button(
                "📄 Télécharger l’attestation CNGE",
                pdf,
                file_name="attestation_CNGE_BPC.pdf"
            )

    if st.button("🔁 Refaire le QCM"):
        st.session_state.reponses = [None] * len(questions)
        st.experimental_rerun()
