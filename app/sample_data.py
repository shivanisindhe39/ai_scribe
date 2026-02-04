SAMPLE_REQUEST = {
    "patient_info": {
        "name": "Jane Doe",
        "age": 45,
        "sex": "F",
        "mrn": "123456",
        "pmh": ["hypertension", "type 2 diabetes"],
    },
    "visit_context": "Primary care follow-up for diabetes and blood pressure.",
    "transcript": (
        "Patient reports increased thirst and fatigue over the last month. "
        "She has been taking metformin but missed doses this week. "
        "Denies chest pain or shortness of breath. "
        "Vitals today: BP 148/92, HR 82, weight 198 lb. "
        "Exam: clear lungs, regular heart rhythm. "
        "Plan discussed: reinforce medication adherence, "
        "check A1c and CMP, and follow up in 3 months."
    ),
}

SAMPLE_CLINICAL_CHECK_REQUEST = {
    "patient_info": {
        "name": "Jane Doe",
        "age": 45,
        "sex": "F",
        "mrn": "123456",
    },
    "soap_note": {
        "subjective": "Reports increased thirst and fatigue. Missed metformin doses.",
        "objective": "BP 148/92, HR 82, weight 198 lb. Lungs clear.",
        "assessment": "Type 2 diabetes, hypertension.",
        "plan": "Check A1c and CMP, reinforce adherence, follow up in 3 months.",
    },
}
