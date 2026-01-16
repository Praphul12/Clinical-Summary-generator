# main.py

import streamlit as st
import pandas as pd
import requests
import json
from summarizers import (
    DataLoader,
    VitalSummarizer,
    MedicationSummarizer,
    DiagnosisSummarizer,
    WoundsSummarizer,
    NotesSummarizer,
    OASISSummarizer,
    SummaryGenerator
)

# API Configuration
API_BASE_URL = "http://localhost:8000"

@st.cache_data
def load_clinical_data(data_dir="data"):
    return {
        "diagnoses_df": pd.read_csv(f"{data_dir}/diagnoses.csv"),
        "meds_df": pd.read_csv(f"{data_dir}/medications.csv"),
        "vitals_df": pd.read_csv(f"{data_dir}/vitals.csv"),
        "notes_df": pd.read_csv(f"{data_dir}/notes.csv"),
        "wounds_df": pd.read_csv(f"{data_dir}/wounds.csv"),
        "oasis_df": pd.read_csv(f"{data_dir}/oasis.csv"),
    }

Dataframes = load_clinical_data()

def get_latest_episode(patient_id: int) -> int:
    df = Dataframes["diagnoses_df"]
    patient_episodes = df[df["patient_id"] == patient_id]["episode_id"]

    if patient_episodes.empty:
        raise ValueError("No episodes found for this patient")

    return patient_episodes.max()

REPO = DataLoader(Dataframes)

def generate_clinical_facts(patient_id: int) -> list[dict]:
    
    episode_id = get_latest_episode(patient_id)
    
    diagnoses_df = REPO.get("diagnoses_df", patient_id, episode_id)
    meds_df = REPO.get("meds_df", patient_id, episode_id)
    vitals_df = REPO.get("vitals_df", patient_id, episode_id)
    wounds_df = REPO.get("wounds_df", patient_id, episode_id)
    notes_df = REPO.get("notes_df", patient_id, episode_id)
    oasis_df = REPO.get_patient_only("oasis_df", patient_id)

    generator = SummaryGenerator(
        [
            DiagnosisSummarizer(diagnoses_df),
            MedicationSummarizer(meds_df),
            VitalSummarizer(vitals_df),
            WoundsSummarizer(wounds_df),
            NotesSummarizer(notes_df),
            OASISSummarizer(oasis_df)
        ]
    )
    
    return generator.generate()

def call_llm_api(clinical_facts: list[dict]) -> str:
    """Call FastAPI endpoint to generate summary"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/generate-summary",
            json={"clinical_facts": clinical_facts},
            timeout=30
        )
        response.raise_for_status()
        return response.json()["summary_markdown"]
    except requests.exceptions.RequestException as e:
        raise Exception(f"API error: {str(e)}")


def get_patient_ids():
    return sorted(Dataframes["diagnoses_df"]["patient_id"].unique().tolist())




# Streamlit UI
st.set_page_config(page_title="Clinical Summary Generator", layout="wide")

st.title("🩺 Clinical Summary Generator")
st.markdown("*LLM summarization powered by FastAPI*")

# Patient selection
patient_ids = get_patient_ids()

selected_patient = st.selectbox(
    "Select Patient ID",
    patient_ids,
    index=None,
    placeholder="Choose a patient"
)

generate = st.button("Generate Clinical Summary", type="primary")

if generate and selected_patient is not None:
    try:
        with st.spinner("Processing clinical data..."):
            # Step 1: Generate clinical facts locally
            clinical_facts = generate_clinical_facts(selected_patient)
        
        with st.spinner("Generating AI summary via API..."):
            # Step 2: Call API to generate summary
            markdown_summary = call_llm_api(clinical_facts)
        
        st.success("✅ Summary generated successfully!")
        
        # Create tabs for different views
        tab1, tab2 = st.tabs(["📋 Clinical Summary", "🔍 Raw Data"])
        
        with tab1:
            st.markdown("---")
            # Display the full markdown summary
            st.markdown(markdown_summary)
            st.markdown("---")
            
            # Download section
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="📥 Download Summary (Markdown)",
                    data=markdown_summary,
                    file_name=f"clinical_summary_patient_{selected_patient}.md",
                    mime="text/markdown"
                )
            with col2:
                st.download_button(
                    label="📥 Download Summary (TXT)",
                    data=markdown_summary,
                    file_name=f"clinical_summary_patient_{selected_patient}.txt",
                    mime="text/plain"
                )
        
        with tab2:
            st.subheader("Raw Clinical Facts")
            st.json(clinical_facts)
            
            st.download_button(
                label="📥 Download Raw Data (JSON)",
                data=json.dumps(clinical_facts, indent=2),
                file_name=f"clinical_facts_patient_{selected_patient}.json",
                mime="application/json"
            )

    except Exception as e:
        st.error(f" Error: {str(e)}")
        st.exception(e)

elif generate and selected_patient is None:
    st.warning("⚠️ Please select a patient ID first.")

