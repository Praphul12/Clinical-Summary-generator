# Data Documentation

This document explains the provided dataset and key home health clinical terms.

## Key Terminology

### 1. Episode
In Home Health care, patient care is organized into **Episodes**.
- An episode typically lasts **60 days** (or less if the patient is discharged early).
- `episode_id` is the unique identifier for these periods of care.
- `patient_id` identifies the patient across multiple episodes.
- For this assignment, you may see data for one or more episodes per patient. Focus on generating a summary for the **current/latest episode** while mentioning relevant history.

### 2. OASIS (Outcome and Assessment Information Set)
OASIS is a standard dataset collected for all home health patients to assess their functional status and care needs.
- **M-Items**: You might see columns like `M1830_BATHING` or simply `bathing`. These correspond to standardized questions about the patient's ability to perform activities of daily living (ADLs).
- **Scores**: Typically, lower numbers mean "Independent" and higher numbers mean "Dependent" or "Needs Assistance".
    - Example: `0 - Independent` vs `4 - Totally Dependent`.
- This provides the most objective measure of a patient's functional ability.

### 3. ICD-10 (Diagnoses)
- Standard medical classification list for diagnoses.
- `diagnosis_code`: The alphanumeric string (e.g., `I10`).
- `diagnosis_description`: The human-readable name (e.g., `Essential (Primary) Hypertension`).

## File Definitions

### `diagnoses.csv`
Contains the medical conditions for the patient for a specific episode.
- **Key Columns**: `patient_id`, `diagnosis_description`
- **Usage**: Use this to identify the *Primary Diagnosis* (usually the first one listed or flagged) and *Comorbidities*.

### `medications.csv`
Active medications the patient is currently taking.
- **Key Columns**: `medication_name`, `frequency` (how often), `classification` (drug class).
- **Usage**: List the patient's medication regimen. Look for patterns (e.g., multiple anti-hypertensives suggests uncontrolled blood pressure).

### `vitals.csv`
Vital sign readings recorded during visits.
- **Key Columns**: `visit_date`, `vital_type` (BP, HR, BS=Blood Sugar, etc.), `reading`.
- **Usage**: Identify ranges and trends. Are they stable? Are there alerts (high/low values)?

### `notes.csv`
Free-text clinical notes written by nurses and therapists.
- **Key Columns**: `note_date`, `note_type`, `note_text`.
- **Usage**: This is unstructured data. It provides context, "colour", and details not found in structured fields.
- *Tip*: Narrative notes often contain the most specific details about *why* a patient is struggling.

### `wounds.csv`
Details about active wounds, ulcers, or surgical incisions.
- **Key Columns**: `location`, `description`, `length_cm`, `width_cm`.
- **Usage**: Critical for patients with "Wound Care" as a diagnosis. Descriptions of healing status (e.g., "granulating," "slough") are important.

### `oasis.csv`
Functional assessments.
- **Key Columns**: `grooming`, `bathing`, `ambulation`, `transfer`.
- **Usage**: Use this to describe the patient's ability to care for themselves at home.
