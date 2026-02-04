from fastapi import FastAPI, HTTPException
from pydantic import ValidationError

from .llm import generate_clinical_check, generate_scribe_response
from .rules import DISCLAIMER, run_rules
from .schemas import (
    ClinicalCheckRequest,
    ClinicalCheckResponse,
    ScribeRequest,
    ScribeResponse,
)

app = FastAPI(title="AI Medical Scribe")


@app.post("/scribe", response_model=ScribeResponse)
def scribe(payload: ScribeRequest) -> ScribeResponse:
    try:
        llm_data = generate_scribe_response(
            patient_info=payload.patient_info,
            transcript=payload.transcript,
            visit_context=payload.visit_context,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="LLM call failed") from exc

    try:
        try:
            validated = ScribeResponse.model_validate(llm_data)
        except AttributeError:
            validated = ScribeResponse.parse_obj(llm_data)
    except ValidationError as exc:
        raise HTTPException(
            status_code=500, detail="LLM response validation failed"
        ) from exc

    return validated


def _merge_unique(items_a: list[str], items_b: list[str]) -> list[str]:
    seen: set[str] = set()
    merged: list[str] = []
    for item in items_a + items_b:
        normalized = item.strip()
        if not normalized:
            continue
        key = normalized.lower()
        if key in seen:
            continue
        seen.add(key)
        merged.append(normalized)
    return merged


@app.post("/clinical-check", response_model=ClinicalCheckResponse)
def clinical_check(payload: ClinicalCheckRequest) -> ClinicalCheckResponse:
    rules_output = run_rules(payload.patient_info, payload.soap_note)

    try:
        try:
            soap_note_data = payload.soap_note.model_dump()
        except AttributeError:
            soap_note_data = payload.soap_note.dict()
        llm_output = generate_clinical_check(
            patient_info=payload.patient_info,
            soap_note=soap_note_data,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="LLM call failed") from exc

    missing_information = _merge_unique(
        rules_output.get("missing_information", []),
        llm_output.get("missing_information", []),
    )
    safety_flags = _merge_unique(
        rules_output.get("safety_flags", []),
        llm_output.get("safety_flags", []),
    )
    follow_up_questions = _merge_unique(
        rules_output.get("follow_up_questions", []),
        llm_output.get("follow_up_questions", []),
    )

    response_data = {
        "missing_information": missing_information,
        "safety_flags": safety_flags,
        "follow_up_questions": follow_up_questions,
        "disclaimer": llm_output.get("disclaimer") or DISCLAIMER,
    }

    try:
        try:
            validated = ClinicalCheckResponse.model_validate(response_data)
        except AttributeError:
            validated = ClinicalCheckResponse.parse_obj(response_data)
    except ValidationError as exc:
        raise HTTPException(
            status_code=500, detail="Clinical check response validation failed"
        ) from exc

    return validated
