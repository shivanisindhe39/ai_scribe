from typing import Any, Dict, List

from pydantic import BaseModel, Field


class ScribeRequest(BaseModel):
    patient_info: Dict[str, Any] = Field(
        ...,
        description="Patient demographics and background in key-value form.",
        examples=[
            {
                "name": "Jane Doe",
                "age": 45,
                "sex": "F",
                "mrn": "123456",
            }
        ],
    )
    transcript: str = Field(
        ...,
        description="Clinician-patient visit transcript.",
        min_length=1,
    )
    visit_context: str = Field(
        ...,
        description="High-level context for the visit.",
    )


class SOAPNote(BaseModel):
    subjective: str
    objective: str
    assessment: str
    plan: str


class CodeSuggestion(BaseModel):
    code: str
    description: str


class ScribeResponse(BaseModel):
    soap_note: SOAPNote
    problem_list: List[str]
    meds: List[str]
    allergies: List[str]
    icd10_suggestions: List[CodeSuggestion]
    cpt_suggestions: List[CodeSuggestion]


class ClinicalCheckRequest(BaseModel):
    patient_info: Dict[str, Any] = Field(
        ...,
        description="Patient demographics and background in key-value form.",
    )
    soap_note: SOAPNote


class ClinicalCheckResponse(BaseModel):
    missing_information: List[str]
    safety_flags: List[str]
    follow_up_questions: List[str]
    disclaimer: str
