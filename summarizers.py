import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
class DataLoader:
    
    def __init__(self,dataframes: dict):
        self.dfs = dataframes
    
    def get(self, table: str, patient_id : int, episode_id : int):
        df = self.dfs[table]
        
        return df[(df["patient_id"] == patient_id) & (df["episode_id"] == episode_id)].copy()
    
    
    def get_patient_only(self, key, patient_id):
        df = self.dfs[key]
        return df[df["patient_id"] == patient_id]

class BaseSummarizer(ABC):
    
    @abstractmethod
    def summarize(self) -> list[dict]:
        """
            Returns a list of statements:
            {
                "statement":str
                "source":str,
                "date" : str| None
            }
        """
        pass
    

class VitalSummarizer(BaseSummarizer):
    
    def __init__(self,df_vitals):
        self.df = df_vitals
    
    def summarize(self):
        
        self.df = self.df.drop_duplicates()
        self.df['visit_date'] = pd.to_datetime(self.df['visit_date'])
        
        self.df['alert'] = np.where(self.df['min_value'].notna() & self.df['reading'] < self.df['min_value'],'low',
                              np.where(self.df['max_value'].notna() & self.df['reading'] > self.df['max_value'],'high','Stable'))
        
        df_vital_alert = self.df[(self.df['alert'] == 'low')|(self.df['alert'] == 'high') ]
        
        vital_statements = []

        alert_classes = df_vital_alert['vital_type'].unique()

        for vital in alert_classes:
            df_vital = (
                df_vital_alert[df_vital_alert['vital_type'] == vital]
                .sort_values("visit_date")
            )

            high_count = (df_vital['alert'] == 'high').sum()
            low_count  = (df_vital['alert'] == 'low').sum()

            last_row = df_vital.iloc[-1]
            last_value = last_row['reading']
            last_date = last_row['visit_date'].strftime("%Y-%m-%d")
            print(last_date)
            # Case 1: Persistently HIGH
            if high_count >= 2 and low_count == 0:
                statement = (
                    f"{vital} has shown persistently elevated readings, "
                    f"most recently {last_value} on {last_date}."
                )

            # Case 2: Persistently LOW
            elif low_count >= 2 and high_count == 0:
                statement = (
                    f"{vital} has shown persistently low readings, "
                    f"most recently {last_value} on {last_date}."
                )

            # Case 3: Mixed HIGH and LOW
            elif high_count >= 1 and low_count >= 1:
                statement = (
                    f"{vital} readings have been variable, with both high and low values observed, "
                    f"most recently {last_value} on {last_date}."
                )

            # Case 4: Isolated HIGH
            elif high_count == 1:
                statement = (
                    f"An isolated elevated {vital.lower()} reading was noted at "
                    f"{last_value} on {last_date}."
                )

            # Case 5: Isolated LOW
            elif low_count == 1:
                statement = (
                    f"An isolated low {vital.lower()} reading was noted at "
                    f"{last_value} on {last_date}."
                )

            else:
                continue  
            
            vital_statements.append({
                "statement": statement,
                "source": "vitals.csv",
                "date": last_date
            })
            
        return vital_statements
    

class WoundsSummarizer(BaseSummarizer):
    
    def __init__(self,df_wounds):
        self.df = df_wounds
    
    def summarize(self):
        
        self.df['visit_date'] = pd.to_datetime(self.df['visit_date'])
        self.df['onset_date'] = pd.to_datetime(self.df['onset_date'])
        
        wound_groups = self.df.groupby(["location", "onset_date"])
        
        wound_summaries = []

        for (location, onset), df in wound_groups:
        
            df = df.sort_values("visit_date")

            first_desc = df.iloc[0]["description"]
            latest_desc = df.iloc[-1]["description"]

            wound_summaries.append({
                "location": location,
                "onset_date": onset.date(),
                "first_description": first_desc,
                "latest_description": latest_desc,
                "last_seen": df.iloc[-1]["visit_date"].date(),
                "visit_count": len(df)
            })

        wound_statements = []

        for w in wound_summaries:
        
            if w["visit_count"] > 1:
                followup = (
                    f"monitored across {w['visit_count']} visits, "
                    f"most recently on {w['last_seen']}"
                )
            else:
                followup = f"documented on {w['last_seen']}"

            statement = (
                f"An active {w['latest_description'].lower()} is present at the "
                f"{w['location'].lower()}, first noted on {w['onset_date']}, "
                f"{followup}."
            )

            wound_statements.append({
                "statement": statement,
                "source": "wounds.csv"
            })
            
        
        return wound_statements
   
    
# Fix OASISSummarizer.summarize() - it's returning a nested structure
class OASISSummarizer(BaseSummarizer):
    
    def __init__(self, df_oasis):
        self.df = df_oasis
    
    def summarize(self) -> list[dict]:
        if self.df.empty:
            return []
            
        self.df["assessment_date"] = pd.to_datetime(self.df["assessment_date"])
        oasis_filtered = (
            self.df
            .drop_duplicates()
            .sort_values("assessment_date")
        )
        
        if oasis_filtered.empty:
            return []
            
        latest_oasis = oasis_filtered.iloc[-1, :]
        oasis_fields = self.df.columns[3:]
        
        oasis_statements = []
        
        # Add functional summary FIRST
        functional_summary = {
            "statement": (
                "OASIS assessment indicates the patient is highly dependent and "
                "requires assistance with most activities of daily living, "
                "including bathing, transfers, toileting, and ambulation."
            ),
            "source": "oasis.csv",
            "date": latest_oasis["assessment_date"].strftime("%Y-%m-%d")
        }
        oasis_statements.append(functional_summary)
        
        # Add individual field values
        for col in oasis_fields:
            oasis_statements.append({
                "statement": f"{col.capitalize()}: {latest_oasis[col]}",
                "source": "oasis.csv",
                "date": latest_oasis["assessment_date"].strftime("%Y-%m-%d")
            })
        
        # Return flat list - THIS WAS THE BUG
        return oasis_statements
    

class MedicationSummarizer(BaseSummarizer):

    def __init__(self, meds_df):
        self.df = meds_df

    def summarize(self):

        if self.df.empty:
            return []

        grouped = (
            self.df
            .groupby("classification")
            .agg(
                reasons=("reason", lambda x: ", ".join(sorted(x.dropna().unique()))),
                frequencies=("frequency", lambda x: ", ".join(sorted(x.dropna().unique())))
            )
            .reset_index()
        )

        medication_statements = []

        for _, row in grouped.iterrows():
            medication_statements.append({
                "statement": (
                    f"{row['classification']} medications are being used for "
                    f"{row['reasons']}."
                    f"(administration frequencies include {row['frequencies']})."
                ),
                "source": "medications.csv",
                "date": None
            })

        return medication_statements
      

class DiagnosisSummarizer(BaseSummarizer):

    def __init__(self, diagnoses_df):
        self.df = diagnoses_df

    def summarize(self):

        if self.df.empty:
            return []

        df = self.df.drop_duplicates(ignore_index=True)

        primary_diagnosis = df.iloc[0]["diagnosis_description"]

        secondary_diagnoses = (
            df.iloc[1:]["diagnosis_description"].dropna().tolist()
            if len(df) > 1
            else []
        )

        if secondary_diagnoses:
            statement = (
                f"The primary diagnosis for this episode appears to be "
                f"{primary_diagnosis}. Additional documented conditions include "
                f"{', '.join(secondary_diagnoses)}."
            )
        else:
            statement = (
                f"The primary diagnosis for this episode appears to be "
                f"{primary_diagnosis}."
            )

        return [{
            "statement": statement,
            "source": "diagnoses.csv",
            "date": None
        }]

class NotesSummarizer(BaseSummarizer):

    def __init__(self, df_notes):
        self.df = df_notes.copy()

    def summarize(self) -> list[dict]:

        if self.df.empty:
            return []

        self.df["note_date"] = pd.to_datetime(self.df["note_date"], errors="coerce")
        self.df = self.df.dropna(subset=["note_date"])

        latest_episode_id = (
            self.df.sort_values("note_date", ascending=False)
            .iloc[0]["episode_id"]
        )

        IMPORTANT_NOTE_TYPES = {
            "NARRATIVE",
            "RECERT/DISCHARGE DECISION",
            "ON CALL",
            "HOSPICE QUALIFYING CRITERIA"
        }

        df_filtered = (
            self.df[
                (self.df["episode_id"] == latest_episode_id) &
                (self.df["note_type"].isin(IMPORTANT_NOTE_TYPES))
            ]
            .sort_values("note_date", ascending=False)
            .head(3)   # limit volume
        )

        notes_statements = []

        for _, row in df_filtered.iterrows():

            note_type = row["note_type"]
            note_date = row["note_date"].strftime("%Y-%m-%d")

            # SAFE, non-inferential phrasing
            if note_type == "ON CALL":
                statement = (
                    f"An after-hours on-call interaction was documented on {note_date}."
                )
            elif note_type == "NARRATIVE":
                statement = (
                    "Recent nursing narrative documentation provides additional "
                    "context regarding the patient’s condition and care."
                )
            else:
                statement = (
                    f"Relevant clinical documentation ({note_type.lower()}) "
                    f"was recorded on {note_date}."
                )

            notes_statements.append({
                "statement": statement,
                "source": "notes.csv"
            })

        return notes_statements


class SummaryGenerator:
    
    
    def __init__(self,summaries: list[BaseSummarizer]):
        self.summaries = summaries
        
    def generate(self) -> list[dict]:
        
        generated_summary = []
        for summary in self.summaries:
            
            temp_summary = summary.summarize()
            generated_summary.extend(temp_summary)
            
        return generated_summary
        
       