from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class AllDrugDrugInteractions(Base):
    __tablename__ = "all_drug_drug_interactions"
    __table_args__ = {"schema": "drug_interaction_compendia_v2"}

    id = Column(Integer, primary_key=True)
    drug_a_concept_name = Column(String)
    drug_b_concept_name = Column(String)
    event_concept_name = Column(String)
    drug_a_concept_id = Column(String)
    drug_b_concept_id = Column(String)
    event_concept_id = Column(String)
    drug_a_vocabulary_id = Column(String)
    drug_b_vocabulary_id = Column(String)
    severity_bnf = Column(String)
    severity_ansm = Column(String)
    severity_code = Column(Integer)
    evidence = Column(String)
    event_type = Column(String)
    description = Column(String)

class SingleDrugPositiveControls(Base):
    __tablename__ = "single_drug_positive_controls"
    __table_args__ = {"schema": "drug_interaction_compendia_v2"}

    id = Column(Integer, primary_key=True)
    drug_concept_name = Column(String)
    event_concept_name = Column(String)
    drug_concept_id = Column(String)
    event_concept_id = Column(String)
    drug_vocabulary_id = Column(String)
    event_vocabulary_id = Column(String)
    event_type = Column(String)
    frequency = Column(String)
    source = Column(String)

class SiderDrugIndications(Base):
    __tablename__ = "sider_drug_indications"
    __table_args__ = {"schema": "drug_interaction_compendia_v2"}

    id = Column(Integer, primary_key=True)
    drug_concept_id = Column(String)
    event_concept_id = Column(String)
    drug_concept_name = Column(String)
    event_concept_name = Column(String) 
    drug_vocabulary_id = Column(String)
    event_vocabulary_id = Column(String)

class PTtoHLTMapping(Base):
    __tablename__ = "pt_to_hlt_or_hlgt"
    __table_args__ = {"schema": "cdmv5"}

    id = Column(Integer, primary_key=True)
    descendant_concept_name = Column(String)
    ancestor_concept_name = Column(String)
    ancestor_concept_class_id = Column(String)

class BarklaData(Base):
    __tablename__ = "barkla_weighted_rate"
    __table_args__ = {"schema": "drug_interaction_compendia_v2"}

    id = Column(Integer, primary_key=True)
    side_effect = Column(String)
    drug_name = Column(String)
    count = Column(Integer)
    unsurprising_background_rate = Column(Float)
    surprising_background_rate = Column(Float)
    prob_s_ij_0 = Column(Float)
    control_value = Column(Float)
    signal = Column(Boolean)
    combined_rate = Column(Float)

class FAERSData(Base):
    __tablename__ = "faers_counts_2024"
    __table_args__ = {"schema": "drug_interaction_compendia_v2"}

    id = Column(Integer, primary_key=True)
    drug_name = Column(String)
    side_effect = Column(String)
    drug_side_effect_occurrence_count = Column(Integer)
    case_count_with_drug = Column(Integer)
    rate = Column(Float)
    # case_count_with_side_effect = Column(Integer)
    wilson_interval = Column(Float)

class DrugClass(Base):
    __tablename__ = "bnf_drug_classes"
    __table_args__ = {"schema": "drug_interaction_compendia_v2"}

    drug_name = Column(String, primary_key=True)
    bnf_order = Column(String)
    title = Column(String)

class Patient(Base):
    __tablename__ = "patients"
    __table_args__ = {"schema": "mimic_iii_clinical_database_1_4"}

    ROW_ID = Column(Integer)
    SUBJECT_ID = Column(Integer, primary_key=True)
    GENDER = Column(String)
    DOB = Column(String)
    DOD = Column(String)
    DOD_HOSP = Column(String)
    DOD_SSN = Column(String)
    EXPIRE_FLAG = Column(Integer)

class Prescription(Base):
    __tablename__ = "prescriptions"
    __table_args__ = {"schema": "mimic_iii_clinical_database_1_4"}

    ROW_ID = Column(Integer, primary_key=True)
    SUBJECT_ID = Column(Integer)
    HADM_ID = Column(Integer)
    ICUSTAY_ID = Column(Integer)
    STARTDATE = Column(String)
    ENDDATE = Column(String)
    DRUG_TYPE = Column(String)
    DRUG = Column(String)
    DRUG_NAME_POE = Column(String)
    DRUG_NAME_GENERIC = Column(String)
    FORMULARY_DRUG_CD = Column(String)
    GSN = Column(String)
    NDC = Column(Float)
    PROD_STRENGTH = Column(String)
    DOSE_VAL_RX = Column(String)
    DOSE_UNIT_RX = Column(String)
    FORM_VAL_DISP = Column(String)
    FORM_UNIT_DISP = Column(String)
    ROUTE = Column(String)
    
class Diagnosis(Base):
    __tablename__ = "diagnoses"
    __table_args__ = {"schema": "mimic_iii_clinical_database_1_4"}

    ROW_ID = Column(Integer, primary_key=True)
    SUBJECT_ID = Column(Integer)
    HADM_ID = Column(Integer)
    SEQ_NUM = Column(Integer)
    ICD9_CODE = Column(String)

class D_Icd(Base):
    __tablename__ = "d_icd"
    __table_args__ = {"schema": "mimic_iii_clinical_database_1_4"}

    ROW_ID = Column(Integer)
    ICD9_CODE = Column(String, primary_key=True)
    SHORT_TITLE = Column(String)
    LONG_TITLE = Column(String)


class Admission(Base):
    __tablename__ = "admissions"
    __table_args__ = {"schema": "mimic_iii_clinical_database_1_4"}

    ROW_ID = Column(Integer)
    SUBJECT_ID = Column(Integer)
    HADM_ID = Column(Integer, primary_key=True)
    ADMITTIME = Column(String)
    DISCHTIME = Column(String)
    DEATHTIME = Column(String)
    ADMISSION_TYPE = Column(String)
    ADMISSION_LOCATION = Column(String)
    DISCHARGE_LOCATION = Column(String)
    INSURANCE = Column(String)
    LANGUAGE = Column(String)
    RELIGION = Column(String)
    MARITAL_STATUS = Column(String)
    ETHNICITY = Column(String)
    EDREGTIME = Column(String)
    EDOUTTIME = Column(String)
    DIAGNOSIS = Column(String)
    HOSPITAL_EXPIRE_FLAG = Column(Integer)
    HAS_CHARTEVENTS_DATA = Column(Integer)