from pydantic import BaseModel
from typing import Optional, List

# Response from all_drug_drug_interactions table
class DDIResponse(BaseModel):
    # id: int
    drug_a_concept_name: str
    drug_b_concept_name: str
    event_concept_name: str
    severity_bnf: Optional[str]
    severity_ansm: str
    severity_code: int
    evidence: Optional[str]
    description: str

class SideEffectResponse(BaseModel):
    # id: int
    drug_concept_name: str
    event_concept_name: Optional[str]
    # drug_concept_id: str
    # event_concept_id: Optional[str]
    # drug_vocabulary_id: str
    # event_type: Optional[str]
    frequency: Optional[str]
    source: Optional[str]

class IndicationResponse(BaseModel):
    drug_concept_name: Optional[str]
    event_concept_name: Optional[str]

class AlternativeSearchResponse(BaseModel):
    drug_concept_name: Optional[str]
    event_concept_name: Optional[str]

class DrugClassResponse(BaseModel):
    drug_name: str
    bnf_order: Optional[str]
    title: Optional[str]

class PrescriptionResponse(BaseModel):
    start_date: str
    end_date: str
    drug: str
    drug_name_generic: str
    formulary_drug_cd: str
    dose_val_rx: str
    dose_unit_rx: str
    route: str

class PatientPortfolioResponse(BaseModel):
    patient_id: int
    patient_gender: str
    patient_age: int
    patient_dob: str
    prescriptions: List[PrescriptionResponse]

class DiagnosisResponse(BaseModel):
    icd9_code: str
    short_title: str
    long_title: str
    hadm_ids: List[int]

class AdmissionResponse(BaseModel):
    hadm_id: int
    admission_time: str
    discharge_time: str
    diagnosis: str