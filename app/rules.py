from typing import Any, Dict, List, Optional

from .schemas import SOAPNote

DISCLAIMER = (
    "This tool is for documentation review only. "
    "It does not provide medical advice, diagnosis, or treatment."
)


def _normalize_text(soap_note: SOAPNote) -> str:
    return " ".join(
        [
            soap_note.subjective,
            soap_note.objective,
            soap_note.assessment,
            soap_note.plan,
        ]
    ).lower()


def _get_age(patient_info: Dict[str, Any]) -> Optional[int]:
    age = patient_info.get("age")
    if age is None:
        return None
    if isinstance(age, int):
        return age
    if isinstance(age, str):
        try:
            return int(age.strip())
        except ValueError:
            return None
    return None


def _get_sex(patient_info: Dict[str, Any]) -> str | None:
    sex = patient_info.get("sex") or patient_info.get("gender")
    if not sex:
        return None
    return str(sex).strip().lower()


def run_rules(patient_info: Dict[str, Any], soap_note: SOAPNote) -> Dict[str, List[str]]:
    missing_information: List[str] = []
    safety_flags: List[str] = []
    follow_up_questions: List[str] = []

    text = _normalize_text(soap_note)
    age = _get_age(patient_info)
    sex = _get_sex(patient_info)

    allergies = patient_info.get("allergies") or patient_info.get("allergy")
    if not allergies and "allerg" not in text:
        missing_information.append("Allergy status is not documented.")
        follow_up_questions.append("Any medication, food, or environmental allergies?")

    if sex in {"f", "female", "woman", "girl"} and age is not None and 12 <= age <= 55:
        if "pregnan" not in text and "lmp" not in text:
            missing_information.append("Pregnancy status is not documented.")
            follow_up_questions.append("Is there any chance of pregnancy?")

    if age is not None and age < 18:
        safety_flags.append(
            "Flag for review: pediatric patient; check documentation for "
            "age-appropriate dosing and consent."
        )
    if age is not None and age >= 65:
        safety_flags.append(
            "Flag for review: older adult; check documentation for fall risk "
            "and polypharmacy concerns."
        )

    if "chest pain" in text and "ecg" not in text and "ekg" not in text:
        follow_up_questions.append("Was any cardiac workup performed or discussed?")

    return {
        "missing_information": missing_information,
        "safety_flags": safety_flags,
        "follow_up_questions": follow_up_questions,
    }
