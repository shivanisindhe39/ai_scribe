SYSTEM_PROMPT = (
    "You are an AI medical scribe. Create a concise, clinically accurate summary "
    "based only on the provided information. Do not invent facts. "
    "Return ONLY valid JSON matching the required schema."
)

USER_PROMPT_TEMPLATE = """Patient info (JSON):
{patient_info}

Visit context:
{visit_context}

Transcript:
{transcript}

Return JSON exactly with this shape:
{{
  "soap_note": {{
    "subjective": "...",
    "objective": "...",
    "assessment": "...",
    "plan": "..."
  }},
  "problem_list": ["..."],
  "meds": ["..."],
  "allergies": ["..."],
  "icd10_suggestions": [
    {{"code": "...", "description": "..."}}
  ],
  "cpt_suggestions": [
    {{"code": "...", "description": "..."}}
  ]
}}
"""

CLINICAL_SAFETY_SYSTEM_PROMPT = (
    "You are a clinical documentation safety checker. "
    "You do NOT provide medical advice. "
    "Only suggest questions to ask or flags for review. "
    "Return ONLY valid JSON matching the required schema."
)

CLINICAL_SAFETY_USER_PROMPT = """Patient info (JSON):
{patient_info}

SOAP note (JSON):
{soap_note}

Return JSON exactly with this shape:
{{
  "missing_information": ["..."],
  "safety_flags": ["..."],
  "follow_up_questions": ["..."],
  "disclaimer": "..."
}}

Rules:
- Do NOT give medical advice or recommendations.
- Use neutral language: "Review ...", "Confirm ...", "Ask ...".
- If nothing is missing, return an empty list for missing_information.
"""
