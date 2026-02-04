import json
import os
import re
import traceback
from pathlib import Path
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv
from openai import OpenAI

from .prompts import (
    CLINICAL_SAFETY_SYSTEM_PROMPT,
    CLINICAL_SAFETY_USER_PROMPT,
    SYSTEM_PROMPT,
    USER_PROMPT_TEMPLATE,
)

# ======================
# ENV / CONFIG
# ======================
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

if LLM_PROVIDER == "openai" and not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY missing but LLM_PROVIDER=openai")

# ======================
# LLM CALLS
# ======================
def _ollama_chat(messages: List[Dict[str, str]], temperature: float) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "options": {"temperature": temperature},
        "stream": False,
    }
    r = requests.post(OLLAMA_URL, json=payload, timeout=120)
    r.raise_for_status()
    return r.json()["message"]["content"]


def _openai_chat(messages: List[Dict[str, str]], temperature: float) -> str:
    if _client is None:
        raise RuntimeError("OpenAI client not initialized")

    resp = _client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        temperature=temperature,
    )
    if not resp.choices:
        raise RuntimeError("No choices returned by OpenAI")
    return resp.choices[0].message.content or ""


def _chat(messages: List[Dict[str, str]], temperature: float) -> str:
    if LLM_PROVIDER == "ollama":
        return _ollama_chat(messages, temperature)
    return _openai_chat(messages, temperature)

# ======================
# PROMPT BUILDERS
# ======================
def _build_messages(
    patient_info: Dict[str, Any],
    transcript: str,
    visit_context: str,
) -> List[Dict[str, str]]:
    user_prompt = USER_PROMPT_TEMPLATE.format(
        patient_info=json.dumps(patient_info, indent=2),
        transcript=transcript,
        visit_context=visit_context,
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]


def _build_clinical_messages(
    patient_info: Dict[str, Any],
    soap_note: Dict[str, Any],
) -> List[Dict[str, str]]:
    user_prompt = CLINICAL_SAFETY_USER_PROMPT.format(
        patient_info=json.dumps(patient_info, indent=2),
        soap_note=json.dumps(soap_note, indent=2),
    )
    return [
        {"role": "system", "content": CLINICAL_SAFETY_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

# ======================
# JSON HELPERS
# ======================
def _strip_code_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```.*?\n", "", text)
        text = re.sub(r"\n```$", "", text)
    return text


def _extract_json(text: str) -> Dict[str, Any]:
    text = _strip_code_fences(text)
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON found in LLM output")
    return json.loads(match.group(0))

# ======================
# PUBLIC API FUNCTIONS
# ======================
def generate_scribe_response(
    patient_info: Dict[str, Any],
    transcript: str,
    visit_context: str,
) -> Dict[str, Any]:
    messages = _build_messages(patient_info, transcript, visit_context)
    content = _chat(messages, temperature=0.2)
    return _extract_json(content)


def generate_clinical_check(
    patient_info: Dict[str, Any],
    soap_note: Dict[str, Any],
) -> Dict[str, Any]:
    messages = _build_clinical_messages(patient_info, soap_note)
    content = _chat(messages, temperature=0.1)
    return _extract_json(content)
