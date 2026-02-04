import json
import requests
import streamlit as st

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="AI Medical Scribe", layout="wide")
st.title("🩺 AI Medical Scribe + Clinical Safety Check (Local Ollama)")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Input")
    patient_info = st.text_area(
        "Patient Info (JSON)",
        value=json.dumps({
            "age": 56,
            "sex": "F",
            "pmh": ["Hypertension", "Type 2 Diabetes"],
            "meds": ["Metformin"],
            "allergies": ["NKDA"]
        }, indent=2),
        height=220
    )

    visit_context = st.text_input(
        "Visit Context",
        value="Primary care follow-up for diabetes and blood pressure"
    )

    transcript = st.text_area(
        "Transcript",
        value="Patient reports fatigue and increased thirst. Missed some metformin doses. No chest pain. BP 148/92 HR 82. Plan: reinforce adherence, order HbA1c and CMP, follow up in 3 months.",
        height=180
    )

    if st.button("Generate Scribe Output"):
        try:
            payload = {
                "patient_info": json.loads(patient_info),
                "visit_context": visit_context,
                "transcript": transcript
            }
            r = requests.post(f"{API_BASE}/scribe", json=payload, timeout=120)
            r.raise_for_status()
            st.session_state["scribe_output"] = r.json()
            st.success("✅ Scribe output generated!")
        except Exception as e:
            st.error(f"❌ Error: {e}")

with col2:
    st.subheader("Output")
    scribe_output = st.session_state.get("scribe_output")

    if scribe_output:
        st.markdown("### 📝 Scribe Output")
        st.json(scribe_output)

        st.divider()
        st.markdown("### ✅ Clinical Safety Check")

        if st.button("Run Safety Check"):
            try:
                payload = {
                    "patient_info": json.loads(patient_info),
                    "soap_note": scribe_output["soap_note"]
                }
                r = requests.post(f"{API_BASE}/clinical-check", json=payload, timeout=120)
                r.raise_for_status()
                st.session_state["safety_output"] = r.json()
                st.success("✅ Safety check generated!")
            except Exception as e:
                st.error(f"❌ Error: {e}")

    safety_output = st.session_state.get("safety_output")
    if safety_output:
        st.json(safety_output)

