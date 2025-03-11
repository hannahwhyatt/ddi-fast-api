"""
Routes for the API

NOTE: get_drug_names must include single drug names. omitted for development purposes.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.models import AllDrugDrugInteractions, SingleDrugPositiveControls, SiderDrugIndications, PTtoHLTMapping, BarklaData, FAERSData, DrugClass, Patient, Prescription, Diagnosis, D_Icd, Admission
import pandas as pd

from app.db.session import SessionLocal
from app.db.schemas import DDIResponse, SideEffectResponse, IndicationResponse, AlternativeSearchResponse, DrugClassResponse, PatientPortfolioResponse, PrescriptionResponse, DiagnosisResponse, AdmissionResponse
from fastapi import HTTPException
from typing import List, Dict
from sqlalchemy import func
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Get the set of drug names
@router.get("/drug_names", 
    response_model=List[str],
    summary="Get all unique drug names in the database",
    response_description="A list of drug names as strings.")
def get_drug_names(db: Session = Depends(get_db)):
    try:
        drug_a_names = [name[0] for name in db.query(AllDrugDrugInteractions.drug_a_concept_name).distinct().all()]
        drug_b_names = [name[0] for name in db.query(AllDrugDrugInteractions.drug_b_concept_name).distinct().all()]
        single_drug_names = [name[0] for name in db.query(SingleDrugPositiveControls.drug_concept_name).distinct().all()]
        all_drug_names = set(drug_a_names + drug_b_names) # + single_drug_names)
        all_drug_names.discard(None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return list(all_drug_names)

# Get the set of drug names
@router.get("/barkla_drug_names", 
    response_model=List[str],
    summary="Get all unique drug names in the Barkla data table",
    response_description="A list of drug names as strings.")
def get_drug_names(db: Session = Depends(get_db)):
    try:
        drug_names = [name[0] for name in db.query(BarklaData.drug_name).distinct().all()]
        drug_names = set(drug_names)
        drug_names.discard(None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return list(drug_names)

# Get the set of FAERS drug names
@router.get("/faers_drug_names", 
    response_model=List[str],
    summary="Get all unique drug names in the FAERS data table",
    response_description="A list of drug names as strings.")
def get_faers_drug_names(db: Session = Depends(get_db)):
    try:
        drug_names = [name[0] for name in db.query(FAERSData.drug_name).distinct().all()]
        drug_names = set(drug_names)
        drug_names.discard(None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return list(drug_names)

# Get the set of side effect names
@router.get("/side_effects_names", 
    # response_model=List[str],
    summary="Get all unique side effect names in the database",
    response_description="A list of side effect names as strings.")
def get_side_effect_names(db: Session = Depends(get_db)):
    try:
        side_effects = [name[0] for name in db.query(SingleDrugPositiveControls.event_concept_name).distinct().all()]
        side_effects = set(side_effects)
        side_effects.discard(None)
        hlgt = get_ancestor_side_effects(side_effects, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return list(set(hlgt))

# Get the set of side effect names
@router.get("/barkla_side_effects_names", 
    # response_model=List[str],
    summary="Get all unique side effect names in the Barkla database",
    response_description="A list of side effect names as strings.")
def get_side_effect_names(db: Session = Depends(get_db)):
    try:
        side_effects = [name[0] for name in db.query(BarklaData.side_effect).distinct().all()]
        side_effects = set(side_effects)
        side_effects.discard(None)
        side_effects = sorted(side_effects)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return list(side_effects)

# Get the interactions for a set of drugs
@router.get("/interactions", 
    response_model=List[DDIResponse],
    summary="Get drug-drug interactions for a list of drugs",
    response_description="List of drug-drug interactions with severity level")
def get_interactions(
    drug_list: List[str] = Query(
        ..., 
        description="List of drug names to check for interactions",
        example=["aspirin", "warfarin"]
    ), 
    db: Session = Depends(get_db)):
    try:
        interactions = db.query(AllDrugDrugInteractions).filter(
            AllDrugDrugInteractions.drug_a_concept_name.in_(drug_list),
            AllDrugDrugInteractions.drug_b_concept_name.in_(drug_list)
        ).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return interactions 

# Get the side effects for a set of drugs
@router.get("/side_effects", 
    response_model=List[SideEffectResponse],
    summary="Get side effects for a list of drugs",
    description="Retrieves side effects for the specified drugs from the database with BNF source.",
    response_description="List of side effects for the specified drugs.")
def get_side_effects(
    drug_list: List[str] = Query(
        ..., 
        description="List of drug names to get side effects for",
        example=["aspirin"]
    ), 
    db: Session = Depends(get_db)):
    try:
        side_effects = db.query(SingleDrugPositiveControls).filter(
            SingleDrugPositiveControls.drug_concept_name.in_(drug_list),
            SingleDrugPositiveControls.source == 'BNF',
            SingleDrugPositiveControls.frequency != 'Not reported (Interaction Effect)'
        ).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return side_effects

# Get indications for a given drug
@router.get("/single_drug_indications", 
    response_model=List[IndicationResponse],
    summary="Get indications for a single drug",
    description="Retrieves all medical conditions that a specific drug is indicated for.",
    response_description="List of dictionaries with drug name and indications."
    )
def get_single_drug_indications(
    drug_name: str = Query(
        ..., 
        description="Name of the drug to get indications for",
        example="aspirin"
    ), 
    db: Session = Depends(get_db)):
    try:
        indications = db.query(SiderDrugIndications).filter(
            SiderDrugIndications.drug_concept_name == drug_name,
            SiderDrugIndications.event_concept_name != 'Sudden death'
        ).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return indications

# Get indicatios for a list of drugs
@router.get("/indications",
    summary="Get indications for a list of drugs",
    description="Retrieves all medical conditions that a list of drugs are indicated for.",
    response_description="List of dictionaries with drug name and indications."
    )
def get_indications(
    drug_list: List[str] = Query(
        ..., 
        description="List of drugs to get indications for",
        example=["aspirin", "omeprazole"]
    ), 
    db: Session = Depends(get_db)):
    try:
        indications = db.query(SiderDrugIndications).filter(
            SiderDrugIndications.drug_concept_name.in_(drug_list),
            SiderDrugIndications.event_concept_name != 'Sudden death'
        ).all()
        
        # Group indications by drug
        result = {}
        for indication in indications:
            if indication.drug_concept_name not in result:
                result[indication.drug_concept_name] = []
            result[indication.drug_concept_name].append(indication)
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Get all drugs with matching indications
@router.get("/alternative_search",
    summary="Find alternative drugs with same indications",
    description="""
    Searches for alternative drugs that share the same set of medical indications.
    Excludes the drug being replaced from the results.
    """,
    response_description="List of dictionaries with drug names."
    )
def alternative_search(
    replaced_drug: str = Query(
        ..., 
        description="Drug to find alternatives for", 
        example="aspirin"
    ),
    indication_list: List[str] = Query(
        ..., 
        description="List of indications that alternative drugs should match",
        example=["Pain"]
    ), 
    db: Session = Depends(get_db)):
    try:
        # Get drugs with matching indications
        subquery = db.query(
            SiderDrugIndications.drug_concept_name,
            SiderDrugIndications.event_concept_name
        ).filter(
            SiderDrugIndications.event_concept_name.in_(indication_list),
            SiderDrugIndications.event_concept_name != 'Sudden death',
            SiderDrugIndications.drug_concept_name != replaced_drug,
            SiderDrugIndications.drug_concept_name.isnot(None)
        ).subquery()

        alternative_drugs = db.query(subquery.c.drug_concept_name).group_by(
            subquery.c.drug_concept_name
        ).having(
            func.count(subquery.c.event_concept_name) == len(indication_list)
        ).distinct().all()
        if alternative_drugs:
            alternative_drugs = [{"drug_concept_name": drug[0]} for drug in alternative_drugs]
        else:
            alternative_drugs = []
    except Exception as e:
        logger.error(f"Error in alternative_search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

    return alternative_drugs

# Get interactions for alternative drugs
@router.get("/alternative_interactions", 
    response_model=List[DDIResponse],
    summary="Get any interactions given a replacement drug and the existing portfolio",
    response_description="List of dictionaries with interactions."
    )
def alternative_interactions(
    replaced_drug: str = Query(
        ..., 
        description="Drug that has been replaced and is no longer in the patient's portfolio.", 
        example="aspirin"
    ),
    replacement_drug: str = Query(
        ..., 
        description="ALternative drug.", 
        example="ibuprofen"
    ), 
    drug_list: List[str] = Query(
        ..., 
        description="List of drugs with which to check for interactions (patient portfolio).",
        example=["omeprazole", "warfarin"]
    ), 
    db: Session = Depends(get_db)):
    try:
        interactions = db.query(AllDrugDrugInteractions).filter(
            (AllDrugDrugInteractions.drug_a_concept_name != replaced_drug) &  # Ensure replaced_drug is excluded
            (AllDrugDrugInteractions.drug_b_concept_name != replaced_drug) &  
            (
                # Case 1: replacement_drug is drug_a, drug_b must be in drug_list
                ((AllDrugDrugInteractions.drug_a_concept_name == replacement_drug) & 
                 (AllDrugDrugInteractions.drug_b_concept_name.in_(drug_list))) |
                # Case 2: replacement_drug is drug_b, drug_a must be in drug_list
                ((AllDrugDrugInteractions.drug_b_concept_name == replacement_drug) & 
                 (AllDrugDrugInteractions.drug_a_concept_name.in_(drug_list)))
            )
        ).all()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return interactions 

    
# Get ancestor concept names for a set of side effects
@router.get("/ancestor_side_effects",
    summary="Get MedDRA ancestor concept names for a list of side effects",
    response_description="Dictionary of side effects and their ancestor concept names, multiple ancestors are separated by '/'",
    # response_model=Dict[str, str]

    )
def get_ancestor_side_effects(
    pt_list: List[str] = Query(
        ..., 
        description="List of side effects to get ancestor concept names for",
        example=["Headache", "Dizziness"]
    ), 
    db: Session = Depends(get_db)):
    try:

        # Fetch side effects for the given drug list
        side_effects = db.query(PTtoHLTMapping).filter(
            PTtoHLTMapping.descendant_concept_name.in_(pt_list)
        ).all()
        # Extract descendant concept names from side effects
        descendant_names = [side_effect.descendant_concept_name for side_effect in side_effects]

        ancestor_mappings = db.query(PTtoHLTMapping).filter(
            PTtoHLTMapping.descendant_concept_name.in_(descendant_names),
            PTtoHLTMapping.ancestor_concept_class_id == 'HLGT'
        ).all()


        # Prepare the result
        result = {}
        for mapping in ancestor_mappings:
            if mapping.descendant_concept_name not in result:
                result[mapping.descendant_concept_name] = []
            result[mapping.descendant_concept_name].append(mapping.ancestor_concept_name)
        for key, value in result.items():
            result[key] = '/'.join(list(set(value)))
    except Exception as e:
        logger.error(f"Error in get_ancestor_side_effects: {str(e)}") 
        raise HTTPException(status_code=500, detail=str(e))
    
    return result
    

# Get most likely culprit drug for a given side effect and portfolio of drugs
@router.get("/culprit_drug",
    summary="Get most likely culprit drugs for a given side effect and portfolio of drugs",
    response_description="List of dictionaries with drug names and their scores.")
def get_culprit_drug(
    side_effect: str = Query(
        ..., 
        description="Side effect to get culprit drug for",
        example="Headache"
    ), 
    drug_list: List[str] = Query(
        ..., 
        description="List of drugs to check for culprit drug",
        example=["aspirin", "ibuprofen"]
    ), 
    db: Session = Depends(get_db)):
    try:
        drug_list = [drug.lower() for drug in drug_list]
        side_effect = side_effect.lower()

        # Fetch rows from barkla data
        barkla_data = db.query(BarklaData).filter(
            BarklaData.side_effect == side_effect,
            BarklaData.drug_name.in_(drug_list)
        ).all()

        # If there are no barkla data, return empty list
        if not barkla_data:
            return []

        # If there are barkla data, calculate the total combined rate
        total_combined_rate = sum(row.combined_rate for row in barkla_data)

        # Calculate the score for each drug
        for row in barkla_data:
            row.score = row.combined_rate / total_combined_rate

        #  Create a ranked list of drugs from most likely to least likely culprit
        ranked_drugs = sorted(barkla_data, key=lambda x: x.score, reverse=True)
        results = [{"drug_name": row.drug_name, "combined_rate": row.combined_rate, "score": row.score} for row in ranked_drugs]

        return results

    except Exception as e:
        logger.error(f"Error in get_culprit_drug: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Get most likely side effects for a given portfolio of drugs
@router.get("/most_likely_side_effects",
    summary="Get most likely side effects for a given portfolio of drugs",
    response_description="List of dictionaries of drugs with their most likely side effects and their scores.")
def get_most_likely_side_effect(
    drug_list: List[str] = Query(
        ..., 
        description="List of drugs to check for culprit drug",
        example=["aspirin", "ibuprofen"]
    ), 
    db: Session = Depends(get_db)):
    try:
        drug_list = [drug.lower() for drug in drug_list]
        # Barkla data for the patient's drugs and the specified side effect
        barkla_data = db.query(BarklaData).with_entities(
            BarklaData.drug_name,
            BarklaData.side_effect,
            BarklaData.combined_rate
        ).filter(
            BarklaData.drug_name.in_(drug_list)
        ).all()

        # If there are no barkla data, return empty list
        if not barkla_data:
            return []

        barkla_data = pd.DataFrame(barkla_data)
        barkla_data.columns = ['drug_name', 'side_effect', 'combined_rate']

        # Sum rates for the same side effects across the provided drugs
        side_effects_rates = barkla_data.groupby('side_effect').sum('combined_rate').reset_index()
        side_effects_rates = side_effects_rates.rename(columns={'combined_rate': 'total_rate'})

        #  Sort side effects by total rate
        side_effects_rates = side_effects_rates.sort_values(by='total_rate', ascending=False)

        #  Return the top 5 side effects
        top_side_effects = side_effects_rates.head(10)
        # top_side_effects = side_effects_rates

        # Determine the drug most likely causing each of the top side effects
        top_results = []
        for _, row in top_side_effects.iterrows():
            side_effect = row['side_effect']
            total_rate = row['total_rate']

            # Find the drug contributing most to this side effect
            contributing_drug_data = barkla_data[barkla_data['side_effect'] == side_effect]
            most_likely_drug = contributing_drug_data.loc[
                contributing_drug_data['combined_rate'].idxmax(), 'drug_name'
            ]

            top_results.append({
                'side_effect': side_effect,
                'total_rate': total_rate,
                'most_likely_drug': most_likely_drug
            })
            
        return top_results

    except Exception as e:
        logger.error(f"Error in get_most_likely_side_effect: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Get most likely side effects for a given portfolio of drugs based on FAERS data
@router.get("/most_likely_side_effects_faers",
    summary="Get most likely side effects for a given portfolio of drugs based on FAERS data",
    response_description="List of dictionaries of drugs with their most likely side effects and their scores.")
def get_most_likely_side_effect_faers(
    drug_list: List[str] = Query(
        ..., 
        description="List of drugs to check for culprit drug",
        example=["aspirin", "ibuprofen"]
    ), 
    db: Session = Depends(get_db)):
    try: 
        drug_list = [drug.lower() for drug in drug_list]
        faers_data = db.query(FAERSData).with_entities(
            FAERSData.drug_name,
            FAERSData.side_effect,
            FAERSData.drug_side_effect_occurrence_count,
            FAERSData.case_count_with_drug,
            FAERSData.rate,
            FAERSData.wilson_interval
        ).filter(
            FAERSData.drug_name.in_(drug_list)
        ).all()

        faers_data = pd.DataFrame(faers_data)
        faers_data.columns = ['drug_name', 'side_effect', 'drug_side_effect_occurrence_count', 'case_count_with_drug', 'rate', 'wilson_interval']

        #  Sort side effects by rate
        faers_data = faers_data.sort_values(by=['drug_name', 'rate'], ascending=[True, False])

        #  Return the top 5 side effects for each drug
        top_results = faers_data.groupby('drug_name').head(5).reset_index(drop=True)
        top_results = top_results.to_dict(orient='records')

        return top_results
    
    except Exception as e:
        logger.error(f"Error in get_most_likely_side_effect_faers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/drug_classes",
    summary="Get drug class for each drug in a list of drugs",
    response_description="List of dictionaries with drug names and their classes.")
def get_drug_classes(
    drug_list: List[str] = Query(
        ..., 
        description="List of drugs to get drug classes for",
        example=["aspirin", "ibuprofen"]
    ), 
    db: Session = Depends(get_db)):
    try:
        # Convert input drug list to lowercase
        drug_list = [drug.lower() for drug in drug_list]
        
        drug_classes = db.query(DrugClass).filter(
            func.lower(DrugClass.drug_name).in_(drug_list)
        ).all()
        return drug_classes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/patient_portfolio_mimic",
    summary="Get patient portfolio for a given patient ID",
    response_description="List of dictionaries with drug names and their classes.")
def get_patient_portfolio_mimic(
    patient_id: str = Query(..., description="Patient ID to get portfolio for"),
    db: Session = Depends(get_db)):
    
    # Query patient information
    patient = db.query(Patient).filter(Patient.SUBJECT_ID == patient_id).first()
    
    if not patient:
        raise HTTPException(status_code=404, detail=f"Patient with ID {patient_id} not found")
    
    # Calculate age from DOB
    dob = datetime.strptime(patient.DOB, "%Y-%m-%d %H:%M:%S")
    age = (datetime.now() - dob).days // 365
    
    # Query patient prescriptions
    prescriptions = db.query(
        Prescription.STARTDATE,
        Prescription.ENDDATE,
        Prescription.DRUG,
        Prescription.DRUG_NAME_GENERIC,
        Prescription.FORMULARY_DRUG_CD,
        Prescription.DOSE_VAL_RX,
        Prescription.DOSE_UNIT_RX,
        Prescription.ROUTE
    ).filter(Prescription.SUBJECT_ID == patient_id).all()
    
    # Format prescriptions as per schema
    prescription_list = []
    for p in prescriptions:
        # Handle potential None values by converting them to empty strings
        prescription_list.append(
            PrescriptionResponse(
                start_date=str(p.STARTDATE) if p.STARTDATE else "",
                end_date=str(p.ENDDATE) if p.ENDDATE else "",
                drug=p.DRUG if p.DRUG else "",
                drug_name_generic=p.DRUG_NAME_GENERIC if p.DRUG_NAME_GENERIC else "",
                formulary_drug_cd=p.FORMULARY_DRUG_CD if p.FORMULARY_DRUG_CD else "",
                dose_val_rx=p.DOSE_VAL_RX if p.DOSE_VAL_RX else "",
                dose_unit_rx=p.DOSE_UNIT_RX if p.DOSE_UNIT_RX else "",
                route=p.ROUTE if p.ROUTE else ""
            )
        )
    
    # Create response object
    response = PatientPortfolioResponse(
        patient_id=int(patient_id),
        patient_gender=patient.GENDER,
        patient_age=age,
        patient_dob=str(patient.DOB),
        prescriptions=prescription_list
    )
    
    return response

@router.get("/patient_diagnoses_mimic",
    summary="Get patient diagnoses for a given patient ID",
    response_description="List of dictionaries with diagnoses.")
def get_patient_diagnoses_mimic(
    patient_id: str = Query(..., description="Patient ID to get diagnoses for"),
    db: Session = Depends(get_db)):
    try:
        # Query patient information
        patient = db.query(Patient).filter(Patient.SUBJECT_ID == patient_id).first()
        
        if not patient:
            raise HTTPException(status_code=404, detail=f"Patient with ID {patient_id} not found")
        
        # Query diagnoses with hadm_id
        diagnoses = db.query(Diagnosis).filter(Diagnosis.SUBJECT_ID == patient_id).all()
        
        # Get ICD9 codes from diagnoses
        icd9_codes = [d.ICD9_CODE for d in diagnoses]
            
        # Get titles for each diagnosis code
        diagnoses_with_titles = db.query(D_Icd).filter(D_Icd.ICD9_CODE.in_(icd9_codes)).all()
        
        # Create a mapping of ICD9 codes to their titles
        icd9_to_titles = {d.ICD9_CODE: (d.SHORT_TITLE, d.LONG_TITLE) for d in diagnoses_with_titles}
        
        # Create a mapping of ICD9 codes to hadm_ids
        icd9_to_hadm_ids = {}
        for d in diagnoses:
            if d.ICD9_CODE not in icd9_to_hadm_ids:
                icd9_to_hadm_ids[d.ICD9_CODE] = []
            if d.HADM_ID and d.HADM_ID not in icd9_to_hadm_ids[d.ICD9_CODE]:
                icd9_to_hadm_ids[d.ICD9_CODE].append(d.HADM_ID)
        
        # Format diagnoses with titles and hadm_ids
        diagnosis_list = []
        for icd9_code in set(icd9_codes):  # Use set to get unique codes
            # Get hadm_ids for this diagnosis
            hadm_ids = icd9_to_hadm_ids.get(icd9_code, [])
            
            # If we have titles for this code, use them
            if icd9_code in icd9_to_titles:
                short_title, long_title = icd9_to_titles[icd9_code]
                diagnosis_list.append({
                    "icd9_code": icd9_code,
                    "short_title": short_title,
                    "long_title": long_title,
                    "hadm_ids": hadm_ids
                })
            else:
                # If no titles found, provide default values
                diagnosis_list.append({
                    "icd9_code": icd9_code,
                    "short_title": "Unknown",
                    "long_title": "Unknown",
                    "hadm_ids": hadm_ids
                })
        
        return diagnosis_list
    
    except Exception as e:
        logger.error(f"Error in get_patient_diagnoses_mimic: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/admission_details",
    response_model=AdmissionResponse,
    summary="Get admission details for a given hospital admission ID",
    response_description="Admission details including admission time, discharge time, and diagnosis.")
def get_admission_details(
    hadm_id: int = Query(..., description="Hospital admission ID to get details for"),
    db: Session = Depends(get_db)):
    try:
        # Query admission information
        admission = db.query(Admission).filter(Admission.HADM_ID == hadm_id).first()
        
        if not admission:
            raise HTTPException(status_code=404, detail=f"Admission with ID {hadm_id} not found")
        
        # Create response object
        response = AdmissionResponse(
            hadm_id=admission.HADM_ID,
            admission_time=str(admission.ADMITTIME) if admission.ADMITTIME else "",
            discharge_time=str(admission.DISCHTIME) if admission.DISCHTIME else "",
            diagnosis=admission.DIAGNOSIS if admission.DIAGNOSIS else ""
        )
        
        return response
    
    except Exception as e:
        logger.error(f"Error in get_admission_details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    

